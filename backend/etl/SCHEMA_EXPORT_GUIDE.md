# BigQuery Schema Export Guide

## Overview

`export_schemas.py` is a utility for exporting BigQuery table schemas to JSON files. While the ADK agent **automatically loads schemas** from BigQuery at runtime, this tool serves additional purposes.

## When to Use This Tool

### ✅ **Use Cases:**

1. **Documentation & Versioning** 📚
   - Commit schemas to git for version control
   - Track schema evolution over time
   - Share table structures with team members

2. **CI/CD Integration** 🔄
   ```bash
   # In your CI pipeline
   python -m backend.etl.export_schemas --all --output-dir docs/schemas/
   git add docs/schemas/
   git commit -m "docs: update BigQuery schemas"
   ```

3. **Schema Comparison** 🔍
   ```bash
   # Compare dev vs prod
   python -m backend.etl.export_schemas --compare schemas/dev.json schemas/prod.json
   ```

4. **Offline Development** 💻
   - Work without BigQuery access
   - Reference table structures during development
   - Mock schemas for testing

5. **Data Catalog** 📊
   - Generate documentation for data governance
   - Create schema registry for data discovery
   - Feed metadata into data catalog tools

### ❌ **Don't Use For:**

- **Runtime schema loading** - ADK agent already does this automatically via `schema_cache.py`
- **Production agent configuration** - Schemas are loaded live from BigQuery
- **Replacing the cache** - The `.cache/bigquery_schemas/` is managed automatically

## Usage Examples

### Export Single Dataset

```powershell
# Export DNB Statistics schema
python -m backend.etl.export_schemas `
  --dataset dnb_statistics `
  --output schemas/dnb_statistics.json
```

### Export All Datasets

```powershell
# Export all configured datasets
python -m backend.etl.export_schemas --all --output-dir schemas/

# Output:
# schemas/dnb_statistics.json
# schemas/dnb_public_register.json
```

### Compare Schemas

```powershell
# Compare two environments
python -m backend.etl.export_schemas `
  --compare schemas/dev/dnb_statistics.json schemas/prod/dnb_statistics.json
```

### Version Control Integration

```powershell
# Add to your deployment script
cd C:\Users\rjjaf\_Projects\orkhon

# Export current schemas
python -m backend.etl.export_schemas --all --output-dir docs/schemas/

# Commit if changed
git add docs/schemas/
git commit -m "docs: update BigQuery schemas [skip ci]"
```

## Output Format

The exported JSON includes:

```json
{
  "project_id": "woven-art-475517-n4",
  "dataset_id": "dnb_statistics",
  "exported_at": "2025-11-06T12:00:00.000000",
  "dataset_location": "europe-west4",
  "tables": {
    "exchange_rates_day": {
      "columns": [
        {
          "name": "currency",
          "type": "STRING",
          "mode": "NULLABLE",
          "description": null
        },
        {
          "name": "date",
          "type": "DATE",
          "mode": "NULLABLE",
          "description": null
        },
        {
          "name": "rate",
          "type": "FLOAT64",
          "mode": "NULLABLE",
          "description": null
        }
      ],
      "description": "Daily exchange rates",
      "num_rows": 15000,
      "size_bytes": 1234567,
      "created": "2025-01-01T00:00:00",
      "modified": "2025-11-06T10:00:00"
    }
  }
}
```

## Integration Points

### 1. Git Workflow

Add to `.gitignore` if you want to exclude:
```gitignore
# Optional: Exclude generated schemas (regenerate as needed)
schemas/*.json
```

Or track them:
```bash
# Track schemas for versioning
git add schemas/
```

### 2. CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Update Schemas

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:  # Manual trigger

jobs:
  export-schemas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install google-cloud-bigquery
      
      - name: Export schemas
        env:
          GOOGLE_CLOUD_PROJECT: ${{ secrets.GCP_PROJECT_ID }}
        run: |
          python -m backend.etl.export_schemas --all --output-dir docs/schemas/
      
      - name: Commit changes
        run: |
          git config user.name "Schema Bot"
          git config user.email "bot@example.com"
          git add docs/schemas/
          git commit -m "docs: update BigQuery schemas" || echo "No changes"
          git push
```

### 3. Documentation Generation

```python
# Example: Generate markdown docs from schemas
import json

with open("schemas/dnb_statistics.json") as f:
    schema = json.load(f)

for table_name, table_info in schema["tables"].items():
    print(f"## {table_name}\n")
    print(f"{table_info['description']}\n")
    print("| Column | Type | Mode |")
    print("|--------|------|------|")
    for col in table_info["columns"]:
        print(f"| {col['name']} | {col['type']} | {col['mode']} |")
```

## Comparison with Runtime Schema Loading

| Feature | `export_schemas.py` | ADK Runtime (schema_cache.py) |
|---------|---------------------|-------------------------------|
| **Purpose** | Documentation, versioning, CI/CD | Agent operation |
| **Timing** | Manual/scheduled | Automatic at agent startup |
| **Storage** | Git, docs/ folder | `.cache/bigquery_schemas/` |
| **Format** | User-friendly JSON | Optimized cache format |
| **TTL** | Manually regenerated | 24 hours (configurable) |
| **Use in production** | ❌ Not used by agents | ✅ Required for agents |

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     Normal Operation                         │
│  (You DON'T need export_schemas.py for this)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    1. ETL Extract → Bronze (Parquet)
    2. Upload → BigQuery (creates tables)
    3. ADK Agent Startup → Auto-load schemas → Cache (.cache/)
    4. Agent runs → Uses cached schemas


┌─────────────────────────────────────────────────────────────┐
│                  Additional Use Cases                        │
│     (Use export_schemas.py for these)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    • Documentation: Export schemas to docs/
    • Version Control: Commit schemas to git
    • CI/CD: Validate schemas in pipeline
    • Comparison: Detect drift between environments
    • Offline: Work without BigQuery access
```

## Troubleshooting

### Error: "GOOGLE_CLOUD_PROJECT not set"

```powershell
$env:GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Error: "Permission denied"

Ensure your service account has BigQuery metadata read permissions:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:YOUR_SA@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/bigquery.metadataViewer"
```

### Schema differences detected

This is expected! Schemas evolve over time. Use this information to:
- Update documentation
- Plan migrations
- Validate deployments
- Communicate changes to team

## Related Files

- `backend/adk/agents/data_science/sub_agents/bigquery/schema_cache.py` - Runtime schema caching
- `backend/gcp/upload_parquet.py` - Creates tables in BigQuery
- `.cache/bigquery_schemas/` - Automatic schema cache (used by agents)
