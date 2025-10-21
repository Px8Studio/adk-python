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
API Agents Coordinator

This is the root agent for the api_agents package.
It coordinates access to various API integration agents including DNB APIs
(Echo, Statistics, Public Register) and Google Search.

Hierarchy:
  api_agents root_agent (this)
  ├─ dnb_echo_agent
  ├─ dnb_statistics_agent
  ├─ dnb_public_register_agent
  ├─ dnb_openapi_agent (unified)
  └─ google_search_agent
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent

# Import specialized agents
from .dnb_echo.agent import dnb_echo_agent  # type: ignore
from .dnb_statistics.agent import dnb_statistics_agent  # type: ignore
from .dnb_public_register.agent import dnb_public_register_agent  # type: ignore
from .dnb_openapi.agent import dnb_openapi_unified_agent  # type: ignore
from .google_search.agent import google_search_agent  # type: ignore

# Model configuration
MODEL = os.getenv("API_AGENTS_MODEL", "gemini-2.0-flash")

# Load instructions from file for better maintainability
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
    INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
    INSTRUCTION = """You are an API integration coordinator for the Orkhon platform.

Your role:
1. Route user requests to the appropriate specialized API agent
2. Coordinate multi-API workflows when needed
3. Provide clear summaries of API responses

Available agents:
- dnb_echo_agent: Test DNB API connectivity
- dnb_statistics_agent: Access DNB economic and financial statistics
- dnb_public_register_agent: Search DNB public registers (licenses, registrations)
- dnb_openapi_unified_agent: Unified access to all DNB APIs via OpenAPI
- google_search_agent: Perform web searches via Google Custom Search

Workflow:
1. Analyze the user's request to understand which API(s) are needed
2. Use transfer_to_agent() to delegate to the appropriate specialist
3. Synthesize and summarize results for the user
4. For multi-API workflows, coordinate between agents sequentially or explain the approach

Guidelines:
- Be explicit about which agent you're delegating to and why
- Provide context from previous responses when coordinating multiple calls
- Handle errors gracefully and suggest alternatives
- Keep responses concise but informative
"""

# Root agent for api_agents package
root_agent = Agent(
    name="api_agents_root",
    model=MODEL,
    description=(
        "Coordinator for API integration agents. Routes requests to specialized "
        "agents for DNB APIs (Echo, Statistics, Public Register), unified DNB "
        "OpenAPI access, and Google Search."
    ),
    instruction=INSTRUCTION,
    sub_agents=[
        dnb_echo_agent,
        dnb_statistics_agent,
        dnb_public_register_agent,
        dnb_openapi_unified_agent,
        google_search_agent,
    ],
    output_key="api_agents_response",
)

# Backwards compatibility
agent = root_agent
