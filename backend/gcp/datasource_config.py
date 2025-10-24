"""
Datasource Configuration Management

Loads and validates datasource profiles from YAML files.
Provides type-safe configuration for multi-datasource GCP infrastructure.

Usage:
    from backend.gcp.datasource_config import load_datasource_config
    
    config = load_datasource_config("dnb_statistics")
    print(config.bigquery.dataset_id)  # Access typed configuration
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# ==========================================
# Configuration Models
# ==========================================

class TableDefaults(BaseModel):
    """Default table configuration."""
    partition_field: str | None = None
    partition_type: str = "DAY"
    clustering_fields: list[str] = Field(default_factory=list)
    write_disposition: str = "WRITE_TRUNCATE"


class BigQueryConfig(BaseModel):
    """BigQuery configuration for a datasource."""
    dataset_id: str
    location: str = "us-central1"
    description: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    table_defaults: TableDefaults = Field(default_factory=TableDefaults)


class StorageConfig(BaseModel):
    """Cloud Storage configuration for a datasource."""
    bucket_name: str
    location: str = "us-central1"
    storage_class: str = "STANDARD"
    staging_prefix: str = "bronze"
    labels: dict[str, str] = Field(default_factory=dict)


class SchemaConfig(BaseModel):
    """Schema detection configuration."""
    auto_detect: bool = True
    source_format: str = "PARQUET"


class QualityConfig(BaseModel):
    """Data quality configuration."""
    require_partition_field: bool = True
    validate_schema: bool = True


class PipelineConfig(BaseModel):
    """Data pipeline configuration."""
    bronze_path: str
    table_naming: str = "double_underscore"
    schema: SchemaConfig = Field(default_factory=SchemaConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)


class DatasourceMeta(BaseModel):
    """Datasource metadata."""
    id: str
    name: str
    description: str | None = None
    provider: str | None = None
    source_url: str | None = None
    
    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure datasource ID is slug-compatible."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Datasource ID must be alphanumeric with _ or -: {v}")
        return v


class DatasourceConfig(BaseModel):
    """Complete datasource configuration."""
    
    datasource: DatasourceMeta
    gcp: dict[str, Any]  # Raw dict, parsed into specific configs below
    pipeline: dict[str, Any]  # Raw dict, parsed into PipelineConfig
    categories: list[str] = Field(default_factory=list)
    
    def __init__(self, **data):
        """Initialize and parse nested configurations."""
        super().__init__(**data)
        # Parse nested configs
        self._bigquery_config = BigQueryConfig(**self.gcp.get("bigquery", {}))
        self._storage_config = StorageConfig(**self.gcp.get("storage", {}))
        self._pipeline_config = PipelineConfig(**self.pipeline)
    
    @property
    def bigquery(self) -> BigQueryConfig:
        """Get BigQuery configuration."""
        return self._bigquery_config
    
    @property
    def storage(self) -> StorageConfig:
        """Get Storage configuration."""
        return self._storage_config
    
    @property
    def pipeline_config(self) -> PipelineConfig:
        """Get Pipeline configuration."""
        return self._pipeline_config


# ==========================================
# Profile Management Functions
# ==========================================

def get_profiles_dir() -> Path:
    """Get datasource profiles directory."""
    return Path(__file__).parent / "profiles"


def list_datasources() -> list[str]:
    """
    List all available datasource profiles.
    
    Returns:
        List of datasource IDs (profile filenames without .yaml)
    
    Example:
        >>> datasources = list_datasources()
        >>> print(datasources)
        ['dnb_statistics', 'dnb_public_register', 'eiopa_data']
    """
    profiles_dir = get_profiles_dir()
    
    if not profiles_dir.exists():
        logger.warning(f"Profiles directory not found: {profiles_dir}")
        return []
    
    # Find all YAML files (excluding _schema.yaml and other _ prefixed files)
    datasources = [
        f.stem for f in profiles_dir.glob("*.yaml")
        if not f.stem.startswith("_") and f.stem.lower() != "readme"
    ]
    
    return sorted(datasources)


def load_datasource_config(datasource_id: str) -> DatasourceConfig:
    """
    Load datasource configuration from YAML profile.
    
    Args:
        datasource_id: Datasource identifier (e.g., 'dnb_statistics')
    
    Returns:
        DatasourceConfig object with parsed configuration
    
    Raises:
        FileNotFoundError: If profile doesn't exist
        ValueError: If profile YAML is invalid
    
    Example:
        >>> config = load_datasource_config("dnb_statistics")
        >>> print(config.datasource.name)
        'DNB Statistics API'
        >>> print(config.bigquery.dataset_id)
        'dnb_statistics'
        >>> print(config.storage.bucket_name)
        'orkhon-dnb-statistics'
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{datasource_id}.yaml"
    
    if not profile_path.exists():
        available = list_datasources()
        available_list = ", ".join(available) if available else "none"
        raise FileNotFoundError(
            f"Datasource profile not found: {datasource_id}\n"
            f"Available profiles: {available_list}\n"
            f"Expected path: {profile_path}"
        )
    
    logger.info(f"Loading datasource profile: {datasource_id}")
    logger.debug(f"Profile path: {profile_path}")
    
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in profile {datasource_id}: {exc}") from exc
    
    try:
        config = DatasourceConfig(**data)
        logger.info(f"✓ Loaded profile for: {config.datasource.name}")
        return config
    except Exception as exc:
        raise ValueError(
            f"Invalid datasource profile structure in {datasource_id}:\n{exc}"
        ) from exc


