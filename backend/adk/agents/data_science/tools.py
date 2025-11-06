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

"""Tools for the Data Science root coordinator agent.

These tools wrap sub-agents using AgentTool pattern, following the official
ADK data-science sample. This allows the coordinator to call sub-agents as
tools and synthesize their responses naturally.
"""

from __future__ import annotations

import logging

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# Import sub-agents
from .sub_agents.analytics.agent import get_analytics_agent
from .sub_agents.bigquery.agent import get_bigquery_agent

logger = logging.getLogger(__name__)


async def call_bigquery_agent(
    question: str,
    tool_context: ToolContext,
) -> str:
  """Tool to call BigQuery database (NL2SQL) agent.
  
  Use this tool to:
  - Query BigQuery datasets with natural language
  - Retrieve data samples
  - Check table schemas
  - List available tables
  
  Args:
    question: Natural language question about the data
    tool_context: Tool context with database settings
    
  Returns:
    Structured response from BigQuery agent with SQL and results
  """
  logger.debug("call_bigquery_agent: %s", question)
  
  # Create agent tool wrapper (following official ADK sample pattern)
  agent_tool = AgentTool(agent=get_bigquery_agent())
  
  # Call the agent asynchronously
  bigquery_agent_output = await agent_tool.run_async(
      args={"request": question}, 
      tool_context=tool_context
  )
  
  # Store output in context for potential reuse by analytics agent
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
    tool_context: Tool context containing query results from previous agents
    
  Returns:
    Analysis results with insights, code, and visualizations
  """
  logger.debug("call_analytics_agent: %s", question)
  
  # Extract data from previous BigQuery agent calls
  bigquery_data = ""
  if "bigquery_query_result" in tool_context.state:
    bigquery_data = tool_context.state["bigquery_query_result"]
  
  # Prepare question with embedded data context
  question_with_data = f"""
Question to answer: {question}

Actual data to analyze is available in the following data table:

<BIGQUERY_DATA>
{bigquery_data}
</BIGQUERY_DATA>

Use this data to answer the question. The data is already loaded - you do not
need to query the database again.
"""
  
  # Create agent tool wrapper (following official ADK sample pattern)
  agent_tool = AgentTool(agent=get_analytics_agent())
  
  # Call the agent asynchronously
  analytics_agent_output = await agent_tool.run_async(
      args={"request": question_with_data},
      tool_context=tool_context
  )
  
  # Store output in context
  tool_context.state["analytics_agent_output"] = analytics_agent_output
  
  return analytics_agent_output
