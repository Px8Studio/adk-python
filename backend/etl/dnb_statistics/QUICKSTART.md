# DNB Statistics - BigQuery Quick Start

**5-minute guide to upload DNB Statistics data to BigQuery.**

📖 **For comprehensive documentation**, see the [Central BigQuery Upload Guide](../../gcp/docs/BIGQUERY_UPLOAD.md).

---

## 🚀 Quick Start

### 1. Prerequisites

- ✅ GCP project configured
- ✅ Authentication set up (`gcloud auth application-default login`)
- ✅ DNB Statistics data extracted (`python -m backend.etl.dnb_statistics.orchestrator --all`)

### 2. Setup Infrastructure

```powershell
poetry run python -m backend.gcp.setup --datasource dnb_statistics --all
```

This creates:
- GCS bucket: `orkhon-dnb-statistics`
- BigQuery dataset: `dnb_statistics`

### 3. Upload Data

```powershell
# Upload everything
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all

# Or upload by category
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --category insurance_pensions
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --category market_data
```

### 4. Verify

```powershell
# List tables
bq ls your-project-id:dnb_statistics

# Query sample data
bq query --use_legacy_sql=false "
SELECT * FROM \`your-project-id.dnb_statistics.market_data__interest_rates__market_interest_rates_day\`
LIMIT 10
"
```

---

## 📊 Data Structure

### Table Naming: `double_underscore`

DNB Statistics uses hierarchical naming:

```
{category}__{subcategory}__{endpoint}
```

**Examples:**
- `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`
- `market_data__interest_rates__market_interest_rates_day`
- `macroeconomic__national_accounts__gdp_quarter`

**Why 3 levels?** DNB Statistics has a hierarchical structure:
```
insurance_pensions (category)
  ├── insurers (subcategory)
  │   ├── insurance_corps_balance_sheet_quarter (endpoint)
  │   └── insurance_corps_solvency_quarter
  └── pension_funds (subcategory)
      └── pension_funds_balance_sheet_quarter
```

### Partitioning & Clustering

**Partitioned by:** `period` field (daily granularity)
- Faster queries filtering by date
- Lower costs (only scans relevant partitions)

**Example query leveraging partitioning:**
```sql
SELECT * FROM `project.dnb_statistics.market_data__interest_rates__market_interest_rates_day`
WHERE period >= '2024-01-01'  -- Only scans 2024 data
```

---

## 📂 Categories

- `insurance_pensions` - Insurance companies and pension funds
- `market_data` - Exchange rates, interest rates, ECB rates
- `macroeconomic` - Balance of payments, FDI, national accounts
- `payment_systems` - Payment transactions and infrastructure

---

## 🎯 Common Commands

```powershell
# List available datasources
poetry run python -m backend.gcp.upload_parquet --list-datasources

# List available files
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all --list

# Dry run (preview)
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all --dry-run

# Upload specific tables
poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --tables exchange_rates_day market_interest_rates_day
```

---

## 🔧 VS Code Tasks

Convenient tasks are available in VS Code:
- **📊 BigQuery: Upload All DNB Statistics**
- **📊 BigQuery: Upload Category (Insurance & Pensions)**
- **📊 BigQuery: Upload Category (Market Data)**
- **📊 BigQuery: List Available Files**
- **📊 BigQuery: Dry Run (Preview Upload)**

---

## 🛠️ Troubleshooting

See the [Central BigQuery Upload Guide - Troubleshooting Section](../../gcp/docs/BIGQUERY_UPLOAD.md#-troubleshooting).

**Common issues:**
- **Authentication errors**: Run `gcloud auth application-default login`
- **Bucket not found**: Run `poetry run python -m backend.gcp.setup --datasource dnb_statistics --bucket`
- **No parquet files**: Extract data first with `python -m backend.etl.dnb_statistics.orchestrator --all`

---

## 📚 Learn More

- [Central BigQuery Upload Guide](../../gcp/docs/BIGQUERY_UPLOAD.md) - Comprehensive documentation
- [Multi-Datasource Architecture](../../gcp/docs/MULTI_DATASOURCE_ARCHITECTURE.md) - System design
- [Profile Configuration](../../gcp/profiles/dnb_statistics.yaml) - Datasource settings
- [DNB Statistics ETL README](./README.md) - Extraction documentation

---

**Datasource**: DNB Statistics  
**Dataset ID**: `dnb_statistics`  
**Bucket**: `orkhon-dnb-statistics`  
**Table Naming**: `double_underscore` (hierarchical)  
**Partitioning**: By `period` field (DAY)
