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

"""Database Agent: get data from database (BigQuery) using NL2SQL."""

import logging
import os
from typing import Dict, Any

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from . import tools
from .prompts import return_instructions_alloydb


class DataScienceAlloyDbAgent(LlmAgent):
    """Subclass to keep the runner aligned with the data_science app."""

logger = logging.getLogger(__name__)


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""
    logger.debug("setup_before_agent_call")

    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = (
            tools.get_database_settings()
        )


def store_results_in_context(
    tool: "BaseTool",
    args: Dict[str, Any],
    tool_context: "ToolContext",
    tool_response: Dict,
) -> Optional[Dict]:
    """Store AlloyDB results in invocation-level state."""

    if tool.name == ADK_BUILTIN_ALLOYDB_EXECUTE_SQL_TOOL:
        if tool_response["status"] == "SUCCESS":
            # Store in tool_context.state (for local use)
            tool_context.state["alloydb_query_result"] = tool_response["rows"]

            # CRITICAL: Also store in invocation_context.state for cross-agent access
            invocation_context = tool_context._invocation_context
            if invocation_context:
                invocation_context.state["alloydb_query_result"] = tool_response["rows"]
                logger.info(
                    "Stored AlloyDB results in invocation state: %d rows",
                    len(tool_response["rows"]),
                )

    return None


alloydb_agent = DataScienceAlloyDbAgent(
    model=os.getenv("ALLOYDB_AGENT_MODEL", ""),
    name="alloydb_agent",
    instruction=return_instructions_alloydb(),
    output_key="alloydb_agent_output",
    tools=[
        tools.alloydb_nl2sql,
        tools.run_alloydb_query,
        # tools.get_toolbox_toolset(),
    ],
    # before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
