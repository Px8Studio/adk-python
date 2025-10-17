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
DNB Agent - Interacts with Dutch Central Bank (DNB) APIs via GenAI Toolbox.
"""

from __future__ import annotations

from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

# Create agent with Toolbox tools using ADK's native integration
agent = Agent(
  name="dnb_agent",
  model="gemini-2.0-flash",
  instruction="""You are a helpful assistant that can access DNB (De Nederlandsche Bank) APIs.

You have access to:
- Echo API: Test connectivity
- Statistics API: Access economic and financial statistics
- Public Register API: Access public registration data

When users ask about DNB data:
1. Use the appropriate API tools
2. Explain what you're retrieving
3. Present the data in a clear, understandable format
4. Provide context where helpful

Always be clear about data sources and limitations.""",
  tools=[
    ToolboxToolset(
      server_url="http://localhost:5000",
      toolset_name="dnb-tools"
    )
  ]
)
