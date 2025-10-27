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
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types

from .prompts import return_instructions_bigquery

_logger = logging.getLogger(__name__)

# BigQuery built-in tools in ADK
# https://google.github.io/adk-docs/tools/built-in-tools/#bigquery
ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL = "execute_sql"

# User agent identifier for API calls
USER_AGENT = "orkhon-data-science-agent"


def setup_before_agent_call(callback_context: CallbackContext) -> None:
  """Setup callback executed before agent processes a request.
  
  Loads database configuration and schema information into the context.
  """
  _logger.info("Setting up BigQuery agent context")
  
  # Load project and dataset info from environment
  # Support multiple env var names for flexibility
  project_id = (
      os.getenv("BQ_DATA_PROJECT_ID")
      or os.getenv("BQ_PROJECT_ID")
      or os.getenv("GOOGLE_CLOUD_PROJECT")
  )
  dataset_id = os.getenv("BQ_DATASET_ID")
  
  if project_id and dataset_id:
    callback_context.set_in_context(
        "database_config",
        {
            "project_id": project_id,
            "dataset_id": dataset_id,
        },
    )
    _logger.info(
        f"Loaded BigQuery config: {project_id}.{dataset_id}"
    )


def store_results_in_context(
    callback_context: CallbackContext,
    tool: BaseTool,
    tool_context: ToolContext,
    tool_response: Any,
) -> None:
  """Store query results in context for potential reuse."""
  if tool.name == ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL:
    callback_context.set_in_context("last_query_result", tool_response)


# Configure BigQuery toolset
tool_filter = [ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL]

bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.ALLOWED,
    max_query_result_rows=100,
    application_name="orkhon-data-science-agent",
)

bigquery_toolset = BigQueryToolset(
    tool_filter=tool_filter,
    bigquery_tool_config=bigquery_tool_config,
)

# For backwards compatibility, create a default instance
bigquery_agent = LlmAgent(
    model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="bigquery_agent",
    instruction=return_instructions_bigquery(),
    tools=[
        bigquery_toolset,
    ],
    before_agent_callback=setup_before_agent_call,
    after_tool_callback=store_results_in_context,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

def get_bigquery_agent() -> LlmAgent:
  """Create a new BigQuery agent instance.
  
  Returns a fresh instance each time to avoid parent conflicts.
  """
  # Configure BigQuery toolset
  tool_filter = [ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL]
  
  bigquery_tool_config = BigQueryToolConfig(
      write_mode=WriteMode.ALLOWED,
      max_query_result_rows=100,
      application_name="orkhon-data-science-agent",
  )
  
  bigquery_toolset = BigQueryToolset(
      tool_filter=tool_filter,
      bigquery_tool_config=bigquery_tool_config,
  )

  # Create the BigQuery agent
  return LlmAgent(
      model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.0-flash-exp"),
      name="bigquery_agent",
      instruction=return_instructions_bigquery(),
      tools=[
          bigquery_toolset,
      ],
      before_agent_callback=setup_before_agent_call,
      after_tool_callback=store_results_in_context,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )
