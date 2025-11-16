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

"""Root orchestrator agent for the Orkhon multi-agent system.

This agent coordinates between specialized coordinator agents that handle
different API domains (DNB, etc.). It delegates queries to the appropriate
coordinator based on the user's intent.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from google.adk.agents import Agent

from api_coordinators.dnb_coordinator.agent import (
  get_dnb_coordinator_agent,
)

def _try_import_data_science_agent() -> Optional[object]:
  """Load the data-science agent as a proper package import.

  Why: The sample lives under "agents/data-science/data_science/agent.py" and
  uses relative imports like "from .prompts import ...". Loading by file path
  breaks those. Instead, temporarily add the outer folder to sys.path and
  import "data_science.agent" so Python resolves relatives correctly.
  """
  try:
    here = Path(__file__).resolve()
    outer_dir = here.parent.parent / "data-science"
    inner_pkg = outer_dir / "data_science"
    agent_file = inner_pkg / "agent.py"

    if not agent_file.exists():
      logging.error("Data-science agent file not found at %s", agent_file)
      return None

    # Ensure dataset config has a sane default if not provided by env/CLI
    # This avoids fatal logs inside the data_science module during import.
    import os as _os  # local import to avoid polluting module scope
    if not _os.getenv("DATASET_CONFIG_FILE"):
      # Prefer a DNB-oriented config if present, else fall back to flights.
      default_cfg = "dnb_dataset_config.json"
      if not (outer_dir / default_cfg).exists():
        default_cfg = "flights_dataset_config.json"
      _os.environ.setdefault("DATASET_CONFIG_FILE", default_cfg)

    # Add the outer folder so that "import data_science.agent" works
    outer_str = str(outer_dir)
    if outer_str not in sys.path:
      sys.path.insert(0, outer_str)

    import importlib as _il
    module = _il.import_module("data_science.agent")

    getter = getattr(module, "get_root_agent", None)
    if callable(getter):
      return getter()
    agent_obj = getattr(module, "root_agent", None)
    if agent_obj is not None:
      return agent_obj
    logging.warning(
        "Data-science module loaded but missing get_root_agent/root_agent"
    )
  except Exception:
    logging.exception(
        "Data-science root agent unavailable; continuing without it"
    )
  return None

# Build root agent following ADK conventions

def get_root_agent() -> Agent:
  """Create the root agent with sub-agents for API coordination."""
  import os as _os
  
  # Ensure dataset config has a sane default if not provided
  if not _os.getenv("DATASET_CONFIG_FILE"):
    # Check for DNB config first, fallback to flights
    here = Path(__file__).resolve()
    outer_dir = here.parent.parent / "data-science"
    default_cfg = "dnb_dataset_config.json"
    if not (outer_dir / default_cfg).exists():
      default_cfg = "flights_dataset_config.json"
    _os.environ.setdefault("DATASET_CONFIG_FILE", default_cfg)
  
  dnb_coordinator = get_dnb_coordinator_agent()

  # Load data science root agent
  data_science_root = _try_import_data_science_agent()

  sub_agents: list[Agent] = [dnb_coordinator]
  if data_science_root is not None:
    sub_agents.append(data_science_root)
  else:
    logging.warning(
        "Data-science root agent unavailable; continuing without it"
    )

  # Follow ADK sample pattern: pick model from env with a sensible default.
  # Use ROOT_AGENT_MODEL for consistency with data-science sample.
  model_name = _os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash")

  root = Agent(
      model=model_name,
      name="orkhon_root_agent",
      description="Orkhon root orchestrator for data science and API operations",
      instruction="""You are the Root Orchestrator for the Orkhon system.

CAPABILITIES:
You coordinate access to:
1. DNB API Operations (via dnb_coordinator_agent)
   - DNB Statistics API: Economic data, insurance/pension statistics, market data
   - DNB Public Register API: Financial institutions, publications, regulatory data
   - DNB Echo API: Health checks and connectivity tests

2. Data Science & Analytics (via data_science_root_agent)
   - BigQuery data warehouse queries (DNB insurance/statistics datasets already loaded)
   - Data analysis and visualization
   - Machine learning model training (BQML)
   - SQL query generation from natural language

WORKFLOW:
1. Understand user's intent
2. Route to appropriate sub-agent:
   - For DNB API access → transfer to dnb_coordinator_agent
   - For data analysis, BigQuery queries, ML → transfer to data_science_root_agent
3. Synthesize and present results clearly

IMPORTANT:
- The BigQuery data warehouse contains DNB insurance and statistics data
- Always prefer data warehouse queries over API calls for analytical tasks
- Be concise, accurate, and explain your reasoning
""",
      sub_agents=sub_agents,
  )
  return root


# Create the root agent instance
root_agent = get_root_agent()