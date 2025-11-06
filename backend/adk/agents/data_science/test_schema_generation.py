"""
Test CREATE TABLE Schema Generation

Quick validation script to verify the schema formatter is working correctly
and producing ADK-compliant CREATE TABLE statements.

Usage:
    python backend/adk/agents/data_science/test_schema_generation.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Use relative imports from the utils module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.schema_formatter import (
  format_schema_as_create_table_statements,
  format_schema_summary,
)


def load_cached_schema(project_id: str, dataset_id: str) -> dict:
  """Load schema from cache."""
  # Try multiple possible cache locations
  possible_paths = [
    Path(f".cache/bigquery_schemas/{project_id}_{dataset_id}.json"),
    Path(__file__).parent.parent.parent.parent / f".cache/bigquery_schemas/{project_id}_{dataset_id}.json",
  ]
  
  for cache_file in possible_paths:
    if cache_file.exists():
      print(f"✓ Found cache: {cache_file}")
      with open(cache_file) as f:
        return json.load(f)
  
  print(f"❌ Schema cache not found in any of these locations:")
  for p in possible_paths:
    print(f"   - {p}")
  print("\nRun this first to generate cache:")
  print(f"  python backend/adk/agents/data_science/run_dnb_openapi_agent.py")
  return None


def test_create_table_generation():
  """Test CREATE TABLE statement generation."""
  print("=" * 70)
  print("TESTING CREATE TABLE SCHEMA GENERATION")
  print("=" * 70 + "\n")
  
  # Load DNB Statistics schema
  print("Step 1: Loading cached schema...")
  schema_cache = load_cached_schema(
    "woven-art-475517-n4",
    "dnb_statistics"
  )
  
  if not schema_cache:
    return False
  
  # Extract tables - handle both old and new cache formats
  tables = None
  
  # Try new format (datasets array)
  datasets = schema_cache.get("datasets", [])
  if datasets and len(datasets) > 0:
    tables = datasets[0].get("schema", {}).get("tables", {})
  
  # Try old format (direct schema)
  if not tables:
    tables = schema_cache.get("schema", {}).get("tables", {})
  
  if not tables:
    print("❌ No tables found in schema cache")
    print(f"Cache keys: {list(schema_cache.keys())}")
    return False
  
  print(f"✓ Loaded {len(tables)} tables\n")
  
  # Step 2: Test summary generation
  print("Step 2: Testing schema summary...")
  summary = format_schema_summary(
    tables=tables,
    show_column_count=True,
    show_row_count=True,
  )
  print(summary)
  print()
  
  # Step 3: Test CREATE TABLE generation (limited)
  print("Step 3: Testing CREATE TABLE generation (first 3 tables)...")
  print("-" * 70)
  
  create_statements = format_schema_as_create_table_statements(
    project_id="woven-art-475517-n4",
    dataset_id="dnb_statistics",
    tables=tables,
    include_table_description=True,
    max_tables=3,  # Just show first 3 for testing
  )
  
  print(create_statements)
  print("-" * 70)
  print()
  
  # Step 4: Validate format
  print("Step 4: Validating CREATE TABLE format...")
  
  # Required checks
  required_checks = [
    ("Full table names", "`woven-art-475517-n4`.dnb_statistics." in create_statements),
    ("CREATE TABLE keyword", "CREATE TABLE" in create_statements),
    ("Proper SQL syntax", "(" in create_statements and ");" in create_statements),
    ("Column types present", any(t in create_statements for t in ["STRING", "FLOAT", "INTEGER"])),
  ]
  
  # Optional checks (will be implemented in Phase 2)
  optional_checks = [
    ("Column descriptions", 'OPTIONS(description=' in create_statements),
  ]
  
  all_passed = True
  for check_name, result in required_checks:
    status = "✓" if result else "✗"
    print(f"  {status} {check_name}")
    if not result:
      all_passed = False
  
  for check_name, result in optional_checks:
    status = "✓" if result else "ℹ"
    suffix = "" if result else " (Phase 2 - add via BigQuery table/column descriptions)"
    print(f"  {status} {check_name}{suffix}")
    # Don't fail on optional checks
  
  print()
  
  # Step 5: Token estimation
  print("Step 5: Token estimation...")
  token_estimate = len(create_statements.split()) * 1.3  # Rough estimate
  print(f"  Approximate tokens (3 tables): {token_estimate:.0f}")
  
  full_statements = format_schema_as_create_table_statements(
    project_id="woven-art-475517-n4",
    dataset_id="dnb_statistics",
    tables=tables,
    include_table_description=True,
    max_tables=None,  # All tables
  )
  full_token_estimate = len(full_statements.split()) * 1.3
  print(f"  Approximate tokens (all {len(tables)} tables): {full_token_estimate:.0f}")
  print()
  
  # Summary
  if all_passed:
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Start the agent: adk web backend/adk/agents/data_science")
    print("  2. Ask a query: 'Show me the schema for exchange_rates_day'")
    print("  3. Try a complex query: 'What are the top 3 currency rates in 2024?'")
    print("\nExpected improvement:")
    print("  - 30-50% better SQL accuracy for complex queries")
    print("  - Fewer column name errors")
    print("  - Better JOIN detection")
    return True
  else:
    print("=" * 70)
    print("❌ SOME TESTS FAILED")
    print("=" * 70)
    return False


if __name__ == "__main__":
  success = test_create_table_generation()
  sys.exit(0 if success else 1)
