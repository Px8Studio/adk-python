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

from google.adk.agents import Agent
from google.genai import types
from _common.config import get_model


# Patch ToolboxToolset.close to await the underlying async client close
try:
  import inspect
  from google.adk.tools.toolbox_toolset import ToolboxToolset  # type: ignore

  async def _patched_toolbox_close(self) -> None:
    client = getattr(self, "_toolbox_client", None)
    if client:
      maybe = client.close()
      if inspect.isawaitable(maybe):
        await maybe

  # Apply patch only once
  if not getattr(ToolboxToolset.close, "__patched__", False):  # type: ignore[attr-defined]
    ToolboxToolset.close = _patched_toolbox_close  # type: ignore[assignment]
    setattr(ToolboxToolset.close, "__patched__", True)  # type: ignore[attr-defined]
except Exception:
  # Best-effort patch; ignore if ToolboxToolset not used
  pass


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

  # Also add the data-science directory so `data_science` package is importable.
  data_science_dir = agents_dir / "data-science"
  data_science_dir_str = str(data_science_dir)
  if data_science_dir.exists() and data_science_dir_str not in sys.path:
    sys.path.insert(0, data_science_dir_str)
  
  try:
    # Import from sibling packages
    from api_coordinators.dnb_coordinator.agent import get_dnb_coordinator_agent  # type: ignore
    from data_science.agent import (  # type: ignore
        get_root_agent as get_data_science_coordinator,
    )
  except ImportError as e:
    agents_dir_str = str(agents_dir.resolve()) if "agents_dir" in locals() else "<unknown>"
    data_science_dir_str = str(data_science_dir.resolve()) if "data_science_dir" in locals() else "<unknown>"
    raise ImportError(
        f"Failed to import coordinators. "
        f"Agents directory: {agents_dir_str}, "
        f"added data_science dir: {data_science_dir_str}, "
        f"sys.path: {sys.path[:3]}..."
    ) from e

  # Get coordinator agents
  dnb_coordinator = get_dnb_coordinator_agent()
  data_science_coordinator = get_data_science_coordinator()  # fresh instance

  # Model configuration (profile-based)
  model_name = get_model("fast")

  # Build the root agent with ONLY the two domain coordinators
  root = Agent(
      model=model_name,
      name="root_agent",
      instruction="""You are the Root Orchestrator for the Orkhon system.
          
Your role is to:
1. Understand the user's query and intent
2. Delegate to the appropriate coordinator agent:
   - dnb_coordinator: For DNB API queries (Echo, Statistics, Public Register)
   - data_science_coordinator: For analytics and data science workflows
""",
      sub_agents=[  # Ensure each sub-agent instance is unique per load
        dnb_coordinator,
        data_science_coordinator,
      ],
  )
  return root


# Create the root agent instance for ADK to discover
root_agent = get_root_agent()