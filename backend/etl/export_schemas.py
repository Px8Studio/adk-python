"""
BigQuery Schema Export Utility

Export BigQuery table schemas to JSON for documentation, versioning, and offline development.

Use Cases:
----------
1. **Documentation**: Generate schema docs for team members
2. **Version Control**: Track schema changes over time in git
3. **Offline Development**: Work without BigQuery access
4. **CI/CD**: Validate schemas in deployment pipelines
5. **Schema Comparison**: Detect drift between environments

Usage:
------
    # Export single dataset
    python -m backend.etl.export_schemas --dataset dnb_statistics --output schemas/dnb_statistics.json

    # Export all configured datasets
    python -m backend.etl.export_schemas --all --output-dir schemas/

    # Compare two schemas
    python -m backend.etl.export_schemas --compare schemas/dev.json schemas/prod.json

Environment Variables:
---------------------
    GOOGLE_CLOUD_PROJECT: GCP project ID
    BQ_DATASET_ID: Default dataset to export (optional)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from google.cloud import bigquery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def export_bq_schemas(
    project_id: str,
    dataset_id: str,
    output_path: str | Path,
) -> dict[str, Any]:
  """
  Export BigQuery dataset schemas to JSON.
  
  Args:
    project_id: GCP project ID
    dataset_id: BigQuery dataset ID
    output_path: Output JSON file path
  
  Returns:
    Dictionary with export statistics
  """
  logger.info(f"Exporting schemas for {project_id}.{dataset_id}")
  
  try:
    client = bigquery.Client(project=project_id)
    dataset = client.get_dataset(f"{project_id}.{dataset_id}")
    
    schema_data = {
      "project_id": project_id,
      "dataset_id": dataset_id,
      "exported_at": datetime.utcnow().isoformat(),
      "dataset_location": dataset.location,
      "tables": {}
    }
    
    table_count = 0
    for table_ref in client.list_tables(dataset):
      table = client.get_table(table_ref)
      
      schema_data["tables"][table.table_id] = {
        "columns": [
          {
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode,
            "description": field.description,
          }
          for field in table.schema
        ],
        "description": table.description or "",
        "num_rows": table.num_rows or 0,
        "size_bytes": table.num_bytes or 0,
        "created": table.created.isoformat() if table.created else None,
        "modified": table.modified.isoformat() if table.modified else None,
      }
      table_count += 1
      logger.debug(f"  Exported: {table.table_id} ({table.num_rows:,} rows)")
    
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
      json.dump(schema_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Exported {table_count} tables to {output_path}")
    
    return {
      "project_id": project_id,
      "dataset_id": dataset_id,
      "tables_exported": table_count,
      "output_path": str(output_path),
    }
  
  except Exception as exc:
    logger.error(f"❌ Failed to export schemas: {exc}")
    raise


def compare_schemas(schema1_path: Path, schema2_path: Path) -> None:
  """
  Compare two schema JSON files and report differences.
  
  Args:
    schema1_path: First schema file (e.g., dev)
    schema2_path: Second schema file (e.g., prod)
  """
  logger.info(f"Comparing schemas:")
  logger.info(f"  File 1: {schema1_path}")
  logger.info(f"  File 2: {schema2_path}")
  
  try:
    with open(schema1_path) as f1, open(schema2_path) as f2:
      schema1 = json.load(f1)
      schema2 = json.load(f2)
    
    tables1 = set(schema1.get("tables", {}).keys())
    tables2 = set(schema2.get("tables", {}).keys())
    
    # Tables only in schema1
    only_in_1 = tables1 - tables2
    if only_in_1:
      logger.warning(f"Tables only in {schema1_path.name}:")
      for table in sorted(only_in_1):
        logger.warning(f"  - {table}")
    
    # Tables only in schema2
    only_in_2 = tables2 - tables1
    if only_in_2:
      logger.warning(f"Tables only in {schema2_path.name}:")
      for table in sorted(only_in_2):
        logger.warning(f"  + {table}")
    
    # Tables in both - check for column differences
    common_tables = tables1 & tables2
    differences = []
    
    for table in sorted(common_tables):
      cols1 = {c["name"] for c in schema1["tables"][table]["columns"]}
      cols2 = {c["name"] for c in schema2["tables"][table]["columns"]}
      
      if cols1 != cols2:
        differences.append(table)
        only_in_cols1 = cols1 - cols2
        only_in_cols2 = cols2 - cols1
        
        if only_in_cols1 or only_in_cols2:
          logger.warning(f"Column differences in {table}:")
          if only_in_cols1:
            for col in sorted(only_in_cols1):
              logger.warning(f"  - {col}")
          if only_in_cols2:
            for col in sorted(only_in_cols2):
              logger.warning(f"  + {col}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COMPARISON SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Tables only in {schema1_path.name}: {len(only_in_1)}")
    logger.info(f"Tables only in {schema2_path.name}: {len(only_in_2)}")
    logger.info(f"Tables with column differences: {len(differences)}")
    logger.info(f"Total tables compared: {len(common_tables)}")
    logger.info("=" * 70)
    
    if not only_in_1 and not only_in_2 and not differences:
      logger.info("✅ Schemas are identical!")
    else:
      logger.warning("⚠️  Schemas have differences (see above)")
  
  except Exception as exc:
    logger.error(f"❌ Failed to compare schemas: {exc}")
    raise


def main():
  """Main CLI entry point."""
  parser = argparse.ArgumentParser(
    description="Export BigQuery schemas to JSON",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=__doc__,
  )
  
  # Export options
  export_group = parser.add_argument_group("Export options")
  export_group.add_argument(
    "--dataset",
    type=str,
    help="Dataset ID to export",
  )
  export_group.add_argument(
    "--project-id",
    type=str,
    default=os.getenv("GOOGLE_CLOUD_PROJECT"),
    help="GCP project ID (default: from GOOGLE_CLOUD_PROJECT env var)",
  )
  export_group.add_argument(
    "--output",
    type=Path,
    help="Output JSON file path",
  )
  export_group.add_argument(
    "--all",
    action="store_true",
    help="Export all configured datasets (dnb_statistics, dnb_public_register)",
  )
  export_group.add_argument(
    "--output-dir",
    type=Path,
    default=Path("schemas"),
    help="Output directory for --all (default: schemas/)",
  )
  
  # Compare options
  compare_group = parser.add_argument_group("Compare options")
  compare_group.add_argument(
    "--compare",
    nargs=2,
    type=Path,
    metavar=("SCHEMA1", "SCHEMA2"),
    help="Compare two schema JSON files",
  )
  
  args = parser.parse_args()
  
  # Validate project ID
  if not args.compare and not args.project_id:
    logger.error("ERROR: GOOGLE_CLOUD_PROJECT not set")
    logger.error("Set via: $env:GOOGLE_CLOUD_PROJECT='your-project-id'")
    sys.exit(1)
  
  # Compare mode
  if args.compare:
    compare_schemas(args.compare[0], args.compare[1])
    return
  
  # Export mode
  if args.all:
    datasets = ["dnb_statistics", "dnb_public_register"]
    logger.info(f"Exporting {len(datasets)} datasets to {args.output_dir}")
    
    results = []
    for dataset_id in datasets:
      output_path = args.output_dir / f"{dataset_id}.json"
      try:
        result = export_bq_schemas(args.project_id, dataset_id, output_path)
        results.append(result)
      except Exception:
        logger.error(f"Failed to export {dataset_id}")
    
    logger.info(f"\n✅ Exported {len(results)}/{len(datasets)} datasets")
    return
  
  # Single dataset export
  if not args.dataset or not args.output:
    parser.error("--dataset and --output required (or use --all)")
  
  export_bq_schemas(args.project_id, args.dataset, args.output)


if __name__ == "__main__":
  main()