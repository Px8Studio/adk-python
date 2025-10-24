# GCP Infrastructure Management

Python-based utilities for managing Google Cloud Platform resources programmatically for the Orkhon project.

## 📚 Overview

This package provides professional-grade GCP management tools following Python best practices:

- **Type-safe clients** with proper error handling
- **Cross-platform** - works on Windows, macOS, Linux
- **Testable** - modular design for unit testing
- **Reusable** - import as library or use as CLI
- **Well-documented** - comprehensive docstrings

## 🏗️ Architecture

```
backend/gcp/
├── __init__.py           # Package exports
├── auth.py               # Authentication manager
├── storage_manager.py    # GCS operations
├── bigquery_manager.py   # BigQuery operations
├── setup.py              # CLI setup script
└── README.md             # This file
```

### Why Python over Shell Scripts?

| Feature | Python | PowerShell/Bash |
|---------|--------|-----------------|
| **Cross-platform** | ✅ Yes | ❌ No |
| **Type safety** | ✅ Yes | ❌ Limited |
| **Error handling** | ✅ Robust | ⚠️ Basic |
| **Testing** | ✅ Easy | ⚠️ Difficult |
| **Reusability** | ✅ Import as library | ❌ Script only |
| **IDE support** | ✅ Full autocomplete | ⚠️ Limited |
| **Google Cloud SDK** | ✅ Official client libs | ⚠️ CLI wrappers |

---

## 🚀 Quick Start

### 1. Setup Authentication

**Option A: Application Default Credentials (Recommended for Development)**
```powershell
# Authenticate with your Google account
gcloud auth application-default login

# Set default project
gcloud config set project your-project-id
```

**Option B: Service Account (Recommended for Production)**
```powershell
# Set environment variable pointing to key file
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

### 2. Configure Environment

Edit `.env` file:
```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GCS_BUCKET=dnb-data
BQ_DATASET_ID=dnb_statistics
```

### 3. Setup Infrastructure

```powershell
# Setup everything (bucket + dataset)
python -m backend.gcp.setup --all

# Or setup individually
python -m backend.gcp.setup --bucket    # GCS bucket only
python -m backend.gcp.setup --dataset   # BigQuery dataset only

# Validate setup
python -m backend.gcp.setup --validate
```

---

## 📦 Module Reference

### GCPAuth

**Purpose**: Centralized authentication management

```python
from backend.gcp import GCPAuth

# Auto-detect credentials (ADC or service account)
auth = GCPAuth()

# Explicit service account
auth = GCPAuth(service_account_path="path/to/key.json")

# Get credentials and project
credentials = auth.get_credentials()
project_id = auth.get_project_id()

# Validate
auth.validate()
```

**Authentication Priority**:
1. Explicit `credentials` parameter
2. Service account JSON file
3. Application Default Credentials (ADC)

---

### StorageManager

**Purpose**: Manage Google Cloud Storage buckets and objects

```python
from backend.gcp import GCPAuth, StorageManager

auth = GCPAuth()
storage = StorageManager(auth)

# Create bucket
storage.create_bucket(
    "my-bucket",
    location="us-central1",
    storage_class="STANDARD",
    labels={"project": "orkhon"}
)

# Upload file
storage.upload_file(
    local_path="data/file.parquet",
    bucket_name="my-bucket",
    blob_path="data/file.parquet"
)

# Download file
storage.download_file(
    bucket_name="my-bucket",
    blob_path="data/file.parquet",
    local_path="downloads/file.parquet"
)

# List objects
objects = storage.list_objects("my-bucket", prefix="data/")

# Check existence
exists = storage.bucket_exists("my-bucket")
exists = storage.object_exists("my-bucket", "data/file.parquet")

# Delete
storage.delete_object("my-bucket", "data/file.parquet")
storage.delete_bucket("my-bucket", force=True)

