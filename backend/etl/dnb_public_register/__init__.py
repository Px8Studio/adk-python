"""
DNB Public Register ETL Package

Extracts comprehensive data from DNB Public Register API and stores in Parquet format.

Modules:
- config: Configuration and settings
- base: Base classes and utilities
- extractors: Endpoint-specific extraction logic
- orchestrator: Main ETL coordinator
"""

from __future__ import annotations

__version__ = "1.0.0"
