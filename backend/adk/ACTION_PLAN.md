# ACTION PLAN: Adopt Data-Science Agent Today

> **30-minute implementation guide to get data-science agent running in Orkhon**

---

## ⏰ Timeline

- **0-10 min:** Import agent via git subtree
- **10-20 min:** Configure environment and dependencies
- **20-25 min:** Test in isolation
- **25-30 min:** Integrate with root agent

**Total: 30 minutes to working data-science capabilities** 🚀

---

## 📋 Prerequisites

✅ Orkhon project cloned and working  
✅ `uv` package manager installed  
✅ GCP project with BigQuery enabled  
✅ Terminal open in PowerShell  

---

## 🚀 Step 1: Verify Existing Agent (2 min)

**✅ GOOD NEWS: You already have the data_science agent!**

```powershell
# Verify existing agent
cd C:\Users\rjjaf\_Projects\orkhon
ls backend\adk\agents\data_science
```

**You should see:**
- ✅ `agent.py` - Main agent file
- ✅ `sub_agents/` - Specialized sub-agents
- ✅ `tools.py` - Agent tools
- ✅ `utils/` - Utility functions
- ✅ `dnb_datasets_config.json` - **Your custom Orkhon config** 🎯
- ✅ `QUICKSTART.md` - **Your custom docs** 🎯

**Decision: Keep your custom version!** You've already adapted it for Orkhon.

### Optional: Compare with Upstream

If you want to check what features upstream has that you might want to adopt:

```powershell
# Add adk-samples remote (one-time setup)
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples

# See differences (read-only, safe)
git diff dev adk-samples/main:python/agents/data-science/agent.py -- backend/adk/agents/data_science/agent.py

# Or view upstream version
git show adk-samples/main:python/agents/data-science/agent.py | more
```

**Note:** Since you already have a working version, **SKIP the import step** and proceed to configuration.

---

## 🤔 Your Situation: Already Have Custom data_science Agent

### What You Have (Orkhon Custom Version)
- ✅ **Custom dataset config** - `dnb_datasets_config.json` (not in upstream)
- ✅ **Orkhon-specific docs** - `QUICKSTART.md` 
- ✅ **Already integrated** - Imports and structure match your project
- ✅ **Working code** - Tested in your environment

### What Upstream Has (ADK Official Sample)
- ✅ **AlloyDB support** - MCP Toolbox integration (optional)
- ✅ **CHASE-SQL method** - Advanced NL2SQL (you might want this)
- ✅ **BQML RAG pipeline** - Reference guide ingestion (optional)
- ✅ **W&B Weave tracing** - OpenTelemetry integration (optional)
- ✅ **Cloud Run deployment** - Production configs (useful later)

### Recommended Path Forward

**Option A: Keep Your Custom Version (Recommended)**
- ✅ **Pros:** Already working, Orkhon-specific, no merge conflicts
- ❌ **Cons:** Manual effort to adopt upstream features

**Option B: Replace with Upstream + Re-apply Customizations**
- ✅ **Pros:** Get all upstream features immediately
- ❌ **Cons:** Need to re-apply `dnb_datasets_config.json` and other customizations
- ❌ **Risk:** Lose Orkhon-specific changes

**Option C: Hybrid (Cherry-pick Features)**
- ✅ **Pros:** Keep customizations, selectively adopt upstream features
- ❌ **Cons:** More manual work

**Decision: Go with Option A** ✅ Your version is already integrated and working!

### If You Want to Adopt Upstream Features Later

```powershell
# Compare specific files
git diff dev adk-samples/main:python/agents/data-science/<FILE> -- backend/adk/agents/data_science/<FILE>

# Cherry-pick specific features manually
# (Copy code snippets you want from upstream into your version)
```

---

## 🔧 Step 2: Install Dependencies (5 min)

```powershell
cd backend\adk

# Install data-science dependencies
uv sync

# Verify installation
.venv\Scripts\python.exe -c "import pandas; import sqlglot; print('✅ Dependencies OK')"
```

---

## ⚙️ Step 3: Configure Environment (10 min)

### 3.1: Create .env File

```powershell
# Copy example config
copy agents\data_science\.env.example agents\data_science\.env

# Edit with your settings
notepad agents\data_science\.env
```

### 3.2: Set Required Variables

**Minimal configuration for BigQuery-only:**

```bash
# ============================================================================
# Model Backend
# ============================================================================
GOOGLE_GENAI_USE_VERTEXAI=1

# ============================================================================
# GCP Configuration
# ============================================================================
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# ============================================================================
# BigQuery Configuration
# ============================================================================
BQ_DATA_PROJECT_ID=your-gcp-project-id
BQ_COMPUTE_PROJECT_ID=your-gcp-project-id
BQ_DATASET_ID=dnb_statistics

# ============================================================================
# Dataset Configuration
# ============================================================================
# Use sample dataset first (comes with agent)
DATASET_CONFIG_FILE='./forecasting_sticker_sales_dataset_config.json'

# Or use your DNB data (requires creating config file)
# DATASET_CONFIG_FILE='./orkhon_dnb_config.json'

# ============================================================================
# NL2SQL Method
# ============================================================================
NL2SQL_METHOD='BASELINE'

# ============================================================================
# Agent Model
# ============================================================================
ROOT_AGENT_MODEL='gemini-2.0-flash-exp'

# ============================================================================
# Extensions (leave empty for auto-creation)
# ============================================================================
CODE_INTERPRETER_EXTENSION_NAME=''
BQML_RAG_CORPUS_NAME=''

# ============================================================================
# Optional: W&B Weave Tracing (skip for now)
# ============================================================================
# WANDB_PROJECT_ID=''
# WANDB_API_KEY=''
```

