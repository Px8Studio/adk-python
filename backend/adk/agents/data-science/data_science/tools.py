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

    # Prevent infinite loops: cap analytics attempts per turn/session
    try:
        attempts = int(tool_context.state.get("analytics_attempts", 0))
    except Exception:
        attempts = 0
    if attempts >= 2:
        logger.warning("Analytics agent attempt cap reached: %s", attempts)
        return (
            "Analytics was already attempted multiple times. Skipping another "
            "run to avoid loops. If you'd like to try again, please adjust "
            "the request (e.g., choose fewer series or shorter date range)."
        )
    tool_context.state["analytics_attempts"] = attempts + 1

    # if question == "N/A":
    #    return tool_context.state["db_agent_output"]

    bigquery_data = ""
    bigquery_data_json = ""
    bigquery_preview = None
    alloydb_data = ""

    if "bigquery_query_result" in tool_context.state:
        bigquery_data = tool_context.state["bigquery_query_result"]
        logger.info(
            "Found BigQuery data with %s items/chars",
            len(bigquery_data)
        )
    else:
        logger.warning("No 'bigquery_query_result' found in tool_context.state")

    if "bigquery_query_result_json" in tool_context.state:
        bigquery_data_json = tool_context.state["bigquery_query_result_json"]
        logger.debug(
            "BigQuery JSON payload length: %s", len(bigquery_data_json)
        )
    if "bigquery_query_result_preview" in tool_context.state:
        bigquery_preview = tool_context.state["bigquery_query_result_preview"]
        logger.debug(
            "BigQuery preview sample rows: %s",
            len(bigquery_preview),
        )
    
    if "alloydb_query_result" in tool_context.state:
        alloydb_data = tool_context.state["alloydb_query_result"]
        logger.info(
            "Found AlloyDB data with %s items/chars",
            len(alloydb_data) if isinstance(alloydb_data, (list, str)) else "unknown"
        )

    if not (bigquery_data or bigquery_data_json or alloydb_data):
        logger.warning(
            "No data found in context for analytics agent. Available keys: %s",
            list(tool_context.state.to_dict().keys()),
        )
        return (
            "No data available for analysis. Please ensure data has been "
            "retrieved from BigQuery or AlloyDB first."
        )

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze this question is available in the following data
  tables:

    BigQuery results are provided below in JSON format. To load them, use:

        import io
        import pandas as pd
        bigquery_df = pd.read_json(io.StringIO(bigquery_json))

    Ensure you convert the `period` column with `pd.to_datetime` and sort it.

    <BIGQUERY_JSON>
    {bigquery_data_json or bigquery_data}
    </BIGQUERY_JSON>

    <BIGQUERY_PREVIEW>
    {json.dumps(bigquery_preview, default=str) if bigquery_preview else ''}
    </BIGQUERY_PREVIEW>

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
        state_keys_after_run = list(tool_context.state.to_dict().keys())
        logger.debug(
            "Analytics agent state keys after run: %s", state_keys_after_run
        )
        logger.debug(
            "Analytics agent artifact delta after run: %s",
            tool_context.actions.artifact_delta,
        )
        
        if not analytics_agent_output or analytics_agent_output.strip() == "":
            logger.error("Analytics agent returned empty text output")
            
            # Try to extract and display artifacts anyway
            try:
                artifact_keys = await tool_context.list_artifacts()
                if artifact_keys:
                    logger.info(
                        "Found artifacts despite empty output: %s",
                        artifact_keys
                    )
                    return (
                        "Result: Visualization artifacts created successfully.\n\n"
                        "Explanation:\n"
                        f"- Artifacts: {', '.join(artifact_keys)}\n"
                        "- The model returned no textual summary; this synthesized message prevents retry loops.\n"
                        "- Please inspect the charts; you may ask for deeper analysis."
                    )
            except Exception as artifact_error:
                logger.warning(
                    "Could not list artifacts: %s", artifact_error
                )

            # Check artifact delta in case artifacts were just created.
            if tool_context.actions.artifact_delta:
                artifact_keys = sorted(tool_context.actions.artifact_delta)
                logger.info(
                    "Artifacts registered via delta despite empty output: %s",
                    artifact_keys,
                )
                return (
                    "Result: Charts registered successfully.\n\n"
                    "Explanation:\n"
                    f"- Registered artifacts: {', '.join(artifact_keys)}\n"
                    "- Model omitted text; synthetic summary returned.\n"
                    "- Open artifacts panel to view visuals."
                )
            
            # No artifacts and no output - synthesize a minimal but non-empty
            # response so the root agent can conclude and not retry endlessly.
            return (
                "Result: Analytics execution yielded no output.\n\n"
                "Explanation:\n"
                "- No text and no artifacts detected.\n"
                "- Verify columns ('period','value','main_item') exist and that plt.savefig()+load_artifacts() were invoked.\n"
                "- Rephrase request or reduce complexity if this persists."
            )
        
        logger.info(
            "Analytics agent returned output of length: %s",
            len(analytics_agent_output)
        )
        tool_context.state["analytics_agent_output"] = analytics_agent_output
        return analytics_agent_output
        
    except Exception as e:
        logger.error("Error calling analytics agent: %s", e, exc_info=True)
        return (
            f"Error during analytics processing: {str(e)}. "
            "Please check your request and try again."
        )
