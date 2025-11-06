# Quick Start: Adopting ADK Data-Science Agent

> **Get the production-grade data-science agent running in Orkhon in 30 minutes**

---

## TL;DR

```powershell
# 1. Import data-science agent via git subtree (one-time setup)
cd C:\Users\rjjaf\_Projects\orkhon
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples
git subtree add --prefix=backend/adk/agents/data_science adk-samples main:python/agents/data-science --squash

# 2. Install dependencies
cd backend\adk
uv sync

# 3. Configure environment
copy agents\data_science\.env.example agents\data_science\.env
# Edit .env with your settings (see below)

# 4. Test it!
uv run adk run agents/data_science
```

---

## Why Adopt This Agent?

The official ADK data-science sample is **production-grade** and provides:

✅ **4 specialized sub-agents** (BigQuery, AlloyDB, Data Science, BQML)  
✅ **NL2SQL engine** with CHASE-SQL research methodology  
✅ **NL2Py capabilities** via Vertex AI Code Interpreter  
✅ **Cross-dataset joins** (BigQuery ↔ AlloyDB)  
✅ **Dataset configuration system** (JSON-based)  
✅ **RAG pipeline** for BQML reference guide  
✅ **OpenTelemetry tracing** (W&B Weave compatible)  
✅ **Comprehensive testing** (unit + integration + eval)  
✅ **Deployment configs** (Cloud Run, Agent Engine)  

**Building this from scratch would take 4-6 weeks.** With git subtree, you get it in 30 minutes and stay sync'd with upstream improvements.

---

## Step 1: Import via Git Subtree (5 min)

```powershell
# Navigate to Orkhon root
cd C:\Users\rjjaf\_Projects\orkhon

# Add adk-samples as remote (if not already added)
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples

# Import data-science agent as subtree
git subtree add --prefix=backend/adk/agents/data_science `
    adk-samples main:python/agents/data-science `
    --squash

# Commit the import
git commit -m "feat(adk): Import data-science agent from ADK samples via git subtree"
```

**What this does:**
- Copies `python/agents/data-science/` from adk-samples into `backend/adk/agents/data_science/`
- Maintains connection to upstream for future updates
- Squashes history to keep Orkhon's git log clean

---

## Step 2: Install Dependencies (5 min)

```powershell
cd backend\adk

# Install data-science dependencies
uv sync

# Verify installation
.venv\Scripts\python.exe -c "import google.adk; import pandas; import sqlglot; print('✅ Dependencies OK')"
```

**Key new dependencies:**
- `pandas`, `numpy` - Data manipulation
- `sqlglot` - SQL parsing/optimization
- `db-dtypes` - BigQuery data types
- `toolbox-core` - MCP Toolbox client
- `pg8000` - PostgreSQL driver (for AlloyDB)
- `opentelemetry-*` - Tracing to W&B Weave

---

## Step 3: Configure Environment (10 min)

### Option A: BigQuery Only (Recommended for Quick Start)

```powershell
# Copy example config
copy agents\data_science\.env.example agents\data_science\.env

# Edit agents\data_science\.env
notepad agents\data_science\.env
```

**Minimal `.env` for BigQuery:**
```bash
# Model Backend
GOOGLE_GENAI_USE_VERTEXAI=1

# GCP Project
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery
BQ_DATA_PROJECT_ID=your-gcp-project-id
BQ_COMPUTE_PROJECT_ID=your-gcp-project-id
BQ_DATASET_ID=dnb_statistics

# Dataset Config (use sample dataset first)
DATASET_CONFIG_FILE='./forecasting_sticker_sales_dataset_config.json'

# NL2SQL Method
NL2SQL_METHOD='BASELINE'

# Root Agent Model
ROOT_AGENT_MODEL='gemini-2.0-flash-exp'

# Code Interpreter (leave empty, auto-creates on first run)
CODE_INTERPRETER_EXTENSION_NAME=''

# BQML RAG (leave empty, setup later)
BQML_RAG_CORPUS_NAME=''
```

### Option B: Use Orkhon's DNB Data (Advanced)

Create a custom dataset config for your DNB BigQuery data:

```powershell
# Create Orkhon-specific dataset config
notepad agents\data_science\orkhon_dnb_config.json
```

**`orkhon_dnb_config.json`:**
```json
{
  "datasets": [
    {
      "type": "bigquery",
      "name": "dnb_statistics",
      "description": "DNB Statistics API data including insurance companies, pension funds, market data, and financial metrics. Use this for querying Dutch central bank statistical data."
    }
  ],
  "cross_dataset_relations": {
    "foreign_keys": []
  }
}
```

