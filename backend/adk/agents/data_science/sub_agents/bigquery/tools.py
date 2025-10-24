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

from google.cloud import bigquery

if TYPE_CHECKING:
  from google.adk.tools.tool_context import ToolContext

_logger = logging.getLogger(__name__)


def get_database_settings() -> dict:
  """Get BigQuery database settings including schema information.

  Returns:
    Dictionary containing project IDs, dataset ID, and schema information.
  """
  bq_data_project_id = os.getenv("BQ_DATA_PROJECT_ID", "")
  bq_compute_project_id = os.getenv("BQ_COMPUTE_PROJECT_ID", bq_data_project_id)
  bq_dataset_id = os.getenv("BQ_DATASET_ID", "")

  if not bq_data_project_id or not bq_dataset_id:
    _logger.warning(
        "BQ_DATA_PROJECT_ID or BQ_DATASET_ID not set. "
        "Schema information will be limited."
    )
    return {
        "data_project_id": bq_data_project_id,
        "compute_project_id": bq_compute_project_id,
        "dataset_id": bq_dataset_id,
        "schema": "BigQuery schema not available. Please configure "
        "BQ_DATA_PROJECT_ID and BQ_DATASET_ID environment variables.",
    }

  # Get schema information from BigQuery
  client = bigquery.Client(project=bq_compute_project_id)
  schema_info = []

  try:
    dataset_ref = client.dataset(bq_dataset_id, project=bq_data_project_id)
    tables = client.list_tables(dataset_ref)

    for table_item in tables:
      table_ref = dataset_ref.table(table_item.table_id)
      table = client.get_table(table_ref)

      schema_info.append(f"\nTable: {table.table_id}")
      schema_info.append("Columns:")
      for field in table.schema:
        schema_info.append(
            f"  - {field.name} ({field.field_type}): {field.description or 'No description'}"
        )

  except Exception as e:  # pylint: disable=broad-except
    _logger.warning("Failed to retrieve BigQuery schema: %s", e)
    schema_info.append(f"Failed to retrieve schema: {e}")

  return {
      "data_project_id": bq_data_project_id,
      "compute_project_id": bq_compute_project_id,
      "dataset_id": bq_dataset_id,
      "schema": "\n".join(schema_info),
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
  dataset_id = db_settings.get("dataset_id", "")
  data_project_id = db_settings.get("data_project_id", "")

  prompt = f"""Based on the following BigQuery schema, generate a SQL query to answer the user's question.

Schema:
{schema}

Dataset: {data_project_id}.{dataset_id}

User Question: {nl_query}

Generate ONLY the SQL query without any explanation. Use fully qualified table names in the format `{data_project_id}.{dataset_id}.table_name`.
"""

  # This would normally call the LLM to generate SQL
  # For now, return a template that the agent will fill in
  return prompt
