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
DNB Public Register Agent - Focused on Public Register API tools only.
"""

from __future__ import annotations

import os
from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
# Default to generator convention: dnb_public_register_tools; allow override
_TOOLSET_NAME = os.getenv("DNB_PUBLIC_REGISTER_TOOLSET_NAME", "dnb_public_register_tools")

# ADK Web expects 'root_agent'
root_agent = Agent(
  name="dnb_api_public_register",
  model="gemini-2.0-flash",
  instruction="""You are a helpful assistant specialized in the DNB Public Register API.
Use ONLY tools whose names start with 'dnb-public-register-'.
If a user asks about echo or statistics, ask to switch to the matching agent instead.

Important: Parameter names are case-sensitive and follow the API definition exactly. Do not normalize casing.
- Example: publications_search requires query parameter 'RegisterCode' (capital R), not 'registerCode'.
- Example: many endpoints use path parameter 'registerCode' (lowercase r) in the URL path.
- Dates should follow the examples in the docs, e.g., 'YYYY-MM-dd' like '2024-01-30'.

When users provide register codes, relation numbers, dates, or languages, validate them before calling tools. If you suspect a casing mismatch, restate the exact parameter names you will send and correct them before invoking the tool.""",
  tools=[
    ToolboxToolset(
      server_url=_TOOLBOX_URL,
      toolset_name=_TOOLSET_NAME
    )
  ]
)

agent = root_agent