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

def get_root_agent() -> Agent:
    """Create a fresh root agent instance.
    
    Returns a new instance each time to avoid parent conflicts during hot-reload.
    """
    # Import coordinators here to get fresh instances
    from api_coordinators import (  # type: ignore
        get_dnb_coordinator_agent,
        get_dnb_openapi_coordinator_agent,
    )
    from data_science.agent import get_root_agent as get_data_science_agent  # type: ignore
    
    # Example (names are illustrative; keep your existing construction):
    # bigquery_agent = get_bigquery_agent()
    # data_science_agent = get_analytics_agent()  # returns an Agent/LlmAgent
    
    # Build the root agent. Fix: use sub_agents= instead of agents=
    root = Agent(
        model=MODEL,
        name="root_agent",
        description=(
            "Primary system coordinator that routes user requests to "
            "specialized domain coordinators for API integrations, data processing, "
            "and utility operations. Executes tasks autonomously with minimal confirmation."
        ),
        instruction=INSTRUCTION,
        sub_agents=[
            get_dnb_coordinator_agent(),
            get_dnb_openapi_coordinator_agent(),
            get_data_science_agent(),
        ],
        tools=[load_artifacts_tool],
        output_key="root_response",
    )
    return root


# Export for ADK web loader
root_agent = get_root_agent()