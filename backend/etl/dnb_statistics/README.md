# DNB Statistics ETL Pipeline

Comprehensive ETL pipeline for extracting, transforming, and loading all financial statistics data from the DNB (De Nederlandsche Bank) Statistics API.

## Overview

This pipeline:
- ✅ Extracts data from **all DNB Statistics API endpoints** using the Kiota-generated client
- ✅ **Smart pagination**: Automatically detects truncated datasets and switches to full pagination
- ✅ **Completeness verification**: Tracks which datasets may be incomplete
- ✅ **Metadata tracking**: Maintains extraction history, timestamps, and data quality indicators
- ✅ **Incremental updates**: Supports date-based filtering for delta loads
- ✅ Applies rate limiting to stay under API limits
- ✅ Saves data in efficient **Parquet** format (analytics-ready)
- ✅ Organizes data by logical categories

## Architecture

### Components

```
dnb_statistics/
├── config.py             # Configuration (API keys, paths, settings)
├── base.py               # Base extractor classes with smart pagination
├── extractors.py         # Endpoint-specific extractors (17+ endpoints)
├── orchestrator.py       # Main coordination script
├── metadata.py           # Extraction metadata tracking
├── metadata_report.py    # Metadata query and reporting utility
└── README.md             # This file
```

### Data Flow

```
┌─────────────┐
│  DNB Stats  │  (API)
│     API     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Extractor  │  (Python + Kiota client)
│   Pipeline  │
└──────┬──────┘
       │
       └─► 1-bronze/    (Clean Parquet - analytics-ready)
```

### Data Storage Structure

```
backend/data/
└── 1-bronze/dnb_statistics/         # Clean Parquet files
    ├── market_data/
    │   ├── exchange_rates_day.parquet
    │   ├── market_interest_rates_day.parquet
    │   └── ...
    ├── macroeconomic/
    ├── financial_statements/
    ├── insurance_pensions/
    ├── investments/
    └── payments/
```

## Available Endpoints

✅ **ALL 71 ENDPOINTS IMPLEMENTED!** (100% coverage)

### Summary by Category

- **Market Data**: 8 endpoints (exchange rates, interest rates, ECB rates)
- **Macroeconomic**: 8 endpoints (balance of payments, FDI, monetary indicators)
- **Financial Statements**: 14 endpoints (banks, MFIs, other financial institutions)
- **Insurance & Pensions**: 17 endpoints (insurance corps, pension funds, premiums/claims)
- **Investments & Securities**: 16 endpoints (holdings, household investments, sustainable finance)
- **Loans & Mortgages**: 3 endpoints (securitisation, residential mortgages)
- **Payments**: 4 endpoints (transactions, infrastructure)
- **Other**: 1 endpoint (statutory interest rates)

### List All Available Endpoints
```bash
python -m backend.etl.dnb_statistics.orchestrator --list
```

This will show all 71 endpoints organized by category.

## Usage

### Prerequisites

1. **API Key**: Get your DNB API key from https://api.portal.dnb.nl/
2. **Set environment variable**:
   ```powershell
   $env:DNB_SUBSCRIPTION_KEY_DEV = "your-api-key-here"
   ```

3. **Install dependencies**:
   ```bash
   pip install pandas pyarrow httpx kiota-abstractions kiota-http
   ```

### Quick Start

**Extract everything:**
```bash
python -m backend.etl.dnb_statistics.orchestrator --all
```

**Extract specific endpoints:**
```bash
python -m backend.etl.dnb_statistics.orchestrator --endpoints exchange_rates_day market_interest_rates_day
```

**Extract by category:**
```bash
python -m backend.etl.dnb_statistics.orchestrator --category market_data
```

**List available endpoints:**
```bash
python -m backend.etl.dnb_statistics.orchestrator --list
```

**Dry run (preview):**
```bash
python -m backend.etl.dnb_statistics.orchestrator --all --dry-run
```

### Metadata Reporting

**View extraction metadata summary:**
```bash
python -m backend.etl.dnb_statistics.metadata_report
```

**Check for incomplete datasets:**
```bash
python -m backend.etl.dnb_statistics.metadata_report --incomplete
```

**Find stale datasets (not updated in 24h):**
```bash
python -m backend.etl.dnb_statistics.metadata_report --stale
```

