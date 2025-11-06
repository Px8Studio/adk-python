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

# Import sub-agents - use relative imports for local modules
from .sub_agents.analytics.agent import get_analytics_agent
from .sub_agents.bigquery.agent import get_bigquery_agent
from .sub_agents.bigquery.tools import get_database_settings as get_bq_database_settings
from .sub_agents.bqml.agent import root_agent as bqml_agent

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
  """Generate dataset definitions WITH actual table schemas for agent instructions.
  
  This follows the ADK sample pattern by including table/column metadata.
  
  Returns:
    Formatted string with dataset descriptions and table listings
  """
  if not _database_settings:
    return "No datasets configured."
  
  bq_settings = _database_settings.get("bigquery", {})
  datasets = bq_settings.get("datasets", [])
  
  if not datasets:
    return "No BigQuery datasets available."
  
  # Get project ID for fully qualified table names
  project_id = bq_settings.get("project_id", "unknown")
  
  lines = ["", "【Database Schema】", ""]
  
  for dataset in datasets:
    name = dataset.get("name", "unknown")
    desc = dataset.get("description", "No description")
    
    lines.append(f"## Dataset: {name}")
    lines.append(f"Description: {desc}")
    lines.append("")
    
    # Get table schema
    schema = dataset.get("schema", {})
    tables = schema.get("tables", {})
    
    if tables:
      # Generate CREATE TABLE statements (ADK pattern)
      # This format is optimal for LLM understanding:
      # - Full table names with project prefix
      # - OPTIONS(description) for columns with descriptions
      # - Self-documenting schema
      create_statements = format_schema_as_create_table_statements(
        project_id=project_id,
        dataset_id=name,
        tables=tables,
        include_table_description=True,
        max_tables=20,  # Limit for token management (can adjust based on needs)
      )
      
      lines.append(create_statements)
      lines.append("")
    else:
      lines.append("(No tables found - schema may not have loaded)")
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
  
  This follows the ADK sample pattern by including schemas in instructions.
  
  Returns:
    Configured root agent
  """
  # Get environment configuration
  model = os.getenv("MODEL", "gemini-2.5-flash")
  google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
  bigquery_location = os.getenv("BIGQUERY_LOCATION", "us-central1")
  
  # Get database settings (now includes full schemas)
  database_settings = _database_settings.get("bigquery", {})
  
  # Build instruction with schema information (like ADK sample)
  instruction = f"""
You are the Orkhon Data Science Coordinator, an expert assistant for analyzing
Dutch financial and economic data from De Nederlandsche Bank (DNB).

**Your Role:**
- Coordinate analysis across multiple specialized sub-agents
- Route queries to the appropriate sub-agent (BigQuery, Analytics, or BQML)
- Synthesize results into clear, actionable insights

**Available Sub-Agents:**
1. **bigquery_agent**: Query and explore BigQuery datasets
2. **analytics_agent**: Perform statistical analysis and visualization
3. **bqml_agent**: Build and evaluate machine learning models

**Database Schema (CREATE TABLE format with column descriptions):**
{get_dataset_definitions_for_instructions()}

**Database Configuration:**
- Project: {database_settings.get('project_id', 'Not configured')}
- Default Dataset: {database_settings.get('dataset_id', 'dnb_statistics')}
- Location: {database_settings.get('location', bigquery_location)}

**Table Naming Convention:**
Tables follow: `category__subcategory__endpoint_name`
Example: `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`

**Instructions:**
1. For data queries → Use bigquery_agent
2. For analysis/visualization → Use analytics_agent  
3. For ML models → Use bqml_agent
4. The schema above shows CREATE TABLE statements with OPTIONS(description) for columns
5. Use column descriptions to understand data meaning and relationships
6. Always use fully qualified table names: `project.dataset.table`
7. Provide clear, data-driven insights to the user

Remember: The CREATE TABLE statements show the exact schema with types and
descriptions. Sub-agents have access to this information for accurate SQL generation.
"""

  # Create root agent with sub-agents using correct parameter name
  root_agent = Agent(
      name="data_science_coordinator",
      model=model,
      instruction=instruction,
      description="Coordinates data science workflows across DNB datasets",
      sub_agents=[
          get_bigquery_agent(),
          get_analytics_agent(),
          bqml_agent,
      ],
      tools=[load_artifacts_tool],
      before_agent_callback=load_database_settings_in_context,
      # Remove generation_config - let model use defaults
      # generation_config=types.GenerateContentConfig(
      #     temperature=1.0,
      #     top_k=40.0,
      #     top_p=0.95,
      # ),
  )
  
  _logger.info("Orkhon Data Science Coordinator initialized")
  return root_agent


# Initialize dataset configurations and database settings at module load
_dataset_config = load_dataset_config()
_database_settings = init_database_settings(_dataset_config)

# Create the root agent
root_agent = get_root_agent()
