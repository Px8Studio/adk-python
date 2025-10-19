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
  ├─ dnb_coordinator       (DNB API operations)
  ├─ google_coordinator    (Google API operations - future)
  └─ data_coordinator      (Data processing - future)
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent

# Import category coordinators
# ADK adds the agents directory to sys.path, so these absolute imports work
from api_coordinators.dnb_coordinator.agent import dnb_coordinator_agent  # type: ignore

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
    name="root_agent",
    model=MODEL,
    description=(
        "Main coordinator agent. Routes requests to "
        "specialized domain coordinators for API integrations, data processing, "
        "and utility operations. Handles multi-domain workflows and maintains "
        "conversational context."
    ),
    instruction=INSTRUCTION,
    # Sub-agents: LLM will use transfer_to_agent() to delegate
    sub_agents=[
        dnb_coordinator_agent,
        # Future coordinators will be added here:
        # google_coordinator_agent,
        # data_coordinator_agent,
    ],
    # Output key for tracking in state
    output_key="root_response",
)