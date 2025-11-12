"""
Schema Formatter for ADK Agent Instructions

Converts BigQuery schema cache to CREATE TABLE statements with OPTIONS(description).
This format is optimized for LLM understanding and follows the official ADK pattern.

Usage:
    from backend.adk.utils.schema_formatter import format_schema_as_create_table_statements
    
    # Load cached schema
    with open(".cache/bigquery_schemas/project_dataset.json") as f:
        schema_cache = json.load(f)
    
    # Generate CREATE TABLE statements
    sql_statements = format_schema_as_create_table_statements(
        project_id="woven-art-475517-n4",
        dataset_id="dnb_statistics",
        tables=schema_cache["datasets"][0]["schema"]["tables"]
    )
    
    # Use in agent instructions
    instruction = f\"""
    【Database Schema】
    {sql_statements}
    \"""
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_schema_as_create_table_statements(
  project_id: str,
  dataset_id: str,
  tables: dict[str, Any],
  *,
  include_table_description: bool = True,
  max_tables: int | None = None,
) -> str:
  """
  Convert BigQuery schema to CREATE TABLE statements for LLM instructions.
  
  Follows the official ADK pattern from data-science sample agent:
  - Full table names with project prefix
  - OPTIONS(description="...") for columns with descriptions
  - Compact, readable format
  
  Args:
      project_id: GCP project ID
      dataset_id: BigQuery dataset ID
      tables: Dict of table_name -> table_info from schema cache
      include_table_description: Include table-level descriptions if available
      max_tables: Limit number of tables (for token management)
      
  Returns:
      CREATE TABLE statements as formatted SQL string
  """
  if not tables:
    logger.warning(f"No tables found for {dataset_id}")
    return f"-- No tables found in dataset {dataset_id}"
  
  statements = []
  processed = 0
  
  for table_name, table_info in sorted(tables.items()):
    if max_tables and processed >= max_tables:
      statements.append(
        f"\n-- ... and {len(tables) - processed} more tables\n"
      )
      break
    
    # Generate field definitions with descriptions
    field_lines = []
    fields = table_info.get("fields", [])
    
    if not fields:
      logger.warning(f"No fields found for table {table_name}")
      continue
    
    for field in fields:
      field_name = field.get("name", "unknown")
      field_type = field.get("type", "STRING")
      field_desc = field.get("description")
      field_mode = field.get("mode", "NULLABLE")
      
      # Build field definition
      if field_desc:
        # Escape quotes in descriptions
        escaped_desc = field_desc.replace('"', '\\"')
        field_line = (
          f"  {field_name} {field_type} "
          f'OPTIONS(description="{escaped_desc}")'
        )
      else:
        field_line = f"  {field_name} {field_type}"
      
      # Add mode if REQUIRED or REPEATED
      if field_mode != "NULLABLE":
        field_line = f"{field_line}  -- {field_mode}"
      
      field_lines.append(field_line)
    
    # Join fields with commas
    fields_sql = ",\n".join(field_lines)
    
    # Build CREATE TABLE statement
    create_table_sql = (
      f"CREATE TABLE `{project_id}`.{dataset_id}.{table_name}\n"
      f"(\n{fields_sql}\n);"
    )
    
    # Optionally add table-level description as comment
    if include_table_description:
      table_desc = table_info.get("description")
      if table_desc:
        create_table_sql = (
          f"-- {table_desc}\n{create_table_sql}"
        )
    
    statements.append(create_table_sql)
    processed += 1
  
  return "\n\n".join(statements)


def format_single_table_schema(
  project_id: str,
  dataset_id: str,
  table_name: str,
  table_info: dict[str, Any],
) -> str:
  """
  Format a single table's schema as CREATE TABLE statement.
  
  Useful for focused queries or agent tools that operate on specific tables.
  
  Args:
      project_id: GCP project ID
      dataset_id: BigQuery dataset ID
      table_name: Table name
      table_info: Table schema info from cache
      
  Returns:
      CREATE TABLE statement for this table
  """
  return format_schema_as_create_table_statements(
    project_id=project_id,
    dataset_id=dataset_id,
    tables={table_name: table_info},
    include_table_description=True,
  )


def format_schema_summary(
  tables: dict[str, Any],
  *,
  show_column_count: bool = True,
  show_row_count: bool = True,
) -> str:
  """
  Generate a compact table listing summary.
  
  Useful for high-level dataset overview without full CREATE TABLE detail.
  
  Args:
      tables: Dict of table_name -> table_info from schema cache
      show_column_count: Include column counts
      show_row_count: Include row counts
      
  Returns:
      Formatted summary string
  """
  if not tables:
    return "No tables available."
  
  lines = [f"Available Tables ({len(tables)}):"]
  
  for table_name, table_info in sorted(tables.items()):
    parts = [f"- {table_name}"]
    
    if show_column_count:
      num_cols = len(table_info.get("fields", []))
      parts.append(f"({num_cols} columns)")
    
    if show_row_count:
      num_rows = table_info.get("num_rows")
      if num_rows is not None:
        parts.append(f"{num_rows:,} rows")
    
    table_desc = table_info.get("description")
    if table_desc:
      parts.append(f"- {table_desc}")
    
    lines.append(" ".join(parts))
  
  return "\n".join(lines)


def get_related_tables(
  tables: dict[str, Any],
  search_terms: list[str],
  *,
  match_table_name: bool = True,
  match_column_name: bool = True,
  match_description: bool = True,
) -> dict[str, Any]:
  """
  Filter tables by search terms for relevant context.
  
  Useful for large datasets where including all tables exceeds token limits.
  
  Args:
      tables: Dict of table_name -> table_info from schema cache
      search_terms: Terms to search for (case-insensitive)
      match_table_name: Search in table names
      match_column_name: Search in column names
      match_description: Search in descriptions
      
  Returns:
      Filtered dict of matching tables
  """
  if not search_terms:
    return tables
  
  search_lower = [term.lower() for term in search_terms]
  matching_tables = {}
  
  for table_name, table_info in tables.items():
    matched = False
    
    # Check table name
    if match_table_name:
      if any(term in table_name.lower() for term in search_lower):
        matched = True
    
    # Check column names
    if match_column_name and not matched:
      for field in table_info.get("fields", []):
        field_name = field.get("name", "").lower()
        if any(term in field_name for term in search_lower):
          matched = True
          break
    
    # Check descriptions
    if match_description and not matched:
      # Table description
      table_desc = table_info.get("description", "").lower()
      if any(term in table_desc for term in search_lower):
        matched = True
      
      # Column descriptions
      if not matched:
        for field in table_info.get("fields", []):
          field_desc = field.get("description", "").lower()
          if any(term in field_desc for term in search_lower):
            matched = True
            break
    
    if matched:
      matching_tables[table_name] = table_info
  
  logger.info(
    f"Filtered to {len(matching_tables)}/{len(tables)} tables "
    f"matching: {', '.join(search_terms)}"
  )
  
  return matching_tables
