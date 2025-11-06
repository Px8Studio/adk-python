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

"""Tools for the Data Science root coordinator agent."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from google.adk.tools.agent_tool import AgentTool

if TYPE_CHECKING:
  from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


async def call_bigquery_agent(
    question: str,
    tool_context: ToolContext,
) -> str:
  """Tool to call BigQuery database (NL2SQL) agent with Chase SQL support.
  
  Args:
    question: Natural language question about the data in BigQuery
    tool_context: ADK tool context for state management
    
  Returns:
    Query results from BigQuery agent
  """
  logger.info(f"Routing to BigQuery agent: {question}")
  
  # The AgentTool will handle the actual agent invocation
  # This is just a placeholder that won't be called directly
  # when using AgentTool pattern
  return f"Query routed to BigQuery agent: {question}"


async def call_analytics_agent(
    analysis_request: str,
    tool_context: ToolContext,
) -> str:
  """Tool to call analytics agent for Python-based analysis and visualization.
  
  Args:
    analysis_request: Description of the analysis to perform
    tool_context: ADK tool context for state management
    
  Returns:
    Analysis results from analytics agent
  """
  logger.info(f"Routing to Analytics agent: {analysis_request}")
  return f"Analysis routed to Analytics agent: {analysis_request}"


async def call_bqml_agent(
    ml_request: str,
    tool_context: ToolContext,
) -> str:
  """Tool to call BQML agent for machine learning operations.
  
  Args:
    ml_request: Description of the ML model to build or use
    tool_context: ADK tool context for state management
    
  Returns:
    ML results from BQML agent
  """
  logger.info(f"Routing to BQML agent: {ml_request}")
  return f"ML request routed to BQML agent: {ml_request}"
