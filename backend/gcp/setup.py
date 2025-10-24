"""
GCP Infrastructure Setup Script

Python-based CLI for setting up GCP resources for any datasource.

Usage:
    # List available datasources
    python -m backend.gcp.setup --list-datasources

    # Setup all resources for a datasource
    python -m backend.gcp.setup --datasource dnb_statistics --all

    # Setup only storage
    python -m backend.gcp.setup --datasource dnb_statistics --bucket

    # Setup only BigQuery
    python -m backend.gcp.setup --datasource dnb_statistics --dataset

    # Validate existing setup
    python -m backend.gcp.setup --datasource dnb_statistics --validate
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .auth import GCPAuth
from .bigquery_manager import BigQueryManager
from .storage_manager import StorageManager
from .datasource_config import (
    load_datasource_config,
    list_datasources,
    DatasourceConfig,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ==========================================
# Configuration
# ==========================================

def get_project_id() -> str:
    """Get GCP project ID from environment."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        logger.error("Set it in your .env file or environment")
        sys.exit(1)
    return project_id


# ==========================================
# Setup Functions
# ==========================================

def setup_authentication() -> GCPAuth:
    """Initialize authentication."""
    logger.info("=" * 70)
    logger.info("AUTHENTICATING WITH GOOGLE CLOUD")
    logger.info("=" * 70)
    
    # Check for service account key
    sa_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if sa_key_path:
        auth = GCPAuth(service_account_path=Path(sa_key_path))
    else:
        logger.info("Using Application Default Credentials (ADC)")
        auth = GCPAuth()
    
    # Validate
    validation = auth.validate()
    
    logger.info("\n")
    return auth


def setup_storage(auth: GCPAuth, config: DatasourceConfig) -> bool:
    """Create GCS bucket."""
    logger.info("=" * 70)
    logger.info("SETTING UP GOOGLE CLOUD STORAGE")
    logger.info("=" * 70)
    
    storage_mgr = StorageManager(auth)
    bucket_name = config.storage.bucket_name
    location = config.storage.location
    
    try:
        storage_mgr.create_bucket(
            bucket_name,
            location=location,
            storage_class=config.storage.storage_class,
            labels=config.storage.labels,
        )
        
        # Verify
        bucket_info = storage_mgr.get_bucket_info(bucket_name)
        logger.info(f"\nBucket Details:")
        logger.info(f"  Name: {bucket_info['name']}")
        logger.info(f"  Location: {bucket_info['location']}")
        logger.info(f"  Storage Class: {bucket_info['storage_class']}")
        logger.info(f"  Created: {bucket_info['time_created']}")
        
        logger.info("\n✓ Storage setup complete")
        return True
    
    except Exception as exc:
        logger.error(f"✗ Failed to setup storage: {exc}", exc_info=True)
        return False


def setup_bigquery(auth: GCPAuth, config: DatasourceConfig) -> bool:
    """Create BigQuery dataset."""
    logger.info("=" * 70)
    logger.info("SETTING UP GOOGLE BIGQUERY")
    logger.info("=" * 70)
    
    bq_mgr = BigQueryManager(auth, location=config.bigquery.location)
    dataset_id = config.bigquery.dataset_id
    
    try:
        bq_mgr.create_dataset(
            dataset_id,
            description=config.bigquery.description or f"{config.datasource.name} data from ETL pipeline",
            labels=config.bigquery.labels,
        )
        
        # Verify
        dataset_info = bq_mgr.get_dataset_info(dataset_id)
        logger.info(f"\nDataset Details:")
        logger.info(f"  Dataset ID: {dataset_info['dataset_id']}")
        logger.info(f"  Project: {dataset_info['project']}")
        logger.info(f"  Location: {dataset_info['location']}")
        logger.info(f"  Created: {dataset_info['created']}")
        
        logger.info("\n✓ BigQuery setup complete")
        return True
    
    except Exception as exc:
        logger.error(f"✗ Failed to setup BigQuery: {exc}", exc_info=True)
        return False