**Save and close the file.**

### 3.3: Load Sample Data (Optional)

**If using sample dataset:**
```powershell
cd agents\data_science

# Load forecasting_sticker_sales into BigQuery
..\..\.venv\Scripts\python.exe data_science\utils\create_bq_table.py

cd ..\..
```

**If using existing DNB data, skip this step.**

---

## ✅ Step 4: Test in Isolation (5 min)

```powershell
cd backend\adk

# Run data-science agent
uv run adk run agents/data_science
```

**Test queries:**
```
1. "What datasets do you have access to?"
2. "Show me the schema for the main table"
3. "Query the top 5 records"
```

**Expected behavior:**
- Agent should respond with dataset information
- Should show table schema
- Should execute queries successfully

**Troubleshooting:**
- If "DATASET_CONFIG_FILE not set" → Check `.env` file exists in `agents/data_science/`
- If BigQuery errors → Verify GCP project and credentials
- If import errors → Run `uv sync` again

---

## 🔗 Step 5: Integrate with Root Agent (5 min)

### 5.1: Update Root Agent

Edit `backend/adk/agents/root_agent/agent.py`:

```python
def get_root_agent() -> Agent:
  """Creates the root agent with sub-agents for API coordination."""
  
  # ... existing imports ...
  
  # ADD THIS IMPORT
  from data_science.agent import root_agent as data_science_coordinator
  
  dnb_coordinator = get_dnb_coordinator_agent()
  
  # Model configuration from environment
  model_name = os.environ.get("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash-exp")
  
  # Build the root agent with ALL coordinators
  root = Agent(
      model=model_name,
      name="root_agent",
      instruction="""You are the Root Orchestrator for the Orkhon system.
          
Your role is to:
1. Understand the user's query and intent
2. Delegate to the appropriate coordinator agent:
   - dnb_coordinator: For DNB API queries (Echo, Statistics, Public Register)
   - data_science_coordinator: For data analysis, BigQuery, and analytics
3. Present results clearly to the user
4. Handle errors gracefully

When routing queries:
- DNB API operations → dnb_coordinator
- Data science operations → data_science_coordinator
- Multi-domain workflows → chain coordinators sequentially

Always explain what you're doing and why.
""",
      description="System root orchestrator for Orkhon multi-agent system",
      sub_agents=[
          dnb_coordinator,
          data_science_coordinator  # ← ADDED
      ]
  )

  return root
```

### 5.2: Test Integrated System

```powershell
cd backend\adk

# Run from root agent
uv run adk run agents/root_agent
```

**Test integrated query:**
```
"Query the dnb_statistics dataset for top 5 records and show me the results"
```

**Expected behavior:**
- Root agent → routes to data_science_coordinator
- Data science coordinator → delegates to bigquery_agent
- Results returned with proper formatting

---

## 🎯 Success Criteria

After completing these steps, you should have:

✅ **Data-science agent verified** (already exists - your custom version!)  
✅ **Dependencies installed** and verified  
✅ **Environment configured** with BigQuery access  
✅ **Agent working in isolation** (tested with queries)  
✅ **Integrated with root agent** (routing works)  
✅ **Git committed** with clear commit messages

**Note:** Since you already have a custom data_science agent, most work is configuration and integration, not importing!  

---

## 📊 Current Architecture

```
backend/adk/agents/
├── root_agent/                     # L1: System Root ✅
│   └── agent.py                    # ← MODIFIED
│
├── api_coordinators/               # L2: Domain Coordinators
│   └── dnb_coordinator/ ✅
│
├── data_science/                   # L2: Domain Coordinator ✅ NEW!
│   ├── agent.py                    # Root DS agent
│   ├── sub_agents/                 # L3: Specialists
│   │   ├── bigquery/               # BigQuery NL2SQL ✅
│   │   ├── alloydb/                # AlloyDB NL2SQL (optional)
│   │   ├── data_science/           # NL2Py analytics ✅
│   │   └── bqml_agent.py           # BQML ML training ✅
│   ├── tools.py
│   ├── utils/
│   └── .env                        # ← CREATED
│
└── api_agents/                     # L3: Specialists
    ├── dnb_echo_agent/ ✅
    ├── dnb_statistics_agent/ ✅
    └── dnb_public_register_agent/ ✅
```

**Agent count: 10 agents** (was 8, added 2 data science specialists)

---