# Get info
info = storage.get_bucket_info("my-bucket")
```

---

### BigQueryManager

**Purpose**: Manage BigQuery datasets, tables, and queries

```python
from backend.gcp import GCPAuth, BigQueryManager
from google.cloud import bigquery

auth = GCPAuth()
bq = BigQueryManager(auth, location="us-central1")

# Create dataset
bq.create_dataset(
    "my_dataset",
    description="My dataset",
    labels={"project": "orkhon"}
)

# Create table with schema
schema = [
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("age", "INTEGER"),
    bigquery.SchemaField("date", "DATE"),
]

bq.create_table(
    "my_dataset",
    "my_table",
    schema=schema,
    partition_field="date",
    clustering_fields=["name"],
)

# Load data from GCS
bq.load_table_from_gcs(
    gcs_uri="gs://my-bucket/data.parquet",
    dataset_id="my_dataset",
    table_id="my_table",
    source_format="PARQUET",
    write_disposition="WRITE_TRUNCATE",
)

# Execute query
query_job = bq.execute_query("SELECT * FROM my_dataset.my_table LIMIT 10")

# Dry run (cost estimation)
cost_estimate = bq.execute_query(
    "SELECT * FROM my_dataset.my_table",
    dry_run=True
)
print(f"Estimated cost: ${cost_estimate['cost_estimate_usd']:.4f}")

# List resources
datasets = bq.list_datasets()
tables = bq.list_tables("my_dataset")

# Check existence
exists = bq.dataset_exists("my_dataset")
exists = bq.table_exists("my_dataset", "my_table")

# Get info
dataset_info = bq.get_dataset_info("my_dataset")
table_info = bq.get_table_info("my_dataset", "my_table")

# Delete
bq.delete_table("my_dataset", "my_table")
bq.delete_dataset("my_dataset", delete_contents=True)

# Validate
bq.validate_configuration()
```

---

## 🎯 Use Cases

### 1. Setup Infrastructure Programmatically

```python
from backend.gcp import GCPAuth, StorageManager, BigQueryManager

# Authenticate
auth = GCPAuth()

# Setup storage
storage = StorageManager(auth)
storage.create_bucket("dnb-data", location="us-central1")

# Setup BigQuery
bq = BigQueryManager(auth)
bq.create_dataset("dnb_statistics")

print("✓ Infrastructure ready!")
```

### 2. Automate Data Upload

```python
from pathlib import Path
from backend.gcp import GCPAuth, StorageManager, BigQueryManager

auth = GCPAuth()
storage = StorageManager(auth)
bq = BigQueryManager(auth)

# Upload parquet to GCS
bronze_files = Path("backend/data/1-bronze/dnb_statistics").rglob("*.parquet")

for file_path in bronze_files:
    # Upload to GCS
    gcs_uri = storage.upload_file(
        local_path=file_path,
        bucket_name="dnb-data",
        blob_path=f"bronze/{file_path.name}"
    )
    
    # Load into BigQuery
    table_id = file_path.stem.replace("-", "_")
    
    bq.load_table_from_gcs(
        gcs_uri=gcs_uri,
        dataset_id="dnb_statistics",
        table_id=table_id,
    )
    
    print(f"✓ Loaded {table_id}")
```

### 3. Cost Estimation Before Query

```python
from backend.gcp import GCPAuth, BigQueryManager

auth = GCPAuth()
bq = BigQueryManager(auth)

query = """
SELECT *
FROM `dnb_statistics.market_data__interest_rates__market_interest_rates_day`
WHERE period >= '2024-01-01'
"""

# Dry run to estimate cost
estimate = bq.execute_query(query, dry_run=True)

print(f"Query will process {estimate['gb_processed']:.2f} GB")
print(f"Estimated cost: ${estimate['cost_estimate_usd']:.4f}")

# Execute if cost is acceptable
if estimate['cost_estimate_usd'] < 1.0:
    query_job = bq.execute_query(query)
    print("✓ Query executed")
