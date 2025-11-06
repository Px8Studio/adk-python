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

"""Top-level data science coordinator agent for Orkhon Data Science Multi-Agent System.

This agent coordinates between specialized sub-agents for:
- BigQuery database access (NL2SQL with Chase SQL)
- Analytics and visualization (NL2Py with Code Interpreter)
- BQML for machine learning operations
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmAgent as Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.genai import types

# Import local utilities (agent should be self-contained per ADK pattern)
from .utils.schema_formatter import format_schema_as_create_table_statements

# Import sub-agents and tools
from .sub_agents.bigquery.tools import get_database_settings as get_bq_database_settings
from .sub_agents.bqml.agent import root_agent as bqml_agent
from .tools import call_analytics_agent, call_bigquery_agent

_logger = logging.getLogger(__name__)

# Module-level configuration
_dataset_config: dict = {}
_database_settings: dict = {}
_supported_dataset_types = ["bigquery"]
_required_dataset_config_params = ["name", "description"]


def load_dataset_config() -> dict:
  """Load dataset configuration from JSON file."""
  config_path = Path(__file__).parent / "dnb_datasets_config.json"
  
  if not config_path.exists():
    _logger.warning(f"Dataset config not found at {config_path}")
    return {"datasets": []}
  
  try:
    with open(config_path) as f:
      return json.load(f)
  except Exception as e:
    _logger.error(f"Failed to load dataset config: {e}")
    return {"datasets": []}


def get_database_settings(db_type: str) -> dict:
  """Get database settings for a specific type.
  
  Args:
    db_type: Type of database (e.g., "bigquery")
  
  Returns:
    Database configuration dictionary
  """
  if db_type not in _supported_dataset_types:
    raise ValueError(f"Unsupported database type: {db_type}")
  
  return _database_settings.get(db_type, {})


def init_database_settings(dataset_config: dict) -> dict:
  """Initialize database settings with ACTUAL schemas from BigQuery.
  
  This follows the ADK sample pattern by loading schemas at initialization.
  
  Args:
    dataset_config: Dataset configuration from dnb_datasets_config.json
  
  Returns:
    Initialized database settings with full schemas
  """
  settings = {}
  
  # Extract BigQuery datasets from config
  bq_datasets = [
      d for d in dataset_config.get("datasets", [])
      if d.get("type") == "bigquery"
  ]
  
  if bq_datasets:
    # Construct dataset configs for schema loader (ADK sample format)
    dataset_configs = []
    for ds in bq_datasets:
      dataset_configs.append({
          "name": ds.get("name"),
          "description": ds.get("description", ""),
          "dataset_id": ds.get("dataset_id", ds.get("name")),
          "project_id": ds.get("project_id", os.getenv("GOOGLE_CLOUD_PROJECT")),
          "location": ds.get("location", os.getenv("BIGQUERY_LOCATION", "us-central1")),
      })
    
    # Load ACTUAL schemas from BigQuery (like ADK sample does)
    try:
      bq_settings = get_bq_database_settings(dataset_configs)
      settings["bigquery"] = bq_settings
      
      # Log schema loading success
      num_datasets = len(bq_settings.get("datasets", []))
      total_tables = sum(
          len(ds.get("schema", {}).get("tables", {}))
          for ds in bq_settings.get("datasets", [])
      )
      _logger.info(
          f"Loaded BigQuery schemas: {num_datasets} datasets, {total_tables} tables"
      )
      
    except Exception as e:
      _logger.error(f"Failed to load BigQuery schemas: {e}")
      # Fallback to empty structure
      settings["bigquery"] = {
          "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
          "dataset_id": os.getenv("BQ_DATASET_ID", "dnb_statistics"),
          "location": os.getenv("BIGQUERY_LOCATION", "us-central1"),
          "datasets": []
      }
  
  return settings


def get_dataset_definitions_for_instructions() -> str:
  """Generate high-level dataset summary for coordinator instructions.
  
  Provides overview information only. Detailed schemas are passed via 
  callback_context.state to sub-agents to avoid instruction bloat.
  
  Returns:
    Formatted string with dataset descriptions and table counts
  """
  if not _database_settings:
    return "No datasets configured."
  
  bq_settings = _database_settings.get("bigquery", {})
  datasets = bq_settings.get("datasets", [])
  
  if not datasets:
    return "No BigQuery datasets available."
  
  # Get project ID for reference
  project_id = bq_settings.get("project_id", "unknown")
  
  lines = ["", "【Available Datasets】", ""]
  lines.append(f"**Project ID:** {project_id}")
  lines.append("")
  
  for dataset in datasets:
    name = dataset.get("name", "unknown")
    desc = dataset.get("description", "No description")
    dataset_id = dataset.get("dataset_id", name)
    
    # Get table schema
    schema = dataset.get("schema", {})
    tables = schema.get("tables", {})
    table_count = len(tables)
    
    lines.append(f"## Dataset: {name}")
    lines.append(f"**ID:** `{project_id}.{dataset_id}`")
    lines.append(f"**Description:** {desc}")
    lines.append(f"**Tables:** {table_count} tables available")
    
    if tables:
      # List table names only (no full schemas)
      table_names = sorted(tables.keys())[:10]  # Show first 10
      lines.append(f"**Sample Tables:** {', '.join(f'`{t}`' for t in table_names)}")
      if len(tables) > 10:
        lines.append(f"  _(and {len(tables) - 10} more)_")
    
    lines.append("")
  
  lines.append("**Note:** Detailed table schemas with column definitions are ")
  lines.append("available to sub-agents via context. Use bigquery_agent for SQL ")
  lines.append("queries and analytics_agent for data analysis.")
  lines.append("")
  
  return "\n".join(lines)


def load_database_settings_in_context(
    callback_context: CallbackContext,
) -> str | None:
  """Load database settings into the agent context for sub-agent access.
  
  This follows the ADK sample pattern by passing schemas via callback_context.state.
  
  Args:
    callback_context: The callback context from the agent execution
    
  Returns:
    None or error message if loading fails
  """
  try:
    # Use callback_context.state (ADK best practice)
    if not hasattr(callback_context, 'state'):
      callback_context.state = {}
    
    # Store database settings in agent state (accessible to sub-agents)
    callback_context.state["database_settings"] = _database_settings
    
    # Log summary of what's available
    bq_datasets = _database_settings.get("bigquery", {}).get("datasets", [])
    total_tables = sum(
        len(ds.get("schema", {}).get("tables", {}))
        for ds in bq_datasets
    )
    
    _logger.info(
        f"Loaded database settings into context: "
        f"{len(bq_datasets)} datasets, {total_tables} tables"
    )
    
    return None
    
  except Exception as e:
    error_msg = f"Failed to load database settings: {e}"
    _logger.error(error_msg)
    return error_msg


def get_root_agent() -> Agent:
  """Create the root data science coordinator agent.
  
  Provides high-level dataset overview in instructions. Detailed schemas are
  passed to sub-agents via callback_context.state to avoid token bloat.
  
  Returns:
    Configured root agent
  """
  # Get environment configuration
  model = os.getenv("MODEL", "gemini-2.5-flash")
  google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
  bigquery_location = os.getenv("BIGQUERY_LOCATION", "us-central1")
  
  # Get database settings (includes full schemas in context, not instructions)
  database_settings = _database_settings.get("bigquery", {})
  
  # Build instruction with high-level dataset overview
  instruction = f"""
