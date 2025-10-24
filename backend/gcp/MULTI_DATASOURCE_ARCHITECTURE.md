# Multi-Datasource GCP Architecture

## 🎯 Problem Statement

Current implementation is tightly coupled to DNB Statistics:
- Hard-coded dataset name: `dnb_statistics`
- Single bucket: `dnb-data`
- Upload CLI specific to DNB: `upload_dnb_statistics.py`
- No clear pattern for adding new datasources (EIOPA, World Bank, etc.)

## 🏗️ Proposed Architecture

### **Core Principle: Configuration-Driven Multi-Tenancy**

Each datasource gets its own:
1. **Configuration profile** (YAML file)
2. **GCS bucket** (or bucket prefix)
3. **BigQuery dataset**
4. **Generic upload orchestrator** (reusable across all datasources)

---

## 📁 Directory Structure

```
backend/
├── gcp/
│   ├── __init__.py
│   ├── auth.py                    # ✅ Already exists
│   ├── storage_manager.py         # ✅ Already exists
│   ├── bigquery_manager.py        # ✅ Already exists
│   ├── setup.py                   # ⚠️  Refactor to use profiles
│   ├── upload_parquet.py          # 🆕 Generic orchestrator
│   ├── datasource_config.py       # 🆕 Config loader/validator
│   └── profiles/                  # 🆕 Datasource configurations
│       ├── dnb_statistics.yaml
│       ├── dnb_public_register.yaml
│       ├── eiopa_data.yaml
│       ├── world_bank.yaml
│       └── README.md
│
├── etl/
│   ├── dnb_statistics/            # Extraction logic only
│   ├── dnb_public_register/       # Extraction logic only
│   ├── eiopa_data/                # 🆕 Future datasource
│   └── world_bank/                # 🆕 Future datasource
│
└── data/
    └── 1-bronze/
        ├── dnb_statistics/
        ├── dnb_public_register/
        ├── eiopa_data/            # 🆕
        └── world_bank/            # 🆕
```

---

## 📝 Datasource Profile Schema

**File: `backend/gcp/profiles/dnb_statistics.yaml`**

```yaml
# Datasource Metadata
datasource:
  id: dnb_statistics
  name: "DNB Statistics API"
  description: "Dutch Central Bank statistical data"
  provider: "De Nederlandsche Bank (DNB)"
  source_url: "https://api.dnb.nl/statistics"
  
# GCP Infrastructure
gcp:
  # BigQuery Configuration
  bigquery:
    dataset_id: dnb_statistics
    location: us-central1
    description: "DNB Statistics data warehouse"
    labels:
      datasource: dnb-statistics
      provider: dnb
      project: orkhon
    
    # Table configuration defaults
    table_defaults:
      partition_field: period
      partition_type: DAY
      clustering_fields: []
      write_disposition: WRITE_TRUNCATE
      
  # Cloud Storage Configuration
  storage:
    bucket_name: orkhon-dnb-statistics
    location: us-central1
    storage_class: STANDARD
    staging_prefix: bronze
    labels:
      datasource: dnb-statistics
      purpose: etl-staging
      
# Data Pipeline Configuration
pipeline:
  # Bronze layer path (relative to backend/data/1-bronze/)
  bronze_path: dnb_statistics
  
  # Table naming convention
  # Options: double_underscore, single_underscore, hyphen
  table_naming: double_underscore  # category__subcategory__endpoint
  
  # Schema detection
  schema:
    auto_detect: true
    source_format: PARQUET
    
  # Data quality
  quality:
    require_partition_field: true
    validate_schema: true
    
# Categories (for filtering and organization)
categories:
  - insurance_pensions
  - market_data
  - macroeconomic
  - payment_systems
```

---

## 📝 Generic Configuration Schema

**File: `backend/gcp/profiles/_schema.yaml`** (Reference/Documentation)

```yaml
# Minimal required configuration
datasource:
  id: string              # REQUIRED: Unique identifier (slug format)
  name: string            # REQUIRED: Human-readable name
  description: string     # Optional
  
gcp:
  bigquery:
    dataset_id: string    # REQUIRED: BigQuery dataset ID
    location: string      # Default: us-central1
    
  storage:
    bucket_name: string   # REQUIRED: GCS bucket name
    location: string      # Default: us-central1
    
pipeline:
  bronze_path: string     # REQUIRED: Path under backend/data/1-bronze/
  table_naming: string    # Default: double_underscore
```