else:
    print("⚠️ Query too expensive, please optimize")
```

---

## 🛠️ VS Code Integration

The following tasks are available (see `.vscode/tasks.json`):

- **☁️ GCP: Setup All Infrastructure** - Create bucket + dataset
- **☁️ GCP: Setup Storage Only** - Create GCS bucket
- **☁️ GCP: Setup BigQuery Only** - Create BigQuery dataset
- **☁️ GCP: Validate Setup** - Check if everything is configured correctly

---

## 🔒 Security Best Practices

### 1. Never Commit Credentials

```gitignore
# .gitignore
*.json  # Service account keys
.env    # Environment variables
```

### 2. Use Service Accounts for Production

```powershell
# Create service account
gcloud iam service-accounts create orkhon-uploader

# Grant minimal required permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:orkhon-uploader@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=orkhon-uploader@PROJECT_ID.iam.gserviceaccount.com
```

### 3. Rotate Keys Regularly

- Set up key rotation policy (90 days)
- Use Workload Identity for GKE/Cloud Run
- Consider using Secret Manager for key storage

### 4. Least Privilege Principle

Grant only the permissions needed:

| Task | Required Roles |
|------|---------------|
| Upload data | `storage.objectCreator`, `bigquery.jobUser` |
| Query data | `bigquery.dataViewer`, `bigquery.jobUser` |
| Manage tables | `bigquery.dataEditor`, `bigquery.jobUser` |
| Manage datasets | `bigquery.dataOwner` |

---

## 📊 Cost Optimization

### Storage Costs

- **Standard storage**: $0.020/GB/month
- **Nearline storage**: $0.010/GB/month (access < 1/month)
- **Coldline storage**: $0.004/GB/month (access < 1/quarter)
- **Archive storage**: $0.0012/GB/month (access < 1/year)

```python
# Use lifecycle policies
storage.create_bucket(
    "my-bucket",
    lifecycle_rules=[{
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 90}
    }]
)
```

### BigQuery Costs

- **Storage**: $0.020/GB/month (active), $0.010/GB/month (long-term)
- **Queries**: $6.25/TB scanned (on-demand)

```python
# Always use dry_run to estimate
cost = bq.execute_query(query, dry_run=True)

# Use partitioning to reduce scan volume
bq.create_table(..., partition_field="date")

# Use clustering for filtering
bq.create_table(..., clustering_fields=["category", "type"])
```

---

## 🧪 Testing

```python
# tests/test_gcp_auth.py
from backend.gcp import GCPAuth

def test_auth_with_adc():
    auth = GCPAuth()
    credentials = auth.get_credentials()
    assert credentials is not None
    
    project_id = auth.get_project_id()
    assert project_id is not None
```

Run tests:
```powershell
pytest tests/test_gcp*.py
```

---

## 🐛 Troubleshooting

### Authentication Errors

**Error**: `Could not automatically determine credentials`

**Solution**:
```powershell
gcloud auth application-default login
```

### Permission Denied

**Error**: `Permission denied on bucket/dataset`

**Solution**: Grant required IAM roles
```powershell
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/bigquery.dataEditor"
```

### Quota Exceeded

**Error**: `Quota exceeded for quota metric 'Queries' and limit 'Queries per day'`

**Solution**: Request quota increase or use BigQuery reservation

---

## 📚 References

- [Google Cloud Python Client Libraries](https://cloud.google.com/python/docs/reference)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Cloud Storage Best Practices](https://cloud.google.com/storage/docs/best-practices)
- [IAM Roles Reference](https://cloud.google.com/iam/docs/understanding-roles)

---

## 🎯 Next Steps

1. **Setup infrastructure**: Run `python -m backend.gcp.setup --all`
2. **Upload data**: Use the BigQuery upload scripts in `backend/etl/dnb_statistics/`
3. **Test data science agent**: Run `python backend/adk/run_data_science_agent.py`

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: October 24, 2025
