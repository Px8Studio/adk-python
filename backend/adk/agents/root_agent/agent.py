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

from __future__ import annotations

import logging

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

# Import coordinator tools from the api_coordinators sibling package
try:
    from backend.adk.agents.api_coordinators import (
        toolbox_coordinator,
        experimental_runtime_coordinator,
    )
except ImportError:
    # Fallback: coordinators not available, set to None
    toolbox_coordinator = None
    experimental_runtime_coordinator = None

# Import data_science agent directly (proper ADK pattern)
try:
    # Import using relative path within agents directory
    import sys
    from pathlib import Path
    
    # Add data-science to path if needed
    data_science_path = Path(__file__).parent.parent / 'data-science'
    if str(data_science_path) not in sys.path:
        sys.path.insert(0, str(data_science_path))
    
    from data_science.agent import root_agent as data_science_agent
except ImportError as e:
    import warnings
    warnings.warn(
        f"Could not import data_science agent: {e}\n"
        "The root agent will start without data science capabilities."
    )
    data_science_agent = None

_logger = logging.getLogger(__name__)

# Wrap data science agent as an AgentTool for the root agent
if data_science_agent:
    data_science_tool = AgentTool(
        agent=data_science_agent,
        name="data_science_root_agent",
        description=(
            "A comprehensive data science agent that can analyze BigQuery data, "
            "create machine learning models, and perform advanced analytics. "
            "Use this for: SQL queries, data analysis, machine learning, "
            "BigQuery operations, and statistical analysis."
        ),
    )
else:
    data_science_tool = None

# Build tools list dynamically based on available coordinators and agents
_tools = []
if toolbox_coordinator:
    _tools.append(toolbox_coordinator)
if experimental_runtime_coordinator:
    _tools.append(experimental_runtime_coordinator)
if data_science_tool:
    _tools.append(data_science_tool)

# Build instruction based on available agents
_available_agents = []
agent_num = 1
if toolbox_coordinator:
    _available_agents.append(
        f"{agent_num}. toolbox_coordinator - Access to GenAI Toolbox services (Google Search, Places, etc.)"
    )
    agent_num += 1
if experimental_runtime_coordinator:
    _available_agents.append(
        f"{agent_num}. experimental_runtime_coordinator - Access to experimental runtime services"
    )
    agent_num += 1
if data_science_tool:
    _available_agents.append(
        f"{agent_num}. data_science_root_agent - Advanced data science and analytics capabilities"
    )

_instruction = (
    "You are Orkhon, an AI assistant with access to multiple specialized agents.\n\n"
    "Available agents:\n"
    + "\n".join(_available_agents)
    + "\n\nWhen a user asks a question:"
)
if data_science_tool:
    _instruction += "\n- Route data science/analytics queries to data_science_root_agent"
if toolbox_coordinator:
    _instruction += "\n- Route search/places queries to toolbox_coordinator"
if experimental_runtime_coordinator:
    _instruction += "\n- Route experimental requests to experimental_runtime_coordinator"
_instruction += "\n\nAlways provide clear, helpful responses based on the agent outputs."

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction=_instruction,
    tools=_tools,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
    ),
)