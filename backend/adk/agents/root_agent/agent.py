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
Root Coordinator Agent

The top-level intelligent router for the multi-agent system.
Routes requests to specialized category coordinators.

Hierarchy:
  root_agent (this)
  ├─ dnb_coordinator       (DNB API operations via MCP Toolbox)
  ├─ dnb_openapi_coordinator (DNB API operations via Runtime OpenAPI)
  ├─ data_science_agent    (BigQuery & Analytics operations)
  │  ├─ bigquery_agent     (NL2SQL for BigQuery)
  │  └─ analytics_agent    (NL2Py with Code Interpreter)
  └─ google_coordinator    (Google API operations - future)
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool  # Import the actual tool instance

# Import category coordinators
# ADK adds the agents directory to sys.path, so these absolute imports work
from api_coordinators.dnb_coordinator.agent import dnb_coordinator_agent  # type: ignore
from api_coordinators.dnb_openapi_coordinator.agent import (  # type: ignore
    dnb_openapi_coordinator_agent,
)
from data_science.agent import root_agent as data_science_agent  # type: ignore

# Model configuration
MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash")

# Load instructions from file for better maintainability
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
    INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
    INSTRUCTION = """You are the main system coordinator.

Your role:
1. Understand user requests across multiple domains
2. Route to appropriate category coordinators:
   - DNB API operations → dnb_coordinator_agent
   - Google searches → google_coordinator_agent (coming soon)
   - Data analysis → data_coordinator_agent (coming soon)
3. Synthesize responses from multiple coordinators when needed
4. Maintain conversational context across interactions

Guidelines:
- Be clear about which coordinator you're delegating to and why
- Provide concise summaries of results
- Handle multi-part requests intelligently
- Ask clarifying questions when user intent is ambiguous
- Preserve context for follow-up questions
"""

# Root agent definition
root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "Primary system coordinator that routes user requests to "
        "specialized domain coordinators for API integrations, data processing, "
        "and utility operations. Handles multi-domain workflows and maintains "
        "conversational context."
    ),
    instruction=INSTRUCTION,
    # Sub-agents: LLM will use transfer_to_agent() to delegate
    sub_agents=[
        dnb_coordinator_agent,
        dnb_openapi_coordinator_agent,
        data_science_agent,
        # Future coordinators will be added here:
        # google_coordinator_agent,
    ],
    # Tools: Enable artifact access for generated content from sub-agents
    tools=[load_artifacts_tool],  # ✅ Now passing the tool instance
    # Output key for tracking in state
    output_key="root_response",
)