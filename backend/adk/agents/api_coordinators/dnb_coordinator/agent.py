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
from api_agents.dnb_echo.agent import dnb_echo_agent  # type: ignore
from api_agents.dnb_statistics.agent import dnb_statistics_agent  # type: ignore
from api_agents.dnb_public_register.agent import dnb_public_register_agent  # type: ignore

# Model configuration
MODEL = os.getenv("DNB_COORDINATOR_MODEL", "gemini-2.0-flash")

# Load instructions
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
  INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
  INSTRUCTION = """You coordinate DNB API operations across three specialized domains:

1. **Echo API** (dnb_echo_agent):
   - Connectivity tests, health checks, API availability
   - Use for: "test DNB connection", "is DNB API up?"

2. **Statistics API** (dnb_statistics_agent):
   - Economic datasets, exchange rates, financial statistics
   - Use for: "get exchange rates", "pension fund data", "balance of payments"

3. **Public Register API** (dnb_public_register_agent):
   - License searches, registration data, regulatory info
   - Use for: "find licenses", "search institutions", "regulatory data"

Route to the appropriate specialist based on user request.
If multiple specialists needed, coordinate execution.
Provide clear, structured summaries."""

dnb_coordinator_agent = Agent(
    name="dnb_coordinator",
    model=MODEL,
    description=(
        "Coordinator for DNB (De Nederlandsche Bank) API operations. "
        "Routes to Echo (tests), Statistics (datasets), or Public Register "
        "(licenses/registrations) based on request type."
    ),
    instruction=INSTRUCTION,
    sub_agents=[
        dnb_echo_agent,
        dnb_statistics_agent,
        dnb_public_register_agent,
    ],
    output_key="dnb_coordinator_response",
)

# Backwards compatibility
agent = dnb_coordinator_agent