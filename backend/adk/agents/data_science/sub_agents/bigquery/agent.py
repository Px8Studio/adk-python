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

"""BigQuery Agent: NL2SQL translation and query execution for BigQuery."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types

from .prompts import return_instructions_bigquery
from .tools import get_database_settings_from_context

_logger = logging.getLogger(__name__)

# BigQuery built-in tools in ADK
# https://google.github.io/adk-docs/tools/built-in-tools/#bigquery
ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL = "execute_sql"

# User agent identifier for API calls
USER_AGENT = "orkhon-data-science-agent"


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent context before execution."""
    _logger.info("Setting up BigQuery agent context")

    # Get database settings from the parent context
    database_settings = get_database_settings_from_context(callback_context)

    # Retrieve the InvocationContext required by ToolContext
    inv_ctx = None
    try:
        if hasattr(callback_context, "execution_context") and hasattr(
            callback_context.execution_context, "invocation_context"
        ):
            inv_ctx = callback_context.execution_context.invocation_context
        elif hasattr(callback_context, "invocation_context"):
            inv_ctx = callback_context.invocation_context
    except Exception:  # pragma: no cover - defensive
        inv_ctx = None

    if inv_ctx is None:
        _logger.warning(
            "InvocationContext not available; skipping ToolContext setup."
        )
        return

    # Initialize ToolContext with the invocation context
    tool_context = ToolContext(inv_ctx)

    # Store database settings in the state
    tool_context.state["database_settings"] = database_settings
    tool_context.state["user_agent"] = USER_AGENT

    # Attach tool context to callback context
    callback_context.tool_context = tool_context

    _logger.info(
        f"BigQuery agent context set with project: "
        f"{database_settings.get('project_id')}"
    )


def store_results_in_context(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict,
) -> Optional[Dict]:
    """Store query results in context for potential reuse.
    
    This follows the ADK sample pattern for after_tool_callback.
    """
    if tool.name == ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL:
        # Store in tool context for access by other tools
        tool_context.state["last_query_result"] = tool_response
        _logger.debug("Stored query result in context")
    
    # Return None to use the original tool response
    return None


def get_bigquery_agent() -> LlmAgent:
    """Create a new BigQuery agent instance.
    
    Returns a fresh instance each time to avoid conflicts when used as sub-agent.
    This pattern follows the official ADK data-science sample.
    """
    # Configure BigQuery toolset with each instantiation
    bigquery_tool_config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,  # Changed to BLOCKED for safety by default
        max_query_result_rows=100,
        application_name=USER_AGENT,
    )
    
    bigquery_toolset = BigQueryToolset(
        tool_filter=[ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL],
        bigquery_tool_config=bigquery_tool_config,
    )

    # Create and return fresh agent instance
    agent = LlmAgent(
        model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.5-flash"),
        name="bigquery_agent",
        instruction=return_instructions_bigquery(),
        tools=[bigquery_toolset],
        before_agent_callback=setup_before_agent_call,
        after_tool_callback=store_results_in_context,
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
    )
    
    _logger.debug("Created new BigQuery agent instance with model: %s", 
                  os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.5-flash"))
    return agent


# Module-level instance for backward compatibility and direct usage
# This follows the ADK convention: module exports an agent instance
bigquery_agent = get_bigquery_agent()