def validate_setup(auth: GCPAuth, config: DatasourceConfig) -> bool:
    """Validate the entire GCP setup."""
    logger.info("=" * 70)
    logger.info("VALIDATING GCP SETUP")
    logger.info("=" * 70)
    
    all_valid = True
    
    # Validate authentication
    logger.info("\n1. Authentication")
    try:
        auth.validate()
    except Exception as exc:
        logger.error(f"  ✗ Authentication failed: {exc}")
        all_valid = False
    
    # Validate storage
    logger.info("\n2. Cloud Storage")
    try:
        storage_mgr = StorageManager(auth)
        if storage_mgr.bucket_exists(config.storage.bucket_name):
            logger.info(f"  ✓ Bucket exists: gs://{config.storage.bucket_name}")
            bucket_info = storage_mgr.get_bucket_info(config.storage.bucket_name)
            logger.info(f"    Location: {bucket_info['location']}")
            logger.info(f"    Storage Class: {bucket_info['storage_class']}")
        else:
            logger.error(f"  ✗ Bucket not found: {config.storage.bucket_name}")
            all_valid = False
    except Exception as exc:
        logger.error(f"  ✗ Storage validation failed: {exc}")
        all_valid = False
    
    # Validate BigQuery
    logger.info("\n3. BigQuery")
    try:
        bq_mgr = BigQueryManager(auth, location=config.bigquery.location)
        if bq_mgr.dataset_exists(config.bigquery.dataset_id):
            logger.info(f"  ✓ Dataset exists: {config.bigquery.dataset_id}")
            
            # List tables
            tables = bq_mgr.list_tables(config.bigquery.dataset_id)
            logger.info(f"  ✓ Tables: {len(tables)}")
            if tables:
                logger.info(f"    First few: {', '.join(tables[:5])}")
        else:
            logger.error(f"  ✗ Dataset not found: {config.bigquery.dataset_id}")
            all_valid = False
    except Exception as exc:
        logger.error(f"  ✗ BigQuery validation failed: {exc}")
        all_valid = False
    
    # Summary
    logger.info("\n" + "=" * 70)
    if all_valid:
        logger.info("✓ ALL VALIDATIONS PASSED")
    else:
        logger.error("✗ SOME VALIDATIONS FAILED")
    logger.info("=" * 70 + "\n")
    
    return all_valid


# ==========================================
# CLI
# ==========================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GCP Infrastructure Setup for any datasource",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available datasources
  python -m backend.gcp.setup --list-datasources

  # Setup everything for a datasource
  python -m backend.gcp.setup --datasource dnb_statistics --all

  # Setup only storage
  python -m backend.gcp.setup --datasource dnb_statistics --bucket

  # Setup only BigQuery
  python -m backend.gcp.setup --datasource dnb_statistics --dataset

  # Validate existing setup
  python -m backend.gcp.setup --datasource dnb_statistics --validate

Environment Variables:
  GOOGLE_CLOUD_PROJECT           - GCP project ID (required)
  GOOGLE_APPLICATION_CREDENTIALS - Path to service account key (optional)
        """,
    )
    
    parser.add_argument(
        "--list-datasources",
        action="store_true",
        help="List all available datasource profiles",
    )
    
    parser.add_argument(
        "--datasource",
        type=str,
        metavar="DATASOURCE_ID",
        help="Datasource to setup (e.g., dnb_statistics)",
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Setup all resources (bucket + dataset)",
    )
    
    parser.add_argument(
        "--bucket",
        action="store_true",
        help="Setup GCS bucket only",
    )
    
    parser.add_argument(
        "--dataset",
        action="store_true",
        help="Setup BigQuery dataset only",
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing setup",
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
                    logger.info(f"    Bucket: {config.storage.bucket_name}")
                    logger.info(f"    Dataset: {config.bigquery.dataset_id}")
                except Exception as exc:
                    logger.info(f"  • {ds:30s} - (invalid profile: {exc})")
        sys.exit(0)
    
    # Require datasource for setup operations
    if not args.datasource:
        logger.error("Error: --datasource required for setup operations")
        logger.error("\nRun with --list-datasources to see available datasources")
        sys.exit(1)
    
    # Load datasource configuration
    try:
        config = load_datasource_config(args.datasource)
    except Exception as exc:
        logger.error(f"Failed to load datasource profile '{args.datasource}': {exc}")
        logger.error("\nRun with --list-datasources to see available datasources")
        sys.exit(1)
    
    # Get project ID
    project_id = get_project_id()
    
    logger.info("\n" + "=" * 70)
    logger.info(f"GCP INFRASTRUCTURE SETUP - {config.datasource.name.upper()}")
    logger.info("=" * 70)
    logger.info(f"Datasource: {args.datasource}")
    logger.info(f"Project ID: {project_id}")
    logger.info(f"Location: {config.bigquery.location}")
    logger.info(f"GCS Bucket: {config.storage.bucket_name}")
    logger.info(f"BQ Dataset: {config.bigquery.dataset_id}")
    logger.info("=" * 70 + "\n")
    
    # Setup authentication
    try:
        auth = setup_authentication()
    except Exception as exc:
        logger.error(f"Authentication failed: {exc}")
        sys.exit(1)
    
    # Perform requested operations
    success = True
    
    if args.validate:
        success = validate_setup(auth, config)
    
    elif args.all:
        success = setup_storage(auth, config) and setup_bigquery(auth, config)
        if success:
            logger.info("\n")
            validate_setup(auth, config)
    
    elif args.bucket:
        success = setup_storage(auth, config)
    
    elif args.dataset:
        success = setup_bigquery(auth, config)
    
    else:
        logger.error("No operation specified. Use --all, --bucket, --dataset, or --validate")
        sys.exit(1)
    
    # Exit with appropriate code
    if success:
        logger.info("\n✓ Setup completed successfully!\n")
        sys.exit(0)
    else:
        logger.error("\n✗ Setup failed. Please check the errors above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
