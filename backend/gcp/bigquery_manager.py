"""
Google BigQuery Manager

Python client for managing BigQuery datasets, tables, and queries.

Best Practices:
- Use partitioned tables for time-series data
- Implement clustering for frequently filtered columns
- Set table expiration for temporary tables
- Use dry_run for cost estimation before queries
- Leverage table schemas to validate data quality
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from google.cloud import bigquery
from google.cloud.exceptions import Conflict, NotFound

from backend.gcp.auth import GCPAuth
from backend.gcp.storage_manager import StorageManager

logger = logging.getLogger(__name__)


class BigQueryManager:
    """
    Manage Google BigQuery resources programmatically.
    
    Example:
        >>> auth = GCPAuth()
        >>> bq_mgr = BigQueryManager(auth)
        >>> bq_mgr.create_dataset("my_dataset", location="us-central1")
        >>> bq_mgr.create_table_from_parquet(
        ...     "my_dataset",
        ...     "my_table",
        ...     "gs://bucket/data.parquet"
        ... )
    """
    
    def __init__(self, auth: GCPAuth, *, location: str = "us-central1"):
        """
        Initialize BigQuery Manager.
        
        Args:
            auth: GCPAuth instance for authentication
            location: Default BigQuery location
        """
        self.auth = auth
        self.location = location
        self._client: Optional[bigquery.Client] = None
    
    @property
    def client(self) -> bigquery.Client:
        """Get or create BigQuery client."""
        if self._client is None:
            credentials = self.auth.get_credentials()
            project_id = self.auth.get_project_id()
            
            self._client = bigquery.Client(
                project=project_id,
                credentials=credentials,
                location=self.location,
            )
            
            logger.debug(f"Initialized BigQuery client for project: {project_id}")
        
        return self._client
    
    # ==========================================
    # Dataset Operations
    # ==========================================
    
    def dataset_exists(self, dataset_id: str) -> bool:
        """
        Check if a dataset exists.
        
        Args:
            dataset_id: Dataset ID
        
        Returns:
            True if exists, False otherwise
        """
        dataset_ref = f"{self.client.project}.{dataset_id}"
        
        try:
            self.client.get_dataset(dataset_ref)
            return True
        except NotFound:
            return False
    
    def create_dataset(
        self,
        dataset_id: str,
        *,
        location: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        default_table_expiration_ms: Optional[int] = None,
    ) -> bigquery.Dataset:
        """
        Create a BigQuery dataset.
        
        Args:
            dataset_id: Dataset ID
            location: Dataset location (default: instance location)
            description: Dataset description
            labels: Optional labels
            default_table_expiration_ms: Default table expiration in milliseconds
        
        Returns:
            Created dataset object
        """
        if self.dataset_exists(dataset_id):
            logger.info(f"Dataset already exists: {dataset_id}")
            return self.client.get_dataset(dataset_id)
        
        location = location or self.location
        dataset_ref = f"{self.client.project}.{dataset_id}"
        
        logger.info(f"Creating dataset: {dataset_ref} (location={location})")
        
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        
        if description:
            dataset.description = description
        
        if labels:
            dataset.labels = labels
        
        if default_table_expiration_ms:
            dataset.default_table_expiration_ms = default_table_expiration_ms
        
        dataset = self.client.create_dataset(dataset)
        
        logger.info(f"✓ Created dataset: {dataset_ref}")
        return dataset
    
    def delete_dataset(
        self,
        dataset_id: str,
        *,
        delete_contents: bool = False,
    ) -> bool:
        """
        Delete a BigQuery dataset.
        
        Args:
            dataset_id: Dataset ID
            delete_contents: If True, delete all tables in dataset
        
        Returns:
            True if deleted, False if not found
        """
        if not self.dataset_exists(dataset_id):
            logger.warning(f"Dataset not found: {dataset_id}")
            return False
        
        dataset_ref = f"{self.client.project}.{dataset_id}"
        
        logger.info(f"Deleting dataset: {dataset_ref}")
        self.client.delete_dataset(
            dataset_ref,
            delete_contents=delete_contents,
            not_found_ok=True,
        )
        
        logger.info(f"✓ Deleted dataset: {dataset_ref}")
        return True
    
    def list_datasets(self) -> list[str]:
        """
        List all datasets in the project.
        
        Returns:
            List of dataset IDs
        """
        datasets = list(self.client.list_datasets())
        return [dataset.dataset_id for dataset in datasets]
    
    def get_dataset_info(self, dataset_id: str) -> dict[str, Any]:
        """
        Get information about a dataset.
        
        Args:
            dataset_id: Dataset ID
        
        Returns:
            Dict with dataset information
        """
        dataset_ref = f"{self.client.project}.{dataset_id}"
        dataset = self.client.get_dataset(dataset_ref)
        
        return {
            "dataset_id": dataset.dataset_id,
            "project": dataset.project,
            "location": dataset.location,
            "created": dataset.created,
            "modified": dataset.modified,
            "description": dataset.description,
            "labels": dataset.labels,
            "default_table_expiration_ms": dataset.default_table_expiration_ms,
        }
    
    # ==========================================
    # Table Operations
    # ==========================================
    
    def table_exists(self, dataset_id: str, table_id: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
        
        Returns:
            True if exists, False otherwise
        """
        table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
        
        try:
            self.client.get_table(table_ref)
            return True
        except NotFound:
            return False
    
    def create_table(
        self,
        dataset_id: str,
        table_id: str,
        schema: list[bigquery.SchemaField],
        *,
        description: Optional[str] = None,
        partition_field: Optional[str] = None,
        clustering_fields: Optional[list[str]] = None,
        labels: Optional[dict[str, str]] = None,
    ) -> bigquery.Table:
        """
        Create a BigQuery table.
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
            schema: Table schema (list of SchemaField)
            description: Table description
            partition_field: Field for time partitioning
            clustering_fields: Fields for clustering
            labels: Optional labels
        
        Returns:
            Created table object
        """
        if self.table_exists(dataset_id, table_id):
            logger.info(f"Table already exists: {dataset_id}.{table_id}")
            return self.client.get_table(f"{self.client.project}.{dataset_id}.{table_id}")
        
        table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
        
        logger.info(f"Creating table: {table_ref}")
        
        table = bigquery.Table(table_ref, schema=schema)
        
        if description:
            table.description = description
        
        if partition_field:
            # Verify field exists in schema
            if any(field.name == partition_field for field in schema):
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field=partition_field,
                )
                logger.info(f"  Partitioning by: {partition_field}")
        
        if clustering_fields:
            # Verify fields exist in schema
            valid_fields = [
                f for f in clustering_fields
                if any(field.name == f for field in schema)
            ]
            if valid_fields:
                table.clustering_fields = valid_fields
                logger.info(f"  Clustering by: {', '.join(valid_fields)}")
        
        if labels:
            table.labels = labels
        
        table = self.client.create_table(table)
        
        logger.info(f"✓ Created table: {table_ref}")
        return table
    
    def delete_table(self, dataset_id: str, table_id: str) -> bool:
        """
        Delete a BigQuery table.
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
        
        Returns:
            True if deleted, False if not found
        """
        if not self.table_exists(dataset_id, table_id):
            logger.warning(f"Table not found: {dataset_id}.{table_id}")
            return False
        
        table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
        
        logger.info(f"Deleting table: {table_ref}")
        self.client.delete_table(table_ref, not_found_ok=True)
        
        logger.info(f"✓ Deleted table: {table_ref}")
        return True
    
    def list_tables(self, dataset_id: str) -> list[str]:
        """
        List all tables in a dataset.
        
        Args:
            dataset_id: Dataset ID
        
        Returns:
            List of table IDs
        """
        dataset_ref = f"{self.client.project}.{dataset_id}"
        tables = list(self.client.list_tables(dataset_ref))
        return [table.table_id for table in tables]
    
    def get_table_info(self, dataset_id: str, table_id: str) -> dict[str, Any]:
        """
        Get information about a table.
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
        
        Returns:
            Dict with table information
        """
        table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
        table = self.client.get_table(table_ref)
        
        return {
            "table_id": table.table_id,
            "dataset_id": table.dataset_id,
            "project": table.project,
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "created": table.created,
            "modified": table.modified,
            "description": table.description,
            "schema": [{"name": field.name, "type": field.field_type} for field in table.schema],
            "partitioning": {
                "type": table.time_partitioning.type_ if table.time_partitioning else None,
                "field": table.time_partitioning.field if table.time_partitioning else None,
            },
            "clustering_fields": table.clustering_fields,
            "labels": table.labels,
        }
    
    # ==========================================
    # Data Loading
    # ==========================================
    
    def load_table_from_gcs(
        self,
        gcs_uri: str,
        dataset_id: str,
        table_id: str,
        *,
        source_format: str = "PARQUET",
        write_disposition: str = "WRITE_TRUNCATE",
        autodetect: bool = False,
    ) -> bigquery.LoadJob:
        """
        Load data from GCS into BigQuery table.
        
        Args:
            gcs_uri: GCS URI (gs://bucket/path)
            dataset_id: Dataset ID
            table_id: Table ID
            source_format: Source format (PARQUET, CSV, JSON, AVRO)
            write_disposition: WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY
            autodetect: Auto-detect schema
        
        Returns:
            Completed LoadJob
        """
        table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=getattr(bigquery.SourceFormat, source_format),
            write_disposition=write_disposition,
            autodetect=autodetect,
        )
        
        logger.info(f"Loading {gcs_uri} into {table_ref}")
        logger.info(f"  Format: {source_format}")
        logger.info(f"  Write mode: {write_disposition}")
        
        load_job = self.client.load_table_from_uri(
            gcs_uri,
            table_ref,
            job_config=job_config,
        )
        
        # Wait for completion
        load_job.result()
        
        # Get final table info
        table = self.client.get_table(table_ref)
        logger.info(f"✓ Loaded {table.num_rows:,} rows into {table_ref}")
        
        return load_job
    
    # ==========================================
    # Query Operations
    # ==========================================
    
    def execute_query(
        self,
        query: str,
        *,
        dry_run: bool = False,
    ) -> bigquery.QueryJob | dict[str, Any]:
        """
        Execute a BigQuery SQL query.
        
        Args:
            query: SQL query string
            dry_run: If True, estimate costs without running
        
        Returns:
            QueryJob if executed, cost estimate dict if dry_run
        """
        job_config = bigquery.QueryJobConfig(dry_run=dry_run)
        
        query_job = self.client.query(query, job_config=job_config)
        
        if dry_run:
            # Return cost estimate
            bytes_processed = query_job.total_bytes_processed
            gb_processed = bytes_processed / (1024 ** 3)
            cost_estimate = gb_processed * 6.25 / 1000  # $6.25 per TB
            
            return {
                "bytes_processed": bytes_processed,
                "gb_processed": gb_processed,
                "cost_estimate_usd": cost_estimate,
            }
        
        # Wait for completion
        query_job.result()
        
        logger.info(f"✓ Query completed")
        logger.info(f"  Bytes processed: {query_job.total_bytes_processed:,}")
        logger.info(f"  Slot time: {query_job.slot_millis} ms")
        
        return query_job
    
    # ==========================================
    # Utility Operations
    # ==========================================
    
    def validate_configuration(self) -> dict[str, Any]:
        """
        Validate BigQuery configuration.
        
        Returns:
            Dict with validation results
        """
        project_id = self.client.project
        location = self.location
        
        logger.info("✓ BigQuery configuration validated")
        logger.info(f"  Project: {project_id}")
        logger.info(f"  Location: {location}")
        
        # List datasets to verify access
        datasets = self.list_datasets()
        logger.info(f"  Accessible datasets: {len(datasets)}")
        
        return {
            "project_id": project_id,
            "location": location,
            "num_datasets": len(datasets),
            "datasets": datasets,
        }
    
    # ==========================================
    # Parquet Operations
    # ==========================================
    
    @staticmethod
    def parquet_to_bigquery_schema(parquet_path: str) -> list[bigquery.SchemaField]:
        """
        Infer BigQuery schema from parquet file.
        
        Args:
            parquet_path: Path to local parquet file
        
        Returns:
            List of BigQuery SchemaField objects
        
        Example:
            >>> schema = BigQueryManager.parquet_to_bigquery_schema("data.parquet")
            >>> bq.create_table("dataset", "table", schema=schema)
        """
        import pyarrow.parquet as pq
        from pathlib import Path
        
        # Read parquet schema
        parquet_file = pq.ParquetFile(Path(parquet_path))
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
    
    @staticmethod
    def generate_table_name(
        category: str,
        subcategory: str | None,
        endpoint_name: str
    ) -> str:
        """
        Generate BigQuery table name from DNB folder structure.
        
        Format: {category}__{subcategory}__{endpoint_name}
        
        Args:
            category: Top-level category (e.g., 'insurance_pensions')
            subcategory: Optional subcategory (e.g., 'insurers')
            endpoint_name: Endpoint identifier
        
        Returns:
            BigQuery-compatible table name
        
        Example:
            >>> BigQueryManager.generate_table_name(
            ...     "insurance_pensions", "insurers", "balance_sheet_quarter"
            ... )
            'insurance_pensions__insurers__balance_sheet_quarter'
        """
        parts = [category]
        if subcategory:
            parts.append(subcategory)
        parts.append(endpoint_name)
        
        # Ensure valid BigQuery naming (alphanumeric + underscores)
        table_name = "__".join(parts)
        table_name = table_name.replace("-", "_").lower()
        
        return table_name
    
    @staticmethod
    def parse_table_path(parquet_path: str) -> dict[str, str]:
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
        
        Example:
            >>> info = BigQueryManager.parse_table_path(
            ...     "data/1-bronze/dnb_statistics/insurance_pensions/insurers/balance.parquet"
            ... )
            >>> info["table_name"]
            'insurance_pensions__insurers__balance'
        """
        from pathlib import Path
        
        path = Path(parquet_path)
        parts = path.parts
        
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
            endpoint = path.stem
        elif len(parts) - stats_idx == 3:  # category/file.parquet
            subcategory = None
            endpoint = path.stem
        else:
            raise ValueError(f"Unexpected path structure: {parquet_path}")
        
        table_name = BigQueryManager.generate_table_name(category, subcategory, endpoint)
        
        return {
            "category": category,
            "subcategory": subcategory,
            "endpoint": endpoint,
            "table_name": table_name,
        }
    
    def load_parquet_from_local(
        self,
        parquet_path: str,
        dataset_id: str,
        *,
        table_id: str | None = None,
        gcs_bucket: str | None = None,
        gcs_staging_prefix: str = "bronze",
        partition_field: str | None = None,
        clustering_fields: list[str] | None = None,
        write_disposition: str = "WRITE_TRUNCATE",
        auto_detect_table_name: bool = True,
    ) -> dict[str, Any]:
        """
        Full pipeline: Load parquet from local file to BigQuery.
        
        Workflow:
        1. Auto-detect table name from path (if enabled)
        2. Infer BigQuery schema from parquet
        3. Upload parquet to GCS staging
        4. Create BigQuery table with schema/partitioning
        5. Load data from GCS into BigQuery
        
        Args:
            parquet_path: Local parquet file path
            dataset_id: BigQuery dataset ID
            table_id: Table ID (auto-detected from path if not provided)
            gcs_bucket: GCS bucket name (uses dataset_id-data if not provided)
            gcs_staging_prefix: GCS path prefix (default: 'bronze')
            partition_field: Optional field for time partitioning
            clustering_fields: Optional fields for clustering
            write_disposition: How to handle existing data (WRITE_TRUNCATE, WRITE_APPEND)
            auto_detect_table_name: Auto-detect table name from DNB path structure
        
        Returns:
            Dict with upload statistics
        
        Example:
            >>> bq.load_parquet_from_local(
            ...     "data/1-bronze/dnb_statistics/market_data/rates/daily.parquet",
            ...     dataset_id="dnb_statistics",
            ...     partition_field="period"
            ... )
        """
        from pathlib import Path
        
        local_path = Path(parquet_path)
        
        if not local_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        
        logger.info(f"\n{'=' * 70}")
        logger.info(f"LOADING PARQUET TO BIGQUERY: {local_path.name}")
        logger.info(f"{'=' * 70}\n")
        
        # Auto-detect table name from DNB path structure
        if auto_detect_table_name:
            try:
                table_info = self.parse_table_path(str(local_path))
                detected_table_id = table_info["table_name"]
                
                if table_id is None:
                    table_id = detected_table_id
                    logger.info(f"Auto-detected table name: {table_id}")
                    logger.info(f"  Category: {table_info['category']}")
                    if table_info["subcategory"]:
                        logger.info(f"  Subcategory: {table_info['subcategory']}")
                    logger.info(f"  Endpoint: {table_info['endpoint']}\n")
            except ValueError as e:
                if table_id is None:
                    raise ValueError(
                        f"Could not auto-detect table name from path: {e}\n"
                        "Please provide table_id explicitly."
                    )
        
        if table_id is None:
            raise ValueError("table_id must be provided or auto_detect_table_name must be True")
        
        # Default GCS bucket
        if gcs_bucket is None:
            gcs_bucket = f"{dataset_id}-data"
            logger.info(f"Using default GCS bucket: {gcs_bucket}")
        
        # Step 1: Infer schema from parquet
        logger.info("Step 1: Inferring schema from parquet...")
        schema = self.parquet_to_bigquery_schema(str(local_path))
        logger.info(f"  ✓ Found {len(schema)} columns\n")
        
        # Step 2: Create BigQuery table
        logger.info("Step 2: Creating/verifying BigQuery table...")
        self.create_table(
            dataset_id=dataset_id,
            table_id=table_id,
            schema=schema,
            partition_field=partition_field,
            clustering_fields=clustering_fields,
        )
        logger.info(f"  ✓ Table ready: {dataset_id}.{table_id}\n")
        
        # Step 3: Upload to GCS
        logger.info("Step 3: Uploading to GCS staging...")
        storage = StorageManager(self.auth)
        
        # Build GCS path
        if auto_detect_table_name:
            try:
                table_info = self.parse_table_path(str(local_path))
                gcs_path = f"{gcs_staging_prefix}/{table_info['category']}"
                if table_info["subcategory"]:
                    gcs_path += f"/{table_info['subcategory']}"
                gcs_path += f"/{local_path.name}"
            except ValueError:
                gcs_path = f"{gcs_staging_prefix}/{local_path.name}"
        else:
            gcs_path = f"{gcs_staging_prefix}/{local_path.name}"
        
        gcs_uri = storage.upload_file(
            local_path=str(local_path),
            bucket_name=gcs_bucket,
            blob_path=gcs_path,
        )
        logger.info(f"  ✓ Uploaded to: {gcs_uri}\n")
        
        # Step 4: Load into BigQuery
        logger.info("Step 4: Loading into BigQuery...")
        load_job = self.load_table_from_gcs(
            gcs_uri=gcs_uri,
            dataset_id=dataset_id,
            table_id=table_id,
            source_format="PARQUET",
            write_disposition=write_disposition,
        )
        
        # Get final table info
        table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
        final_table = self.client.get_table(table_ref)
        
        stats = {
            "table_name": table_id,
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



# Example usage (for reference, do not execute at import time):
# 
# storage = StorageManager(auth)
# 
# # Create bucket with labels
# storage.create_bucket(
#     "my-bucket",
#     location="us-central1",
#     labels={"project": "orkhon"}
# )
# 
# # Upload file
# gcs_uri = storage.upload_file(
#     local_path="data.parquet",
#     bucket_name="my-bucket",
#     blob_path="bronze/data.parquet"
# )
# 
# # List objects
# files = storage.list_objects("my-bucket", prefix="bronze/")
# 
# # Check existence
# if storage.bucket_exists("my-bucket"):
#     print("Bucket ready!")
# 
# bq = BigQueryManager(auth, location="us-central1")
# 
# # Create dataset with labels
# bq.create_dataset(
#     "dnb_statistics",
#     description="DNB data",
#     labels={"project": "orkhon"}
# )
# 
# # Create table with schema
# schema = [
#     bigquery.SchemaField("id", "INTEGER"),
#     bigquery.SchemaField("name", "STRING"),
#     bigquery.SchemaField("date", "DATE"),
# ]
# 
# bq.create_table(
#     "dnb_statistics",
#     "my_table",
#     schema=schema,
#     partition_field="date",
#     clustering_fields=["name"]
# )
# 
# # Load data from GCS
# bq.load_table_from_gcs(
#     gcs_uri="gs://bucket/data.parquet",
#     dataset_id="dnb_statistics",
#     table_id="my_table",
#     source_format="PARQUET"
# )
# 
# # Dry run query (cost estimation)
# estimate = bq.execute_query(
#     "SELECT * FROM dnb_statistics.my_table",
#     dry_run=True
# )
# print(f"Cost: ${estimate['cost_estimate_usd']:.4f}")
