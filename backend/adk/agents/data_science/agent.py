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

from google.adk.agents import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.agent_tool import AgentTool

from .prompts import create_coordinator_instruction
from .sub_agents.analytics import analytics_agent
from .sub_agents.bigquery import bigquery_agent
from .sub_agents.bqml import bqml_agent
from .utils import load_cross_dataset_relations, load_dataset_config, reference_guide_rag

# Configure logging
_logger = logging.getLogger(__name__)
_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

# Configuration paths
CONFIG_DIR = Path(__file__).parent
DATASET_CONFIG_FILE = CONFIG_DIR / "dnb_datasets_config.json"
CROSS_DATASET_RELATIONS_FILE = CONFIG_DIR / "cross_dataset_relations.json"


class DatabaseSettings:
  """Database configuration and metadata."""
  
  def __init__(self, dataset_config: Dict[str, Any]):
    self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    self.dataset_id = os.getenv("BIGQUERY_DATASET_ID", "dnb_statistics")
    self.location = os.getenv("BIGQUERY_LOCATION", "us-central1")
    
    # Load dataset configuration
    self.datasets = dataset_config.get("datasets", {})
    self.tables = self._extract_tables()
    self.cross_dataset_relations = self._load_cross_dataset_relations()
    
  def _extract_tables(self) -> Dict[str, Any]:
    """Extract all tables from dataset configuration."""
    tables = {}
    for dataset_name, dataset_info in self.datasets.items():
      for table in dataset_info.get("tables", []):
        table_full_name = f"{self.dataset_id}.{table['name']}"
        tables[table_full_name] = {
          "dataset": dataset_name,
          "description": table.get("description", ""),
          "columns": table.get("columns", [])
        }
    return tables
  
  def _load_cross_dataset_relations(self) -> Optional[Dict[str, Any]]:
    """Load cross-dataset relations if available."""
    if CROSS_DATASET_RELATIONS_FILE.exists():
      try:
        with open(CROSS_DATASET_RELATIONS_FILE) as f:
          return json.load(f)
      except Exception as e:
        _logger.warning(f"Could not load cross-dataset relations: {e}")
    return None
  
  def get_context_for_instructions(self) -> str:
    """Generate context string for agent instructions."""
    context_parts = [
      f"Project: {self.project_id}",
      f"Dataset: {self.dataset_id}",
      f"Location: {self.location}",
      f"Available datasets: {', '.join(self.datasets.keys())}",
      f"Total tables: {len(self.tables)}"
    ]
    
    # Add dataset summaries
    for dataset_name, dataset_info in self.datasets.items():
      desc = dataset_info.get("description", "No description")
      table_count = len(dataset_info.get("tables", []))
      context_parts.append(f"\n{dataset_name}: {desc} ({table_count} tables)")
    
    return "\n".join(context_parts)


def init_database_settings(dataset_config: Dict[str, Any]) -> DatabaseSettings:
  """Initialize database settings from configuration."""
  return DatabaseSettings(dataset_config)


def load_database_settings_in_context(callback_context: CallbackContext) -> None:
  """Load database settings into callback context for sub-agents."""
  if hasattr(callback_context, "database_settings"):
    return  # Already loaded
  
  dataset_config = load_dataset_config()
  database_settings = init_database_settings(dataset_config)
  callback_context.database_settings = database_settings
  
  # Also load reference guide if available
  if hasattr(reference_guide_rag, "load_reference_guide"):
    callback_context.reference_guide = reference_guide_rag.load_reference_guide()


def get_bigquery_agent() -> Agent:
  """Create and configure the BigQuery sub-agent with Chase SQL."""
  from .sub_agents.bigquery.agent import bigquery_agent
  
  # Enhance with Chase SQL if available
  if os.getenv("ENABLE_CHASE_SQL", "true").lower() == "true":
    _logger.info("Chase SQL enabled for BigQuery agent")
    # Chase SQL configuration will be handled in the bigquery agent module
  
  return bigquery_agent


def get_analytics_agent() -> Agent:
  """Create and configure the analytics sub-agent."""
  return analytics_agent.analytics_agent if hasattr(analytics_agent, 'analytics_agent') else analytics_agent


def get_bqml_agent() -> Agent:
  """Create and configure the BQML sub-agent."""
  return bqml_agent.bqml_agent if hasattr(bqml_agent, 'bqml_agent') else bqml_agent


def get_root_agent() -> Agent:
  """Create and configure the root data science coordinator agent.

  Returns:
    Configured Agent for coordinating data science operations
  """
  # Load configurations
  dataset_config = load_dataset_config()
  database_settings = init_database_settings(dataset_config)
  
  # Configure sub-agents based on environment
  sub_agents = []
  
  # BigQuery agent for database operations
  if os.getenv("DISABLE_BIGQUERY_AGENT", "").lower() != "true":
    bigquery_agent_instance = get_bigquery_agent()
    sub_agents.append(bigquery_agent_instance)
    _logger.info("BigQuery agent enabled with Chase SQL support")
  
  # BQML agent for machine learning
  if os.getenv("DISABLE_BQML_AGENT", "").lower() != "true":
    bqml_agent_instance = get_bqml_agent()
    sub_agents.append(bqml_agent_instance)
    _logger.info("BQML agent enabled")
  
  # Analytics agent for data analysis and visualization
  if os.getenv("DISABLE_ANALYTICS_AGENT", "").lower() != "true":
    analytics_agent_instance = get_analytics_agent()
    sub_agents.append(analytics_agent_instance)
    _logger.info("Analytics agent enabled with Code Interpreter")
  
  # Create coordinator tools using AgentTool pattern
  tools = []
  
  if any(agent.name == "bigquery_agent" for agent in sub_agents):
    tools.append(
      AgentTool(
        agent_name="bigquery_agent",
        description="Query BigQuery databases using natural language. Handles SQL generation and execution.",
      )
    )
  
  if any(agent.name == "analytics_agent" for agent in sub_agents):
    tools.append(
      AgentTool(
        agent_name="analytics_agent",
        description="Perform data analysis, create visualizations, and run Python code for statistical analysis.",
      )
    )
  
  if any(agent.name == "bqml_agent" for agent in sub_agents):
    tools.append(
      AgentTool(
        agent_name="bqml_agent",
        description="Build and deploy machine learning models using BigQuery ML.",
      )
    )
  
  # Create the coordinator agent
  coordinator = Agent(
    name="data_science_coordinator",
    model=os.getenv("DATA_SCIENCE_MODEL", "gemini-2.0-flash-exp"),
    instruction=create_coordinator_instruction(database_settings.get_context_for_instructions()),
    description="Coordinates data science operations across BigQuery, analytics, and ML sub-agents",
    tools=tools,
    agents=sub_agents,
    before_call_hook=load_database_settings_in_context,
  )
  
  return coordinator


# Export the agent using ADK convention
root_agent = get_root_agent()

# Also export as data_science_coordinator for compatibility
data_science_coordinator = root_agent

_logger.info("Orkhon Data Science Coordinator ready with enhanced capabilities")
