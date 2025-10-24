"""
DNB Statistics BigQuery Upload Orchestrator

Upload parquet files from Bronze layer to BigQuery via GCS staging.
Uses the professional GCP infrastructure managers.

Usage:
    # Upload everything
    python -m backend.gcp.upload_dnb_statistics --all

    # Upload specific category
    python -m backend.gcp.upload_dnb_statistics --category insurance_pensions

    # Upload specific tables
    python -m backend.gcp.upload_dnb_statistics --tables exchange_rates_day market_interest_rates_day

    # Dry run (no actual upload)
    python -m backend.gcp.upload_dnb_statistics --all --dry-run

Environment Variables:
    GOOGLE_CLOUD_PROJECT: GCP project ID
    GOOGLE_CLOUD_LOCATION: GCP location (default: us-central1)
    GCS_BUCKET: GCS bucket name for staging (default: {dataset}-data)
    BQ_DATASET_ID: BigQuery dataset ID (default: dnb_statistics)
    BQ_PARTITION_FIELD: Field for time partitioning (default: period)
    BQ_CLUSTERING_FIELDS: Comma-separated clustering fields (optional)
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

from backend.gcp import GCPAuth, BigQueryManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ==========================================
# Configuration
# ==========================================

def get_config() -> dict[str, Any]:
    """Load configuration from environment."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT not set. "
            "Set it in your .env file or environment."
        )
    
    dataset_id = os.getenv("BQ_DATASET_ID", "dnb_statistics")
    
    return {
        "project_id": project_id,
        "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        "gcs_bucket": os.getenv("GCS_BUCKET") or f"{dataset_id}-data",
        "bq_dataset": dataset_id,
        "partition_field": os.getenv("BQ_PARTITION_FIELD", "period"),
        "clustering_fields": (
            os.getenv("BQ_CLUSTERING_FIELDS", "").split(",")
            if os.getenv("BQ_CLUSTERING_FIELDS")
            else None
        ),
    }


# ==========================================
# Discovery
# ==========================================

def get_bronze_dir() -> Path:
    """Get Bronze layer directory path."""
    # Try to find bronze dir relative to this script
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
    category: str | None = None,
) -> list[Path]:
    """
    Discover all parquet files in Bronze layer.
    
    Args:
        category: Optional category filter
    
    Returns:
        List of parquet file paths
    """
    bronze_dir = get_bronze_dir()
    search_path = bronze_dir / "dnb_statistics"
    
    if not search_path.exists():
        raise FileNotFoundError(
            f"DNB Statistics directory not found: {search_path}\n"
            "Please run ETL extraction first."
        )
    
    if category:
        search_path = search_path / category
        if not search_path.exists():
            raise ValueError(f"Category directory not found: {category}")
    
    # Find all parquet files (excluding metadata)
    parquet_files = [
        p for p in search_path.rglob("*.parquet")
        if not p.name.startswith("_")
    ]
    
    return sorted(parquet_files)


def discover_by_table_names(
    table_names: list[str],
) -> list[Path]:
    """
    Find parquet files by table names (endpoint names).
    
    Args:
        table_names: List of endpoint/table names
    
    Returns:
        List of parquet file paths
    """
    bronze_dir = get_bronze_dir()
    search_path = bronze_dir / "dnb_statistics"
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
    parquet_files: list[Path],
    cfg: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Upload multiple parquet files to BigQuery.
    
    Args:
        parquet_files: List of parquet file paths
        cfg: Configuration dict
        dry_run: If True, only show what would be uploaded
    
    Returns:
        Upload statistics
    """
    logger.info("\n" + "=" * 70)
    logger.info("DNB STATISTICS → BIGQUERY UPLOAD")
    logger.info("=" * 70)
    logger.info(f"Project: {cfg['project_id']}")
    logger.info(f"Location: {cfg['location']}")
    logger.info(f"GCS Bucket: {cfg['gcs_bucket']}")
    logger.info(f"BQ Dataset: {cfg['bq_dataset']}")
    logger.info(f"Files to upload: {len(parquet_files)}")
    logger.info("=" * 70 + "\n")
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No actual uploads will occur\n")
        bronze_dir = get_bronze_dir()
        for i, pf in enumerate(parquet_files, 1):
            try:
                rel_path = pf.relative_to(bronze_dir)
            except ValueError:
                rel_path = pf
            logger.info(f"[{i}/{len(parquet_files)}] Would upload: {rel_path}")
        return {"dry_run": True, "files": len(parquet_files)}
    
    # Initialize GCP managers
    logger.info("Initializing GCP connection...")
    auth = GCPAuth(project_id=cfg["project_id"])
    bq_mgr = BigQueryManager(auth, location=cfg["location"])
    logger.info(f"✓ Connected to project: {cfg['project_id']}\n")
    
    overall_start = datetime.now()
    results = []
    errors = []
    
    for i, parquet_file in enumerate(parquet_files, 1):
        logger.info(f"\n[{i}/{len(parquet_files)}] Processing: {parquet_file.name}")
        
        try:
            stats = bq_mgr.load_parquet_from_local(
                parquet_path=str(parquet_file),
                dataset_id=cfg["bq_dataset"],
                gcs_bucket=cfg["gcs_bucket"],
                partition_field=cfg["partition_field"],
                clustering_fields=cfg["clustering_fields"],
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
    logger.info(f"https://console.cloud.google.com/bigquery?project={cfg['project_id']}&d={cfg['bq_dataset']}&p={cfg['project_id']}&page=dataset")
    logger.info("")
    
    return {
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
        description="Upload DNB Statistics data to BigQuery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload all tables
  python -m backend.gcp.upload_dnb_statistics --all

  # Upload specific category
  python -m backend.gcp.upload_dnb_statistics --category insurance_pensions

  # Upload specific tables
  python -m backend.gcp.upload_dnb_statistics --tables exchange_rates_day

  # Dry run
  python -m backend.gcp.upload_dnb_statistics --all --dry-run
        """,
    )
    
    # Upload scope
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="Upload all parquet files",
    )
    group.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Upload all files in a category (e.g., insurance_pensions)",
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
        help="List all available parquet files and exit",
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Load configuration
    try:
        cfg = get_config()
    except ValueError as exc:
        logger.error(f"Configuration error: {exc}")
        logger.error("\nRequired environment variables:")
        logger.error("  GOOGLE_CLOUD_PROJECT - Your GCP project ID")
        logger.error("\nOptional environment variables:")
        logger.error("  GOOGLE_CLOUD_LOCATION - GCP location (default: us-central1)")
        logger.error("  GCS_BUCKET - GCS bucket name (default: {dataset}-data)")
        logger.error("  BQ_DATASET_ID - BigQuery dataset ID (default: dnb_statistics)")
        logger.error("  BQ_PARTITION_FIELD - Partition field (default: period)")
        logger.error("  BQ_CLUSTERING_FIELDS - Comma-separated clustering fields")
        sys.exit(1)
    
    # Discover files
    try:
        if args.all:
            parquet_files = discover_parquet_files()
        elif args.category:
            parquet_files = discover_parquet_files(category=args.category)
        elif args.tables:
            parquet_files = discover_by_table_names(args.tables)
        else:
            logger.error("No upload scope specified")
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
        logger.info(f"\nFound {len(parquet_files)} parquet file(s):")
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
            parquet_files=parquet_files,
            cfg=cfg,
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