**View details for specific endpoint:**
```bash
python -m backend.etl.dnb_statistics.metadata_report --endpoint exchange_rates_day
```

**Export metadata to JSON:**
```bash
python -m backend.etl.dnb_statistics.metadata_report --export metadata.json
```

### Using the Simple Runner

```bash
python backend/etl/run_dnb_stats_etl.py
```

## Configuration

Edit `config.py` to customize:

```python
# Pagination
DEFAULT_PAGE_SIZE = 2000  # Max allowed by DNB

# Rate Limiting
RATE_LIMIT_CALLS = 25    # Calls per period
RATE_LIMIT_PERIOD = 60.0  # Seconds

# Batch Processing
BATCH_SIZE = 10000  # Records per Parquet write

# Parquet Settings
PARQUET_COMPRESSION = "snappy"  # or "gzip", "brotli"
```

## Adding New Endpoints

1. **Check the Kiota client** for available endpoint properties in:
   ```
   backend/clients/dnb-statistics/dnb_statistics_client.py
   ```

2. **Create a new extractor** in `extractors.py`:
   ```python
   class MyNewDataExtractor(PaginatedExtractor):
       def get_category(self) -> str:
           return "market_data"  # Or appropriate category
       
       def get_output_filename(self) -> str:
           return "my_new_data"
       
       async def extract(self) -> AsyncIterator[dict[str, Any]]:
           async for record in self.extract_from_endpoint(
               "property_name_from_kiota_client"
           ):
               yield record
   ```

3. **Register it** in `EXTRACTOR_REGISTRY`:
   ```python
   EXTRACTOR_REGISTRY = {
       # ... existing extractors
       "my_new_data": MyNewDataExtractor,
   }
   ```

That's it! The orchestrator will automatically discover and run it.

## Features

### ✅ Smart Pagination & Completeness Verification
- **Automatic truncation detection**: Detects when a dataset hits the 2000-record limit
- **Intelligent pagination**: Automatically switches from single-request to full pagination when needed
- **Completeness tracking**: Flags datasets that may be incomplete for manual verification
- **Full data extraction**: Ensures you get ALL available data, not just the first 2000 records

### ✅ Metadata Tracking & History
- **Extraction history**: Tracks last 10 extractions per endpoint with timestamps
- **Data quality indicators**: Completeness flags, error tracking, and success rates
- **Staleness detection**: Identifies datasets that haven't been updated recently
- **Audit trail**: Complete history of when data was extracted and how much

### ✅ Incremental Updates
- **Date-based filtering**: Support for extracting only new/updated records
- **Delta loads**: Efficient incremental updates instead of full refreshes
- **Last extraction tracking**: Automatically determines if incremental update is appropriate

### ✅ Robust Error Handling
- Automatic retry with exponential backoff
- Graceful failure recovery
- Detailed error logging with metadata tracking

### ✅ Performance Optimized
- Single-request extraction when possible (pageSize=0 API feature)
- Fallback to pagination when necessary
- Batch writes to Parquet
- Efficient memory management

### ✅ Data Quality
- Adds ETL metadata to all records
- Type-safe Parquet schema
- Efficient columnar storage
- Completeness verification

### ✅ Monitoring & Reporting
- Real-time progress tracking
- Detailed statistics per endpoint
- Metadata reporting utilities
- Structured logs in `logs/etl_dnb_statistics.log`
- Built-in metadata JSON for programmatic access

## Output Format

### Parquet (1-bronze)
Columnar format optimized for analytics:
- Efficient compression (5-10x smaller than JSON)
- Fast filtering & aggregation
- Schema enforcement
- Compatible with Pandas, DuckDB, Spark, etc.
- Includes ETL metadata: `_etl_timestamp`, `_etl_source`

### Extraction Metadata
Located at: `backend/data/1-bronze/dnb_statistics/_extraction_metadata.json`

Tracks for each endpoint:
- **Last extraction timestamps**: When data was last fetched
- **Record counts**: How many records were extracted
- **Completeness status**: Whether the dataset appears complete or truncated
- **Extraction history**: Last 10 runs with duration, errors, and warnings
- **Data quality flags**: Indicators for incomplete or stale data