---

## 🔧 Implementation

### **1. Configuration Loader**

**File: `backend/gcp/datasource_config.py`**

```python
"""
Datasource Configuration Management

Loads and validates datasource profiles from YAML files.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class BigQueryConfig(BaseModel):
    """BigQuery configuration for a datasource."""
    dataset_id: str
    location: str = "us-central1"
    description: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    
    class TableDefaults(BaseModel):
        partition_field: str | None = None
        partition_type: str = "DAY"
        clustering_fields: list[str] = Field(default_factory=list)
        write_disposition: str = "WRITE_TRUNCATE"
    
    table_defaults: TableDefaults = Field(default_factory=TableDefaults)


class StorageConfig(BaseModel):
    """Cloud Storage configuration for a datasource."""
    bucket_name: str
    location: str = "us-central1"
    storage_class: str = "STANDARD"
    staging_prefix: str = "bronze"
    labels: dict[str, str] = Field(default_factory=dict)


class PipelineConfig(BaseModel):
    """Data pipeline configuration."""
    bronze_path: str
    table_naming: str = "double_underscore"
    
    class SchemaConfig(BaseModel):
        auto_detect: bool = True
        source_format: str = "PARQUET"
    
    schema: SchemaConfig = Field(default_factory=SchemaConfig)


class DatasourceConfig(BaseModel):
    """Complete datasource configuration."""
    
    class DatasourceMeta(BaseModel):
        id: str
        name: str
        description: str | None = None
        provider: str | None = None
        source_url: str | None = None
    
    datasource: DatasourceMeta
    gcp: dict[str, Any]  # Contains bigquery and storage
    pipeline: dict[str, Any]
    categories: list[str] = Field(default_factory=list)
    
    @validator("datasource")
    def validate_id(cls, v):
        """Ensure datasource ID is slug-compatible."""
        if not v.id.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Datasource ID must be alphanumeric with _ or -: {v.id}")
        return v
    
    @property
    def bigquery(self) -> BigQueryConfig:
        """Get BigQuery configuration."""
        return BigQueryConfig(**self.gcp.get("bigquery", {}))
    
    @property
    def storage(self) -> StorageConfig:
        """Get Storage configuration."""
        return StorageConfig(**self.gcp.get("storage", {}))
    
    @property
    def pipeline_config(self) -> PipelineConfig:
        """Get Pipeline configuration."""
        return PipelineConfig(**self.pipeline)


def get_profiles_dir() -> Path:
    """Get datasource profiles directory."""
    return Path(__file__).parent / "profiles"


def list_datasources() -> list[str]:
    """List all available datasource profiles."""
    profiles_dir = get_profiles_dir()
    
    if not profiles_dir.exists():
        return []
    
    # Find all YAML files (excluding schema and README)
    datasources = [
        f.stem for f in profiles_dir.glob("*.yaml")
        if not f.stem.startswith("_")
    ]
    
    return sorted(datasources)


def load_datasource_config(datasource_id: str) -> DatasourceConfig:
    """
    Load datasource configuration from YAML profile.
    
    Args:
        datasource_id: Datasource identifier (e.g., 'dnb_statistics')
    
    Returns:
        DatasourceConfig object
    
    Raises:
        FileNotFoundError: If profile doesn't exist
        ValueError: If profile is invalid
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{datasource_id}.yaml"
    
    if not profile_path.exists():
        available = list_datasources()
        raise FileNotFoundError(
            f"Datasource profile not found: {datasource_id}\n"
            f"Available profiles: {', '.join(available)}"
        )
    
    logger.info(f"Loading datasource profile: {datasource_id}")
    
    with open(profile_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    try:
        config = DatasourceConfig(**data)
        logger.info(f"✓ Loaded profile for: {config.datasource.name}")
        return config
    except Exception as exc:
        raise ValueError(f"Invalid datasource profile: {exc}") from exc


def create_datasource_profile_template(datasource_id: str) -> str:
    """Generate YAML template for new datasource."""
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
      datasource: {datasource_id.replace("_", "-")}
      project: orkhon
    
    table_defaults:
      partition_field: date  # TODO: Adjust field name
      partition_type: DAY
      clustering_fields: []
      write_disposition: WRITE_TRUNCATE
  
  storage:
    bucket_name: orkhon-{datasource_id.replace("_", "-")}
    location: us-central1
    storage_class: STANDARD
    staging_prefix: bronze
    labels:
      datasource: {datasource_id.replace("_", "-")}
      purpose: etl-staging

pipeline:
  bronze_path: {datasource_id}
  table_naming: double_underscore
  
  schema:
    auto_detect: true
    source_format: PARQUET

categories: []  # TODO: Add data categories
'''
    return template
```

