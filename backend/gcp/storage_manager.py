"""
Google Cloud Storage Manager

Python client for managing GCS buckets, objects, and access control.

Best Practices:
- Use lifecycle policies for cost optimization
- Enable versioning for important data
- Set appropriate IAM policies
- Use signed URLs for temporary access
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from google.cloud import storage
from google.cloud.exceptions import Conflict, NotFound

from .auth import GCPAuth

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manage Google Cloud Storage resources programmatically.
    
    Example:
        >>> auth = GCPAuth()
        >>> storage_mgr = StorageManager(auth)
        >>> storage_mgr.create_bucket("my-data-bucket", location="us-central1")
        >>> storage_mgr.upload_file("data.parquet", "my-data-bucket", "data/data.parquet")
    """
    
    def __init__(self, auth: GCPAuth):
        """
        Initialize Storage Manager.
        
        Args:
            auth: GCPAuth instance for authentication
        """
        self.auth = auth
        self._client: Optional[storage.Client] = None
    
    @property
    def client(self) -> storage.Client:
        """Get or create GCS client."""
        if self._client is None:
            credentials = self.auth.get_credentials()
            project_id = self.auth.get_project_id()
            
            self._client = storage.Client(
                project=project_id,
                credentials=credentials,
            )
            
            logger.debug(f"Initialized Storage client for project: {project_id}")
        
        return self._client
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if a bucket exists.
        
        Args:
            bucket_name: Name of the bucket
        
        Returns:
            True if bucket exists, False otherwise
        """
        try:
            self.client.get_bucket(bucket_name)
            return True
        except NotFound:
            return False
    
    def create_bucket(
        self,
        bucket_name: str,
        *,
        location: str = "us-central1",
        storage_class: str = "STANDARD",
        labels: Optional[dict[str, str]] = None,
    ) -> storage.Bucket:
        """
        Create a new GCS bucket.
        
        Args:
            bucket_name: Name of the bucket (must be globally unique)
            location: GCS location (default: us-central1)
            storage_class: Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
            labels: Optional labels for the bucket
        
        Returns:
            Created bucket object
        
        Raises:
            Conflict: If bucket already exists
        """
        if self.bucket_exists(bucket_name):
            logger.info(f"Bucket already exists: {bucket_name}")
            return self.client.get_bucket(bucket_name)
        
        logger.info(f"Creating bucket: {bucket_name} (location={location}, class={storage_class})")
        
        bucket = self.client.bucket(bucket_name)
        bucket.storage_class = storage_class
        
        if labels:
            bucket.labels = labels
        
        new_bucket = self.client.create_bucket(bucket, location=location)
        
        logger.info(f"✓ Created bucket: gs://{bucket_name}")
        return new_bucket
    
    def delete_bucket(
        self,
        bucket_name: str,
        *,
        force: bool = False,
    ) -> bool:
        """
        Delete a GCS bucket.
        
        Args:
            bucket_name: Name of the bucket
            force: If True, delete all objects first
        
        Returns:
            True if deleted, False if not found
        
        Raises:
            ValueError: If bucket is not empty and force=False
        """
        if not self.bucket_exists(bucket_name):
            logger.warning(f"Bucket not found: {bucket_name}")
            return False
        
        bucket = self.client.get_bucket(bucket_name)
        
        if force:
            logger.info(f"Deleting all objects in bucket: {bucket_name}")
            blobs = list(bucket.list_blobs())
            
            if blobs:
                logger.info(f"  Deleting {len(blobs)} object(s)...")
                bucket.delete_blobs(blobs)
        
        logger.info(f"Deleting bucket: {bucket_name}")
        bucket.delete()
        
        logger.info(f"✓ Deleted bucket: gs://{bucket_name}")
        return True
    
    def upload_file(
        self,
        local_path: Path | str,
        bucket_name: str,
        blob_path: str,
        *,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file to GCS.
        
        Args:
            local_path: Local file path
            bucket_name: GCS bucket name
            blob_path: Destination path in bucket
            content_type: Optional content type
        
        Returns:
            GCS URI (gs://bucket/path)
        """
        local_path = Path(local_path)
        
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        if content_type:
            blob.content_type = content_type
        
        logger.info(f"Uploading {local_path.name} to gs://{bucket_name}/{blob_path}")
        blob.upload_from_filename(str(local_path))
        
        gcs_uri = f"gs://{bucket_name}/{blob_path}"
        logger.info(f"✓ Upload complete: {gcs_uri}")
        
        return gcs_uri
    
    def download_file(
        self,
        bucket_name: str,
        blob_path: str,
        local_path: Path | str,
    ) -> Path:
        """
        Download a file from GCS.
        
        Args:
            bucket_name: GCS bucket name
            blob_path: Source path in bucket
            local_path: Local destination path
        
        Returns:
            Path to downloaded file
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        logger.info(f"Downloading gs://{bucket_name}/{blob_path} to {local_path}")
        blob.download_to_filename(str(local_path))
        
        logger.info(f"✓ Download complete: {local_path}")
        return local_path
    
    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> list[str]:
        """
        List objects in a bucket.
        
        Args:
            bucket_name: GCS bucket name
            prefix: Optional prefix filter
            delimiter: Optional delimiter (e.g., '/' for directories)
        
        Returns:
            List of blob names
        """
        bucket = self.client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        
        return [blob.name for blob in blobs]
    
    def object_exists(
        self,
        bucket_name: str,
        blob_path: str,
    ) -> bool:
        """
        Check if an object exists in GCS.
        
        Args:
            bucket_name: GCS bucket name
            blob_path: Path to object
        
        Returns:
            True if exists, False otherwise
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        return blob.exists()
    
    def delete_object(
        self,
        bucket_name: str,
        blob_path: str,
    ) -> bool:
        """
        Delete an object from GCS.
        
        Args:
            bucket_name: GCS bucket name
            blob_path: Path to object
        
        Returns:
            True if deleted, False if not found
        """
        if not self.object_exists(bucket_name, blob_path):
            logger.warning(f"Object not found: gs://{bucket_name}/{blob_path}")
            return False
        
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        logger.info(f"Deleting gs://{bucket_name}/{blob_path}")
        blob.delete()
        
        logger.info(f"✓ Deleted object")
        return True
    
    def get_bucket_info(self, bucket_name: str) -> dict[str, Any]:
        """
        Get information about a bucket.
        
        Args:
            bucket_name: GCS bucket name
        
        Returns:
            Dict with bucket information
        """
        bucket = self.client.get_bucket(bucket_name)
        
        return {
            "name": bucket.name,
            "location": bucket.location,
            "storage_class": bucket.storage_class,
            "time_created": bucket.time_created,
            "metageneration": bucket.metageneration,
            "versioning_enabled": bucket.versioning_enabled,
            "labels": bucket.labels,
        }
