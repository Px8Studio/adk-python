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

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .prompts import return_instructions_root
from .sub_agents.analytics.agent import get_analytics_agent
from .sub_agents.bigquery.agent import get_bigquery_agent
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
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


def load_database_settings_in_context(callback_context: CallbackContext) -> None:
  """Load database settings into callback context.

  Args:
    callback_context: ADK callback context to store settings
  """
  if "database_settings" not in callback_context.state:
    callback_context.state["database_settings"] = _database_settings
    _logger.debug("Loaded database settings into context")


def get_root_agent() -> LlmAgent:
  """Create and configure the root coordinator agent.

  Returns:
    Configured LlmAgent instance with fresh sub-agent instances
  """
  sub_agents = []

  # Configure sub-agents based on dataset configuration
  for dataset in _dataset_config["datasets"]:
    if dataset["type"] == "bigquery":
      # Create fresh instance to avoid parent conflicts
      sub_agents.append(get_bigquery_agent())

  # Always include analytics agent
  sub_agents.append(get_analytics_agent())

  # ADK Pattern: Use sub_agents for LLM-driven delegation
  # The LLM automatically gets transfer_to_agent() function
  # NO manual tools needed - ADK handles agent communication
  agent = LlmAgent(
      model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
      name="data_science_coordinator",
      instruction=return_instructions_root()
      + get_dataset_definitions_for_instructions(),
      global_instruction=f"""
You are the Orkhon Data Science and Data Analytics Multi-Agent System.
Today's date: {date.today()}

You can delegate to specialized sub-agents:
- bigquery_agent: For database queries and data retrieval
- analytics_agent: For data analysis, visualization, and Python code execution
""",
      sub_agents=sub_agents,  # type: ignore
      before_agent_callback=load_database_settings_in_context,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )

  _logger.info(
      "Initialized root agent with %d sub-agents",
      len(sub_agents),
  )
  return agent


# Initialize configuration on module load
_logger.info("Loading Orkhon Data Science Multi-Agent System...")
_dataset_config = load_dataset_config()
_database_settings = init_database_settings(_dataset_config)

# Create the root agent
root_agent = get_root_agent()

_logger.info("Orkhon Data Science Multi-Agent System ready")
