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

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent

# Import specialized DNB agents
# Use absolute imports so ADK's module loader (which adds the agents dir to sys.path)
# can resolve sibling packages reliably.
from api_agents.dnb_echo.agent import dnb_echo_agent  # type: ignore
from api_agents.dnb_statistics.agent import dnb_statistics_agent  # type: ignore
from api_agents.dnb_public_register.agent import (
    dnb_public_register_agent,
)  # type: ignore

# Optional: OpenAPI-native variants (runtime tool generation)
USE_OPENAPI_VARIANTS = os.getenv("DNB_COORDINATOR_USE_OPENAPI", "0") in ("1", "true", "True")
if USE_OPENAPI_VARIANTS:
    try:
        from api_agents.dnb_openapi.agent import (
            dnb_openapi_echo_agent,
            dnb_openapi_statistics_agent,
            dnb_openapi_public_register_agent,
        )  # type: ignore
        _OPENAPI_ECHO = dnb_openapi_echo_agent
        _OPENAPI_STATS = dnb_openapi_statistics_agent
        _OPENAPI_PR = dnb_openapi_public_register_agent
    except Exception as _e:  # fall back silently if import fails
        _OPENAPI_ECHO = None
        _OPENAPI_STATS = None
        _OPENAPI_PR = None
else:
    _OPENAPI_ECHO = None
    _OPENAPI_STATS = None
    _OPENAPI_PR = None

# Model configuration
MODEL = os.getenv("DNB_COORDINATOR_MODEL", "gemini-2.0-flash")

# Load instructions
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
    INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
    INSTRUCTION = (
        "You coordinate DNB API operations across three specialized domains:\n\n"
        "1. **Echo API** (dnb_echo_agent):\n"
        "   - Connectivity tests, health checks, API availability\n"
        "   - Use for: \"test DNB connection\", \"is DNB API up?\"\n\n"
        "2. **Statistics API** (dnb_statistics_agent):\n"
        "   - Economic datasets, exchange rates, financial statistics\n"
        "   - Use for: \"get exchange rates\", \"pension fund data\", \"balance of payments\"\n\n"
        "3. **Public Register API** (dnb_public_register_agent):\n"
        "   - License searches, registration data, regulatory info\n"
        "   - Use for: \"find licenses\", \"search institutions\", \"regulatory data\"\n"
        "   - IMPORTANT: This agent will automatically discover valid register codes\n"
        "   - Common registers: WFTAF (financial services), Wft (various financial categories)\n"
        "   - Do NOT assume register codes like 'AFM' - let the specialist discover valid codes\n\n"
        "Route to the appropriate specialist based on user request.\n"
        "If multiple specialists needed, coordinate execution.\n"
        "Provide clear, structured summaries."
    )

_sub_agents = [
    _OPENAPI_ECHO or dnb_echo_agent,
    _OPENAPI_STATS or dnb_statistics_agent,
    _OPENAPI_PR or dnb_public_register_agent,
]

dnb_coordinator_agent = Agent(
    name="dnb_coordinator",
    model=MODEL,
    description=(
        "Coordinator for DNB (De Nederlandsche Bank) API operations. "
        "Routes to Echo (tests), Statistics (datasets), or Public Register "
        "(licenses/registrations) based on request type."
    ),
    instruction=INSTRUCTION,
    sub_agents=_sub_agents,
    output_key="dnb_coordinator_response",
)