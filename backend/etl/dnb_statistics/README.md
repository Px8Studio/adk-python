# DNB Statistics ETL Pipeline

Comprehensive ETL pipeline for extracting, transforming, and loading all financial statistics data from the DNB (De Nederlandsche Bank) Statistics API.

## Overview

This pipeline:
- ✅ Extracts data from **all DNB Statistics API endpoints** using the Kiota-generated client
- ✅ Handles pagination automatically (up to 2000 records per page)
- ✅ Applies rate limiting to stay under API limits
- ✅ Saves data in efficient **Parquet** format (analytics-ready)
- ✅ Organizes data by logical categories

## Architecture

### Components

```
dnb_statistics/
├── config.py          # Configuration (API keys, paths, settings)
├── base.py            # Base extractor classes with pagination & rate limiting
├── extractors.py      # Endpoint-specific extractors (20+ endpoints)
├── orchestrator.py    # Main coordination script
└── README.md          # This file
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

### Market Data (6 endpoints)
- `exchange_rates_day` - Daily exchange rates and gold prices
- `exchange_rates_month` - Monthly exchange rates
- `exchange_rates_quarter` - Quarterly exchange rates
- `market_interest_rates_day` - Daily market interest rates
- `market_interest_rates_month` - Monthly market interest rates
- `ecb_interest_rates` - ECB policy rates

### Macroeconomic (3 endpoints)
- `balance_of_payments_quarter` - Quarterly balance of payments
- `balance_of_payments_year` - Yearly balance of payments
- `macroeconomic_scoreboard_quarter` - Quarterly economic indicators

### Financial Statements (2 endpoints)
- `dnb_balance_sheet_month` - Monthly DNB balance sheet
- `mfi_balance_sheet_month` - Monthly MFI balance sheets

### Insurance & Pensions (2 endpoints)
- `pension_funds_balance_sheet` - Pension fund financials
- `insurance_corps_balance_sheet_quarter` - Insurance company financials

### Investments & Securities (2 endpoints)
- `dutch_household_savings_month` - Household savings data
- `dutch_securities_holdings_by_holder` - Securities ownership

### Payments (2 endpoints)
- `payment_transactions_half_year` - Payment volumes & values
- `retail_payment_transactions` - Retail payment statistics

**Total: 17+ implemented endpoints** (easily extensible to all 70+ endpoints)

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

### ✅ Robust Error Handling
- Automatic retry with exponential backoff
- Graceful failure recovery
- Detailed error logging

### ✅ Performance Optimized
- Parallel page fetching (respects rate limits)
- Batch writes to Parquet
- Efficient memory management

### ✅ Data Quality
- Adds ETL metadata to all records
- Type-safe Parquet schema
- Efficient columnar storage

### ✅ Monitoring & Logging
- Real-time progress tracking
- Detailed statistics per endpoint
- Structured logs in `logs/etl_dnb_statistics.log`

## Output Format

### Parquet (1-bronze)
Columnar format optimized for analytics:
- Efficient compression (5-10x smaller than JSON)
- Fast filtering & aggregation
- Schema enforcement
- Compatible with Pandas, DuckDB, Spark, etc.
- Includes ETL metadata: `_etl_timestamp`, `_etl_source`

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

## Next Steps

1. **Add more extractors**: The Kiota client has 70+ endpoints available
2. **Silver layer**: Join datasets, add business logic
3. **Gold layer**: Create aggregated views for dashboards
4. **Scheduling**: Set up with cron/Task Scheduler for daily/weekly runs
5. **Incremental loads**: Add date filtering for delta updates

## Related Documentation

- DNB Statistics API: https://api.dnb.nl/statistics/
- Kiota Client Generation: https://learn.microsoft.com/en-us/openapi/kiota/
- Parquet Format: https://parquet.apache.org/

## Support

For issues or questions:
1. Check the logs: `logs/etl_dnb_statistics.log`
2. Review DNB API documentation
3. Verify API key permissions at https://api.portal.dnb.nl/
