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
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models import GeminiConfig
from google.adk.tools import vertex_ai_search

from .prompts import DATA_SCIENCE_INSTRUCTIONS
from .sub_agents.alloydb.agent import create_alloydb_agent
from .sub_agents.analytics.agent import create_analytics_agent
from .sub_agents.bigquery.agent import create_bigquery_agent
from .sub_agents.bqml.agent import create_bqml_agent
from .tools import create_hand_off_to_analytics_agent, create_hand_off_to_other_agent


logger = logging.getLogger(__name__)

# Module-level cache for singleton root agent
_root_agent_instance: LlmAgent | None = None


def load_dataset_config(config_path: str | Path) -> dict:
  """Load dataset configuration from JSON file."""
  config_path = Path(config_path)
  if not config_path.exists():
    raise FileNotFoundError(f"Dataset config not found: {config_path}")

  logger.info(f"Loading dataset config from: {config_path}")
  with open(config_path, "r", encoding="utf-8") as f:
    return json.load(f)


def get_project_root() -> Path:
  """Get the data-science agent root directory."""
  return Path(__file__).parent.resolve()


def get_dataset_config_path() -> Path:
  """Get the path to dnb_dataset_config.json."""
  # Go up one level from data_science/ to data-science/
  return get_project_root().parent / "dnb_dataset_config.json"


def create_sub_agents() -> dict[str, LlmAgent]:
  """Create all sub-agents and return them in a dictionary.
  
  This ensures each agent is only created once.
  """
  # Load dataset configuration
  config_path = get_dataset_config_path()
  dataset_config = load_dataset_config(config_path)

  # Create each sub-agent exactly once
  sub_agents = {}
  
  try:
    sub_agents["alloydb"] = create_alloydb_agent(dataset_config)
  except Exception as e:
    logger.warning(f"Failed to create AlloyDB agent: {e}")

  try:
    sub_agents["bigquery"] = create_bigquery_agent(dataset_config)
  except Exception as e:
    logger.warning(f"Failed to create BigQuery agent: {e}")

  try:
    sub_agents["bqml"] = create_bqml_agent(dataset_config)
  except Exception as e:
    logger.warning(f"Failed to create BQML agent: {e}")

  try:
    sub_agents["analytics"] = create_analytics_agent(dataset_config)
  except Exception as e:
    logger.warning(f"Failed to create Analytics agent: {e}")

  return sub_agents


def get_root_agent() -> LlmAgent:
  """Get or create the data science root agent.
  
  This implements a singleton pattern to ensure agents are only created once
  per module load.
  """
  global _root_agent_instance

  if _root_agent_instance is not None:
    return _root_agent_instance

  # Create all sub-agents once
  sub_agents = create_sub_agents()

  # Collect agents to add as sub-agents
  agents_list = []
  if "alloydb" in sub_agents:
    agents_list.append(sub_agents["alloydb"])
  if "bigquery" in sub_agents:
    agents_list.append(sub_agents["bigquery"])
  if "bqml" in sub_agents:
    agents_list.append(sub_agents["bqml"])
  if "analytics" in sub_agents:
    agents_list.append(sub_agents["analytics"])

  # Create hand-off tools
  tools = []
  if "analytics" in sub_agents:
    tools.append(create_hand_off_to_analytics_agent(sub_agents["analytics"]))
  if agents_list:
    tools.append(create_hand_off_to_other_agent(agents_list))

  # Add vertex AI search tool
  tools.append(vertex_ai_search)

  # Create the root agent with all sub-agents
  _root_agent_instance = LlmAgent(
    name="data_science_root_agent",
    model="gemini-2.5-flash",
    instruction=DATA_SCIENCE_INSTRUCTIONS,
    description="Data Science Expert Agent for BQML and Analytics",
    model_config=GeminiConfig(temperature=0.01),
    tools=tools,
    sub_agents=agents_list,  # Add all agents at once
  )

  return _root_agent_instance


# Create the root agent when module is imported
root_agent = get_root_agent()
