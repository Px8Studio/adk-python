# BigQuery Upload Guide - Multi-Datasource Edition

**Comprehensive guide for uploading any datasource to Google BigQuery using the Orkhon platform.**

---

## 📋 Overview

This guide covers uploading data from **any configured datasource** to BigQuery via Google Cloud Storage (GCS) staging using the **profile-based multi-datasource architecture**.

**Supported Datasources:**
- **DNB Statistics**: Economic and financial statistics (71 endpoints, time-series data)
- **DNB Public Register**: Regulated financial institutions and publications
- **Future**: EIOPA, World Bank, IMF, and custom datasources

**Key Features:**
- ✨ **Multi-Datasource Support** - One tool for all datasources
- 📝 **Configuration as Code** - YAML profiles define all settings
- 🔒 **Type-Safe Configuration** - Pydantic validation catches errors early
- 🚀 **Zero Code Changes** - Add new datasources by creating YAML files
- 📊 **Self-Documenting** - Profiles contain all metadata and configuration

**Pipeline Flow:**
```
Bronze Layer (Parquet files)
  ↓
Profile Loader (datasource_config.py)
  ↓
Configuration (profiles/{datasource}.yaml)
  ↓
Generic Orchestrator (upload_parquet.py)
  ↓
GCS Staging (gs://orkhon-{datasource}/bronze/)
  ↓
BigQuery Load Job
  ↓
BigQuery Tables ({datasource} dataset)
  ↓
Ready for Analysis (Data Science Agent, BI tools, etc.)
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

3. **Set default project**:
   ```powershell
   gcloud config set project your-project-id
   ```

### 2. Authentication

Choose one of these authentication methods:

**Option A: Service Account (Recommended for Production)**
```powershell
# Create service account
gcloud iam service-accounts create orkhon-uploader \
  --display-name="Orkhon Data Uploader"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:orkhon-uploader@your-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:orkhon-uploader@your-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:orkhon-uploader@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Download key
gcloud iam service-accounts keys create orkhon-uploader-key.json \
  --iam-account=orkhon-uploader@your-project-id.iam.gserviceaccount.com

# Set environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\orkhon-uploader-key.json"
```

**Option B: User Credentials (Simpler for Development)**
```powershell
gcloud auth application-default login
```

### 3. Environment Configuration

Only one environment variable is required:

```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
```

All other configuration (bucket names, dataset IDs, partitioning, clustering, etc.) is defined in the datasource profile.

### 4. Python Dependencies

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

### 1. List Available Datasources

See what datasources are configured:

```powershell
poetry run python -m backend.gcp.upload_parquet --list-datasources
```

Output:
```
Available datasources (2):
  • dnb_statistics               - DNB Statistics API
    Bucket: orkhon-dnb-statistics
    Dataset: dnb_statistics
  • dnb_public_register           - DNB Public Register API
    Bucket: orkhon-dnb-public-register
    Dataset: dnb_public_register
```

### 2. Setup Infrastructure

Create GCS bucket and BigQuery dataset for a datasource:

```powershell
# Setup everything
poetry run python -m backend.gcp.setup --datasource <datasource_id> --all

# Or individually
poetry run python -m backend.gcp.setup --datasource <datasource_id> --bucket
poetry run python -m backend.gcp.setup --datasource <datasource_id> --dataset
```

**Example:**
```powershell
poetry run python -m backend.gcp.setup --datasource dnb_statistics --all
```

### 3. Test with Dry Run

Preview what would be uploaded:

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource <datasource_id> --all --dry-run
```

### 4. Upload Data

```powershell
# Upload all data
poetry run python -m backend.gcp.upload_parquet --datasource <datasource_id> --all

# Upload specific category
poetry run python -m backend.gcp.upload_parquet --datasource <datasource_id> --category <category_name>

# List available files first
poetry run python -m backend.gcp.upload_parquet --datasource <datasource_id> --all --list
```

---

## 📊 Table Naming Conventions

Different datasources use different table naming conventions based on their data structure:

### **DNB Statistics: `double_underscore`**

**Format:** `{category}__{subcategory}__{endpoint}`

**Rationale:** DNB Statistics has a **hierarchical structure** with 3 levels:

```
insurance_pensions                    # Category
  ├── insurers                        # Subcategory
  │   ├── insurance_corps_balance_sheet_quarter   # Endpoint
  │   └── insurance_corps_solvency_quarter
  └── pension_funds                   # Subcategory
      ├── pension_funds_balance_sheet_quarter
      └── pension_funds_premiums_quarter
```