## 🐛 Common Issues & Quick Fixes

### Issue 1: Git subtree fails

**Error:**
```
fatal: refusing to merge unrelated histories
```

**Fix:**
```powershell
git subtree add --prefix=backend/adk/agents/data_science `
    adk-samples main:python/agents/data-science `
    --squash --allow-unrelated-histories
```

### Issue 2: Import errors

**Error:**
```
ImportError: No module named 'data_science'
```

**Fix:**
```powershell
# Ensure __init__.py exists
New-Item -ItemType File -Force backend\adk\agents\data_science\__init__.py

# Verify Python path
cd backend\adk
.venv\Scripts\python.exe -c "import sys; print('\n'.join(sys.path))"
```

### Issue 3: Environment variables not loaded

**Error:**
```
DATASET_CONFIG_FILE env var not set
```

**Fix:**
```powershell
# Ensure .env file is in correct location
ls agents\data_science\.env

# If missing, copy from example
copy agents\data_science\.env.example agents\data_science\.env

# Verify it's being loaded
cd agents\data_science
..\..\..\.venv\Scripts\python.exe -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DATASET_CONFIG_FILE'))"
```

### Issue 4: BigQuery permission denied

**Error:**
```
403 Forbidden: BigQuery API has not been enabled
```

**Fix:**
```powershell
# Enable BigQuery API
gcloud services enable bigquery.googleapis.com --project=your-project-id

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id `
    --member=user:your-email@example.com `
    --role=roles/bigquery.user

gcloud projects add-iam-policy-binding your-project-id `
    --member=user:your-email@example.com `
    --role=roles/bigquery.dataViewer
```

---

## 📝 Commit Messages

```powershell
# After completing integration
git add .
git commit -m "feat(adk): Integrate data-science agent with Orkhon

- Import data-science agent via git subtree from adk-samples
- Configure environment for BigQuery access
- Update root_agent to include data_science_coordinator
- Test integration with DNB data sources

Resolves: #[issue-number]
"
git push origin dev
```

---

## 🎓 What You've Gained

### Immediate Capabilities

✅ **NL2SQL** - Natural language → SQL queries  
✅ **NL2Py** - Natural language → Python data analysis  
✅ **Visualization** - Automatic chart generation  
✅ **Cross-dataset joins** - Query multiple data sources  
✅ **Code execution** - Vertex AI Code Interpreter  

### Production Features

✅ **Testing framework** - Comprehensive test suite  
✅ **Evaluation datasets** - Quality assurance  
✅ **Deployment configs** - Cloud Run ready  
✅ **Tracing** - OpenTelemetry support  
✅ **Session management** - Persistent conversations  

### Time Saved

**Estimated development effort if built from scratch:**
- NL2SQL engine: 2-3 weeks
- NL2Py analytics: 2 weeks
- Code Interpreter integration: 1 week
- BQML agent: 1-2 weeks
- Testing framework: 1 week
- Deployment: 1 week

**Total: 8-10 weeks of engineering effort** ⏰

**Time to integrate: 30 minutes** ⚡

**ROI: ~1200x time savings** 🚀

---

## 📚 Next Steps

### Today (After 30-min setup)
- [ ] Test with sample dataset queries
- [ ] Create custom `orkhon_dnb_config.json` for your data
- [ ] Update root agent instructions for better routing

### This Week
- [ ] Test with real DNB Statistics/Public Register data
- [ ] Build first cross-domain workflow (DNB API → Data Science)
- [ ] Add Orkhon-specific tools/sub-agents

### Next Week
- [ ] Add AlloyDB integration (if needed)
- [ ] Set up BQML RAG corpus (if using ML)
- [ ] Create evaluation datasets for Orkhon use cases

### Month 1
- [ ] Production deployment (Cloud Run or Agent Engine)
- [ ] Performance optimization (caching, prompt tuning)
- [ ] Adopt additional samples (financial-advisor, customer-service)

---

## 📖 Reference Documents

- **Integration Plan:** `backend/INTEGRATION_PLAN.md` (comprehensive 3-phase plan)
- **Adoption Strategy:** `backend/adk/ADOPTION_STRATEGY.md` (general pattern for all samples)
- **Original Sample README:** `backend/adk/agents/data_science/README.md` (full documentation)
- **ADK Docs:** https://google.github.io/adk-docs

---

## 🎉 Congratulations!

You've successfully adopted a production-grade data-science agent in 30 minutes!

**What's possible now:**
```
User: "Query the DNB Statistics dataset for top 10 insurance companies by total assets, 
       then create a bar chart showing the distribution."

Root Agent → Data Science Coordinator → BigQuery Agent (NL2SQL)
                                      → Analytics Agent (NL2Py + visualization)

Result: SQL query executed, data analyzed, chart generated ✅
```

**Keep the momentum going!** 🚀

Adopt more samples:
- `financial-advisor` - Financial domain expertise
- `customer-service` - Multi-turn conversations
- `RAG` - Document Q&A with vector search

**Remember:** Don't reinvent the wheel. Build on the shoulders of giants! 🏔️
