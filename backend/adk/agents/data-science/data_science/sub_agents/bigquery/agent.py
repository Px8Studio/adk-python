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

import json
import logging
import os
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from ...utils.utils import get_env_var, USER_AGENT
try:
    from _common.config import get_llm_model, get_model  # type: ignore
except Exception:  # pragma: no cover
    def get_llm_model() -> str:
        return os.getenv("ORKHON_LLM_MODEL") or os.getenv("ROOT_AGENT_MODEL") or os.getenv("GOOGLE_GEMINI_MODEL") or "gemini-2.5-flash"
    def get_model(profile: str) -> str:
        return get_llm_model()
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types
from . import tools
from .chase_sql import chase_db_tools
from .prompts import return_instructions_bigquery

logger = logging.getLogger(__name__)

NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")

# BigQuery built-in tools in ADK
# https://google.github.io/adk-docs/tools/built-in-tools/#bigquery
ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL = "execute_sql"


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent and cache database settings to avoid repeated queries."""
    
    # Cache database settings on first call to avoid repeated schema queries
    if "database_settings" not in callback_context.state:
        logger.info("Loading and caching BigQuery database settings")
        callback_context.state["database_settings"] = (
            tools.get_database_settings()
        )
        callback_context.state["bigquery_schema_cached"] = True
    else:
        logger.debug("Using cached BigQuery database settings")


def _serialize_value(value: Any) -> Any:
    """Serialize BigQuery values so they are JSON friendly for downstream use."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    if isinstance(value, Mapping):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    return value


def _serialize_row(row: Any) -> Any:
    """Convert BigQuery rows to basic Python types for analytics agent."""
    if isinstance(row, Mapping):
        return {k: _serialize_value(v) for k, v in row.items()}
    if hasattr(row, "items"):
        return {k: _serialize_value(v) for k, v in dict(row).items()}
    return _serialize_value(row)


def store_results_in_context(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict,
) -> Optional[Dict]:
    """Store query results in context and log execution details."""
    
    # We are setting a state for the data science agent to be able to use the
    # sql query results as context
    if tool.name == ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL:
        if tool_response["status"] == "SUCCESS":
            rows = tool_response["rows"]
            serialized_rows = [_serialize_row(row) for row in rows]
            preview_rows = serialized_rows[:5]
            tool_context.state["bigquery_query_result"] = serialized_rows
            tool_context.state["bigquery_query_result_json"] = json.dumps(
                serialized_rows, default=_serialize_value
            )
            tool_context.state["bigquery_query_result_preview"] = preview_rows
            tool_context.state["bigquery_row_count"] = len(serialized_rows)  # ← store count
            logger.info(
                "BigQuery query succeeded, stored %s rows in context",
                len(serialized_rows)
            )
        else:
            logger.warning(
                "BigQuery query failed with status: %s",
                tool_response.get("status")
            )
            tool_context.state["bigquery_row_count"] = 0  # ensure present on failure

    return None


bigquery_tool_filter = [ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL]
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED, application_name=USER_AGENT
)
bigquery_toolset = BigQueryToolset(
    tool_filter=bigquery_tool_filter, bigquery_tool_config=bigquery_tool_config
)


class DataScienceBigQueryAgent(LlmAgent):
    """Subclass to align runner origin with the data_science package."""


bigquery_agent = DataScienceBigQueryAgent(
    model=os.getenv("BIGQUERY_AGENT_MODEL") or get_model("smart"),
    name="bigquery_agent",
    instruction=return_instructions_bigquery(),
    tools=[
        (
            chase_db_tools.initial_bq_nl2sql
            if NL2SQL_METHOD == "CHASE"
            else tools.bigquery_nl2sql
        ),
        bigquery_toolset,
    ],
    before_agent_callback=setup_before_agent_call,
    after_tool_callback=store_results_in_context,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