**Example Tables:**
- `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`
- `market_data__interest_rates__market_interest_rates_day`
- `macroeconomic__national_accounts__gdp_quarter`

**Benefits:**
- Clear hierarchical organization
- Easy to filter by category and subcategory
- Natural grouping for related datasets

### **DNB Public Register: `single_underscore`**

**Format:** `{category}_{filename}`

**Rationale:** DNB Public Register has a **flat structure** with 2 levels:

```
entities                              # Category
  ├── organizations_wftaf_nl          # Filename (already descriptive)
  ├── organizations_wft_nl
  └── organizations_pwpnf_nl
```

**Example Tables:**
- `entities_organizations_wftaf_nl`
- `publications_all_publications_nl`
- `metadata_registers`

**Benefits:**
- Simpler structure matches data organization
- Filenames are already descriptive
- Less redundancy in table names

### **Custom Datasources**

When creating a new datasource profile, choose the naming convention that matches your data structure:

```yaml
# In backend/gcp/profiles/my_datasource.yaml
pipeline:
  table_naming: double_underscore  # or single_underscore, hyphen
```

**Recommendation:**
- Use `double_underscore` for hierarchical data (multiple levels of categorization)
- Use `single_underscore` for flat data (simple category + filename)

---

## 📂 Schema Detection & Type Mapping

Schemas are auto-detected from parquet files with the following type mapping:

| Parquet Type | BigQuery Type |
|--------------|---------------|
| int64, int32 | INTEGER |
| float, double | FLOAT |
| string | STRING |
| bool | BOOLEAN |
| date | DATE |
| timestamp | TIMESTAMP |

**Auto-detection benefits:**
- No manual schema definition required
- Schemas evolve with your data
- Type-safe conversions

**Override if needed:**
```yaml
# In datasource profile
pipeline:
  schema:
    auto_detect: false  # Provide manual schema instead
```

---

## 🎯 Partitioning & Clustering

### **Time-Based Partitioning**

**When to use:** Time-series data with date/timestamp fields

**Example (DNB Statistics):**
```yaml
gcp:
  bigquery:
    table_defaults:
      partition_field: period  # Date field name
      partition_type: DAY      # DAY, HOUR, MONTH, YEAR
```

**Benefits:**
- Faster queries filtering by date
- Lower costs (only scans relevant partitions)
- Better organization for time-series data

**Example query:**
```sql
-- Only scans data from 2024
SELECT * FROM `project.dnb_statistics.market_data__interest_rates__market_interest_rates_day`
WHERE period >= '2024-01-01'
```

### **Clustering**

**When to use:** Frequently filtered or joined columns

**Example (DNB Public Register):**
```yaml
gcp:
  bigquery:
    table_defaults:
      clustering_fields:
        - register_code  # Frequently filtered column
```

**Benefits:**
- Faster queries filtering by clustered columns
- Lower costs (skips irrelevant data blocks)
- Better organization for dimensional data

**Example query:**
```sql
-- Only scans WFTAF register blocks
SELECT * FROM `project.dnb_public_register.entities_organizations_wftaf_nl`
WHERE register_code = 'WFTAF'
```

### **Best Practices**

1. **Partition on date fields** for time-series data
2. **Cluster on frequently filtered columns** (up to 4 columns)
3. **Order clustering fields** by cardinality (low to high)
4. **Test query performance** with `INFORMATION_SCHEMA.JOBS_BY_PROJECT`

---

## 🎯 Usage Examples

### List Available Files

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all --list
```

### Upload by Category

```powershell
# DNB Statistics categories
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --category insurance_pensions
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --category market_data

# DNB Public Register categories
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --category metadata
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --category entities
```

### Upload Specific Tables

```powershell
poetry run python -m backend.gcp.upload_parquet \
  --datasource dnb_statistics \
  --tables exchange_rates_day market_interest_rates_day
```

### Custom Configuration

Edit the datasource profile at `backend/gcp/profiles/{datasource}.yaml`:

```yaml
# Disable partitioning
gcp:
  bigquery:
    table_defaults:
      partition_field: null

# Add clustering
gcp:
  bigquery:
    table_defaults:
      clustering_fields:
        - category
        - subcategory

# Change write mode
gcp:
  bigquery:
    table_defaults:
      write_disposition: WRITE_APPEND  # Instead of WRITE_TRUNCATE
