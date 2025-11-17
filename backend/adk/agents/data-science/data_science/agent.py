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

from __future__ import annotations

import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .prompts import return_instructions_root
from .sub_agents import bqml_agent
from .sub_agents.alloydb.tools import (
    get_database_settings as get_alloydb_database_settings,
)
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
from .tools import call_alloydb_agent, call_analytics_agent, call_bigquery_agent

logger = logging.getLogger(__name__)

# Initialize module-level config variables
_dataset_config = {}
_database_settings = {}
_supported_dataset_types = ["bigquery", "alloydb"]
_required_dataset_config_params = ["name", "description"]


def load_dataset_config() -> dict[str, Any]:
    """Load the dataset configuration from a JSON file.
    
    The config file path is determined in the following priority:
    1. DATASET_CONFIG_FILE environment variable (absolute or relative path)
    2. Default: dnb_dataset_config.json in the agent directory
    
    For Orkhon project, this should point to the DNB-specific configuration
    with BigQuery datasets for DNB statistics and public register data.
    """
    # Get the directory where this agent.py file is located
    agent_dir = Path(__file__).parent.parent
    
    # Check environment variable first
    dataset_config_file_env = os.getenv("DATASET_CONFIG_FILE", "")
    
    if dataset_config_file_env:
        # Use environment variable (support both absolute and relative paths)
        config_path = Path(dataset_config_file_env)
        if not config_path.is_absolute():
            # Try relative to agent directory first
            config_path = agent_dir / dataset_config_file_env
            if not config_path.exists():
                # Try relative to current working directory
                config_path = Path(dataset_config_file_env).resolve()
        dataset_config_file = str(config_path)
    else:
        # Default to DNB config in agent directory
        dataset_config_file = str(agent_dir / "dnb_dataset_config.json")
    
    if not os.path.exists(dataset_config_file):
        raise FileNotFoundError(
            f"Dataset config file not found: {dataset_config_file}\n"
            f"Agent directory: {agent_dir}\n"
            f"Current working directory: {os.getcwd()}\n"
            f"DATASET_CONFIG_FILE env var: {dataset_config_file_env or '(not set)'}\n"
            f"\nTo fix:\n"
            f"1. Set DATASET_CONFIG_FILE=dnb_dataset_config.json in your .env file\n"
            f"2. Or create {agent_dir / 'dnb_dataset_config.json'}"
        )

    logger.info(f"Loading dataset config from: {dataset_config_file}")
    
    with open(dataset_config_file, "r", encoding="utf-8") as f:
        dataset_config = json.load(f)

    if "datasets" not in dataset_config:
        logger.fatal("No 'datasets' entry in dataset config")

    for dataset in dataset_config["datasets"]:
        if "type" not in dataset:
            logger.fatal("Missing dataset type")
        if dataset["type"] not in _supported_dataset_types:
            logger.fatal("Dataset type '%s' not supported", dataset["type"])

        for p in _required_dataset_config_params:
            if p not in dataset:
                logger.fatal(
                    "Missing required param '%s' from %s dataset config",
                    p,
                    dataset["type"],
                )

    return dataset_config


def get_database_settings(db_type: str) -> dict:
    """Wrapper function to get database settings by type"""
    assert db_type in _supported_dataset_types
    if db_type == "bigquery":
        return get_bq_database_settings()
    else:
        return get_alloydb_database_settings()


def init_database_settings(dataset_config: dict) -> dict:
    """Initializes the database settings for the configured datasets"""
    db_settings = {}
    for dataset in dataset_config["datasets"]:
        db_settings[dataset["type"]] = get_database_settings(dataset["type"])
    return db_settings


def load_database_settings_in_context(callback_context: CallbackContext):
    """Load database settings into the callback context on first use."""
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = _database_settings


def get_dataset_definitions_for_instructions() -> str:
    """Returns the dataset definitions instructions block"""

    dataset_definitions = """
<DATASETS>
"""
    for dataset in _dataset_config["datasets"]:
        dataset_type = dataset["type"]
        dataset_definitions += f"""
<{dataset_type.upper()}>
<DESCRIPTION>
{dataset["description"]}
</DESCRIPTION>
<SCHEMA>
--------- The schema of the relevant database with a few sample rows. --------
{_database_settings[dataset_type]["schema"]}
</SCHEMA>
</{dataset_type.upper()}>

"""
    dataset_definitions += """
</DATASETS>
"""

    if "cross_dataset_relations" in _dataset_config:
        dataset_definitions += f"""
<CROSS_DATASET_RELATIONS>
--------- The cross dataset relations between the configured datasets. ---------
{_dataset_config["cross_dataset_relations"]}
</CROSS_DATASET_RELATIONS>
"""

    return dataset_definitions


# Global variable to prevent re-initialization
_root_agent_instance = None

# Import factory functions, not singleton instances
from .sub_agents.bqml.agent import create_bqml_agent
# Add factories for other sub-agents too

def get_root_agent() -> LlmAgent:
    """Factory function creating fresh agent hierarchy.
    
    Returns:
        New root agent with fresh sub-agent instances.
    """
    
    # Create fresh sub-agent instances
    analytics_agent = LlmAgent(
        name="analytics_agent",
        model=_MODEL_ID,
        instruction=return_instructions_analytics_agent(_MODEL_ID),
        description=_ANALYTICS_AGENT_DESCRIPTION,
        tools=[call_alloydb_agent, call_bigquery_agent],
        config=_get_agent_config(_MODEL_ID, temperature=0.01),
    )
    
    # Create fresh BQML agent instance
    bqml_agent_instance = create_bqml_agent()
    
    # Create fresh BigQuery agent instance
    bigquery_agent = create_bigquery_agent()  # Similar factory
    
    # Create fresh AlloyDB agent instance
    alloydb_agent = create_alloydb_agent()  # Similar factory
    
    return LlmAgent(
        name="data_science_root_agent",
        model=_MODEL_ID,
        instruction=return_instructions_root(),
        description=_ROOT_AGENT_DESCRIPTION,
        sub_agents=[
            analytics_agent,
            bqml_agent_instance,  # Use fresh instance
            bigquery_agent,
            alloydb_agent,
        ],
        tools=[call_analytics_agent],
        config=_get_agent_config(_MODEL_ID, temperature=0.01),
    )

# Create singleton for module-level access
root_agent = get_root_agent()


# Initialize dataset configurations and database info before the agent starts
_dataset_config = load_dataset_config()
_database_settings = init_database_settings(_dataset_config)


# Fetch the root agent
root_agent = get_root_agent()