---

## 🚀 Generic Upload Orchestrator

**File: `backend/gcp/upload_parquet.py`**

```python
"""
Generic Parquet Upload Orchestrator

Upload parquet files to BigQuery for any configured datasource.

Usage:
    python -m backend.gcp.upload_parquet --datasource dnb_statistics --all
    python -m backend.gcp.upload_parquet --datasource eiopa_data --category insurance
    python -m backend.gcp.upload_parquet --list-datasources
"""

# Full implementation with datasource-agnostic logic
# See detailed implementation below...
```

---

## 🎯 Benefits

### **1. Horizontal Scalability**
- Add new datasources by creating a YAML profile (5 minutes)
- No code changes required for new datasources
- Self-documenting configuration

### **2. Vertical Scalability**
- Environment-specific overrides (dev/staging/prod)
- Project-level vs datasource-level settings
- Easy to manage with infrastructure-as-code (Terraform/Pulumi)

### **3. Best Practices**
- **Single Responsibility**: ETL extracts, GCP manages infrastructure
- **Convention over Configuration**: Sensible defaults with overrides
- **Type Safety**: Pydantic validation prevents misconfigurations
- **Audit Trail**: YAML profiles in version control

### **4. Developer Experience**
- Clear separation of concerns
- Easy to onboard new datasources
- Consistent patterns across all datasources
- Self-service via templates

---

## 📊 Migration Path

### **Phase 1: Create Infrastructure** ✅ (Next Step)
1. Create `backend/gcp/profiles/` directory
2. Create `datasource_config.py` with Pydantic models
3. Create `dnb_statistics.yaml` profile (migrate existing config)
4. Create generic `upload_parquet.py` orchestrator

### **Phase 2: Refactor Existing** ✅
1. Update `setup.py` to use profiles
2. Replace `upload_dnb_statistics.py` with generic version
3. Update VS Code tasks to use `--datasource` flag
4. Update documentation

### **Phase 3: Add New Datasources** 🆕
1. Create `dnb_public_register.yaml` profile
2. Test with existing data
3. Create templates for EIOPA, World Bank
4. Document onboarding process

### **Phase 4: Advanced Features** 🔮
1. Environment overrides (dev/staging/prod profiles)
2. Multi-project support (sandbox vs production GCP projects)
3. Cost tracking per datasource
4. Data quality metrics per datasource

---

## 🔐 Security Considerations

- Profiles stored in git (no secrets)
- GCP credentials via ADC or service accounts (not in profiles)
- Bucket/dataset permissions managed externally (IAM)
- Labels for cost allocation and access control

---

## 📝 Example Usage

```bash
# List available datasources
poetry run python -m backend.gcp.upload_parquet --list-datasources

# Upload DNB Statistics
poetry run python -m backend.gcp.upload_parquet \
  --datasource dnb_statistics \
  --all

# Upload EIOPA data (once profile exists)
poetry run python -m backend.gcp.upload_parquet \
  --datasource eiopa_data \
  --category insurance \
  --dry-run

# Create new datasource profile
poetry run python -m backend.gcp.upload_parquet \
  --create-profile world_bank
```

---

## 🎓 Next Steps

1. **Review this architecture** - Does it meet your scalability needs?
2. **Implement Phase 1** - Create profiles infrastructure
3. **Migrate DNB Statistics** - Convert to profile-based config
4. **Test & validate** - Ensure backward compatibility
5. **Document** - Update READMEs with new patterns
6. **Scale** - Add EIOPA, World Bank, etc.

---

*This architecture is inspired by industry best practices from:*
- *Terraform module patterns*
- *Kubernetes Helm charts*
- *AWS CDK constructs*
- *dbt project configurations*
