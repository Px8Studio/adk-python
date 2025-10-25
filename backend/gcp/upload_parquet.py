"""
Generic Parquet Upload Orchestrator

Upload parquet files to BigQuery for any configured datasource.
Works with datasource profiles for multi-tenant GCP infrastructure.

Usage:
    # List available datasources
    python -m backend.gcp.upload_parquet --list-datasources

    # Upload all files for a datasource
    python -m backend.gcp.upload_parquet --datasource dnb_statistics --all

    # Upload specific category
    python -m backend.gcp.upload_parquet --datasource dnb_statistics --category insurance_pensions

    # Upload specific tables
    python -m backend.gcp.upload_parquet --datasource dnb_statistics --tables table1 table2

    # Dry run (preview without uploading)
    python -m backend.gcp.upload_parquet --datasource dnb_statistics --all --dry-run

    # Create new datasource profile
    python -m backend.gcp.upload_parquet --create-profile eiopa_data
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from backend.gcp.auth import GCPAuth
from backend.gcp.bigquery_manager import BigQueryManager
from backend.gcp.datasource_config import (
    load_datasource_config,
    list_datasources,
    create_datasource_profile_template,
    save_datasource_profile,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ==========================================
# Discovery
# ==========================================

def get_bronze_dir() -> Path:
    """Get Bronze layer directory path."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    bronze_dir = project_root / "backend" / "data" / "1-bronze"
    
    if not bronze_dir.exists():
        raise FileNotFoundError(
            f"Bronze directory not found: {bronze_dir}\n"
            "Please ensure data has been extracted first."
        )
    
    return bronze_dir


def discover_parquet_files(
    datasource_id: str,
    category: str | None = None,
) -> list[Path]:
    """
    Discover all parquet files for a datasource.
    
    Args:
        datasource_id: Datasource identifier
        category: Optional category filter
    
    Returns:
        List of parquet file paths
    """
    # Load config to get bronze_path
    config = load_datasource_config(datasource_id)
    bronze_dir = get_bronze_dir()
    search_path = bronze_dir / config.pipeline_config.bronze_path
    
    if not search_path.exists():
        raise FileNotFoundError(
            f"Datasource directory not found: {search_path}\n"
            f"Please run ETL extraction for {config.datasource.name} first."
        )
    
    if category:
        search_path = search_path / category
        if not search_path.exists():
            available = [d.name for d in (bronze_dir / config.pipeline_config.bronze_path).iterdir() if d.is_dir()]
            raise ValueError(
                f"Category directory not found: {category}\n"
                f"Available categories: {', '.join(available)}"
            )
    
    # Find all parquet files (excluding metadata files starting with _)
    parquet_files = [
        p for p in search_path.rglob("*.parquet")
        if not p.name.startswith("_")
    ]
    
    return sorted(parquet_files)


def discover_by_table_names(
    datasource_id: str,
    table_names: list[str],
) -> list[Path]:
    """
    Find parquet files by table names (endpoint names).
    
    Args:
        datasource_id: Datasource identifier
        table_names: List of endpoint/table names
    
    Returns:
        List of parquet file paths
    """
    config = load_datasource_config(datasource_id)
    bronze_dir = get_bronze_dir()
    search_path = bronze_dir / config.pipeline_config.bronze_path
    found_files = []
    
    for table_name in table_names:
        # Search for matching files
        matches = list(search_path.rglob(f"{table_name}.parquet"))
        
        if not matches:
            logger.warning(f"No parquet file found for: {table_name}")
            continue
        
        if len(matches) > 1:
            logger.warning(f"Multiple files found for {table_name}, using first: {matches[0]}")
        
        found_files.append(matches[0])
    
    return found_files


# ==========================================
# Upload Workflows
# ==========================================

