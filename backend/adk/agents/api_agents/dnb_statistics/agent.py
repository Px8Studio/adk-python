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
DNB Statistics Agent

Specialized agent for DNB Statistics API operations.
Handles economic datasets, exchange rates, and financial statistics.

Hierarchy:
  root_agent → dnb_coordinator → dnb_statistics_agent (this)
"""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
_TOOLSET_NAME = os.getenv("DNB_STATISTICS_TOOLSET_NAME", "dnb_statistics_tools")
MODEL = os.getenv("DNB_STATISTICS_MODEL", "gemini-2.0-flash")

dnb_statistics_agent = Agent(
  name="dnb_statistics_agent",
  model=MODEL,
  description="Specialist for DNB Statistics API - economic datasets, exchange rates, and financial statistics.",
  instruction="""You are a specialist in DNB Statistics API operations.

CAPABILITIES:
- Economic datasets and indicators
- Exchange rates and currency data
- Financial statistics and balance of payments
- Pension fund data
- Time-series data

TOOLS AVAILABLE:
Use ONLY tools whose names start with 'dnb-statistics-'.

GUIDELINES:
- Summarize datasets clearly with units and time ranges
- Provide context for economic indicators
- Format large datasets for readability
- For echo or public register operations, inform user to route through coordinator""",
  tools=[
        ToolboxToolset(
      server_url=_TOOLBOX_URL,
      toolset_name=_TOOLSET_NAME
    )
  ]
)