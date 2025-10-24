# BigQuery Upload Guide - Multi-Datasource Edition

Upload parquet files from any datasource to Google BigQuery using the profile-based orchestrator.

---

## 📋 Overview

This guide covers uploading data from **any configured datasource** to BigQuery via Google Cloud Storage (GCS) staging using the new **profile-based multi-datasource architecture**.

**What's New in v2.0:**
- ✨ **Multi-Datasource Support** - One tool for all datasources (DNB Statistics, EIOPA, World Bank, etc.)
- 📝 **Configuration as Code** - YAML profiles define all datasource settings
- 🔒 **Type-Safe Configuration** - Pydantic validation catches errors early
- 🚀 **Zero Code Changes** - Add new datasources by creating YAML files
- 📊 **Self-Documenting** - Profiles contain all metadata and configuration

**Pipeline Flow:**
```
Bronze Layer (Parquet)
  ↓ Profile Loader (datasource_config.py)
Configuration (profiles/datasource.yaml)
  ↓ Generic Orchestrator (upload_parquet.py)
GCS Staging (gs://orkhon-{datasource}/bronze/)
  ↓ BigQuery Load Job
BigQuery Tables ({datasource} dataset)
  ↓ Ready for Analysis
Data Science Agent
```

---

## ⚙️ Prerequisites

### 1. Google Cloud Project Setup

1. **Create or select a GCP project**:
   ```powershell
   gcloud projects list
   # Or create new
   gcloud projects create your-project-id
   ```

2. **Enable required APIs**:
   ```powershell
   gcloud services enable bigquery.googleapis.com storage.googleapis.com
   ```