def upload_files(
    datasource_id: str,
    parquet_files: list[Path],
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Upload multiple parquet files to BigQuery.
    
    Args:
        datasource_id: Datasource identifier
        parquet_files: List of parquet file paths
        dry_run: If True, only show what would be uploaded
    
    Returns:
        Upload statistics
    """
    # Load datasource configuration
    config = load_datasource_config(datasource_id)
    
    logger.info("\n" + "=" * 70)
    logger.info(f"UPLOADING: {config.datasource.name}")
    logger.info("=" * 70)
    logger.info(f"Datasource: {datasource_id}")
    
    if dry_run:
        logger.info(f"Location: {config.bigquery.location}")
        logger.info(f"GCS Bucket: {config.storage.bucket_name}")
        logger.info(f"BQ Dataset: {config.bigquery.dataset_id}")
        logger.info(f"Files to upload: {len(parquet_files)}")
        logger.info("=" * 70 + "\n")
        logger.info("🔍 DRY RUN MODE - No actual uploads will occur\n")
        bronze_dir = get_bronze_dir()
        for i, pf in enumerate(parquet_files, 1):
            try:
                rel_path = pf.relative_to(bronze_dir)
            except ValueError:
                rel_path = pf
            logger.info(f"[{i}/{len(parquet_files)}] Would upload: {rel_path}")
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ DRY RUN COMPLETE")
        logger.info(f"  Would upload: {len(parquet_files)} file(s)")
        logger.info("=" * 70 + "\n")
        return {"dry_run": True, "files": len(parquet_files)}
    
    # Get GCP project from env (required for actual uploads)
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT not set. "
            "Set it in your .env file or environment."
        )
    
    logger.info(f"Project: {project_id}")
    logger.info(f"Location: {config.bigquery.location}")
    logger.info(f"BQ Dataset: {config.bigquery.dataset_id}")
    logger.info(f"Files to upload: {len(parquet_files)}")
    logger.info("=" * 70 + "\n")
    
    # Initialize GCP managers
    logger.info("Initializing GCP connection...")
    auth = GCPAuth(project_id=project_id)
    bq_mgr = BigQueryManager(auth, location=config.bigquery.location)
    logger.info(f"✓ Connected to project: {project_id}\n")
    
    overall_start = datetime.now()
    results = []
    errors = []
    
    for i, parquet_file in enumerate(parquet_files, 1):
        logger.info(f"\n[{i}/{len(parquet_files)}] Processing: {parquet_file.name}")
        
        try:
            stats = bq_mgr.load_parquet_from_local(
                parquet_path=str(parquet_file),
                dataset_id=config.bigquery.dataset_id,
                partition_field=config.bigquery.table_defaults.partition_field,
                clustering_fields=config.bigquery.table_defaults.clustering_fields,
                write_disposition=config.bigquery.table_defaults.write_disposition,
                auto_detect_table_name=True,
            )
            results.append(stats)
        
        except Exception as exc:
            logger.error(f"✗ Failed to upload {parquet_file.name}: {exc}", exc_info=True)
            errors.append({
                "file": parquet_file.name,
                "error": str(exc),
            })
            continue
    
    # Summary
    overall_elapsed = (datetime.now() - overall_start).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ UPLOAD COMPLETE")
    logger.info(f"  Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.1f}m)")
    logger.info(f"  Successful: {len(results)}/{len(parquet_files)}")
    
    if errors:
        logger.warning(f"  Failed: {len(errors)}/{len(parquet_files)}")
        logger.warning("\n  Failed files:")
        for err in errors:
            logger.warning(f"    • {err['file']}: {err['error']}")
    
    # Table summary
    if results:
        total_rows = sum(r["num_rows"] for r in results)
        total_size = sum(r["size_bytes"] for r in results)
        
        logger.info(f"\n  Total rows loaded: {total_rows:,}")
        logger.info(f"  Total size: {total_size / (1024**3):.2f} GB")
        logger.info(f"\n  Tables created:")
        for r in results:
            logger.info(f"    • {r['table_name']}: {r['num_rows']:,} rows")
    
    logger.info("=" * 70 + "\n")
    
    # BigQuery UI link
    logger.info(f"View in BigQuery UI:")
    logger.info(f"https://console.cloud.google.com/bigquery?project={project_id}&d={config.bigquery.dataset_id}&p={project_id}&page=dataset")
    logger.info("")
    
    return {
        "datasource": datasource_id,
        "successes": len(results),
        "failures": len(errors),
        "total_rows": sum(r["num_rows"] for r in results) if results else 0,
        "total_size_gb": sum(r["size_bytes"] for r in results) / (1024**3) if results else 0,
        "elapsed_seconds": overall_elapsed,
        "results": results,
        "errors": errors,
    }


# ==========================================
# CLI
# ==========================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Upload parquet files to BigQuery for any configured datasource",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available datasources
  python -m backend.gcp.upload_parquet --list-datasources

  # Upload all tables for a datasource
  python -m backend.gcp.upload_parquet --datasource dnb_statistics --all

  # Upload specific category
  python -m backend.gcp.upload_parquet --datasource dnb_statistics --category insurance_pensions

  # Upload specific tables
  python -m backend.gcp.upload_parquet --datasource dnb_statistics --tables table1 table2

  # Dry run
  python -m backend.gcp.upload_parquet --datasource dnb_statistics --all --dry-run

  # Create new datasource profile
  python -m backend.gcp.upload_parquet --create-profile eiopa_data
        """,
    )
    
    # Datasource management
    parser.add_argument(
        "--list-datasources",
        action="store_true",
        help="List all available datasource profiles",
    )
    
    parser.add_argument(
        "--create-profile",
        type=str,
        metavar="DATASOURCE_ID",
        help="Create a new datasource profile template",
    )
    
    parser.add_argument(
        "--datasource",
        type=str,
        metavar="DATASOURCE_ID",
        help="Datasource to upload (e.g., dnb_statistics)",
    )
    
    # Upload scope
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all",
        action="store_true",
        help="Upload all parquet files for the datasource",
    )
    group.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Upload all files in a category",
    )
    group.add_argument(
        "--tables",
        nargs="+",
        metavar="TABLE",
        help="Upload specific tables by endpoint name (space-separated)",
    )
    
    # Options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually doing it",
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available parquet files for the datasource and exit",
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # List datasources
    if args.list_datasources:
        datasources = list_datasources()
        if not datasources:
            logger.info("\nNo datasource profiles found.")
            logger.info("Create one with: python -m backend.gcp.upload_parquet --create-profile <datasource_id>")
        else:
            logger.info(f"\nAvailable datasources ({len(datasources)}):")
            for ds in datasources:
                try:
                    config = load_datasource_config(ds)
                    logger.info(f"  • {ds:30s} - {config.datasource.name}")
                except Exception as exc:
                    logger.info(f"  • {ds:30s} - (invalid profile: {exc})")
        sys.exit(0)
    
    # Create profile
    if args.create_profile:
        datasource_id = args.create_profile
        logger.info(f"Creating profile for: {datasource_id}")
        
        try:
            template = create_datasource_profile_template(datasource_id)
            profile_path = save_datasource_profile(datasource_id, template)
            
            logger.info(f"\n✓ Created profile: {profile_path}")
            logger.info("\nNext steps:")
            logger.info(f"  1. Edit {profile_path}")
            logger.info("  2. Customize configuration (name, description, labels, etc.)")
            logger.info(f"  3. Setup infrastructure: python -m backend.gcp.setup --datasource {datasource_id} --all")
            logger.info(f"  4. Upload data: python -m backend.gcp.upload_parquet --datasource {datasource_id} --all")
            
        except FileExistsError as exc:
            logger.error(f"✗ {exc}")
            sys.exit(1)
        except Exception as exc:
            logger.error(f"✗ Failed to create profile: {exc}", exc_info=True)
            sys.exit(1)
        
        sys.exit(0)
    
    # Require datasource for upload operations
    if not args.datasource:
        logger.error("Error: --datasource required for upload operations")
        logger.error("\nRun with --list-datasources to see available datasources")
        logger.error("Or run with --create-profile <datasource_id> to create a new one")
        sys.exit(1)
    
    datasource_id = args.datasource
    
    # Discover files
    try:
        if args.all:
            parquet_files = discover_parquet_files(datasource_id)
        elif args.category:
            parquet_files = discover_parquet_files(datasource_id, category=args.category)
        elif args.tables:
            parquet_files = discover_by_table_names(datasource_id, args.tables)
        else:
            logger.error("Error: Must specify --all, --category, or --tables")
            sys.exit(1)
    
    except Exception as exc:
        logger.error(f"Failed to discover files: {exc}")
        sys.exit(1)
    
    if not parquet_files:
        logger.warning("No parquet files found to upload")
        sys.exit(0)
    
    # List mode
    if args.list:
        bronze_dir = get_bronze_dir()
        logger.info(f"\nFound {len(parquet_files)} parquet file(s) for {datasource_id}:")
        for pf in parquet_files:
            try:
                rel_path = pf.relative_to(bronze_dir)
            except ValueError:
                rel_path = pf
            logger.info(f"  • {rel_path}")
        sys.exit(0)
    
    # Upload
    try:
        upload_files(
            datasource_id=datasource_id,
            parquet_files=parquet_files,
            dry_run=args.dry_run,
        )
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Upload interrupted by user")
        sys.exit(130)
    
    except Exception as exc:
        logger.error(f"\n✗ Upload failed: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
