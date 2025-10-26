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

"""BigQuery agent tools and utilities."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from google.adk.tools import ToolContext

if TYPE_CHECKING:
  # Import again under TYPE_CHECKING to satisfy both linter and runtime
  from google.adk.tools import ToolContext

_logger = logging.getLogger(__name__)


def get_database_settings(dataset_configs: list[dict] | None = None) -> dict:
  """Get BigQuery database settings including schema information.

  Supports multiple datasets. If dataset_configs is provided, it will read
  schema from all configured datasets. Otherwise, falls back to single
  BQ_DATASET_ID environment variable for backwards compatibility.

  Args:
    dataset_configs: List of dataset configurations from the config file.
                     Each config should have 'name' and 'type' fields.

  Returns:
    Dictionary containing project IDs, datasets info, and schema information.
  """
  bq_data_project_id = os.getenv("BQ_DATA_PROJECT_ID", "")
  bq_compute_project_id = os.getenv("BQ_COMPUTE_PROJECT_ID", bq_data_project_id)

  if not bq_data_project_id:
    _logger.warning(
        "BQ_DATA_PROJECT_ID not set. Schema information will be limited."
    )
    return {
        "data_project_id": bq_data_project_id,
        "compute_project_id": bq_compute_project_id,
        "datasets": {},
        "schema": "BigQuery schema not available. Please configure "
        "BQ_DATA_PROJECT_ID environment variable.",
    }

  # Get dataset IDs to query
  dataset_ids = []
  if dataset_configs:
    # Multi-dataset mode: use datasets from config
    dataset_ids = [
        cfg["name"] for cfg in dataset_configs if cfg.get("type") == "bigquery"
    ]
    _logger.info("Multi-dataset mode: %s", ", ".join(dataset_ids))
  else:
    # Backwards compatibility: single dataset from env var
    bq_dataset_id = os.getenv("BQ_DATASET_ID", "")
    if bq_dataset_id:
      dataset_ids = [bq_dataset_id]
      _logger.info("Single-dataset mode: %s", bq_dataset_id)

  if not dataset_ids:
    _logger.warning(
        "No datasets configured. Provide dataset_configs or set BQ_DATASET_ID."
    )
    return {
        "data_project_id": bq_data_project_id,
        "compute_project_id": bq_compute_project_id,
        "datasets": {},
        "schema": "No BigQuery datasets configured.",
    }

  # Get schema information from BigQuery for all datasets
  client = bigquery.Client(project=bq_compute_project_id)
  all_schema_info = []
  datasets_info = {}

  for dataset_id in dataset_ids:
    try:
      dataset_ref = client.dataset(dataset_id, project=bq_data_project_id)
      tables = client.list_tables(dataset_ref)

      dataset_schema = [f"\n{'=' * 70}"]
      dataset_schema.append(f"Dataset: {bq_data_project_id}.{dataset_id}")
      dataset_schema.append("=" * 70)

      table_list = []
      for table_item in tables:
        table_ref = dataset_ref.table(table_item.table_id)
        table = client.get_table(table_ref)

        dataset_schema.append(f"\nTable: {table.table_id}")
        dataset_schema.append("Columns:")
        for field in table.schema:
          dataset_schema.append(
              f"  - {field.name} ({field.field_type}): "
              f"{field.description or 'No description'}"
          )

        table_list.append(table.table_id)

      datasets_info[dataset_id] = {
          "project": bq_data_project_id,
          "dataset_id": dataset_id,
          "table_count": len(table_list),
          "tables": table_list,
      }

      all_schema_info.extend(dataset_schema)
      _logger.info(
          "Retrieved schema for %s: %d tables", dataset_id, len(table_list)
      )

    except Exception as e:  # pylint: disable=broad-except
      _logger.warning("Failed to retrieve schema for %s: %s", dataset_id, e)
      all_schema_info.append(f"\nDataset {dataset_id}: Failed to retrieve schema: {e}")
      datasets_info[dataset_id] = {
          "project": bq_data_project_id,
          "dataset_id": dataset_id,
          "error": str(e),
      }

  return {
      "data_project_id": bq_data_project_id,
      "compute_project_id": bq_compute_project_id,
      "datasets": datasets_info,
      "schema": "\n".join(all_schema_info),
  }


def bigquery_nl2sql(nl_query: str, tool_context: ToolContext) -> str:
  """Translate natural language query to BigQuery SQL.

  This is a simplified baseline NL2SQL tool that uses the schema information
  from the database settings to generate SQL queries.

  Args:
    nl_query: Natural language question about the data
    tool_context: ADK tool context containing database settings

  Returns:
    SQL query as a string
  """
  db_settings = tool_context.state.get("database_settings", {}).get("bigquery", {})

  if not db_settings:
    return (
        "Error: Database settings not found. Cannot generate SQL query. "
        "Please ensure BigQuery is properly configured."
    )

  schema = db_settings.get("schema", "")
  data_project_id = db_settings.get("data_project_id", "")
  datasets_info = db_settings.get("datasets", {})

  # Build dataset context for multi-dataset support
  dataset_context = []
  for dataset_id, info in datasets_info.items():
    if "error" not in info:
      dataset_context.append(
          f"Dataset: {data_project_id}.{dataset_id} "
          f"({info.get('table_count', 0)} tables)"
      )

  prompt = f"""Based on the following BigQuery schema, generate a SQL query to answer the user's question.

Available Datasets:
{chr(10).join(dataset_context)}

Schema:
{schema}

User Question: {nl_query}

Generate ONLY the SQL query without any explanation. Use fully qualified table names in the format `{data_project_id}.<dataset_id>.<table_name>`.
When multiple datasets are available, analyze which dataset(s) contain the relevant data for the question.
"""

  # This would normally call the LLM to generate SQL
  # For now, return a template that the agent will fill in
  return prompt
