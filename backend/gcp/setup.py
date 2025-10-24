"""
GCP Infrastructure Setup Script

Python-based CLI for setting up GCP resources for the Orkhon project.

Usage:
    python -m backend.gcp.setup --all
    python -m backend.gcp.setup --bucket
    python -m backend.gcp.setup --dataset
    python -m backend.gcp.setup --validate
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

def get_config() -> dict:
    """Load configuration from environment."""
    config = {
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        "gcs_bucket": os.getenv("GCS_BUCKET", "dnb-data"),
        "bq_dataset": os.getenv("BQ_DATASET_ID", "dnb_statistics"),
    }
    
    if not config["project_id"]:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)
    
    return config


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


def setup_storage(auth: GCPAuth, config: dict) -> bool:
    """Create GCS bucket."""
    logger.info("=" * 70)
    logger.info("SETTING UP GOOGLE CLOUD STORAGE")
    logger.info("=" * 70)
    
    storage_mgr = StorageManager(auth)
    bucket_name = config["gcs_bucket"]
    location = config["location"]
    
    try:
        storage_mgr.create_bucket(
            bucket_name,
            location=location,
            labels={"project": "orkhon", "purpose": "etl-staging"},
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


def setup_bigquery(auth: GCPAuth, config: dict) -> bool:
    """Create BigQuery dataset."""
    logger.info("=" * 70)
    logger.info("SETTING UP GOOGLE BIGQUERY")
    logger.info("=" * 70)
    
    bq_mgr = BigQueryManager(auth, location=config["location"])
    dataset_id = config["bq_dataset"]
    
    try:
        bq_mgr.create_dataset(
            dataset_id,
            description="DNB Statistics data from ETL pipeline",
            labels={"project": "orkhon", "source": "dnb-api"},
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


def validate_setup(auth: GCPAuth, config: dict) -> bool:
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
        if storage_mgr.bucket_exists(config["gcs_bucket"]):
            logger.info(f"  ✓ Bucket exists: gs://{config['gcs_bucket']}")
        else:
            logger.error(f"  ✗ Bucket not found: {config['gcs_bucket']}")
            all_valid = False
    except Exception as exc:
        logger.error(f"  ✗ Storage validation failed: {exc}")
        all_valid = False
    
    # Validate BigQuery
    logger.info("\n3. BigQuery")
    try:
        bq_mgr = BigQueryManager(auth, location=config["location"])
        if bq_mgr.dataset_exists(config["bq_dataset"]):
            logger.info(f"  ✓ Dataset exists: {config['bq_dataset']}")
            
            # List tables
            tables = bq_mgr.list_tables(config["bq_dataset"])
            logger.info(f"  ✓ Tables: {len(tables)}")
        else:
            logger.error(f"  ✗ Dataset not found: {config['bq_dataset']}")
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
        description="GCP Infrastructure Setup for Orkhon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup everything
  python -m backend.gcp.setup --all

  # Setup only storage
  python -m backend.gcp.setup --bucket

  # Setup only BigQuery
  python -m backend.gcp.setup --dataset

  # Validate existing setup
  python -m backend.gcp.setup --validate

Environment Variables:
  GOOGLE_CLOUD_PROJECT     - GCP project ID (required)
  GOOGLE_CLOUD_LOCATION    - GCP location (default: us-central1)
  GCS_BUCKET               - GCS bucket name (default: dnb-data)
  BQ_DATASET_ID            - BigQuery dataset ID (default: dnb_statistics)
  GOOGLE_APPLICATION_CREDENTIALS - Path to service account key (optional)
        """,
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
    
    # Load configuration
    config = get_config()
    
    logger.info("\n" + "=" * 70)
    logger.info("GCP INFRASTRUCTURE SETUP - ORKHON PROJECT")
    logger.info("=" * 70)
    logger.info(f"Project ID: {config['project_id']}")
    logger.info(f"Location: {config['location']}")
    logger.info(f"GCS Bucket: {config['gcs_bucket']}")
    logger.info(f"BQ Dataset: {config['bq_dataset']}")
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
