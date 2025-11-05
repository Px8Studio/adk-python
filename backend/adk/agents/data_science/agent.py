# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Top-level data science coordinator agent for Orkhon Data Science Multi-Agent System.

This agent coordinates between specialized sub-agents for:
- BigQuery database access (NL2SQL with Chase SQL)
- Analytics and visualization (NL2Py with Code Interpreter)
- BQML for machine learning operations
"""

from __future__ import annotations

import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.adk.agents.callback_context import CallbackContext  # Correct import
from google.adk.agents.llm_agent import LlmAgent as Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.genai import types

# Import sub-agents - use relative imports for local modules
from .sub_agents.analytics.agent import get_analytics_agent
from .sub_agents.bigquery.agent import get_bigquery_agent
from .sub_agents.bqml.agent import root_agent as bqml_agent

_logger = logging.getLogger(__name__)

# Module-level configuration
_dataset_config: dict = {}
_database_settings: dict = {}
_supported_dataset_types = ["bigquery"]
_required_dataset_config_params = ["name", "description"]


def load_dataset_config() -> dict:
  """Load dataset configuration from JSON file."""
  config_path = Path(__file__).parent / "dnb_datasets_config.json"
  
  if not config_path.exists():
    _logger.warning(f"Dataset config not found at {config_path}")
    return {"datasets": {}}
  
  try:
    with open(config_path) as f:
      return json.load(f)
  except Exception as e:
    _logger.error(f"Failed to load dataset config: {e}")
    return {"datasets": {}}


def get_database_settings(db_type: str) -> dict:
  """Get database settings for a specific type.
  
  Args:
    db_type: Type of database (e.g., "bigquery")
  
  Returns:
    Database configuration dictionary
  """
  if db_type not in _supported_dataset_types:
    raise ValueError(f"Unsupported database type: {db_type}")
  
  return _database_settings.get(db_type, {})


def init_database_settings(dataset_config: dict) -> dict:
  """Initialize database settings from configuration.
  
  Args:
    dataset_config: Dataset configuration dictionary
  
  Returns:
    Initialized database settings
  """
  settings = {
    "bigquery": {
      "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
      "dataset_id": os.getenv("BQ_DATASET_ID", "dnb_statistics"),
      "location": os.getenv("BIGQUERY_LOCATION", "us-central1"),
      "datasets": dataset_config.get("datasets", {})
    }
  }
  
  return settings


def get_dataset_definitions_for_instructions() -> str:
  """Generate dataset definitions for agent instructions."""
  if not _dataset_config:
    return "No datasets configured."
  
  definitions = []
  datasets = _dataset_config.get("datasets", [])
  
  # Handle both list and dict formats for backwards compatibility
  if isinstance(datasets, dict):
    for dataset_name, dataset_info in datasets.items():
      desc = dataset_info.get("description", "No description")
      table_count = len(dataset_info.get("tables", []))
      definitions.append(f"- {dataset_name}: {desc} ({table_count} tables)")
  elif isinstance(datasets, list):
    for dataset_info in datasets:
      dataset_name = dataset_info.get("name", "unknown")
      desc = dataset_info.get("description", "No description")
      schema = dataset_info.get("schema", {})
      table_count = len(schema.get("tables", {}))
      definitions.append(f"- {dataset_name}: {desc} ({table_count} tables)")
  
  return "\n".join(definitions) if definitions else "No datasets available."


def emit_progress_event(callback_context: CallbackContext, message: str) -> None:
  """Emit progress update to user (placeholder for future ADK feature)."""
  _logger.info(f"Progress: {message}")
  # Future: callback_context.emit_event(types.Event(message=message))


def load_database_settings_in_context(callback_context: CallbackContext) -> None:
  """Load database settings into callback context for sub-agents."""
  if hasattr(callback_context, "database_settings"):
    return  # Already loaded
  
  dataset_config = load_dataset_config()
  database_settings = init_database_settings(dataset_config)
  callback_context.set_in_context("database_settings", database_settings)
  
  _logger.debug(f"Loaded database settings: {database_settings}")


def get_root_agent() -> Agent:
  """Create and configure the root data science coordinator agent.
  
  Returns:
    Configured Agent for coordinating data science operations
  """
  # Load configurations
  dataset_config = load_dataset_config()
  database_settings = init_database_settings(dataset_config)
  
  # Store in module globals for access by sub-agents
  global _dataset_config, _database_settings
  _dataset_config = dataset_config
  _database_settings = database_settings
  
  # Build instruction with dataset context
  instruction = f"""You are the Orkhon Data Science Coordinator, an advanced AI system 
that orchestrates specialized agents for data analysis, database queries, and machine learning.

You have access to the following sub-agents:
1. BigQuery Agent - For SQL queries and database access
2. Analytics Agent - For Python-based data analysis and visualization  
3. BQML Agent - For BigQuery ML model training and prediction

Available Datasets:
{get_dataset_definitions_for_instructions()}

Database Configuration:
- Project: {database_settings['bigquery']['project_id']}
- Dataset: {database_settings['bigquery']['dataset_id']}
- Location: {database_settings['bigquery']['location']}

When a user asks a question:
1. Analyze if it requires database access (use BigQuery agent)
2. Determine if it needs data analysis or visualization (use Analytics agent)
3. Check if it involves machine learning (use BQML agent)
4. Coordinate between agents as needed for complex tasks

Always provide clear, actionable insights from the data.
"""
  
  # Configure sub-agents
  sub_agents = []
  
  # Add BigQuery agent
  try:
    bigquery = get_bigquery_agent()
    sub_agents.append(bigquery)
    _logger.info("BigQuery agent loaded")
  except Exception as e:
    _logger.warning(f"Could not load BigQuery agent: {e}")
  
  # Add Analytics agent
  try:
    analytics = get_analytics_agent()
    sub_agents.append(analytics)
    _logger.info("Analytics agent loaded")
  except Exception as e:
    _logger.warning(f"Could not load Analytics agent: {e}")
  
  # Add BQML agent
  try:
    sub_agents.append(bqml_agent)
    _logger.info("BQML agent loaded")
  except Exception as e:
    _logger.warning(f"Could not load BQML agent: {e}")
  
  # Create the coordinator agent
  coordinator = Agent(
    name="data_science_coordinator",
    model=os.getenv("DATA_SCIENCE_MODEL", "gemini-2.0-flash-exp"),
    instruction=instruction,
    description="Coordinates data science operations across BigQuery, analytics, and ML sub-agents",
    tools=[load_artifacts_tool],
    sub_agents=sub_agents,
    before_agent_callback=load_database_settings_in_context,
  )
  
  return coordinator


# Initialize configuration on module load
_logger.info("Loading Orkhon Data Science Coordinator...")
_dataset_config = load_dataset_config()
_database_settings = init_database_settings(_dataset_config)

# Export BOTH the instance (for your current usage) AND the factory
root_agent = get_root_agent()
data_science_coordinator = root_agent  # Alias for compatibility

# This allows both patterns:
# from adk.agents.data_science import data_science_coordinator  # Your current way
# from adk.agents.data_science.agent import root_agent  # ADK standard way

_logger.info("Orkhon Data Science Coordinator ready")
