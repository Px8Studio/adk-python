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

    bigquery_data = ""
    bigquery_data_json = ""
    bigquery_preview = None
    alloydb_data = ""

    # Prefer JSON if available; otherwise, synthesize JSON from Python data
    if "bigquery_query_result_json" in tool_context.state:
        bigquery_data_json = tool_context.state["bigquery_query_result_json"]
        logger.debug("BigQuery JSON payload length: %s", len(bigquery_data_json))
    if "bigquery_query_result" in tool_context.state:
        bigquery_data = tool_context.state["bigquery_query_result"]
        logger.info("Found BigQuery data with %s items/chars", len(bigquery_data))
        if not bigquery_data_json:
            try:
                # If it's a list/dict, turn into JSON; else string-cast
                if isinstance(bigquery_data, (list, dict)):
                    bigquery_data_json = json.dumps(bigquery_data, default=str)
                else:
                    bigquery_data_json = json.dumps({"data": str(bigquery_data)})
            except Exception as _:
                bigquery_data_json = str(bigquery_data)

    if "bigquery_query_result_preview" in tool_context.state:
        bigquery_preview = tool_context.state["bigquery_query_result_preview"]
        logger.debug("BigQuery preview sample rows: %s", len(bigquery_preview))

    if "alloydb_query_result" in tool_context.state:
        alloydb_data = tool_context.state["alloydb_query_result"]
        logger.info(
            "Found AlloyDB data with %s items/chars",
            len(alloydb_data) if isinstance(alloydb_data, (list, str)) else "unknown",
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

    # Keep payloads reasonable to avoid token bloating
    def _trim(s: str, max_len: int = 150_000) -> str:
        return s if len(s) <= max_len else s[:max_len] + "\n/* trimmed */"

    # Embed data as Python variables so generated code can reference them directly.
    bigquery_json_literal = _trim(bigquery_data_json or "")
    bigquery_preview_literal = json.dumps(bigquery_preview, default=str) if bigquery_preview else ""
    alloydb_json_literal = _trim(
        alloydb_data if isinstance(alloydb_data, str) else json.dumps(alloydb_data, default=str) if alloydb_data else ""
    )

    question_with_data = f"""
Question to answer:
{question}

# Data payload for your Python code (ready-to-use variables)
bigquery_json = r\"\"\"{bigquery_json_literal}\"\"\"
bigquery_preview_json = r\"\"\"{bigquery_preview_literal}\"\"\" 
alloydb_json = r\"\"\"{alloydb_json_literal}\"\"\" 

You MUST:
1) Load BigQuery JSON into a pandas DataFrame:
   import io, pandas as pd
   bigquery_df = pd.read_json(io.StringIO(bigquery_json))
   # If a 'period' or date column exists, use pd.to_datetime and sort values.

2) Create the requested visualization with matplotlib. Then SAVE the artifact:
   import matplotlib.pyplot as plt
   plt.tight_layout()
   plt.savefig("chart.png", dpi=150, bbox_inches="tight")
   # Note: The system collects saved files automatically.

3) Return a short textual RESULT and EXPLANATION. Do NOT print huge tables.

# Optional preview rows (small sample):
# bigquery_preview_json is a small sample you may print for debugging if needed.
"""

    logger.debug("Calling analytics agent with data context")
    agent_tool = AgentTool(agent=analytics_agent)

    try:
        analytics_agent_output = await agent_tool.run_async(
            args={"request": question_with_data}, tool_context=tool_context
        )
        state_keys_after_run = list(tool_context.state.to_dict().keys())
        logger.debug("Analytics agent state keys after run: %s", state_keys_after_run)
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
                    logger.info("Found artifacts despite empty output: %s", artifact_keys)
                    return (
                        "Result: Visualization artifacts created successfully.\n\n"
                        "Explanation:\n"
                        f"- Artifacts: {', '.join(artifact_keys)}\n"
                        "- The model returned no textual summary; showing artifact names.\n"
                        "- Open the artifacts panel to view the charts."
                    )
            except Exception as artifact_error:
                logger.warning("Could not list artifacts: %s", artifact_error)

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

            return (
                "Result: Analytics execution yielded no output.\n\n"
                "Explanation:\n"
                "- No text and no artifacts detected.\n"
                "- Ensure the Python code saves the plot with plt.savefig(...).\n"
                "- Rephrase request or reduce complexity if this persists."
            )

        logger.info("Analytics agent returned output of length: %s", len(analytics_agent_output))
        tool_context.state["analytics_agent_output"] = analytics_agent_output
        return analytics_agent_output

    except Exception as e:
        logger.error("Error calling analytics agent: %s", e, exc_info=True)
        return (
            f"Error during analytics processing: {str(e)}. "
            "Please check your request and try again."
        )