def create_datasource_profile_template(datasource_id: str) -> str:
    """
    Generate YAML template for a new datasource.
    
    Args:
        datasource_id: Unique identifier for the datasource (slug format)
    
    Returns:
        YAML template string
    
    Example:
        >>> template = create_datasource_profile_template("world_bank")
        >>> print(template)
        # Datasource Profile: world_bank
        ...
    """
    # Convert underscores to hyphens for GCP resource names
    gcp_name = datasource_id.replace("_", "-")
    
    template = f'''# Datasource Profile: {datasource_id}
# Generated template - customize as needed

datasource:
  id: {datasource_id}
  name: "TODO: Add human-readable name"
  description: "TODO: Add description"
  provider: "TODO: Add provider name"
  source_url: "TODO: Add source URL"

gcp:
  bigquery:
    dataset_id: {datasource_id}
    location: us-central1
    description: "TODO: Add dataset description"
    labels:
      datasource: {gcp_name}
      project: orkhon
    
    table_defaults:
      partition_field: date  # TODO: Adjust field name or set to null
      partition_type: DAY
      clustering_fields: []
      write_disposition: WRITE_TRUNCATE
  
  storage:
    bucket_name: orkhon-{gcp_name}
    location: us-central1
    storage_class: STANDARD
    staging_prefix: bronze
    labels:
      datasource: {gcp_name}
      purpose: etl-staging

pipeline:
  bronze_path: {datasource_id}
  table_naming: double_underscore
  
  schema:
    auto_detect: true
    source_format: PARQUET
  
  quality:
    require_partition_field: true
    validate_schema: true

categories: []  # TODO: Add data categories
'''
    return template


def save_datasource_profile(datasource_id: str, template: str | None = None) -> Path:
    """
    Save a datasource profile to disk.
    
    Args:
        datasource_id: Datasource identifier
        template: YAML content (generates if not provided)
    
    Returns:
        Path to saved profile
    
    Raises:
        FileExistsError: If profile already exists
    """
    profiles_dir = get_profiles_dir()
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    profile_path = profiles_dir / f"{datasource_id}.yaml"
    
    if profile_path.exists():
        raise FileExistsError(
            f"Profile already exists: {profile_path}\n"
            "Delete or rename the existing profile first."
        )
    
    if template is None:
        template = create_datasource_profile_template(datasource_id)
    
    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    logger.info(f"✓ Created profile: {profile_path}")
    return profile_path


def validate_datasource_config(config: DatasourceConfig) -> dict[str, Any]:
    """
    Validate datasource configuration.
    
    Args:
        config: DatasourceConfig to validate
    
    Returns:
        Dict with validation results
    
    Example:
        >>> config = load_datasource_config("dnb_statistics")
        >>> results = validate_datasource_config(config)
        >>> print(results["valid"])
        True
    """
    issues = []
    warnings = []
    
    # Check required fields
    if not config.datasource.name:
        issues.append("Missing datasource name")
    
    if not config.bigquery.dataset_id:
        issues.append("Missing BigQuery dataset_id")
    
    if not config.storage.bucket_name:
        issues.append("Missing GCS bucket_name")
    
    if not config.pipeline_config.bronze_path:
        issues.append("Missing pipeline bronze_path")
    
    # Check optional but recommended fields
    if not config.datasource.description:
        warnings.append("Missing datasource description (recommended)")
    
    if not config.bigquery.labels:
        warnings.append("No BigQuery labels defined (recommended for cost tracking)")
    
    if not config.storage.labels:
        warnings.append("No Storage labels defined (recommended for cost tracking)")
    
    if not config.categories:
        warnings.append("No categories defined (helpful for organization)")
    
    # Check partition configuration
    if (config.pipeline_config.quality.require_partition_field and 
        not config.bigquery.table_defaults.partition_field):
        warnings.append(
            "quality.require_partition_field is true but "
            "table_defaults.partition_field is not set"
        )
    
    return {
        "valid": len(issues) == 0,
        "datasource_id": config.datasource.id,
        "datasource_name": config.datasource.name,
        "issues": issues,
        "warnings": warnings,
    }
