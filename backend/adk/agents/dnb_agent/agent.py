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
Umbrella DNB agent that coordinates three subagents:
- dnb_api_echo
- dnb_api_statistics
- dnb_api_public_register

This agent is primarily for routing and unified startup in ADK Web.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent as Agent

# Import the three subagents from sibling agent packages.
# ADK adds the agents directory to sys.path, so these absolute imports work.
from dnb_api_echo.agent import root_agent as echo_agent  # type: ignore
from dnb_api_statistics.agent import root_agent as statistics_agent  # type: ignore
from dnb_api_public_register.agent import root_agent as public_register_agent  # type: ignore

# Root umbrella agent exposed for ADK discovery
root_agent = Agent(
    name="dnb_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a coordinator for DNB APIs. Route user requests to the most "
        "relevant subagent: Echo (connectivity tests), Statistics (datasets), "
        "or Public Register (licences/registrations). Provide brief, clear "
        "summaries and cite which API was used."
    ),
    sub_agents=[
        echo_agent,
        statistics_agent,
        public_register_agent,
    ],
)

# Backwards compatibility alias
agent = root_agent
