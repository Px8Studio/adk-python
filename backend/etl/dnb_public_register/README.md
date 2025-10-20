# DNB Public Register ETL Pipeline

Comprehensive ETL pipeline for extracting all data from the DNB Public Register API and storing it in Parquet format for analytics.

## 📁 Architecture

The pipeline follows a **modular, layered approach** optimized for maintainability and scalability:

```
backend/etl/dnb_public_register/
├── __init__.py           # Package initialization
├── config.py             # Centralized configuration
├── base.py               # Base classes (rate limiting, pagination, Parquet writing)
├── extractors.py         # Endpoint-specific extraction logic
├── orchestrator.py       # Main coordinator script
└── README.md             # This file

backend/data/
├── 0-fetch/              # Raw API responses (JSON Lines) - landing zone
├── 1-bronze/             # Cleaned Parquet files - directly from API
├── 2-silver/             # Enriched & joined data - business logic applied
└── 3-gold/               # Analytics-ready aggregations - reporting layer
```

### Design Principles

1. **Separation of Concerns**: Each extractor handles one endpoint category
2. **Rate Limiting**: Built-in token bucket limiter (stays under DNB's 30 calls/min)
3. **Retry Logic**: Exponential backoff for transient failures
4. **Incremental Extraction**: Can extract specific registers/languages
5. **Parquet Storage**: Efficient columnar format for analytics
6. **Metadata Enrichment**: Auto-adds `_etl_extracted_at`, `_etl_extractor` fields

## 🚀 Quick Start

### Prerequisites

```bash
# Set your DNB API key
$env:DNB_SUBSCRIPTION_KEY_DEV = "your-api-key-here"

# Install dependencies
pip install httpx pandas pyarrow
```

### Extract Everything (Recommended for First Run)

```bash
# From project root
python -m backend.etl.dnb_public_register.orchestrator --all
```

This will:
1. ✅ Discover all available registers (metadata)
2. 📰 Extract all publications across all registers
3. 🏢 Extract all organizations
4. 📝 Extract all registrations
5. ⚖️  Extract all register articles (regulatory framework)

**Estimated time**: 15-30 minutes (depending on data volume and API rate limits)

## 📊 Available Data

### Metadata
- **Registers**: All available register codes (WFTAF, WFT, etc.)
- **Languages**: Supported language codes (NL, EN)

### Entities
- **Organizations**: Relation numbers for all registered organizations

### Publications
- **Publications Search**: Publications with filtering by register, organization name, article name

### Registrations
- **Registrations**: Registration details per organization

### Regulatory
- **Register Articles**: Act article codes, names, and descriptions

## 🎯 Usage Examples

### Extract Specific Categories

```bash
# Metadata only
python -m backend.etl.dnb_public_register.orchestrator --metadata

# Organizations only
python -m backend.etl.dnb_public_register.orchestrator --organizations

# Publications only
python -m backend.etl.dnb_public_register.orchestrator --publications
```

### Extract Specific Register

```bash
# Single register
python -m backend.etl.dnb_public_register.orchestrator --publications --register WFTAF

# Multiple registers
python -m backend.etl.dnb_public_register.orchestrator --organizations --register WFTAF --register WFT
```

### Extract in Multiple Languages

```bash
# Dutch and English
python -m backend.etl.dnb_public_register.orchestrator --publications --language NL --language EN
```

### Dry Run (Check What Would Be Extracted)

```bash
python -m backend.etl.dnb_public_register.orchestrator --all --dry-run
```

## 📂 Output Structure

Data is organized by stage and category:

```
backend/data/1-bronze/dnb_public_register/
├── metadata/
│   ├── registers.parquet
│   └── supported_languages.parquet
├── entities/
│   ├── organizations_wftaf_nl.parquet
│   └── organizations_wft_nl.parquet
├── publications/
│   ├── all_publications_nl.parquet
│   └── publications_search_wftaf_nl.parquet
├── registrations/
│   ├── registrations_wftaf_nl.parquet
│   └── registrations_wft_nl.parquet
└── regulatory/
    ├── register_articles_wftaf_nl.parquet
    └── register_articles_wft_nl.parquet
```

### Parquet File Schema Examples

**registers.parquet**:
```
register_code: string
register_name: string
register_type: string
_etl_extracted_at: timestamp
_etl_extractor: string
```

**publications_search_*.parquet**:
```
register_code: string
language_code: string
relation_number: string
register_article_code: string
publication_date: date
valid_from_date: date
organization_name: string
raw_json: string (full API response for reference)
_etl_extracted_at: timestamp
_etl_extractor: string
```

## 🔧 Configuration

All settings are in `config.py`:

### API Settings
```python
DNB_BASE_URL = "https://api.dnb.nl/publicdata/v1"
DNB_API_KEY = os.getenv("DNB_SUBSCRIPTION_KEY_DEV")
```

### Rate Limiting
```python
RATE_LIMIT_CALLS = 30          # DNB allows 30 calls/minute
RATE_LIMIT_PERIOD = 60.0       # seconds
RATE_LIMIT_BUFFER = 1.2        # 20% safety margin
```

### Pagination
```python
DEFAULT_PAGE_SIZE = 25         # DNB API maximum
MAX_CONCURRENT_REQUESTS = 5    # Parallel requests
```

### Parquet Options
```python
PARQUET_ENGINE = "pyarrow"
PARQUET_COMPRESSION = "snappy"  # Good balance of speed/size
PARQUET_ROW_GROUP_SIZE = 10000
```

## 📝 Extending the Pipeline

### Add a New Extractor

1. Create a new class in `extractors.py` inheriting from `BaseExtractor` or `PaginatedExtractor`:

```python
class MyCustomExtractor(PaginatedExtractor):
    def get_category(self) -> str:
        return "my_category"
    
    def get_output_filename(self) -> str:
        return "my_data"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        url = f"{config.DNB_BASE_URL}/api/my-endpoint"
        async for record in self.extract_paginated(url):
            yield record
```

2. Add to `orchestrator.py`:

```python
async def extract_my_custom_data():
    extractor = MyCustomExtractor()
    return await extractor.run()
```

## 🐛 Troubleshooting

### Rate Limit Errors (HTTP 429)

The pipeline automatically handles rate limiting with exponential backoff. If you see frequent 429 errors:

1. Reduce `MAX_CONCURRENT_REQUESTS` in `config.py`
2. Increase `RATE_LIMIT_BUFFER` to slow down requests

### API Key Issues

```bash
# Check your API key is set
echo $env:DNB_SUBSCRIPTION_KEY_DEV

# Verify it works
curl -H "Ocp-Apim-Subscription-Key: $env:DNB_SUBSCRIPTION_KEY_DEV" https://api.dnb.nl/echo-api/helloworld
```

### Missing Data

Some registers may not have all endpoint types available. Check the logs for:
```
📄 Page 1/1: 0 records
```

This indicates the endpoint returned no data (not an error).

## 📊 Monitoring & Logs

Logs are written to:
- **Console**: Real-time progress
- **File**: `backend/logs/etl_dnb_public_register.log`

### Log Levels

```bash
# Set log level
$env:LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

### Key Log Messages

- `🚀 Starting: RegistersExtractor` - Extraction begins
- `📄 Page 1/5: 25 records` - Pagination progress
- `💾 Writing 1,234 records to registers.parquet` - Saving data
- `✅ Completed: RegistersExtractor` - Success with stats
- `❌ Extraction failed: ...` - Error details

## 🔄 Incremental Updates

To refresh data:

```bash
# Re-extract everything
python -m backend.etl.dnb_public_register.orchestrator --all

# Or refresh specific category
python -m backend.etl.dnb_public_register.orchestrator --publications --register WFTAF
```

Files are **overwritten** on each run (no deduplication needed).

## 🎯 Next Steps

After extraction, you can:

1. **Query with DuckDB**:
   ```python
   import duckdb
   
   duckdb.query("""
       SELECT register_code, COUNT(*) as org_count
       FROM read_parquet('backend/data/1-bronze/dnb_public_register/entities/*.parquet')
       GROUP BY register_code
   """).show()
   ```

2. **Load into PostgreSQL**:
   ```python
   import pandas as pd
   
   df = pd.read_parquet('backend/data/1-bronze/dnb_public_register/metadata/registers.parquet')
   df.to_sql('dnb_registers', engine, if_exists='replace')
   ```

3. **Create Silver Layer** (enriched data):
   - Join organizations with publications
   - Denormalize for easier querying
   - Add calculated fields

4. **Create Gold Layer** (analytics):
   - Organization count by register
   - Publication trends over time
   - Compliance metrics

## 📚 References

- [DNB API Documentation](https://api.portal.dnb.nl/)
- [DNB Public Register Info](https://www.dnb.nl/en/public-register)
- [Apache Parquet Format](https://parquet.apache.org/docs/)
- [Kiota HTTP Client](https://learn.microsoft.com/en-us/openapi/kiota/overview)

## 📧 Support

Issues or questions:
1. Check logs in `backend/logs/etl_dnb_public_register.log`
2. Enable DEBUG logging: `$env:LOG_LEVEL = "DEBUG"`
3. Run with `--dry-run` to test without API calls
4. Verify API key works with DNB Echo API

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-21
