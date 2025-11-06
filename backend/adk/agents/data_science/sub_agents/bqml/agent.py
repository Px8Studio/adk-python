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

"""BigQuery ML Agent for model training and prediction."""

from __future__ import annotations

import logging
import os

from google.adk.agents.llm_agent import LlmAgent as Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from ..bigquery.agent import bigquery_agent
from ..bigquery.tools import get_database_settings as get_bq_database_settings
from .prompts import return_instructions_bqml
from .tools import check_bq_models, rag_response

_logger = logging.getLogger(__name__)
USER_AGENT = "orkhon-data-science-agent"


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the BQML agent before execution."""
    _logger.info("Setting up BQML agent context")

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

    # Store user_agent in state
    tool_context.state["user_agent"] = USER_AGENT

    # Get database settings from parent context
    database_settings = get_bq_database_settings(callback_context)
    tool_context.state["database_settings"] = database_settings

    callback_context.tool_context = tool_context
    _logger.info("BQML agent context setup complete")


def get_bqml_agent() -> Agent:
    """Create a new BQML agent instance.
    
    Returns a fresh instance each time to avoid conflicts when used as sub-agent.
    """
    bigquery_tool_config = BigQueryToolConfig(
        write_mode=WriteMode.ALLOWED,  # ALLOWED for CREATE MODEL statements
        max_query_result_rows=80,
        application_name=USER_AGENT,
    )
    
    bq_toolset = BigQueryToolset(
        tool_filter=["execute_sql"], 
        bigquery_tool_config=bigquery_tool_config
    )
    
    agent = Agent(
        model=os.getenv("BQML_AGENT_MODEL", "gemini-2.5-flash"),
        name="bqml_agent",
        instruction=return_instructions_bqml(),
        before_agent_callback=setup_before_agent_call,
        tools=[bq_toolset, check_bq_models, rag_response],
    )
    
    _logger.debug("Created new BQML agent instance with model: %s",
                  os.getenv("BQML_AGENT_MODEL", "gemini-2.5-flash"))
    return agent


# Module-level instance for backward compatibility
root_agent = get_bqml_agent()