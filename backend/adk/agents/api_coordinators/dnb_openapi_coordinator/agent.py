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

"""DNB OpenAPI Coordinator Agent.

Routes requests to runtime OpenAPI-based DNB agents. This coordinator is used
when testers want to exercise the native ADK OpenAPIToolset instead of the MCP
Toolbox definitions.
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent
from api_agents.dnb_openapi.agent import (  # type: ignore
    dnb_openapi_unified_agent,
)

MODEL = os.getenv("DNB_OPENAPI_COORDINATOR_MODEL", "gemini-2.0-flash")
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
    INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
    INSTRUCTION = (
        "You coordinate DNB OpenAPI access. Delegate to the unified OpenAPI agent "
        "and summarize results."
    )

def _clone_for_sub_agent(agent: Agent) -> Agent:
    """Return a clone suitable for reuse in coordinator sub_agents.

    Creates a shallow copy of the provided agent with a distinct name so it can be
    safely referenced in sub_agents without unintended shared state.
    """
    return Agent(
        name=f"{agent.name}_as_sub",
        model=getattr(agent, "model", MODEL),
        instruction=getattr(agent, "instruction", ""),
        description=getattr(agent, "description", ""),
        tools=getattr(agent, "tools", []),
        sub_agents=getattr(agent, "sub_agents", []),
    )

def get_dnb_openapi_coordinator_agent() -> Agent:
    """Create the DNB OpenAPI coordinator agent with sub_agents configured."""
    child_agents = [_clone_for_sub_agent(dnb_openapi_unified_agent)]
    return Agent(
        name="dnb_openapi_coordinator_agent",
        model=MODEL,
        instruction=INSTRUCTION,
        description=(
            "Coordinator for unified DNB OpenAPI access. Delegates to the unified "
            "OpenAPI agent and synthesizes concise responses."
        ),
        sub_agents=child_agents,
        tools=[],
    )

dnb_openapi_coordinator_agent = get_dnb_openapi_coordinator_agent()
