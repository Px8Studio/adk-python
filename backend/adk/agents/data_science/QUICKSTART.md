# Data Science Agent - Quick Start Guide

## 🎯 What Was Implemented

A minimal, working data science multi-agent system based on the ADK samples, ready for BigQuery integration.

### Components Created
- ✅ Root coordinator agent (routes queries between sub-agents)
- ✅ BigQuery agent (NL2SQL with schema awareness)
- ✅ Analytics agent (NL2Py with Code Interpreter)
- ✅ Dataset configuration system
- ✅ Local runner script
- ✅ Environment configuration

## 🚀 Next Steps: Getting Started

### Step 1: Set Up Environment

```powershell
# 1. Copy environment template
cp backend/adk/agents/data_science/.env.example backend/adk/agents/data_science/.env

# 2. Edit .env and fill in these required values:
# GOOGLE_CLOUD_PROJECT=your-project-id
# BQ_DATA_PROJECT_ID=your-project-id
# BQ_DATASET_ID=dnb_statistics
# GOOGLE_GENAI_USE_VERTEXAI=1
# GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 2: Load Data to BigQuery (NEXT)

You need to upload your Bronze layer parquet files to BigQuery.

**Option A: Using bq CLI**
```powershell
# Create dataset
bq mk --location=us-central1 --dataset your-project-id:dnb_statistics

# Load parquet files (example for one table)
bq load --source_format=PARQUET `
  dnb_statistics.insurance_pensions__insurers__insurance_corps_balance_sheet_quarter `
  backend/data/1-bronze/insurance_pensions__insurers__insurance_corps_balance_sheet_quarter.parquet
```

**Option B: Using Python Script (Recommended)**
```python
# Create a script: backend/scripts/upload_to_bigquery.py
from google.cloud import bigquery
import glob

client = bigquery.Client()
dataset_id = "dnb_statistics"

for parquet_file in glob.glob("backend/data/1-bronze/*.parquet"):
    table_name = Path(parquet_file).stem
    table_id = f"{dataset_id}.{table_name}"
    
    job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.PARQUET)
    
    with open(parquet_file, "rb") as f:
        job = client.load_table_from_file(f, table_id, job_config=job_config)
    
    job.result()  # Wait for completion
    print(f"✓ Loaded {table_name}")
```

### Step 3: Test the Agent

```powershell
# Test with a simple query
python backend/adk/run_data_science_agent.py --query "What tables are available?"

# Start interactive mode
python backend/adk/run_data_science_agent.py
```

Example queries to try:
```
You: What data do you have access to?
You: List all tables in the dataset
You: Show me the first 5 records from [table_name]
You: Create a chart showing [some metric] over time
```

## 📁 File Structure

```
backend/adk/agents/
├── root_agent/                      # System orchestrator
│   ├── __init__.py
│   ├── agent.py                     # Integrates all coordinators
│   └── instructions.txt             # System routing logic
├── data_science/                    # Data science coordinator
│   ├── agent.py                     # Coordinator (exports as data_science_coordinator)
│   ├── prompts.py                   # Coordination prompts
│   ├── tools.py                     # Coordination tools
│   ├── dnb_statistics_dataset_config.json
│   ├── .env.example                 # Configuration template
│   ├── .env                         # Your config (create this!)
│   ├── README.md                    # Full documentation
│   └── sub_agents/
│       ├── bigquery/                # BigQuery agent
│       │   ├── agent.py
│       │   ├── prompts.py
│       │   └── tools.py
│       └── analytics/               # Analytics agent
│           ├── agent.py
│           └── prompts.py
└── run_data_science_agent.py        # Standalone runner script
```

## 🔧 Configuration

### Minimal .env (BigQuery Only)
```bash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
BQ_DATA_PROJECT_ID=your-project-id
BQ_COMPUTE_PROJECT_ID=your-project-id
BQ_DATASET_ID=dnb_statistics
```

### Optional Model Selection
```bash
# Defaults to gemini-2.0-flash-exp if not set
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
BIGQUERY_AGENT_MODEL=gemini-2.0-flash-exp
ANALYTICS_AGENT_MODEL=gemini-2.0-flash-exp
```

## 🎯 What to Implement Next

### Priority 1: Data Integration (This Week)
1. Upload parquet files to BigQuery
2. Verify schema and data quality
3. Test agent queries against real data

### Priority 2: BQML Agent (Next Sprint)
- Implement RAG corpus for BigQuery ML docs
- Create BQML sub-agent
- Add model training capabilities

### Priority 3: AlloyDB Agent (Next Sprint)
- Set up MCP Toolbox for Databases
- Configure AlloyDB connection
- Implement cross-dataset queries

## 🐛 Troubleshooting

### "Module not found" errors
```powershell
# Make sure you're running from project root
cd c:\Users\rjjaf\_Projects\orkhon
python backend/adk/run_data_science_agent.py
```

### BigQuery authentication errors
```powershell
# Authenticate with Google Cloud
gcloud auth application-default login
gcloud config set project your-project-id
```

### Environment variable errors
```powershell
# Check your .env file exists and has required variables
cat backend/adk/agents/data_science/.env
```

## 📚 Resources

- **Full README**: `backend/adk/agents/data_science/README.md`
- **Architecture**: `backend/ARCHITECTURE_ENHANCEMENTS.md`
- **ADK Docs**: https://google.github.io/adk-docs/
- **ADK Samples**: https://github.com/google/adk-samples/tree/main/python/agents/data-science

## ✅ Success Criteria

You'll know it's working when:
1. ✅ Runner script starts without errors
2. ✅ Agent responds to "What data do you have?"
3. ✅ BigQuery agent can list tables
4. ✅ Analytics agent can create simple visualizations
5. ✅ Multi-step queries work (SQL → Python analysis)

---

**Status**: MVP Complete - Ready for Data Integration! 🎉