You are the Orkhon Data Science Coordinator, an expert assistant for analyzing
Dutch financial and economic data from De Nederlandsche Bank (DNB).

<YOUR ROLE>
You are a senior data scientist coordinator tasked with:
1. Understanding user requests about DNB financial and economic data
2. Calling appropriate specialized agents/tools to fulfill requests
3. Synthesizing results into clear, natural language responses
4. DO NOT pass raw JSON to users - extract key information and present naturally
</YOUR ROLE>

<AVAILABLE TOOLS>
1. **call_bigquery_agent(question)**: 
   - Use for: SQL queries, data retrieval, schema inspection, listing tables
   - Returns: Structured data with SQL query and results
   
2. **call_analytics_agent(question)**: 
   - Use for: Statistical analysis, data visualization, Python-based insights
   - Requires: Data must be retrieved by call_bigquery_agent first
   - Returns: Analysis with code, visualizations, and insights
   
3. **bqml_agent** (sub-agent):
   - Use for: Machine learning model creation, training, predictions
   - Only use when user specifically requests BQML/BigQuery ML
</AVAILABLE TOOLS>

<AVAILABLE DATASETS>
{get_dataset_definitions_for_instructions()}

<DATABASE CONFIGURATION>
- Project: {database_settings.get('project_id', 'Not configured')}
- Default Dataset: {database_settings.get('dataset_id', 'dnb_statistics')}
- Location: {database_settings.get('location', bigquery_location)}

