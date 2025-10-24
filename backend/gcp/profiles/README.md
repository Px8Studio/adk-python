# Datasource Profiles

This directory contains configuration profiles for each datasource in the Orkhon platform.

## 📋 Overview

Each datasource gets its own YAML profile that defines:
- **Metadata**: Name, description, provider information
- **GCP Resources**: BigQuery dataset, GCS bucket configuration
- **Pipeline Settings**: Data paths, naming conventions, schema detection
- **Categories**: Data categories for organization and filtering

## 🎯 Purpose

Profiles enable:
- **Horizontal Scaling**: Add new datasources without code changes
- **Vertical Scaling**: Environment-specific configurations (dev/prod)
- **Self-Documentation**: All datasource config in one place
- **Type Safety**: Pydantic validation prevents misconfigurations
- **Version Control**: Infrastructure-as-code for data pipelines

## 📁 Profile Structure

### Minimal Profile

```yaml
datasource:
  id: my_datasource          # REQUIRED: Unique slug identifier
  name: "My Data Source"     # REQUIRED: Human-readable name

gcp:
  bigquery:
    dataset_id: my_datasource  # REQUIRED: BigQuery dataset
    
  storage:
    bucket_name: orkhon-my-datasource  # REQUIRED: GCS bucket

pipeline:
  bronze_path: my_datasource   # REQUIRED: Path under backend/data/1-bronze/
```

### Full Profile Example

See `dnb_statistics.yaml` for a complete example with all options.

## 🚀 Adding a New Datasource

### Step 1: Create Profile Template

```bash
poetry run python -m backend.gcp.upload_parquet --create-profile my_datasource
```

This generates `profiles/my_datasource.yaml` with all fields.

### Step 2: Customize Configuration

Edit the generated YAML file:
```yaml
datasource:
  id: my_datasource
  name: "My Data Source API"
  description: "Description of the data"
  provider: "Provider Organization"
  source_url: "https://example.com/api"

gcp:
  bigquery:
    dataset_id: my_datasource
    location: us-central1
    labels:
      datasource: my-datasource
      project: orkhon
    table_defaults:
      partition_field: date
      partition_type: DAY
      
  storage:
    bucket_name: orkhon-my-datasource
    location: us-central1
    labels:
      datasource: my-datasource

pipeline:
  bronze_path: my_datasource
  table_naming: double_underscore

categories:
  - category1
  - category2
```

### Step 3: Setup Infrastructure

```bash
poetry run python -m backend.gcp.setup --datasource my_datasource --all
```

This creates the GCS bucket and BigQuery dataset.

### Step 4: Upload Data

```bash
poetry run python -m backend.gcp.upload_parquet \
  --datasource my_datasource \
  --all
```

## 📝 Configuration Reference

### Datasource Metadata

```yaml
datasource:
  id: string              # Unique identifier (alphanumeric with _ or -)
  name: string            # Display name
  description: string     # Optional description
  provider: string        # Optional provider name
  source_url: string      # Optional source URL
```

### BigQuery Configuration

```yaml
gcp:
  bigquery:
    dataset_id: string           # BigQuery dataset ID (REQUIRED)
    location: string             # Default: us-central1
    description: string          # Dataset description
    labels:                      # Key-value labels for cost tracking
      key: value
    
    table_defaults:
      partition_field: string    # Field for time partitioning (e.g., 'date', 'period')
      partition_type: string     # Default: DAY (or HOUR, MONTH, YEAR)
      clustering_fields: []      # List of fields for clustering
      write_disposition: string  # Default: WRITE_TRUNCATE (or WRITE_APPEND)
```

### Storage Configuration

```yaml
gcp:
  storage:
    bucket_name: string          # GCS bucket name (REQUIRED)
    location: string             # Default: us-central1
    storage_class: string        # Default: STANDARD (or NEARLINE, COLDLINE, ARCHIVE)
    staging_prefix: string       # Default: bronze
    labels:                      # Key-value labels
      key: value
```

### Pipeline Configuration

```yaml
pipeline:
  bronze_path: string            # Path under backend/data/1-bronze/ (REQUIRED)
  table_naming: string           # Default: double_underscore
                                 # Options: double_underscore, single_underscore, hyphen
  
  schema:
    auto_detect: boolean         # Default: true
    source_format: string        # Default: PARQUET (or CSV, JSON, AVRO)
  
  quality:
    require_partition_field: boolean  # Default: true
    validate_schema: boolean          # Default: true
```

### Categories

```yaml
categories:
  - category_name_1
  - category_name_2
```

Categories are used for:
- Filtering uploads (`--category` flag)
- Organizing data in Bronze layer
- Documentation and discovery

## 🔧 Environment-Specific Profiles

For multi-environment setups, create environment-specific profiles:

```
profiles/
  my_datasource.yaml           # Base configuration
  my_datasource.dev.yaml       # Development overrides
  my_datasource.staging.yaml   # Staging overrides
  my_datasource.prod.yaml      # Production overrides
```

Use with:
```bash
poetry run python -m backend.gcp.upload_parquet \
  --datasource my_datasource \
  --env prod \
  --all
```

## 📊 Available Datasources

Run to list all configured datasources:

```bash
poetry run python -m backend.gcp.upload_parquet --list-datasources
```

## 🔐 Security Notes

- **No Secrets in Profiles**: Credentials are managed via GCP IAM
- **Version Control**: Profiles are committed to git
- **Labels**: Use for cost allocation and access control
- **Validation**: Pydantic ensures type safety

## 🎓 Best Practices

1. **Naming Conventions**:
   - Datasource IDs: `snake_case` (e.g., `dnb_statistics`)
   - Bucket names: `orkhon-{datasource-id}` (e.g., `orkhon-dnb-statistics`)
   - Dataset IDs: Same as datasource ID (e.g., `dnb_statistics`)

2. **Labels**:
   - Always include `datasource` label for cost tracking
   - Use consistent label keys across all datasources
   - Add `project: orkhon` to all resources

3. **Partitioning**:
   - Use time-based partitioning for time-series data
   - Choose partition granularity based on query patterns
   - Add clustering for frequently filtered columns

4. **Documentation**:
   - Fill in all metadata fields (name, description, provider, source_url)
   - List all categories
   - Document any special pipeline requirements

## 🐛 Troubleshooting

### Profile Not Found

```
FileNotFoundError: Datasource profile not found: my_datasource
Available profiles: dnb_statistics, dnb_public_register
```

**Solution**: Create the profile with `--create-profile my_datasource`

### Invalid Configuration

```
ValueError: Invalid datasource profile: validation error for DatasourceConfig
```

**Solution**: Check YAML syntax and required fields. See minimal profile example above.

### Bucket Already Exists

```
Conflict: Bucket orkhon-my-datasource already exists
```

**Solution**: Either use existing bucket or choose a different name in the profile.

## 📚 Related Documentation

- [MULTI_DATASOURCE_ARCHITECTURE.md](../MULTI_DATASOURCE_ARCHITECTURE.md) - Architecture overview
- [README.md](../README.md) - GCP managers documentation
- [BIGQUERY_UPLOAD.md](../../etl/dnb_statistics/BIGQUERY_UPLOAD.md) - BigQuery upload guide

## 💡 Examples

See existing profiles:
- `dnb_statistics.yaml` - DNB Statistics API configuration
- `dnb_public_register.yaml` - DNB Public Register configuration

---

*Last Updated: October 24, 2025*
