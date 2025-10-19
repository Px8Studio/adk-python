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
  dnb_openapi_echo_agent,
  dnb_openapi_public_register_agent,
  dnb_openapi_statistics_agent,
)

MODEL = os.getenv("DNB_OPENAPI_COORDINATOR_MODEL", "gemini-2.0-flash")

_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
  INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
  INSTRUCTION = (
      "You coordinate DNB OpenAPI agents that build their tools at runtime. "
      "Use this coordinator when users ask for the experimental native "
      "OpenAPIToolset path instead of the MCP Toolbox tools."
  )


def _clone_for_coordinator(agent: Agent) -> Agent:
  """Create a defensive clone so agents remain reusable elsewhere."""

  return agent.clone()


dnb_openapi_coordinator_agent = Agent(
  name="dnb_openapi_coordinator",
  model=MODEL,
  description=(
      "Coordinator for DNB APIs using runtime OpenAPIToolset agents. "
      "Intended for experimental and side-by-side testing against MCP "
      "Toolbox-powered flows."
  ),
  instruction=INSTRUCTION,
  sub_agents=[
      _clone_for_coordinator(dnb_openapi_echo_agent),
      _clone_for_coordinator(dnb_openapi_statistics_agent),
      _clone_for_coordinator(dnb_openapi_public_register_agent),
  ],
  output_key="dnb_openapi_coordinator_response",
)
