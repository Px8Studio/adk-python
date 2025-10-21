# DNB Public Register API - Endpoint Coverage

This document tracks the implementation status of all DNB Public Register API endpoints in the ETL pipeline.

**Last Updated:** October 21, 2025

## Summary

- **Total Endpoints:** 12
- **Implemented:** 10 ✅
- **Not Implemented:** 2 ❌ (historical endpoints)
- **Coverage:** 83%

---

## Endpoint Details

### ✅ Metadata Endpoints

| Endpoint | Extractor | Status | Notes |
|----------|-----------|--------|-------|
| `GET /api/publicregister/Registers` | `RegistersExtractor` | ✅ | Gets all available registers |
| `GET /api/publicregister/SupportedLanguages` | `SupportedLanguagesExtractor` | ✅ | Gets all supported languages |

### ✅ Organizations Endpoints

| Endpoint | Extractor | Status | Notes |
|----------|-----------|--------|-------|
| `GET /api/publicregister/{registerCode}/Organizations` | `OrganizationRelationNumbersExtractor` | ✅ | Gets relation numbers (lightweight) |
| `GET /api/publicregister/{languageCode}/{registerCode}/Organizations` | `OrganizationDetailsExtractor` | ✅ | **CRITICAL** - Gets full organization details including names, addresses, registrations, etc. |
| `GET /api/publicregister/{registerCode}/Organizations/historicalrecord/{date}` | - | ❌ | Historical relation numbers (not critical for initial implementation) |
| `GET /api/publicregister/{languageCode}/{registerCode}/Organizations/historicalrecord/{date}` | - | ❌ | Historical organization details (not critical for initial implementation) |

### ✅ Publications Endpoints

| Endpoint | Extractor | Status | Notes |
|----------|-----------|--------|-------|
| `GET /api/publicregister/{languageCode}/Publications/{registerCode}` | `PublicationDetailsExtractor` | ✅ | Gets latest publication directly (paginated) |
| `GET /api/publicregister/{languageCode}/Publications/search` | `PublicationsSearchExtractor` | ✅ | Search publications with filters |
| `GET /api/publicregister/{languageCode}/Publications/{registerCode}/historicalrecord/{date}` | - | ❌ | Historical publications (could be added later) |

### ✅ Registrations Endpoints

| Endpoint | Extractor | Status | Notes |
|----------|-----------|--------|-------|
| `GET /api/publicregister/{languageCode}/{registerCode}/Registrations/ActArticleNames` | `RegistrationActArticleNamesExtractor` | ✅ | Gets distinct act article names |
| `GET /api/publicregister/{languageCode}/{registerCode}/Registrations/ActArticleNames/historicalrecord/{date}` | - | ❌ | Historical act article names (not critical) |

### ✅ Register Articles Endpoint

| Endpoint | Extractor | Status | Notes |
|----------|-----------|--------|-------|
| `GET /api/publicregister/{languageCode}/{registerCode}/RegisterArticles` | `RegisterArticlesExtractor` | ✅ | Gets all configured act articles for a register |

---

## Implementation Notes

### Key Changes from Previous Version

1. **Fixed Organizations Extraction:**
   - Previously: Only collected relation numbers using wrong URL
   - Now: Two-step process:
     - Step 1: Get relation numbers via `/api/publicregister/{registerCode}/Organizations`
     - Step 2: Get full details via `/api/publicregister/{languageCode}/{registerCode}/Organizations`
   
2. **All Extractors Now Use Kiota Client:**
   - Previous version used manual HTTP requests for some endpoints
   - Now all extractors use the properly typed Kiota-generated client
   - Better type safety and error handling

3. **Added Missing Extractors:**
   - `OrganizationDetailsExtractor` - **Most important** - gets complete org data
   - `PublicationDetailsExtractor` - Direct publication access
   - `RegistrationActArticleNamesExtractor` - Regulatory metadata
   - `RegisterArticlesExtractor` - Updated to use Kiota client

### Data Richness

The most valuable endpoint is:
```
GET /api/publicregister/{languageCode}/{registerCode}/Organizations
```

This returns complete organization data including:
- ✅ Official, statutory, and trade names
- ✅ Contact channels (addresses, emails, URLs, phone numbers)
- ✅ Registrations (licenses/permits with validity periods)
- ✅ Related organizations (parent/child relationships)
- ✅ Classifications
- ✅ Covered bonds
- ✅ Chamber of Commerce details
- ✅ LEI codes, RSIN codes
- ✅ Liquidation status

### Historical Endpoints (Not Implemented)

The following endpoints support time-travel queries but are not critical for initial implementation:

1. Organizations historical records (2 endpoints)
2. Publications historical records (1 endpoint)
3. Registrations act article names historical (1 endpoint)

These could be added later if historical analysis is needed.

---

## Extraction Workflow

The recommended extraction order in `orchestrator.py`:

```
1. Metadata → Discover all registers and languages
2. Organizations (Relation Numbers) → Get list of org IDs per register
3. Organizations (Full Details) → Get complete data for each org
4. Publications → Search across all publications
5. Registrations (Act Article Names) → Get regulatory metadata
6. Register Articles → Get act articles per register
```

---

## Usage

Extract everything:
```bash
python -m backend.etl.dnb_public_register.orchestrator --all
```

Extract specific categories:
```bash
python -m backend.etl.dnb_public_register.orchestrator --organizations
python -m backend.etl.dnb_public_register.orchestrator --publications
```

Extract specific register:
```bash
python -m backend.etl.dnb_public_register.orchestrator --organizations --register WFTAF
```

---

## Kiota Client Structure

The Kiota-generated client has all endpoints properly typed:

```python
# Metadata
client.api.publicregister.registers.get()
client.api.publicregister.supported_languages.get()

# Organizations
client.api.publicregister.by_language_code("NL").by_register_code("WFTAF").organizations.get()

# Publications
client.api.publicregister.by_language_code("NL").publications.by_register_code("WFTAF").get()
client.api.publicregister.by_language_code("NL").publications.search.get()

# Registrations
client.api.publicregister.by_language_code("NL").by_register_code("WFTAF").registrations.act_article_names.get()

# Register Articles
client.api.publicregister.by_language_code("NL").by_register_code("WFTAF").register_articles.get()
```

All methods are properly typed with request builders and configuration objects.
