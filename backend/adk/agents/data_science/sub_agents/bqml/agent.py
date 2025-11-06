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
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from ..bigquery.agent import bigquery_agent
from ..bigquery.tools import get_database_settings as get_bq_database_settings
from .prompts import return_instructions_bqml
from .tools import check_bq_models, rag_response

_logger = logging.getLogger(__name__)
USER_AGENT = "orkhon-data-science-agent"


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the BQML agent before execution.
    
    This follows the official ADK data-science sample pattern:
    - Use callback_context.state directly (no invocation_context access)
    - Retrieve or initialize database settings
    """
    _logger.debug("Setting up BQML agent context")

    # Get or initialize database settings using the official pattern
    if "database_settings" not in callback_context.state:
        # If not already set by parent, get from environment
        database_settings = get_bq_database_settings(callback_context)
        callback_context.state["database_settings"] = database_settings
    
    _logger.debug("BQML agent context setup complete")


def get_bqml_agent() -> Agent:
    """Create a new BQML agent instance.
    
    Returns a fresh instance each time to avoid conflicts when used as sub-agent.
    """
    # Get database configuration for instructions
    project_id = (
        os.getenv("BQ_PROJECT_ID")
        or os.getenv("BQ_DATA_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    dataset_id = os.getenv("BQ_DATASET_ID", "dnb_statistics")
    location = os.getenv("BIGQUERY_LOCATION", "europe-west4")
    
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
        instruction=return_instructions_bqml(
            project_id=project_id,
            dataset_id=dataset_id,
            location=location,
        ),
        before_agent_callback=setup_before_agent_call,
        tools=[bq_toolset, check_bq_models, rag_response],
    )
    
    _logger.debug("Created new BQML agent instance with model: %s",
                  os.getenv("BQML_AGENT_MODEL", "gemini-2.5-flash"))
    return agent


# Module-level instance for backward compatibility
root_agent = get_bqml_agent()