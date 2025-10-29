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
- BigQuery database access (NL2SQL)
- Analytics and visualization (NL2Py with Code Interpreter)

Note: This agent is typically accessed as a sub-agent of the main root_agent,
but can also be run standalone for data science-specific workflows.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import date

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.load_artifacts_tool import load_artifacts_tool  # Import the actual tool instance
from google.genai import types

from .prompts import return_instructions_root
from .sub_agents.analytics.agent import get_analytics_agent
from .sub_agents.bigquery.agent import get_bigquery_agent
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
    get_dataset_definitions,
)

_logger = logging.getLogger(__name__)

# Module-level configuration
_dataset_config: dict = {}
_database_settings: dict = {}
_supported_dataset_types = ["bigquery"]
_required_dataset_config_params = ["name", "description"]


def load_dataset_config() -> dict:
  """Load dataset configuration from the config file.

  Returns:
    Dictionary containing dataset configuration

  Raises:
    SystemExit: If configuration file is missing or invalid
  """
  dataset_config_file = os.getenv(
      "DATASET_CONFIG_FILE",
      os.path.join(
          os.path.dirname(__file__), "dnb_datasets_config.json"
      ),
  )

  if not dataset_config_file or not os.path.exists(dataset_config_file):
    _logger.fatal("DATASET_CONFIG_FILE not found: %s", dataset_config_file)
    raise SystemExit(1)

  with open(dataset_config_file, "r", encoding="utf-8") as f:
    dataset_config = json.load(f)

  if "datasets" not in dataset_config:
    _logger.fatal("No 'datasets' entry in dataset config")
    raise SystemExit(1)

  # Validate dataset configuration
  for dataset in dataset_config["datasets"]:
    if "type" not in dataset:
      _logger.fatal("Missing dataset type in configuration")
      raise SystemExit(1)

    if dataset["type"] not in _supported_dataset_types:
      _logger.fatal("Dataset type '%s' not supported", dataset["type"])
      raise SystemExit(1)

    for param in _required_dataset_config_params:
      if param not in dataset:
        _logger.fatal(
            "Missing required param '%s' from %s dataset config",
            param,
            dataset["type"],
        )
        raise SystemExit(1)

  return dataset_config


def get_database_settings(db_type: str) -> dict:
  """Get database settings by type.

  Args:
    db_type: Type of database (currently only 'bigquery' supported)

  Returns:
    Dictionary containing database settings
  """
  if db_type not in _supported_dataset_types:
    raise ValueError(f"Unsupported database type: {db_type}")

  if db_type == "bigquery":
    # Get BigQuery dataset configurations from the dataset config
    bq_datasets = [
        ds for ds in _dataset_config["datasets"] if ds.get("type") == "bigquery"
    ]
    return get_bq_database_settings(dataset_configs=bq_datasets)

  return {}


def init_database_settings(dataset_config: dict) -> dict:
  """Initialize database settings for configured datasets.

  Args:
    dataset_config: Dataset configuration dictionary

  Returns:
    Dictionary mapping dataset types to their settings
  """
  db_settings = {}
  for dataset in dataset_config["datasets"]:
    db_type = dataset["type"]
    db_settings[db_type] = get_database_settings(db_type)
    _logger.info("Initialized %s database settings", db_type)

  return db_settings


def get_dataset_definitions_for_instructions() -> str:
  """Build dataset definitions section for agent instructions.

  Returns:
    Formatted string containing dataset information for the agent prompt
  """
  dataset_definitions = "\n<DATASETS>\n"

  for dataset in _dataset_config["datasets"]:
    dataset_type = dataset["type"]
    dataset_definitions += f"""
<{dataset_type.upper()}>
<DESCRIPTION>
{dataset["description"]}
</DESCRIPTION>
<SCHEMA>
--------- Schema of the {dataset_type} database with sample information ---------
{_database_settings.get(dataset_type, {}).get("schema", "Schema not available")}
</SCHEMA>
</{dataset_type.upper()}>
"""

  dataset_definitions += "\n</DATASETS>\n"

  # Add cross-dataset relations if configured
  if "cross_dataset_relations" in _dataset_config:
    dataset_definitions += f"""
<CROSS_DATASET_RELATIONS>
--------- Cross-dataset relations between configured datasets ---------
{json.dumps(_dataset_config["cross_dataset_relations"], indent=2)}
</CROSS_DATASET_RELATIONS>
"""

  return dataset_definitions


def emit_progress_event(callback_context: CallbackContext, message: str) -> None:
  """Emit progress update to user (placeholder for future ADK feature)."""
  # This is a workaround - ADK doesn't officially support progress events yet
  # But we can log them for observability
  _logger.info(f"[PROGRESS] {message}")
  # TODO: When ADK supports custom events, emit to SSE stream

def load_database_settings_in_context(callback_context: CallbackContext) -> None:
  """Load database settings into callback context for sub-agents."""
  db_settings = get_database_settings("bigquery")
  callback_context.set_value("database_settings", db_settings)
  emit_progress_event(callback_context, "Database connection initialized")


def get_root_agent() -> Agent:
  """Create and configure the root data science coordinator agent.

  Returns:
    Configured LlmAgent for coordinating data science operations
  """
  # Get dataset definitions using cached schemas
  dataset_definitions = get_dataset_definitions()

  # Configure sub-agents based on environment
  sub_agents = []

  # BigQuery agent for database operations
  if os.getenv("DISABLE_BIGQUERY_AGENT", "").lower() != "true":
    bigquery_agent = get_bigquery_agent()
    sub_agents.append(bigquery_agent)
    _logger.info("BigQuery agent enabled")
  else:
    _logger.info("BigQuery agent disabled via DISABLE_BIGQUERY_AGENT")

  # Analytics agent for data analysis and visualization
  if os.getenv("DISABLE_ANALYTICS_AGENT", "").lower() != "true":
    analytics_agent_instance = get_analytics_agent()
    sub_agents.append(analytics_agent_instance)
    _logger.info("Analytics agent enabled")
  else:
    _logger.info("Analytics agent disabled via DISABLE_ANALYTICS_AGENT")

  agent = Agent(
      model=os.getenv("DATA_SCIENCE_AGENT_MODEL", "gemini-2.0-flash-exp"),
      name="data_science_coordinator",  # Changed from "root_agent"
      description=(
          "Data science coordinator for BigQuery and analytics operations. "
          "Delegates to specialized sub-agents for database queries and analytics tasks."
      ),
      instruction=f"""
You are a data science coordinator managing specialized sub-agents.

Available Datasets:
{dataset_definitions}

Today's date: {date.today()}

You can delegate to specialized sub-agents:
- bigquery_agent: For database queries and data retrieval
- analytics_agent: For data analysis, visualization, and Python code execution

When analytics_agent generates charts/visualizations, they are saved as 
artifacts. Use the load_artifacts tool to reference and discuss generated 
visualizations.
""",
      sub_agents=sub_agents,  # type: ignore
      tools=[load_artifacts_tool],
      before_agent_callback=load_database_settings_in_context,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )

  _logger.info("Initialized data science coordinator with %d sub-agents", len(sub_agents))
  return agent


from google.adk.agents.llm_agent import LlmAgent as Agent

# Initialize configuration on module load
_logger.info("Loading Orkhon Data Science Coordinator...")
_dataset_config = load_dataset_config()
_database_settings = init_database_settings(_dataset_config)

# Create the coordinator agent (exported as root_agent for backward compat)
root_agent = get_root_agent()

_logger.info("Orkhon Data Science Coordinator ready")
