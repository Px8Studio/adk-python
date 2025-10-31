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
    if "database_settings" in callback_context.state:
        return

    db_settings = {"bigquery": get_bq_database_settings()}
    callback_context.state["database_settings"] = db_settings
    
    schema = db_settings["bigquery"]["schema"]
    callback_context._invocation_context.agent.instruction = (
        return_instructions_bqml() + f"\n\n<BigQuery Schema>\n{schema}\n</BigQuery Schema>"
    )


bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.ALLOWED,
    max_query_result_rows=80,
    application_name=USER_AGENT,
)
bq_toolset = BigQueryToolset(
    tool_filter=["execute_sql"], 
    bigquery_tool_config=bigquery_tool_config
)

root_agent = Agent(
    model=os.getenv("BQML_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="bqml_agent",
    instruction=return_instructions_bqml(),
    before_agent_callback=setup_before_agent_call,
    tools=[bq_toolset, check_bq_models, rag_response],
)