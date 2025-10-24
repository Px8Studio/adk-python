# DNB Public Register - BigQuery Quick Start

**5-minute guide to upload DNB Public Register data to BigQuery.**

📖 **For comprehensive documentation**, see the [Central BigQuery Upload Guide](../../gcp/docs/BIGQUERY_UPLOAD.md).

---

## 🚀 Quick Start

### 1. Prerequisites

- ✅ GCP project configured
- ✅ Authentication set up (`gcloud auth application-default login`)
- ✅ DNB Public Register data extracted (`python -m backend.etl.dnb_public_register.orchestrator --all`)

### 2. Setup Infrastructure

```powershell
poetry run python -m backend.gcp.setup --datasource dnb_public_register --all
```

This creates:
- GCS bucket: `orkhon-dnb-public-register`
- BigQuery dataset: `dnb_public_register`

### 3. Upload Data

```powershell
# Upload everything
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --all

# Or upload by category
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --category metadata
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --category entities
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --category publications
```

### 4. Verify

```powershell
# List tables
bq ls your-project-id:dnb_public_register

# Query sample data
bq query --use_legacy_sql=false "
SELECT * FROM \`your-project-id.dnb_public_register.entities_organizations_wftaf_nl\`
LIMIT 10
"
```

---

## 📊 Data Structure

### Table Naming: `single_underscore`

DNB Public Register uses flat naming:

```
{category}_{filename}
```

**Examples:**
- `metadata_registers`
- `entities_organizations_wftaf_nl`
- `publications_all_publications_nl`
- `regulatory_register_articles_wftaf_nl`

**Why 2 levels?** DNB Public Register has a flat structure:
```
entities (category)
  ├── organizations_wftaf_nl (filename - already descriptive)
  ├── organizations_wft_nl
  └── organizations_pwpnf_nl
```

### Clustering

**Clustered by:** `register_code` (for efficient filtering by register)
- Faster queries filtering by register (e.g., WFTAF, WFT)
- Lower costs (only scans relevant data blocks)

**Example query leveraging clustering:**
```sql
SELECT * FROM `project.dnb_public_register.entities_organizations_wftaf_nl`
WHERE register_code = 'WFTAF'  -- Only scans WFTAF blocks
```

---

## 📂 Categories

- `metadata` - Registers and supported languages
- `entities` - Organizations (regulated financial institutions)
- `publications` - Financial institution publications
- `registrations` - Registration details and act article names
- `regulatory` - Register articles (regulatory framework)

---

## 🎯 Common Commands

```powershell
# List available datasources
poetry run python -m backend.gcp.upload_parquet --list-datasources

# List available files
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --all --list

# Dry run (preview)
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --all --dry-run

# Upload specific tables
poetry run python -m backend.gcp.upload_parquet --datasource dnb_public_register --tables registers organizations_wftaf_nl
```

---

## 🔧 VS Code Tasks

Convenient tasks are available in VS Code:
- **📊 BigQuery: Upload All DNB Public Register**
- **📊 BigQuery: Upload Metadata (DNB Public Register)**
- **📊 BigQuery: Upload Entities (DNB Public Register)**
- **📊 BigQuery: Upload Publications (DNB Public Register)**
- **📊 BigQuery: List Available Files (DNB Public Register)**
- **📊 BigQuery: Dry Run DNB Public Register**

---

## 🛠️ Troubleshooting

See the [Central BigQuery Upload Guide - Troubleshooting Section](../../gcp/docs/BIGQUERY_UPLOAD.md#-troubleshooting).

**Common issues:**
- **Authentication errors**: Run `gcloud auth application-default login`
- **Bucket not found**: Run `poetry run python -m backend.gcp.setup --datasource dnb_public_register --bucket`
- **No parquet files**: Extract data first with `python -m backend.etl.dnb_public_register.orchestrator --all`
- **Missing register_code field**: Metadata tables don't have `register_code`, upload them separately

---

## 📊 Example Queries

**Count organizations by register:**
```sql
SELECT 
  register_code,
  COUNT(*) AS organization_count
FROM `your-project-id.dnb_public_register.entities_*`
GROUP BY register_code
ORDER BY organization_count DESC
```

**Find recent publications:**
```sql
SELECT 
  organization_name,
  publication_date,
  register_code
FROM `your-project-id.dnb_public_register.publications_all_publications_nl`
WHERE publication_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY publication_date DESC
LIMIT 20
```

**Explore regulatory framework:**
```sql
SELECT 
  register_code,
  COUNT(DISTINCT act_article_code) AS article_count
FROM `your-project-id.dnb_public_register.regulatory_*`
GROUP BY register_code
```

---

## 📚 Learn More

- [Central BigQuery Upload Guide](../../gcp/docs/BIGQUERY_UPLOAD.md) - Comprehensive documentation
- [Multi-Datasource Architecture](../../gcp/docs/MULTI_DATASOURCE_ARCHITECTURE.md) - System design
- [Profile Configuration](../../gcp/profiles/dnb_public_register.yaml) - Datasource settings
- [DNB Public Register ETL README](./README.md) - Extraction documentation

---

**Datasource**: DNB Public Register  
**Dataset ID**: `dnb_public_register`  
**Bucket**: `orkhon-dnb-public-register`  
**Table Naming**: `single_underscore` (flat)  
**Clustering**: By `register_code`
