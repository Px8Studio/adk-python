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

"""Tools for the ADK Sampmles Data Science Agent."""

import logging

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import alloydb_agent, analytics_agent, bigquery_agent

logger = logging.getLogger(__name__)


async def call_bigquery_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call bigquery database (nl2sql) agent."""
    logger.debug("call_bigquery_agent: %s", question)

    agent_tool = AgentTool(agent=bigquery_agent)

    bigquery_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["bigquery_agent_output"] = bigquery_agent_output
    return bigquery_agent_output


async def call_alloydb_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call alloydb database (nl2sql) agent."""
    logger.debug("call_alloydb_agent: %s", question)

    agent_tool = AgentTool(agent=alloydb_agent)

    alloydb_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["alloydb_agent_output"] = alloydb_agent_output
    return alloydb_agent_output


async def call_analytics_agent(
    question: str,
    tool_context: ToolContext,
):
    """
    This tool can generate Python code to process and analyze a dataset.

    Some of the tasks it can do in Python include:
    * Creating graphics for data visualization;
    * Processing or filtering existing datasets;
    * Combining datasets to create a joined dataset for further analysis.

    The Python modules available to it are:
    * io
    * math
    * re
    * matplotlib.pyplot
    * numpy
    * pandas

    The tool DOES NOT have the ability to retrieve additional data from
    a database. Only the data already retrieved will be analyzed.

    Args:
        question (str): Natural language question or analytics request.
        tool_context (ToolContext): The tool context to use for generating the
            SQL query.

    Returns:
        Response from the analytics agent.

    """
    logger.debug("call_analytics_agent: %s", question)

    # if question == "N/A":
    #    return tool_context.state["db_agent_output"]

    bigquery_data = ""
    alloydb_data = ""

    if "bigquery_query_result" in tool_context.state:
        bigquery_data = tool_context.state["bigquery_query_result"]
        logger.info(f"Found BigQuery data with {len(bigquery_data) if isinstance(bigquery_data, (list, str)) else 'unknown'} items/chars")
    else:
        logger.warning("No 'bigquery_query_result' found in tool_context.state")
    
    if "alloydb_query_result" in tool_context.state:
        alloydb_data = tool_context.state["alloydb_query_result"]
        logger.info(f"Found AlloyDB data with {len(alloydb_data) if isinstance(alloydb_data, (list, str)) else 'unknown'} items/chars")

    if not bigquery_data and not alloydb_data:
        logger.warning("No data found in context for analytics agent. Available keys: %s", list(tool_context.state.keys()))
        return "No data available for analysis. Please ensure data has been retrieved from BigQuery or AlloyDB first."

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze this question is available in the following data
  tables:

  <BIGQUERY>
  {bigquery_data}
  </BIGQUERY>

  <ALLOYDB>
  {alloydb_data}
  </ALLOYDB>

  """

    logger.debug("Calling analytics agent with data context")
    agent_tool = AgentTool(agent=analytics_agent)

    try:
        analytics_agent_output = await agent_tool.run_async(
            args={"request": question_with_data}, tool_context=tool_context
        )
        
        if not analytics_agent_output or analytics_agent_output.strip() == "":
            logger.error("Analytics agent returned empty output")
            return "Analytics agent execution completed but no output was generated. This may indicate an issue with the code executor or model configuration."
        
        logger.info(f"Analytics agent returned output of length: {len(analytics_agent_output)}")
        tool_context.state["analytics_agent_output"] = analytics_agent_output
        return analytics_agent_output
    except Exception as e:
        logger.error(f"Error calling analytics agent: {e}", exc_info=True)
        return f"Error during analytics processing: {str(e)}"