```

---

## 🔍 Verification

### Check Tables in BigQuery

**Via Command Line:**
```powershell
bq ls your-project-id:dnb_statistics
bq ls your-project-id:dnb_public_register
```

**Via Web Console:**
1. Open BigQuery console: https://console.cloud.google.com/bigquery
2. Navigate to your project → dataset
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

```powershell
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/bigquery.dataEditor"
```

### Bucket Not Found

**Error:** `Bucket gs://orkhon-{datasource} does not exist`

**Solution:** Create the bucket:
```powershell
poetry run python -m backend.gcp.setup --datasource <datasource_id> --bucket
```

### Dataset Not Found

**Error:** `Dataset {datasource} not found`

**Solution:** Create the dataset:
```powershell
poetry run python -m backend.gcp.setup --datasource <datasource_id> --dataset
```

### Schema Mismatch

**Error:** `Schema mismatch when loading data`

**Solution:** The upload script creates tables with auto-detected schemas. If you need to recreate a table:
```powershell
# Delete the table
bq rm -f your-project-id:datasource.table_name

# Re-upload
poetry run python -m backend.gcp.upload_parquet --datasource <datasource_id> --tables table_name
```

### Partition Field Not Found

**Error:** `Field 'period' not found in schema`

**Solution:** Not all tables have the partition field. Either:
1. Disable partitioning for specific tables
2. Update the profile to set `partition_field: null`

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
- Choose appropriate storage class (Standard, Nearline, Coldline)

---

## 🔄 Maintenance

### Re-uploading Data

The upload script uses `WRITE_TRUNCATE` by default, which replaces existing table data. To append instead:

1. Modify the datasource profile:
   ```yaml
   gcp:
     bigquery:
       table_defaults:
         write_disposition: WRITE_APPEND
   ```

2. Or override per upload (future enhancement)

### Updating Schemas

If your parquet schema changes:

1. Delete the existing BigQuery table:
   ```powershell
   bq rm -f your-project-id:datasource.table_name
   ```

2. Re-upload with the new schema:
   ```powershell
   poetry run python -m backend.gcp.upload_parquet --datasource <datasource_id> --tables table_name
   ```

### Cleaning Up

**Remove GCS staging files:**
```powershell
gsutil rm -r gs://orkhon-{datasource}/bronze/
```

**Delete dataset (and all tables):**
```powershell
bq rm -r -f your-project-id:datasource
```

**Delete bucket:**
```powershell
gsutil rm -r gs://orkhon-{datasource}
```

---

## 🆕 Adding New Datasources

### 1. Create Profile

```powershell
poetry run python -m backend.gcp.upload_parquet --create-profile my_datasource
```

This creates `backend/gcp/profiles/my_datasource.yaml` with a template.

### 2. Edit Profile

Open the YAML file and customize:

```yaml
datasource:
  id: my_datasource
  name: "My Data Source"
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
      partition_field: date  # If time-series data
      partition_type: DAY
      clustering_fields: []  # If dimensional data
      
  storage:
    bucket_name: orkhon-my-datasource
    location: us-central1

pipeline:
  bronze_path: my_datasource
  table_naming: single_underscore  # or double_underscore

categories:
  - category1
  - category2
```

### 3. Setup Infrastructure

```powershell
poetry run python -m backend.gcp.setup --datasource my_datasource --all
```

### 4. Upload Data

```powershell
poetry run python -m backend.gcp.upload_parquet --datasource my_datasource --all
```

No code changes needed!

---

## 📚 References

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [BigQuery Data Loading Best Practices](https://cloud.google.com/bigquery/docs/best-practices-data-import)
- [BigQuery Partitioning and Clustering](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Multi-Datasource Architecture](../MULTI_DATASOURCE_ARCHITECTURE.md)
- [Profile System Documentation](../profiles/README.md)
- [GCP Infrastructure Management](../README.md)

---

## 🔗 Datasource-Specific Guides

For datasource-specific quick starts and examples:
- [DNB Statistics Quick Start](../../etl/dnb_statistics/QUICKSTART.md)
- [DNB Public Register Quick Start](../../etl/dnb_public_register/QUICKSTART.md)

---

## 🐛 Issues & Support

If you encounter issues:

1. Check the logs in `backend/logs/bigquery_upload.log`
2. Verify environment variables in `.env`
3. Review GCP IAM permissions
4. Check BigQuery quotas and limits
5. Validate datasource profile with `--list-datasources`

For questions or improvements, open an issue in the project repository.

---

**Status**: ✅ Ready for Production Use (Multi-Datasource v2.0)
**Version**: 2.0.0
**Last Updated**: October 24, 2025
**Architecture**: Profile-based multi-datasource system
