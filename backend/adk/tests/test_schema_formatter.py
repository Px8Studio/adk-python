"""
Unit tests for schema_formatter.py

Tests CREATE TABLE statement generation following ADK best practices.
"""

from __future__ import annotations

import pytest

from backend.adk.utils.schema_formatter import (
  format_schema_as_create_table_statements,
  format_single_table_schema,
  format_schema_summary,
  get_related_tables,
)


@pytest.fixture
def sample_tables():
  """Sample table schema data for testing."""
  return {
    "exchange_rates_day": {
      "fields": [
        {
          "name": "currency",
          "type": "STRING",
          "mode": "NULLABLE",
          "description": "ISO 4217 currency code (3 characters)",
        },
        {
          "name": "date",
          "type": "DATE",
          "mode": "NULLABLE",
          "description": "Observation date for time-series data",
        },
        {
          "name": "rate",
          "type": "FLOAT",
          "mode": "NULLABLE",
          "description": None,  # No description
        },
        {
          "name": "_etl_timestamp",
          "type": "STRING",
          "mode": "NULLABLE",
          "description": "ETL extraction timestamp in ISO 8601 format (UTC)",
        },
      ],
      "num_rows": 10509,
      "description": "Daily foreign exchange rates from DNB",
    },
    "insurance_balance_sheet": {
      "fields": [
        {
          "name": "sector",
          "type": "STRING",
          "mode": "REQUIRED",
          "description": "Economic sector classification",
        },
        {
          "name": "value",
          "type": "FLOAT",
          "mode": "NULLABLE",
          "description": None,
        },
      ],
      "num_rows": 560,
      "description": None,
    },
  }


def test_format_schema_as_create_table_statements_basic(sample_tables):
  """Test basic CREATE TABLE generation."""
  result = format_schema_as_create_table_statements(
    project_id="test-project",
    dataset_id="test_dataset",
    tables=sample_tables,
  )
  
  # Check basic structure
  assert "CREATE TABLE `test-project`.test_dataset.exchange_rates_day" in result
  assert "CREATE TABLE `test-project`.test_dataset.insurance_balance_sheet" in result
  
  # Check column definitions
  assert 'currency STRING OPTIONS(description="ISO 4217 currency code (3 characters)")' in result
  assert 'date DATE OPTIONS(description="Observation date for time-series data")' in result
  
  # Check column without description (no OPTIONS clause)
  assert "rate FLOAT" in result
  assert 'rate FLOAT OPTIONS' not in result
  
  # Check ETL metadata
  assert '_etl_timestamp STRING OPTIONS(description="ETL extraction timestamp' in result


def test_format_schema_with_table_descriptions(sample_tables):
  """Test table-level descriptions are included as comments."""
  result = format_schema_as_create_table_statements(
    project_id="test-project",
    dataset_id="test_dataset",
    tables=sample_tables,
    include_table_description=True,
  )
  
  # Check table description appears as comment
  assert "-- Daily foreign exchange rates from DNB" in result
  
  # Table without description shouldn't have comment
  assert result.count("-- ") == 1  # Only one table has description


def test_format_schema_max_tables_limit(sample_tables):
  """Test max_tables parameter limits output."""
  result = format_schema_as_create_table_statements(
    project_id="test-project",
    dataset_id="test_dataset",
    tables=sample_tables,
    max_tables=1,
  )
  
  # Should only include 1 table
  assert result.count("CREATE TABLE") == 1
  
  # Should include "more tables" message
  assert "and 1 more tables" in result or "more tables" in result


def test_format_single_table_schema(sample_tables):
  """Test single table formatting."""
  result = format_single_table_schema(
    project_id="test-project",
    dataset_id="test_dataset",
    table_name="exchange_rates_day",
    table_info=sample_tables["exchange_rates_day"],
  )
  
  # Should only have one CREATE TABLE
  assert result.count("CREATE TABLE") == 1
  assert "exchange_rates_day" in result
  assert "insurance_balance_sheet" not in result
  
  # Should have all columns
  assert "currency" in result
  assert "date" in result
  assert "rate" in result


def test_format_schema_summary(sample_tables):
  """Test compact table summary generation."""
  result = format_schema_summary(
    tables=sample_tables,
    show_column_count=True,
    show_row_count=True,
  )
  
  # Check header
  assert "Available Tables (2):" in result
  
  # Check table listings
  assert "exchange_rates_day" in result
  assert "(4 columns)" in result
  assert "10,509 rows" in result
  
  # Check descriptions
  assert "Daily foreign exchange rates from DNB" in result


def test_format_schema_summary_no_counts(sample_tables):
  """Test summary without counts."""
  result = format_schema_summary(
    tables=sample_tables,
    show_column_count=False,
    show_row_count=False,
  )
  
  # Should still have table names
  assert "exchange_rates_day" in result
  assert "insurance_balance_sheet" in result
  
  # Should NOT have counts
  assert "columns" not in result
  assert "rows" not in result


def test_get_related_tables_by_name(sample_tables):
  """Test filtering tables by name."""
  result = get_related_tables(
    tables=sample_tables,
    search_terms=["exchange"],
    match_table_name=True,
  )
  
  assert "exchange_rates_day" in result
  assert "insurance_balance_sheet" not in result
  assert len(result) == 1


def test_get_related_tables_by_column(sample_tables):
  """Test filtering tables by column name."""
  result = get_related_tables(
    tables=sample_tables,
    search_terms=["currency"],
    match_column_name=True,
  )
  
  assert "exchange_rates_day" in result
  assert "insurance_balance_sheet" not in result


def test_get_related_tables_by_description(sample_tables):
  """Test filtering tables by description."""
  result = get_related_tables(
    tables=sample_tables,
    search_terms=["sector"],
    match_description=True,
  )
  
  # Should find "insurance_balance_sheet" which has "sector" column with description
  assert "insurance_balance_sheet" in result


def test_get_related_tables_multiple_terms(sample_tables):
  """Test filtering with multiple search terms."""
  result = get_related_tables(
    tables=sample_tables,
    search_terms=["exchange", "insurance"],
    match_table_name=True,
  )
  
  # Should match both tables
  assert len(result) == 2


def test_empty_tables_input():
  """Test behavior with empty tables dict."""
  result = format_schema_as_create_table_statements(
    project_id="test-project",
    dataset_id="test_dataset",
    tables={},
  )
  
  assert "No tables found" in result


def test_description_with_quotes():
  """Test handling of quotes in descriptions."""
  tables = {
    "test_table": {
      "fields": [
        {
          "name": "col1",
          "type": "STRING",
          "mode": "NULLABLE",
          "description": 'Contains "quoted" text',
        }
      ],
      "description": None,
    }
  }
  
  result = format_schema_as_create_table_statements(
    project_id="test-project",
    dataset_id="test_dataset",
    tables=tables,
  )
  
  # Quotes should be escaped
  assert 'Contains \\"quoted\\" text' in result


def test_required_mode_annotation():
  """Test REQUIRED mode is annotated."""
  tables = {
    "test_table": {
      "fields": [
        {
          "name": "id",
          "type": "INTEGER",
          "mode": "REQUIRED",
          "description": "Primary key",
        }
      ],
      "description": None,
    }
  }
  
  result = format_schema_as_create_table_statements(
    project_id="test-project",
    dataset_id="test_dataset",
    tables=tables,
  )
  
  # REQUIRED mode should be indicated
  assert "REQUIRED" in result
