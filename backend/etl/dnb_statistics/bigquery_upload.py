"""
BigQuery Upload Utilities

Handles uploading parquet files from Bronze layer to BigQuery via GCS staging.

Features:
- Auto-generates BigQuery table names from folder structure
- Infers schemas from parquet files
- Creates partitioned and clustered tables
- Uploads via GCS for efficient loading
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from google.cloud import bigquery, storage
from google.cloud.exceptions import NotFound

from . import config

logger = logging.getLogger(__name__)


# ==========================================
# Table Naming
# ==========================================

def generate_table_name(
    category: str,
    subcategory: str | None,
    endpoint_name: str
) -> str:
    """
    Generate BigQuery table name from folder structure.
    
    Format: {category}__{subcategory}__{endpoint_name}
    Examples:
        - insurance_pensions__insurers__insurance_corps_balance_sheet_quarter
        - market_data__interest_rates__market_interest_rates_day
    
    Args:
        category: Top-level category (e.g., 'insurance_pensions')
        subcategory: Optional subcategory (e.g., 'insurers')
        endpoint_name: Endpoint identifier
    
    Returns:
        BigQuery-compatible table name
    """
    parts = [category]
    if subcategory:
        parts.append(subcategory)
    parts.append(endpoint_name)
    
    # Ensure valid BigQuery naming (alphanumeric + underscores)
    table_name = "__".join(parts)
    table_name = table_name.replace("-", "_").lower()
    
    return table_name


def parse_table_path(parquet_path: Path) -> dict[str, str]:
    """
    Parse category/subcategory/endpoint from parquet file path.
    
    Expected structure:
        data/1-bronze/dnb_statistics/{category}/{subcategory}/{endpoint}.parquet
        OR
        data/1-bronze/dnb_statistics/{category}/{endpoint}.parquet
    
    Args:
        parquet_path: Path to parquet file
    
    Returns:
        Dict with 'category', 'subcategory' (optional), 'endpoint', 'table_name'
    """
    parts = parquet_path.parts
    
    # Find the index of 'dnb_statistics'
    try:
        stats_idx = parts.index("dnb_statistics")
    except ValueError:
        raise ValueError(f"Path does not contain 'dnb_statistics': {parquet_path}")
    
    # Extract category and endpoint
    category = parts[stats_idx + 1]
    
    # Check if there's a subcategory
    if len(parts) - stats_idx == 4:  # category/subcategory/file.parquet
        subcategory = parts[stats_idx + 2]
        endpoint = parquet_path.stem
    elif len(parts) - stats_idx == 3:  # category/file.parquet
        subcategory = None
        endpoint = parquet_path.stem
    else:
        raise ValueError(f"Unexpected path structure: {parquet_path}")
    
    table_name = generate_table_name(category, subcategory, endpoint)
    
    return {
        "category": category,
        "subcategory": subcategory,
        "endpoint": endpoint,
        "table_name": table_name,
    }


# ==========================================
# Schema Inference
# ==========================================

def parquet_to_bigquery_schema(parquet_path: Path) -> list[bigquery.SchemaField]:
    """
    Infer BigQuery schema from parquet file.
    
    Args:
        parquet_path: Path to parquet file
    
    Returns:
        List of BigQuery SchemaField objects
    """
    # Read parquet schema
    parquet_file = pq.ParquetFile(parquet_path)
    arrow_schema = parquet_file.schema_arrow
    
    # Map Arrow types to BigQuery types
    type_mapping = {
        "int64": "INTEGER",
        "int32": "INTEGER",
        "int16": "INTEGER",
        "int8": "INTEGER",
        "uint64": "INTEGER",
        "uint32": "INTEGER",
        "uint16": "INTEGER",
        "uint8": "INTEGER",
        "float": "FLOAT",
        "float64": "FLOAT",
        "float32": "FLOAT",
        "double": "FLOAT",
        "string": "STRING",
        "large_string": "STRING",
        "binary": "BYTES",
        "large_binary": "BYTES",
        "bool": "BOOLEAN",
        "date32": "DATE",
        "date64": "DATE",
        "timestamp": "TIMESTAMP",
        "time64": "TIME",
        "decimal128": "NUMERIC",
        "decimal256": "BIGNUMERIC",
    }
    
    schema_fields = []
    for field in arrow_schema:
        field_type = str(field.type)
        
        # Handle nested types
        if field_type.startswith("struct"):
            bq_type = "RECORD"
        elif field_type.startswith("list"):
            bq_type = "REPEATED"
        else:
            # Get base type
            base_type = field_type.split("[")[0].split("(")[0]
            bq_type = type_mapping.get(base_type, "STRING")
        
        mode = "NULLABLE" if field.nullable else "REQUIRED"
        
        schema_fields.append(
            bigquery.SchemaField(
                name=field.name,
                field_type=bq_type,
                mode=mode,
            )
        )
    
    return schema_fields


# ==========================================
# GCS Upload
# ==========================================

def upload_to_gcs(
    local_path: Path,
    bucket_name: str,
    blob_path: str,
    storage_client: storage.Client | None = None,
) -> str:
    """
    Upload file to Google Cloud Storage.
    
    Args:
        local_path: Local file path
        bucket_name: GCS bucket name
        blob_path: Destination path in bucket (e.g., 'bronze/category/file.parquet')
        storage_client: Optional GCS client (will create if not provided)
    
    Returns:
        GCS URI (gs://bucket/path)
    """
    if storage_client is None:
        storage_client = storage.Client()
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    
    logger.info(f"Uploading {local_path.name} to gs://{bucket_name}/{blob_path}")
    blob.upload_from_filename(str(local_path))
    
    gcs_uri = f"gs://{bucket_name}/{blob_path}"
    logger.info(f"✓ Upload complete: {gcs_uri}")
    
    return gcs_uri


# ==========================================
# BigQuery Table Creation
# ==========================================

def create_bigquery_table(
    dataset_id: str,
    table_id: str,
    schema: list[bigquery.SchemaField],
    partition_field: str | None = None,
    clustering_fields: list[str] | None = None,
    bq_client: bigquery.Client | None = None,
) -> bigquery.Table:
    """
    Create or update BigQuery table with schema and partitioning.
    
    Args:
        dataset_id: BigQuery dataset ID
        table_id: Table ID
        schema: List of SchemaField objects
        partition_field: Optional field for time partitioning
        clustering_fields: Optional fields for clustering
        bq_client: Optional BigQuery client
    
    Returns:
        BigQuery Table object
    """
    if bq_client is None:
        bq_client = bigquery.Client()
    
    table_ref = f"{bq_client.project}.{dataset_id}.{table_id}"
    
    # Check if table exists
    try:
        existing_table = bq_client.get_table(table_ref)
        logger.info(f"Table {table_ref} already exists - will replace data")
        return existing_table
    except NotFound:
        logger.info(f"Creating new table: {table_ref}")
    
    # Create table definition
    table = bigquery.Table(table_ref, schema=schema)
    
    # Add partitioning if specified
    if partition_field:
        # Check if field exists in schema
        if any(field.name == partition_field for field in schema):
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field,
            )
            logger.info(f"  Partitioning by: {partition_field}")
    
    # Add clustering if specified
    if clustering_fields:
        # Verify fields exist
        valid_fields = [
            f for f in clustering_fields
            if any(field.name == f for field in schema)
        ]
        if valid_fields:
            table.clustering_fields = valid_fields
            logger.info(f"  Clustering by: {', '.join(valid_fields)}")
    
    # Create table
    table = bq_client.create_table(table)
    logger.info(f"✓ Created table: {table_ref}")
    
    return table


# ==========================================
# BigQuery Load Job
# ==========================================

def load_parquet_from_gcs(
    gcs_uri: str,
    dataset_id: str,
    table_id: str,
    write_disposition: str = "WRITE_TRUNCATE",
    bq_client: bigquery.Client | None = None,
) -> bigquery.LoadJob:
    """
    Load parquet file from GCS into BigQuery table.
    
    Args:
        gcs_uri: GCS URI (gs://bucket/path)
        dataset_id: BigQuery dataset ID
        table_id: Table ID
        write_disposition: How to handle existing data (WRITE_TRUNCATE, WRITE_APPEND)
        bq_client: Optional BigQuery client
    
    Returns:
        Completed LoadJob
    """
    if bq_client is None:
        bq_client = bigquery.Client()
    
    table_ref = f"{bq_client.project}.{dataset_id}.{table_id}"
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=write_disposition,
        autodetect=False,  # Use existing table schema
    )
    
    logger.info(f"Loading {gcs_uri} into {table_ref}")
    logger.info(f"  Write mode: {write_disposition}")
    
    # Start load job
    load_job = bq_client.load_table_from_uri(
        gcs_uri,
        table_ref,
        job_config=job_config,
    )
    
    # Wait for completion
    load_job.result()
    
    # Get results
    destination_table = bq_client.get_table(table_ref)
    logger.info(f"✓ Loaded {destination_table.num_rows:,} rows into {table_ref}")
    
    return load_job


# ==========================================
# Full Upload Pipeline
# ==========================================

def upload_parquet_to_bigquery(
    parquet_path: Path,
    gcs_bucket: str,
    bq_dataset: str,
    partition_field: str | None = "period",
    clustering_fields: list[str] | None = None,
    gcs_staging_prefix: str = "bronze",
    write_disposition: str = "WRITE_TRUNCATE",
) -> dict[str, Any]:
    """
    Full pipeline: Upload parquet to GCS → Create BQ table → Load data.
    
    Args:
        parquet_path: Local parquet file path
        gcs_bucket: GCS bucket name
        bq_dataset: BigQuery dataset ID
        partition_field: Optional field for time partitioning (default: 'period')
        clustering_fields: Optional fields for clustering
        gcs_staging_prefix: GCS path prefix (default: 'bronze')
        write_disposition: How to handle existing data
    
    Returns:
        Dict with upload statistics
    """
    logger.info(f"\n{'=' * 70}")
    logger.info(f"UPLOADING: {parquet_path.name}")
    logger.info(f"{'=' * 70}\n")
    
    # Parse table info from path
    table_info = parse_table_path(parquet_path)
    table_name = table_info["table_name"]
    
    logger.info(f"Table name: {table_name}")
    logger.info(f"  Category: {table_info['category']}")
    if table_info["subcategory"]:
        logger.info(f"  Subcategory: {table_info['subcategory']}")
    logger.info(f"  Endpoint: {table_info['endpoint']}\n")
    
    # Initialize clients
    storage_client = storage.Client()
    bq_client = bigquery.Client()
    
    # 1. Infer schema from parquet
    logger.info("Step 1: Inferring schema from parquet...")
    schema = parquet_to_bigquery_schema(parquet_path)
    logger.info(f"  Found {len(schema)} columns")
    
    # 2. Create BigQuery table
    logger.info("\nStep 2: Creating/verifying BigQuery table...")
    create_bigquery_table(
        dataset_id=bq_dataset,
        table_id=table_name,
        schema=schema,
        partition_field=partition_field,
        clustering_fields=clustering_fields,
        bq_client=bq_client,
    )
    
    # 3. Upload to GCS
    logger.info("\nStep 3: Uploading to GCS staging...")
    gcs_path = f"{gcs_staging_prefix}/{table_info['category']}"
    if table_info["subcategory"]:
        gcs_path += f"/{table_info['subcategory']}"
    gcs_path += f"/{parquet_path.name}"
    
    gcs_uri = upload_to_gcs(
        local_path=parquet_path,
        bucket_name=gcs_bucket,
        blob_path=gcs_path,
        storage_client=storage_client,
    )
    
    # 4. Load into BigQuery
    logger.info("\nStep 4: Loading into BigQuery...")
    load_job = load_parquet_from_gcs(
        gcs_uri=gcs_uri,
        dataset_id=bq_dataset,
        table_id=table_name,
        write_disposition=write_disposition,
        bq_client=bq_client,
    )
    
    # Get final table info
    table_ref = f"{bq_client.project}.{bq_dataset}.{table_name}"
    final_table = bq_client.get_table(table_ref)
    
    stats = {
        "table_name": table_name,
        "table_ref": table_ref,
        "gcs_uri": gcs_uri,
        "num_rows": final_table.num_rows,
        "size_bytes": final_table.num_bytes,
        "schema_fields": len(schema),
        "partitioned": partition_field is not None,
        "clustered": clustering_fields is not None,
    }
    
    logger.info(f"\n{'=' * 70}")
    logger.info("✓ UPLOAD COMPLETE")
    logger.info(f"  Table: {table_ref}")
    logger.info(f"  Rows: {stats['num_rows']:,}")
    logger.info(f"  Size: {stats['size_bytes'] / (1024**2):.2f} MB")
    logger.info(f"{'=' * 70}\n")
    
    return stats
