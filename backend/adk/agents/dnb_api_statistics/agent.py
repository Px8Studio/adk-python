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
DNB Statistics Agent - Focused on DNB Statistics API tools only.
"""

from __future__ import annotations

import os
from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
_TOOLSET_NAME = os.getenv("DNB_TOOLSET_NAME", "dnb-tools")

# ADK Web expects 'root_agent'
root_agent = Agent(
  name="dnb_api_statistics ",
  model="gemini-2.0-flash",
  instruction="""You are a helpful assistant specialized in the DNB Statistics API.
Use ONLY tools whose names start with 'dnb-statistics-'.
If a user asks about echo or public register, ask to switch to the matching agent instead.
When returning results, summarize datasets, units, and time ranges clearly.""",
  tools=[
    ToolboxToolset(
      server_url=_TOOLBOX_URL,
      toolset_name=_TOOLSET_NAME
    )
  ]
)

agent = root_agent