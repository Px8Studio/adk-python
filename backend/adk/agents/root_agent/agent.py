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

import os
import sys
from pathlib import Path
from typing import Any

from google.adk.agents.llm_agent import Agent
from google.genai import types


def get_root_agent() -> Agent:
  """Creates the root agent with sub-agents for API coordination.

  Returns:
      The root agent configured with coordinator sub-agents.
  """
  # Import coordinator agents at runtime to avoid module loading issues
  # Add the parent agents directory to sys.path for sibling package imports
  agents_dir = Path(__file__).parent.parent
  agents_dir_str = str(agents_dir)
  
  if agents_dir_str not in sys.path:
    sys.path.insert(0, agents_dir_str)
  
  try:
    # Import from sibling packages
    from api_coordinators import get_dnb_coordinator_agent  # type: ignore
    from data_science import root_agent as data_science_coordinator  # type: ignore
  except ImportError as e:
    raise ImportError(
        f"Failed to import coordinators. "
        f"Agents directory: {agents_dir_str}, "
        f"sys.path: {sys.path[:3]}..."
    ) from e

  # Get coordinator agents
  dnb_coordinator = get_dnb_coordinator_agent()

  # Model configuration from environment
  model_name = os.environ.get("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash-exp")
  
  # Build the root agent with sub-agents
  root = Agent(
      model=model_name,
      name="root_agent",
      instruction="""You are the Root Orchestrator for the Orkhon system.
          
Your role is to:
1. Understand the user's query and intent
2. Delegate to the appropriate coordinator agent:
   - dnb_coordinator: For DNB API queries (statistics, company info, public register)
   - data_science_coordinator: For data queries, analytics, visualizations, and BigQuery operations
3. Present results clearly to the user
4. Handle errors gracefully and provide helpful feedback

When routing queries:
- DNB API operations → dnb_coordinator
- Data science operations → data_science_coordinator
- Multi-domain workflows → chain operations between coordinators

Always explain what you're doing and why you're delegating to a specific coordinator.
""",
      sub_agents=[dnb_coordinator, data_science_coordinator]
  )

  return root


# Create the root agent instance for ADK to discover
root_agent = get_root_agent()