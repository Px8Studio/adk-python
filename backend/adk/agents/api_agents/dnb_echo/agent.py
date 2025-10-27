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
DNB Echo Agent

Specialized agent for DNB Echo API operations.
Handles connectivity tests and health checks.

Hierarchy:
  root_agent → dnb_coordinator → dnb_echo_agent (this)
"""

from __future__ import annotations

import os
from google.adk.agents import LlmAgent as Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

# Configuration
_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
_TOOLSET_NAME = os.getenv("DNB_ECHO_TOOLSET_NAME", "dnb_echo_tools")
MODEL = os.getenv("DNB_ECHO_MODEL", "gemini-2.0-flash")

dnb_echo_agent = Agent(
    name="dnb_echo_agent",
    model=MODEL,
    description="Specialist for DNB Echo API connectivity tests and health checks.",
    instruction="""You are a specialist in DNB Echo API operations.

CAPABILITIES:
- Test API connectivity (helloworld endpoint)
- Check API health status
- Verify API availability

TOOLS AVAILABLE:
Use ONLY tools whose names start with 'dnb-echo-' (e.g., dnb-echo-helloworld).

GUIDELINES:
- Provide clear status messages about connectivity
- Format results in a user-friendly way
- If API is down, provide helpful troubleshooting steps
- For statistics or public register operations, inform user to route through coordinator""",
    tools=[
        ToolboxToolset(
            server_url=_TOOLBOX_URL,
            toolset_name=_TOOLSET_NAME
        )
    ]
)