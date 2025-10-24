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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from google.adk.tools.tool_context import ToolContext


def call_bigquery_agent(query: str, tool_context: ToolContext) -> str:
  """Call the BigQuery agent with a natural language query.

  Args:
    query: Natural language question about the data in BigQuery
    tool_context: ADK tool context for state management

  Returns:
    Query results from BigQuery agent
  """
  # This tool will be automatically connected to the bigquery_agent sub-agent
  # by ADK when it's included in the root agent's tools list
  return f"Calling BigQuery agent with query: {query}"


def call_analytics_agent(analysis_request: str, tool_context: ToolContext) -> str:
  """Call the Analytics agent with a data analysis request.

  Args:
    analysis_request: Natural language description of analysis to perform
    tool_context: ADK tool context containing any data from previous steps

  Returns:
    Analysis results from Analytics agent
  """
  # This tool will be automatically connected to the analytics_agent sub-agent
  # by ADK when it's included in the root agent's tools list
  return f"Calling Analytics agent with request: {analysis_request}"
