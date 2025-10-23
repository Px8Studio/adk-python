For a clean BigQuery rollout of these new subcategory folders, treat everything as “DNB data” but keep a predictable hierarchy.

- **Project layout** – create or reuse a BigQuery dataset like `dnb_statistics`. Within it, use table names that mirror the bronze path: `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`, `insurance_pensions__pension_funds__pension_funds_balance_sheet`, etc. That schema scales, reads well in BI tools, and avoids proliferating datasets.

- **Source of truth** – keep the Parquet outputs under `backend/data/1-bronze/dnb_statistics/<category>/<subcategory>/`. Each folder becomes one BigQuery table. When you commit new schemas or transformations, version-control them (Terraform/Dataform/dbt or at minimum SQL files) so the warehouse metadata matches the repo.

- **In VS Code**  
  - Add a deployment script (Python or Makefile/PowerShell) that:  
    1. Exports the relevant Parquet file(s) to a GCS staging bucket (`gs://dnb-data/bronze/...`).  
    2. Runs `bq load --source_format=PARQUET` (or the Python BigQuery client) to load/replace the destination table. Include schema enforcement, partition fields (e.g., `period`), and clustering keys where sensible.  
  - Store table definitions (optional) as SQL or YAML so changes are diffable.  
  - Configure environment vars/service account JSON for the BigQuery project (`GOOGLE_APPLICATION_CREDENTIALS`), and add a VS Code task/launch config for “Deploy insurance/pensions data”.

- **One-time setup in BigQuery Web UI**  
  1. Create dataset `dnb_statistics` (choose default location, encryption).  
  2. Set up dataset-level IAM (service account from VS Code needs `roles/bigquery.dataEditor` and `roles/bigquery.jobUser`).  
  3. Optional: create dataset labels (e.g., `source=dnb`).  

- **Loading tables (per subfolder)**  
  - Option A (recommended): use the scripted `bq load` from VS Code so CI/CD can repeat it.  
  - Option B: in the BigQuery console, click “Create table”, select `Parquet`, point to the staged `gs://...` file, pick the dataset/table name (`insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`), enable partitioning on `period`, clustering on business keys, and set “Write preference” to replace/append as needed.

- **Ongoing operations**  
  - Automate the deployment (GitHub Actions/Azure DevOps) to trigger after a successful ETL run.  
  - Consider views for higher-level groupings (e.g., a `dnb_statistics.insurance_corporations` view unioning related tables).  
  - Monitor load jobs in the BigQuery Job History; add Data Catalog tags if governance requires.  
  - Document the pipeline (README or SYSTEM_FLOW.md) so anyone can trace: local ETL → GCS → BigQuery.

Natural follow-ups:  
1. Stand up a GCS bucket and sample `bq load` script for one subcategory.  
2. Decide on partitioning/clustering defaults per table family before mass-loading.