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

"""Coordinator agent package for Orkhon DNB integrations."""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.toolbox_toolset import ToolboxToolset

from .dnb_coordinator.agent import dnb_coordinator_agent, get_dnb_coordinator_agent

# Toolbox Coordinator - provides access to GenAI Toolbox services
toolbox_server_url = os.getenv("TOOLBOX_SERVER_URL", "http://127.0.0.1:5000")

toolbox_agent = Agent(
    name="toolbox_agent",
    model="gemini-2.5-flash",
    instruction="""You are a specialist in accessing GenAI Toolbox services.
    
    You have access to various toolsets through the GenAI Toolbox including:
    - Google Search capabilities
    - Google Places API
    - DNB Statistics API
    - DNB Public Register API
    - DNB Echo API
    
    When a user asks for information, use the appropriate toolset to retrieve it.
    Provide clear, concise responses based on the tool outputs.""",
    description="Access to GenAI Toolbox services (Google Search, Places, DNB APIs)",
    tools=[
        ToolboxToolset(
            server_url=toolbox_server_url,
            toolset_name="dnb_statistics_tools",
        ),
        ToolboxToolset(
            server_url=toolbox_server_url,
            toolset_name="dnb_public_register_tools",
        ),
        ToolboxToolset(
            server_url=toolbox_server_url,
            toolset_name="dnb_echo_tools",
        ),
    ],
)

toolbox_coordinator = AgentTool(
    agent=toolbox_agent,
    name="toolbox_coordinator",
    description="Coordinator for GenAI Toolbox services",
)

# Experimental Runtime Coordinator - placeholder for future experimental features
experimental_runtime_agent = Agent(
    name="experimental_runtime_agent",
    model="gemini-2.5-flash",
    instruction="""You are an experimental runtime coordinator.
    
    This agent is reserved for experimental runtime features and advanced
    capabilities that are still under development.
    
    Currently, you should inform users that experimental features are not
    yet available but will be added in future releases.""",
    description="Access to experimental runtime services (under development)",
    tools=[],
)

experimental_runtime_coordinator = AgentTool(
    agent=experimental_runtime_agent,
    name="experimental_runtime_coordinator",
    description="Coordinator for experimental runtime features",
)

__all__ = [
    "dnb_coordinator_agent",
    "get_dnb_coordinator_agent",
    "toolbox_coordinator",
    "experimental_runtime_coordinator",
]
