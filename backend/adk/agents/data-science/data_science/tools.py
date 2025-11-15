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

"""Tools for the ADK Samples Data Science Agent.

This file diverged from the upstream reference by adding retry / artifact
fallback logic and richer data packaging. We retain those enhancements but
add the required forward-annotation import and fix typos.
"""
from __future__ import annotations

import json
import logging
import os
import hashlib

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

    try:
        result = await agent_tool.run_async(
            args={"request": question}, tool_context=tool_context
        )
        logger.info("BigQuery agent completed successfully")
        tool_context.state["bigquery_agent_output"] = result
        return result
        
    except Exception as e:
        error_msg = str(e).lower()
        logger.error("BigQuery agent error: %s", e, exc_info=True)
        
        # Provide helpful error messages for common issues
        if "invalid column" in error_msg or "unrecognized name" in error_msg:
            return (
                f"Query failed - column not found: {str(e)}. "
                "Please check the database schema and use valid column names."
            )
        elif "table not found" in error_msg or "not found: table" in error_msg:
            return (
                f"Query failed - table not found: {str(e)}. "
                "Please check the dataset configuration and table names."
            )
        elif "syntax error" in error_msg:
            return (
                f"SQL syntax error: {str(e)}. "
                "The generated query has syntax issues. Please try rephrasing."
            )
        else:
            # Re-raise unexpected errors
            raise


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
    
    # Access invocation-level state
    invocation_context = tool_context._invocation_context
    
    bigquery_data = ""
    alloydb_data = ""
    
    # Check invocation_context.state (shared across all agents)
    if invocation_context:
        if "bigquery_query_result" in invocation_context.state:
            bigquery_data = invocation_context.state["bigquery_query_result"]
            logger.info("Found BigQuery data in invocation state")
        if "alloydb_query_result" in invocation_context.state:
            alloydb_data = invocation_context.state["alloydb_query_result"]
            logger.info("Found AlloyDB data in invocation state")
    
    # Fallback to tool_context.state (for backward compatibility)
    if not bigquery_data and "bigquery_query_result" in tool_context.state:
        bigquery_data = tool_context.state["bigquery_query_result"]
    if not alloydb_data and "alloydb_query_result" in tool_context.state:
        alloydb_data = tool_context.state["alloydb_query_result"]
    
    if not bigquery_data and not alloydb_data:
        return {
            "error": "No data available for analysis. Please run a database query first using call_bigquery_agent or call_alloydb_agent."
        }
    
    question_with_data = f"""
Question to answer: {question}

Actual data to analyze this question is available in the following data tables:

<BIGQUERY>
{bigquery_data}
</BIGQUERY>

<ALLOYDB>
{alloydb_data}
</ALLOYDB>
"""
    
    agent_tool = AgentTool(agent=analytics_agent)
    
    analytics_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    
    # Store output in invocation state for potential re-use
    if invocation_context:
        invocation_context.state["analytics_agent_output"] = analytics_agent_output
    
    return analytics_agent_output