**Update `.env`:**
```bash
DATASET_CONFIG_FILE='./orkhon_dnb_config.json'
BQ_DATASET_ID=dnb_statistics
```

---

## Step 4: Load Sample Data (Optional, 5 min)

If you want to test with the provided sample datasets first:

### Option 1: Forecasting Sticker Sales (BigQuery Only)

```powershell
cd agents\data_science

# Load sample data into BigQuery
..\..\.venv\Scripts\python.exe data_science\utils\create_bq_table.py
```

### Option 2: Use Your Existing DNB Data

If you've already run the ETL pipelines, your BigQuery should have:
- `dnb_statistics` dataset with tables
- `dnb_public_register` dataset with tables

**Verify:**
```powershell
bq ls --project_id=your-project dnb_statistics
```

---

## Step 5: Test the Agent (5 min)

### Test in ADK CLI

```powershell
cd backend\adk

# Run data-science agent directly
uv run adk run agents/data_science
```

**Test queries:**
1. "What datasets do you have access to?"
2. "Show me the schema for the main table"
3. "Query the top 5 records and show me the results"
4. "Create a bar chart of the data by category"

### Test in ADK Web UI

```powershell
# Start ADK Web server
uv run adk web agents

# Open http://localhost:8000
# Select "data_science_root_agent" from dropdown
```

---

## Step 6: Integrate with Root Agent (10 min)

Now connect the data-science agent to Orkhon's root orchestrator.

### Update Root Agent

Edit `backend/adk/agents/root_agent/agent.py`:

```python
def get_root_agent() -> Agent:
  """Creates the root agent with sub-agents for API coordination."""
  
  # Add import for data_science coordinator
  from data_science.agent import root_agent as data_science_coordinator
  
  dnb_coordinator = get_dnb_coordinator_agent()
  
  root = Agent(
      model=os.environ.get("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash-exp"),
      name="root_agent",
      instruction="""You are the Root Orchestrator for the Orkhon system.
          
Your role is to:
1. Understand the user's query and intent
2. Delegate to the appropriate coordinator agent:
   - dnb_coordinator: For DNB API queries (Echo, Statistics, Public Register)
   - data_science_coordinator: For data analysis, BigQuery, and analytics
3. Present results clearly to the user

When routing queries:
- DNB API operations → dnb_coordinator
- Data science operations → data_science_coordinator
- Multi-domain workflows → chain coordinators sequentially
""",
      description="System root orchestrator for Orkhon multi-agent system",
      sub_agents=[dnb_coordinator, data_science_coordinator]  # ✅ Added data_science
  )
  
  return root
```

### Test Integrated System

```powershell
# Run from root agent
uv run adk run agents/root_agent
```

**Test cross-domain query:**
```
"Query the DNB Statistics dataset for the top 10 insurance companies by assets, 
then create a visualization showing the distribution."
```

This should:
1. Root agent → Data Science coordinator
2. Data Science coordinator → BigQuery agent (query)
3. Data Science coordinator → Analytics agent (visualization)

---

## Architecture After Integration

```
backend/adk/agents/
├── root_agent/                     # L1: System Root
│   └── agent.py                    # ← MODIFIED: Import data_science
│
├── api_coordinators/               # L2: Domain Coordinators
│   └── dnb_coordinator/
│       └── agent.py
│
├── data_science/                   # L2: Domain Coordinator (NEW!)
│   ├── agent.py                    # Root DS agent
│   ├── sub_agents/                 # L3: Specialists
│   │   ├── bqml_agent.py
│   │   ├── bigquery/
│   │   │   ├── agent.py           # BigQuery NL2SQL agent
│   │   │   └── tools.py
│   │   ├── alloydb/
│   │   │   ├── agent.py           # AlloyDB NL2SQL agent
│   │   │   └── tools.py
│   │   └── data_science/
│   │       ├── agent.py           # NL2Py analytics agent
│   │       └── tools.py
│   ├── tools.py
│   ├── utils/
│   └── orkhon_dnb_config.json     # ← Custom dataset config
│
└── api_agents/                     # L3: Specialists
    ├── dnb_echo_agent/
    ├── dnb_statistics_agent/
    └── dnb_public_register_agent/
```

