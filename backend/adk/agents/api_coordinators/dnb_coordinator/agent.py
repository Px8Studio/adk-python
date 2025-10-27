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

"""
DNB API Coordinator Agent

Category coordinator for DNB (De Nederlandsche Bank) API operations.
Routes to specialized agents for Echo, Statistics, and Public Register APIs.

Hierarchy:
  root_agent (from root_agent/agent.py)
  └─ dnb_coordinator (this)
     ├─ dnb_echo_agent
     ├─ dnb_statistics_agent
     └─ dnb_public_register_agent
"""

from __future__ import annotations

import importlib
import inspect
import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent

# Import specialized DNB agents (leaf agents that may already be part of api_agents_root)
from api_agents.dnb_echo.agent import dnb_echo_agent  # type: ignore
from api_agents.dnb_statistics.agent import dnb_statistics_agent  # type: ignore
from api_agents.dnb_public_register.agent import (
  dnb_public_register_agent,
)  # type: ignore

# Optional: OpenAPI-native variants (runtime tool generation)
USE_OPENAPI_VARIANTS = os.getenv("DNB_COORDINATOR_USE_OPENAPI", "0") in ("1", "true", "True")
if USE_OPENAPI_VARIANTS:
  try:
    from api_agents.dnb_openapi.agent import (  # type: ignore
      dnb_openapi_echo_agent,
      dnb_openapi_statistics_agent,
      dnb_openapi_public_register_agent,
    )
  except Exception:
    USE_OPENAPI_VARIANTS = False

MODEL = os.getenv("DNB_COORDINATOR_MODEL", "gemini-2.0-flash")
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
  INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
  INSTRUCTION = (
    "You coordinate DNB API agents. Route requests to the right DNB agent and "
    "summarize results. Prefer precise, concise answers."
  )

def _clone_for_sub_agent(agent: Agent, suffix: str = "_as_sub") -> Agent:
  """Create a fresh Agent instance suitable for reuse as a sub_agent.

  Avoids parent conflicts by not reusing the original Agent instance.
  Copies essential fields and tools; does not copy parent linkage.
  """
  # Best-effort copy of core fields commonly used in app agents.
  return Agent(
    name=f"{getattr(agent, 'name', 'agent')}{suffix}",
    model=getattr(agent, "model", MODEL),
    instruction=getattr(agent, "instruction", ""),
    description=getattr(agent, "description", ""),
    tools=list(getattr(agent, "tools", [])),
    sub_agents=[],  # Avoid recursively reusing children to prevent conflicts
  )

def get_dnb_coordinator_agent() -> Agent:
  """Create the DNB coordinator agent with cloned sub_agents to prevent parent conflicts."""
  child_agents = [
    _clone_for_sub_agent(dnb_echo_agent),
    _clone_for_sub_agent(dnb_statistics_agent),
    _clone_for_sub_agent(dnb_public_register_agent),
  ]

  if USE_OPENAPI_VARIANTS:
    child_agents.extend(
      [
        _clone_for_sub_agent(dnb_openapi_echo_agent),            # type: ignore[name-defined]
        _clone_for_sub_agent(dnb_openapi_statistics_agent),      # type: ignore[name-defined]
        _clone_for_sub_agent(dnb_openapi_public_register_agent), # type: ignore[name-defined]
      ]
    )

  # Rely on ADK's built-in transfer tool auto-exposed when sub_agents are set.
  return Agent(
    name="dnb_coordinator_agent",
    model=MODEL,
    instruction=INSTRUCTION,
    description=(
      "Coordinator for DNB API operations. Delegates to specialized DNB agents "
      "and synthesizes concise responses."
    ),
    sub_agents=child_agents,
    tools=[],
  )

# Module-level instance for ADK loader compatibility
dnb_coordinator_agent = get_dnb_coordinator_agent()