Example metadata entry:
```json
{
  "endpoint_name": "exchange_rates_day",
  "category": "market_data",
  "filename": "exchange_rates_day",
  "last_extraction": "2025-10-21T17:23:18.351Z",
  "total_records": 2000,
  "is_complete": false,
  "extraction_history": [
    {
      "timestamp": "2025-10-21T17:23:18.351Z",
      "total_records": 2000,
      "total_pages": 1,
      "is_complete": false,
      "completeness_notes": [
        "Dataset has exactly 2000 records - may be truncated at API limit"
      ],
      "duration_seconds": 1.66
    }
  ]
}
```

## Performance

**Typical extraction times:**
- Single endpoint (1K records): ~5 seconds
- Single endpoint (100K records): ~2 minutes
- All endpoints (~17): ~30-45 minutes
- Full refresh: Can be parallelized or scheduled incrementally

**Rate Limiting:**
- Conservative: 25 calls/minute (under DNB limit)
- Automatic backoff on 429 errors
- Configurable throttling

## Troubleshooting

### API Key Not Set
```
ValueError: DNB_SUBSCRIPTION_KEY_DEV environment variable must be set
```
**Solution:** Set the environment variable:
```powershell
$env:DNB_SUBSCRIPTION_KEY_DEV = "your-key"
```

### Rate Limit Errors (429)
**Solution:** The pipeline handles this automatically with exponential backoff. If persistent:
- Reduce `RATE_LIMIT_CALLS` in `config.py`
- Increase `RATE_LIMIT_BUFFER`

### Out of Memory
**Solution:** Reduce `BATCH_SIZE` in `config.py` to write smaller chunks.

### Missing Dependencies
```bash
pip install pandas pyarrow httpx kiota-abstractions kiota-http
```

### Incomplete Datasets Warning
If you see warnings about incomplete datasets (exactly 2000 records):
1. **Check the metadata report**:
   ```bash
   python -m backend.etl.dnb_statistics.metadata_report --incomplete
   ```
2. **The pipeline now automatically handles this** by switching to full pagination
3. **Re-run the extraction** and it will fetch all available data

## Working with Metadata

### Query Metadata Programmatically
```python
from backend.etl.dnb_statistics.metadata import ExtractionMetadata

metadata = ExtractionMetadata()

# Get incomplete endpoints
incomplete = metadata.get_incomplete_endpoints()
for item in incomplete:
    print(f"{item['endpoint']}: {item['total_records']} records")

# Get stale endpoints (>24h old)
stale = metadata.get_stale_endpoints(max_age_hours=24)

# Check if endpoint should use incremental
should_incr, last_time = metadata.should_extract_incremental(
    'exchange_rates_day',
    max_age_hours=24
)
```

### Reset Metadata
To start fresh:
```bash
# Delete the metadata file
rm backend/data/1-bronze/dnb_statistics/_extraction_metadata.json

# Next extraction will create new metadata
```

## Next Steps

### ✅ Completed
1. ✅ **Completeness verification**: Automatically detects truncated datasets
2. ✅ **Smart pagination**: Switches to full pagination when needed
3. ✅ **Metadata tracking**: Complete extraction history and data quality indicators
4. ✅ **Incremental update support**: Date-based filtering infrastructure ready

### 🔄 Recommended Actions
1. **Re-run full extraction** to verify all datasets are complete:
   ```bash
   python -m backend.etl.dnb_statistics.orchestrator --all
   ```

2. **Check the metadata report** for any remaining incomplete datasets:
   ```bash
   python -m backend.etl.dnb_statistics.metadata_report --incomplete
   ```

3. **Monitor data freshness** with the staleness check:
   ```bash
   python -m backend.etl.dnb_statistics.metadata_report --stale
   ```

### 🚀 Future Enhancements
1. **Silver layer**: Join datasets, add business logic
2. **Gold layer**: Create aggregated views for dashboards
3. **Scheduling**: Set up with cron/Task Scheduler for daily/weekly runs
4. **Dashboard integration**: Connect to BI tools for visualization

## Related Documentation

- DNB Statistics API: https://api.dnb.nl/statistics/
- Kiota Client Generation: https://learn.microsoft.com/en-us/openapi/kiota/
- Parquet Format: https://parquet.apache.org/

## Support

For issues or questions:
1. Check the logs: `logs/etl_dnb_statistics.log`
2. Review DNB API documentation
3. Verify API key permissions at https://api.portal.dnb.nl/
