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
DNB Echo Agent - Focused on Echo API tools only.
"""

from __future__ import annotations

import os
from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
# Use per-agent env var with sensible default matching generator: dnb_echo_tools
_TOOLSET_NAME = os.getenv("DNB_ECHO_TOOLSET_NAME", "dnb_echo_tools")

# ADK Web expects 'root_agent'
root_agent = Agent(
  name="dnb_api_echo",
  model="gemini-2.0-flash",
  instruction="""You are a helpful assistant specialized in the DNB Echo API.
Use ONLY tools whose names start with 'dnb-echo-' (e.g., dnb-echo-helloworld).
If a user asks about statistics or public register, ask to switch to the matching agent instead.""",
  tools=[
    ToolboxToolset(
      server_url=_TOOLBOX_URL,
      toolset_name=_TOOLSET_NAME
    )
  ]
)

# For compatibility with patterns that import 'agent'
agent = root_agent