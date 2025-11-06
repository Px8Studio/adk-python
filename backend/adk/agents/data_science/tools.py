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

"""Tools for the Orkhon Data Science root coordinator agent.

Following official ADK data-science sample pattern for multi-agent coordination.
"""

from __future__ import annotations

import logging

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.analytics.agent import analytics_agent
from .sub_agents.bigquery.agent import bigquery_agent

logger = logging.getLogger(__name__)


async def call_bigquery_agent(
    question: str,
    tool_context: ToolContext,
) -> str:
  """Tool to call BigQuery database (NL2SQL) agent.
  
  Use this for querying DNB datasets with natural language.
  
  Args:
    question: Natural language question about the data
    tool_context: Tool context with database settings
    
  Returns:
    Response from BigQuery agent with SQL and results
  """
  logger.debug("call_bigquery_agent: %s", question)
  
  agent_tool = AgentTool(agent=bigquery_agent)
  
  bigquery_agent_output = await agent_tool.run_async(
      args={"request": question}, 
      tool_context=tool_context
  )
  
  # Store for coordinator's use (not for analytics - that uses query_result)
  tool_context.state["bigquery_agent_output"] = bigquery_agent_output
  
  return bigquery_agent_output


async def call_analytics_agent(
    question: str,
    tool_context: ToolContext,
) -> str:
  """Tool to call Analytics agent for data analysis and visualization.
  
  This tool can generate Python code to process and analyze datasets.
  
  Capabilities:
  - Creating graphics for data visualization
  - Processing or filtering existing datasets
  - Statistical analysis (mean, median, correlations, etc.)
  - Combining datasets for joined analysis
  
  Available Python modules:
  - pandas, numpy
  - matplotlib.pyplot, seaborn
  - scipy, scikit-learn (basic)
  
  The tool DOES NOT retrieve data from databases - it only analyzes
  data that was already retrieved by call_bigquery_agent.
  
  Args:
    question: Natural language analytics request
    tool_context: Tool context containing query results from BigQuery agent
    
  Returns:
    Analysis results with insights, code, and visualizations
  """
  logger.debug("call_analytics_agent: %s", question)
  
  # Extract actual query results (stored by BigQuery agent's after_tool_callback)
  # Following official sample pattern: analytics reads "bigquery_query_result"
  bigquery_data = ""
  if "bigquery_query_result" in tool_context.state:
    bigquery_data = tool_context.state["bigquery_query_result"]
  
  # Embed data context in the question
  question_with_data = f"""
Question to answer: {question}

Actual data to analyze is available in the following data table:

<BIGQUERY_DATA>
{bigquery_data}
</BIGQUERY_DATA>

Use this data to answer the question. The data is already loaded - you do not
need to query the database again.
"""
  
  agent_tool = AgentTool(agent=analytics_agent)
  
  analytics_agent_output = await agent_tool.run_async(
      args={"request": question_with_data},
      tool_context=tool_context
  )
  
  tool_context.state["analytics_agent_output"] = analytics_agent_output
  
  return analytics_agent_output