3. **Create GCS bucket** (if it doesn't exist):
   ```powershell
   gsutil mb -p your-project-id -l us-central1 gs://dnb-data
   ```

4. **Create BigQuery dataset**:
   ```powershell
   bq mk --dataset --location=us-central1 your-project-id:dnb_statistics
   ```

### 2. Authentication

Choose one of these authentication methods:

**Option A: Service Account (Recommended for Production)**
```powershell
# Create service account
gcloud iam service-accounts create dnb-uploader

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:dnb-uploader@your-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:dnb-uploader@your-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:dnb-uploader@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Download key
gcloud iam service-accounts keys create dnb-uploader-key.json \
  --iam-account=dnb-uploader@your-project-id.iam.gserviceaccount.com

# Set environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\dnb-uploader-key.json"
```

**Option B: User Credentials (Simpler for Development)**
```powershell
gcloud auth application-default login
```

### 3. Python Dependencies

Install the required packages:

```powershell
poetry install
```

This installs:
- `google-cloud-bigquery` - BigQuery client
- `google-cloud-storage` - GCS client
- `pyarrow` - Parquet file handling
- `pandas` - Data manipulation

---

## 🚀 Quick Start

> **Note:** This guide uses the new profile-based multi-datasource architecture. All datasources are configured via YAML profiles in `backend/gcp/profiles/`.

### 1. List Available Datasources

See what datasources are configured:

```powershell
poetry run python -m backend.gcp.upload_parquet --list-datasources
```

Output:
```
Available datasources (1):
  • dnb_statistics               - DNB Statistics API
    Bucket: orkhon-dnb-statistics
    Dataset: dnb_statistics
```

### 2. Configure Environment

Only one environment variable is required:

```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
```

All other configuration (bucket names, dataset IDs, partitioning, etc.) is defined in the datasource profile.

### 3. Setup Infrastructure

Create GCS bucket and BigQuery dataset for a datasource:

```powershell
# Setup everything
poetry run python -m backend.gcp.setup --datasource dnb_statistics --all

# Or individually
poetry run python -m backend.gcp.setup --datasource dnb_statistics --bucket
poetry run python -m backend.gcp.setup --datasource dnb_statistics --dataset
```

### 4. Test with Dry Run

Preview what would be uploaded:

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all --dry-run
```

Or use the VS Code task: **📊 BigQuery: Dry Run (Preview Upload)**

### 5. Upload a Single Category (Recommended First Step)

Start with a smaller category to verify everything works:

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --category market_data
```

Or use the VS Code task: **📊 BigQuery: Upload Category (Market Data)**

### 6. Upload All Data

Once verified, upload everything:

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all
```

Or use the VS Code task: **📊 BigQuery: Upload All DNB Statistics**

---

## 📊 Table Structure

### Naming Convention

Tables follow the pattern:
```
{category}__{subcategory}__{endpoint_name}
```

**Examples:**
- `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`
- `market_data__interest_rates__market_interest_rates_day`
- `macroeconomic__national_accounts__gdp_quarter`

### Schema

Schemas are auto-detected from parquet files with type mapping:

| Parquet Type | BigQuery Type |
|--------------|---------------|
| int64, int32 | INTEGER |
| float, double | FLOAT |
| string | STRING |
| bool | BOOLEAN |
| date | DATE |
| timestamp | TIMESTAMP |

### Partitioning & Clustering

**Default Configuration:**
- **Partitioned by:** `period` field (day-level partitioning)
- **Clustered by:** None (configurable via `BQ_CLUSTERING_FIELDS`)

**Benefits:**
- Faster queries filtering by date
- Lower costs (only scans relevant partitions)
- Better organization for time-series data

---

## 🎯 Usage Examples

### List Available Files

See what parquet files are ready to upload:

```powershell
poetry run python -m backend.gcp.upload_dnb_statistics --all --list
```

### Upload Specific Tables

Upload only specific endpoints:

```powershell
poetry run python -m backend.gcp.upload_dnb_statistics --tables exchange_rates_day market_interest_rates_day
```

### Upload by Category

Upload all tables in a category:

```powershell
# Insurance & Pensions
poetry run python -m backend.gcp.upload_dnb_statistics --category insurance_pensions

# Market Data
poetry run python -m backend.gcp.upload_dnb_statistics --category market_data

# Macroeconomic
poetry run python -m backend.gcp.upload_dnb_statistics --category macroeconomic
```

### Custom Configuration

Edit the datasource profile at `backend/gcp/profiles/dnb_statistics.yaml`:

```yaml
# Disable partitioning
gcp:
  bigquery:
    table_defaults:
      partition_field: null  # Disable partitioning

# Add clustering
gcp:
  bigquery:
    table_defaults:
      clustering_fields:
        - category
        - subcategory
```

---

## 🆕 Adding New Datasources

### 1. Create Profile

```powershell
poetry run python -m backend.gcp.upload_parquet --create-profile eiopa_data
```

This creates `backend/gcp/profiles/eiopa_data.yaml` with a template.

### 2. Edit Profile

Open the YAML file and customize:

```yaml
datasource:
  id: eiopa_data
  name: "EIOPA Insurance Data"
  description: "European Insurance and Occupational Pensions Authority datasets"
  provider: "EIOPA"
  source_url: "https://www.eiopa.europa.eu"

gcp:
  bigquery:
    dataset_id: eiopa_data
    location: eu-west1  # EU data stored in EU
    labels:
      datasource: eiopa
      provider: eiopa
      project: orkhon
  
  storage:
    bucket_name: orkhon-eiopa-data
    location: eu-west1

pipeline:
  bronze_path: eiopa_data
  table_naming: double_underscore
  schema_config:
    auto_detect: true
  quality:
    require_partition_field: true

categories:
  - solvency_ii
  - statistical_returns
  - stress_tests
```

### 3. Setup Infrastructure

```powershell
poetry run python -m backend.gcp.setup --datasource eiopa_data --all
```

### 4. Upload Data

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource eiopa_data --all
```

No code changes needed!

---

## 🔍 Verification

### Check Tables in BigQuery

**Via Command Line:**
```powershell
bq ls your-project-id:dnb_statistics
```

**Via Web Console:**
1. Open BigQuery console: https://console.cloud.google.com/bigquery
2. Navigate to your project → `dnb_statistics` dataset
3. Browse tables

**Via Data Science Agent:**
```powershell
python backend/adk/run_data_science_agent.py --query "What tables are available?"
```

### Query Sample Data

**Via Command Line:**
```powershell
bq query --use_legacy_sql=false "
SELECT * FROM \`your-project-id.dnb_statistics.market_data__interest_rates__market_interest_rates_day\`
LIMIT 10
"
```

**Via Data Science Agent:**
```powershell
python backend/adk/run_data_science_agent.py --query "Show me the top 10 records from market interest rates"
```

---

## 🛠️ Troubleshooting

### Authentication Errors

**Error:** `Could not automatically determine credentials`

**Solution:** Set up authentication:
```powershell
gcloud auth application-default login
# Or set service account key
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\key.json"
```

### Permission Denied

**Error:** `Permission denied on dataset/bucket`

**Solution:** Ensure your account/service account has required roles:
- `roles/bigquery.dataEditor`
- `roles/bigquery.jobUser`
- `roles/storage.admin`

### Bucket Not Found

**Error:** `Bucket gs://dnb-data does not exist`

**Solution:** Create the bucket:
```powershell
gsutil mb -p your-project-id -l us-central1 gs://dnb-data
```

### Dataset Not Found

**Error:** `Dataset dnb_statistics not found`

**Solution:** Create the dataset:
```powershell
bq mk --dataset --location=us-central1 your-project-id:dnb_statistics
```

### Schema Mismatch

**Error:** `Schema mismatch when loading data`

**Solution:** The upload script creates tables with auto-detected schemas. If you need to recreate a table:
```powershell
# Delete the table
bq rm -f your-project-id:dnb_statistics.table_name

# Re-upload
poetry run python -m backend.etl.dnb_statistics.upload_to_bigquery --tables table_name
```

---

## 📈 Monitoring & Costs

### Monitor Upload Progress

Check the terminal output for:
- Upload status per file
- Row counts
- Data sizes
- GCS URIs
- BigQuery table references

### Check BigQuery Job History

View load jobs in the console:
```
https://console.cloud.google.com/bigquery?project=your-project-id&page=jobs
```

### Estimate Costs

**Storage Costs:**
- Active storage: $0.020 per GB/month
- Long-term storage (90+ days): $0.010 per GB/month

**Query Costs:**
- On-demand: $6.25 per TB scanned
- Flat-rate: $2,000/month for 100 slots (for heavy usage)

**Load Jobs:**
- Free (no charges for loading data)

**Data Transfer:**
- GCS → BigQuery in same region: Free
- Cross-region: $0.01-0.08 per GB

**Cost Optimization Tips:**
- Use partitioned tables to reduce scan volumes
- Filter by partition key in queries
- Use clustering for frequently filtered columns
- Set up dataset expiration for temporary tables

---

## 🔄 Maintenance

### Re-uploading Data

The upload script uses `WRITE_TRUNCATE` by default, which replaces existing table data. To append instead:

1. Modify `bigquery_upload.py`:
   ```python
   write_disposition = "WRITE_APPEND"
   ```

2. Or add a CLI flag (future enhancement)

### Updating Schemas

If your parquet schema changes:

1. Delete the existing BigQuery table:
   ```powershell
   bq rm -f your-project-id:dnb_statistics.table_name
   ```

2. Re-upload with the new schema:
   ```powershell
   poetry run python -m backend.gcp.upload_dnb_statistics --tables table_name
   ```

### Cleaning Up

**Remove GCS staging files:**
```powershell
gsutil rm -r gs://dnb-data/bronze/
```

**Delete dataset (and all tables):**
```powershell
bq rm -r -f your-project-id:dnb_statistics
```

---

## 🎯 Next Steps

After successfully uploading your data:

1. **Test the Data Science Agent:**
   ```powershell
   python backend/adk/run_data_science_agent.py
   ```

2. **Create Views for Common Queries:**
   - Aggregate views across related tables
   - Union views for time-series continuity
   - Materialized views for frequently accessed data

3. **Set Up Monitoring:**
   - Create dashboards in Looker Studio
   - Set up BigQuery scheduled queries
   - Configure Data Catalog for data discovery

4. **Optimize for Production:**
   - Enable table expiration for temporary tables
   - Set up automated ETL → Upload pipeline
   - Configure IAM policies for team access
   - Add data quality checks

---

## 📚 References

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [BigQuery Data Loading Best Practices](https://cloud.google.com/bigquery/docs/best-practices-data-import)
- [BigQuery Partitioning and Clustering](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Orkhon Architecture Documentation](../ARCHITECTURE_ENHANCEMENTS.md)

---

## 🐛 Issues & Support

If you encounter issues:

1. Check the logs in `backend/logs/bigquery_upload.log`
2. Verify environment variables in `.env`
3. Review GCP IAM permissions
4. Check BigQuery quotas and limits

For questions or improvements, open an issue in the project repository.

---

## 📖 Profile System Documentation

For detailed documentation on the profile system, see:
- `backend/gcp/profiles/README.md` - Comprehensive profile guide
- `backend/gcp/MULTI_DATASOURCE_ARCHITECTURE.md` - Architecture overview
- `backend/gcp/datasource_config.py` - Configuration loader implementation

---

**Status**: ✅ Ready for Production Use (Multi-Datasource v2.0)
**Version**: 2.0.0
**Last Updated**: October 24, 2025
**Migration**: Phase 2 Complete - DNB Statistics migrated to profile system
