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

"""BigQuery database configuration and schema management tools."""

from __future__ import annotations

import logging
import os
from typing import Any

from google.cloud import bigquery

from .schema_cache import get_cached_schema, set_cached_schema

_logger = logging.getLogger(__name__)


def _get_dataset_schema(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
) -> dict[str, Any]:
  """Retrieve schema for a single dataset with caching.
  
  Args:
    client: BigQuery client instance
    project_id: GCP project ID
    dataset_id: BigQuery dataset ID
    
  Returns:
    Dictionary with dataset schema information
  """
  # Check cache first
  cache_key = f"{project_id}:{dataset_id}"
  cached = get_cached_schema(cache_key)
  if cached:
    return cached
  
  # Fetch from BigQuery
  _logger.info("Fetching schema for %s (cache miss)", cache_key)
  
  dataset_ref = f"{project_id}.{dataset_id}"
  tables = client.list_tables(dataset_ref)
  
  table_schemas = {}
  for table in tables:
    full_table = client.get_table(table)
    table_schemas[table.table_id] = {
        "fields": [
            {
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,
                "description": field.description,
            }
            for field in full_table.schema
        ],
        "num_rows": full_table.num_rows,
        "description": full_table.description,
    }
  
  schema = {
      "project_id": project_id,
      "dataset_id": dataset_id,
      "tables": table_schemas,
  }
  
  # Cache the result
  set_cached_schema(cache_key, schema)
  _logger.info(
      "Retrieved schema for %s: %d tables", dataset_id, len(table_schemas)
  )
  
  return schema


def get_database_settings(
    dataset_configs: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
  """Get BigQuery database settings and schemas with caching.
  
  Args:
    dataset_configs: List of dataset configurations, each with:
      - project_id: GCP project ID
      - dataset_id: BigQuery dataset ID (or name for multi-dataset configs)
      - name: Display name for the dataset (optional)
      - description: Dataset description (optional)
    
    If not provided, uses BQ_DATASET_ID and GCP_PROJECT_ID from env.
    
  Returns:
    Dictionary containing database configuration and schemas
  """
  # Get dataset configurations
  if not dataset_configs:
    # Fallback to environment variables
    dataset_id = os.getenv("BQ_DATASET_ID")
    project_id = (
        os.getenv("BQ_DATA_PROJECT_ID")
        or os.getenv("BQ_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    
    if not dataset_id or not project_id:
      _logger.warning(
          "No datasets configured. Provide dataset_configs or set "
          "BQ_DATASET_ID and BQ_DATA_PROJECT_ID (or BQ_PROJECT_ID/GOOGLE_CLOUD_PROJECT)."
      )
      return {"datasets": []}
    
    dataset_configs = [{
        "project_id": project_id,
        "dataset_id": dataset_id,
    }]
  
  _logger.info(
      "Retrieving BigQuery schemas for %d dataset(s): %s",
      len(dataset_configs),
      # Fixed: Handle both 'dataset_id' and 'name' keys
      ", ".join(cfg.get("dataset_id", cfg.get("name", "unknown")) for cfg in dataset_configs),
  )
  
  datasets = []
  for config in dataset_configs:
    try:
      # Support both legacy (dataset_id) and new (name) schema
      dataset_name = config.get("name", config.get("dataset_id"))
      dataset_id = config.get("dataset_id", dataset_name)
      
      # Get project_id from config or fall back to environment variable
      project_id = config.get("project_id")
      if not project_id:
        project_id = (
            os.getenv("BQ_DATA_PROJECT_ID") 
            or os.getenv("BQ_PROJECT_ID") 
            or os.getenv("GOOGLE_CLOUD_PROJECT")
        )
      
      if not project_id:
        raise ValueError(
            f"No project_id found for dataset '{dataset_name}'. "
            "Set BQ_DATA_PROJECT_ID, BQ_PROJECT_ID, or GOOGLE_CLOUD_PROJECT "
            "in your .env file."
        )
      
      # Get or create schema for this dataset
      schema_key = f"{project_id}.{dataset_id}"
      if schema_key not in _schema_cache:
        _logger.info(
            "Fetching schema for %s.%s", project_id, dataset_id
        )
        _schema_cache[schema_key] = _get_bigquery_schema(
            project_id=project_id,
            dataset_id=dataset_id,
        )
      
      datasets.append({
          "name": dataset_name,
          "description": config.get("description", ""),
          "schema": _schema_cache[schema_key],
      })
      
    except Exception as e:
      _logger.error(
          "Failed to retrieve schema for %s.%s: %s",
          config.get("project_id", "unknown"),
          config.get("dataset_id", config.get("name", "unknown")),
          e,
      )
  
  return {"datasets": datasets}


def get_dataset_definitions() -> str:
  """Get formatted dataset definitions for agent instructions.
  
  Returns:
    Formatted string listing available datasets
  """
  settings = get_database_settings()
  datasets = settings.get("datasets", [])
  
  if not datasets:
    return "No datasets configured."
  
  definitions = []
  for dataset in datasets:
    name = dataset["name"]
    desc = dataset.get("description", "No description")
    table_count = len(dataset.get("schema", {}).get("tables", {}))
    
    definitions.append(f"- {name}: {desc} ({table_count} tables)")
  
  return "\n".join(definitions)

# Module-level schema cache to avoid NameError and enable reuse across calls.
_schema_cache: dict[str, dict] = {}

def _get_from_schema_cache(key: str):
  # Simple helper; avoids KeyError patterns scattered across code.
  return _schema_cache.get(key)

def _set_in_schema_cache(key: str, value: dict) -> None:
  _schema_cache[key] = value

# Example usage inside your existing schema retrieval function:
def get_dataset_schema(project_id: str, dataset_id: str) -> dict:
  # ...existing code...
  cache_key = f"{project_id}.{dataset_id}"
  cached = _get_from_schema_cache(cache_key)
  if cached is not None:
    return cached

  # ...existing code to fetch schema from BigQuery...
  schema = fetched_schema_dict  # replace with your existing variable

  _set_in_schema_cache(cache_key, schema)
  return schema