**Updated hierarchy:**
```
root_agent (L1: System Root)
├── dnb_coordinator (L2: Domain Coordinator)
│   ├── dnb_echo_agent (L3: Specialist)
│   ├── dnb_statistics_agent (L3: Specialist)
│   └── dnb_public_register_agent (L3: Specialist)
└── data_science_coordinator (L2: Domain Coordinator) ← NEW!
    ├── bigquery_agent (L3: Specialist)
    ├── alloydb_agent (L3: Specialist)
    ├── analytics_agent (L3: Specialist)
    └── bqml_agent (L2: Sub-coordinator with RAG)
```

**Total agent count: 10 agents** (was 8, added 2 data science specialists)

---

## Pulling Upstream Updates

When ADK improves the data-science sample:

```powershell
cd C:\Users\rjjaf\_Projects\orkhon

# Pull updates from upstream
git subtree pull --prefix=backend/adk/agents/data_science `
    adk-samples main:python/agents/data-science `
    --squash

# Resolve conflicts if needed (prefer upstream for core logic)

# Test after update
cd backend\adk
uv sync
uv run adk run agents/data_science
```

---

## Common Issues & Solutions

### Issue 1: Import errors for data_science

**Symptom:**
```
ImportError: cannot import name 'root_agent' from 'data_science.agent'
```

**Solution:**
```powershell
# Ensure __init__.py exists
if (-not (Test-Path agents\data_science\__init__.py)) {
    New-Item -ItemType File agents\data_science\__init__.py
}

# Verify Python can find it
.venv\Scripts\python.exe -c "from data_science.agent import root_agent; print(root_agent)"
```

### Issue 2: Environment variable errors

**Symptom:**
```
DATASET_CONFIG_FILE env var not set
```

**Solution:**
```powershell
# Set in PowerShell session
$env:DATASET_CONFIG_FILE='./forecasting_sticker_sales_dataset_config.json'

# Or ensure .env file is in agents/data_science/
cd agents\data_science
if (-not (Test-Path .env)) {
    copy .env.example .env
    notepad .env  # Configure values
}
```

### Issue 3: BigQuery permission errors

**Symptom:**
```
403 Forbidden: BigQuery API has not been enabled
```

**Solution:**
```powershell
# Enable BigQuery API
gcloud services enable bigquery.googleapis.com --project=your-project-id

# Grant permissions to your user account
gcloud projects add-iam-policy-binding your-project-id `
    --member=user:your-email@example.com `
    --role=roles/bigquery.user
```

### Issue 4: Code Interpreter extension creation fails

**Symptom:**
```
Failed to create Code Interpreter extension
```

**Solution:**
```powershell
# Enable required APIs
gcloud services enable aiplatform.googleapis.com --project=your-project-id

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id `
    --member=user:your-email@example.com `
    --role=roles/aiplatform.user
```

---

## Next Steps

### Immediate (Today)
- ✅ Import data-science agent
- ✅ Test with sample dataset
- ✅ Integrate with root agent

### This Week
- [ ] Create custom `orkhon_dnb_config.json` for your BigQuery data
- [ ] Test queries against real DNB Statistics/Public Register data
- [ ] Build first cross-domain workflow (DNB API → Data Science)

### Next Week
- [ ] Add AlloyDB integration (if needed)
- [ ] Set up BQML RAG corpus (if using ML features)
- [ ] Create Orkhon-specific sub-agents (DNB Insights, Compliance, etc.)

### Month 1
- [ ] Production deployment (Cloud Run or Agent Engine)
- [ ] Custom evaluation datasets for Orkhon use cases
- [ ] Performance optimization (caching, prompt tuning)

---

## Resources

- **Original ADK Sample:** https://github.com/google/adk-samples/tree/main/python/agents/data-science
- **Video Walkthrough:** https://www.youtube.com/watch?v=efcUXoMX818
- **Integration Plan:** `backend/INTEGRATION_PLAN.md`
- **ADK Docs:** https://google.github.io/adk-docs

---

## Pattern for Adopting Other ADK Samples

This same git subtree approach works for **any** ADK sample:

```powershell
# General pattern
git subtree add --prefix=backend/adk/agents/{AGENT_NAME} `
    adk-samples main:python/agents/{AGENT_NAME} `
    --squash
```

**Recommended agents to adopt:**
- `financial-advisor` - Financial domain expertise
- `customer-service` - Multi-turn conversations
- `RAG` - Document Q&A with vector search
- `llm-auditor` - Agent evaluation and monitoring

**Key principle:** Start with official samples, customize for Orkhon, stay sync'd with upstream. Don't reinvent the wheel! 🚀
