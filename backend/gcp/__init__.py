"""
Google Cloud Platform Infrastructure Management

Python-based utilities for managing GCP resources programmatically.

This package provides:
- Resource creation/deletion (buckets, datasets, tables)
- Authentication management
- IAM and permissions configuration
- Infrastructure validation
- Cost estimation

Prefer Python clients over shell commands for:
- Better error handling
- Type safety
- Cross-platform compatibility
- Testability
- Programmatic control
"""

from __future__ import annotations

from .auth import GCPAuth
from .bigquery_manager import BigQueryManager
from .storage_manager import StorageManager

__all__ = [
    "GCPAuth",
    "BigQueryManager",
    "StorageManager",
]