Table naming: `category__subcategory__endpoint_name`
Example: `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`
</DATABASE CONFIGURATION>

<INSTRUCTIONS>
- If user asks questions answerable directly from schema, answer directly
- For data queries: call call_bigquery_agent
- For analysis/visualization: call call_bigquery_agent first, then call_analytics_agent
- For BQML: delegate to bqml_agent sub-agent
- After receiving tool/agent responses:
  * Extract key information from structured responses
  * Present results in natural, conversational format
  * Use Markdown formatting for readability
  * DO NOT show raw JSON - synthesize it into prose
  * Include visualizations when available
</INSTRUCTIONS>

<WORKFLOW>
1. Understand user request
2. Call appropriate tool(s) to get data/analysis
3. **Extract and synthesize** results from tool responses
4. **Respond in natural language** with clear explanations
5. Use Markdown format with sections like:
   - **Result:** Natural language summary
   - **Explanation:** How the result was derived
   - **Key Findings:** Important insights (if applicable)
</WORKFLOW>

<EXAMPLE INTERACTIONS>
User: "Show me insurance data"
You: [Call call_bigquery_agent] → Extract table data → Present as formatted table with description

User: "Analyze trends in that data"  
You: [Data already available] → [Call call_analytics_agent] → Extract insights and charts → Present findings naturally

User: "List available tables"
You: [Call call_bigquery_agent] → Extract table names → Present as bulleted list with descriptions
</EXAMPLE INTERACTIONS>

<CRITICAL RULES>
- NEVER return raw JSON to users
- ALWAYS synthesize tool responses into natural language
- Use proper Markdown formatting for structure
- Extract and highlight key insights
- Tools handle execution; you handle presentation
- Be conversational and helpful, not technical/robotic
</CRITICAL RULES>
"""

  # Create root agent with TOOLS (not sub-agents) for BigQuery and Analytics
  # Following official ADK sample pattern
  root_agent = Agent(
      name="data_science_coordinator",
      model=model,
      instruction=instruction,
      description="Coordinates data science workflows across DNB datasets",
      sub_agents=[
          bqml_agent,  # Only BQML as direct sub-agent
      ],
      tools=[
          call_bigquery_agent,  # Tool wrapper for BigQuery agent
          call_analytics_agent,  # Tool wrapper for Analytics agent
          load_artifacts_tool,  # For loading saved artifacts
      ],
      before_agent_callback=load_database_settings_in_context,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )
  
  _logger.info("Orkhon Data Science Coordinator initialized")
  return root_agent


# Initialize dataset configurations and database settings at module load
_dataset_config = load_dataset_config()
_database_settings = init_database_settings(_dataset_config)

# Create the root agent
root_agent = get_root_agent()
