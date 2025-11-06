# Data Science Agent Integration Plan

## Overview

This document outlines the strategy for integrating the official ADK `data-science` sample into the Orkhon project while maintaining sync with upstream updates.

---

## Integration Strategy: Git Subtree

### Why Git Subtree?

- ✅ **Upstream sync**: Pull updates when ADK improves the data-science agent
- ✅ **Local customization**: Modify for Orkhon without losing upstream tracking
- ✅ **Clean deployment**: No submodule complexity (code is part of the repo)
- ✅ **Proven approach**: Already using this pattern with other upstream repos

### Setup Commands

```powershell
# Navigate to orkhon root
cd C:\Users\rjjaf\_Projects\orkhon

# Add adk-samples as a remote (if not already added)
git remote add adk-samples-upstream https://github.com/google/adk-samples.git

# Initial import: Add data-science as subtree
git subtree add --prefix=backend/adk/agents/data_science \
    adk-samples-upstream main:python/agents/data-science \
    --squash

# Later: Pull updates from upstream
git subtree pull --prefix=backend/adk/agents/data_science \
    adk-samples-upstream main:python/agents/data-science \
    --squash

# Push local changes back upstream (optional, if contributing)
git subtree push --prefix=backend/adk/agents/data_science \
    adk-samples-upstream feature/orkhon-improvements
```

---

## What the Data-Science Sample Provides

### 🎯 Production-Grade Multi-Agent System

**Architecture (4 specialized sub-agents):**
- **BigQuery Agent** - NL2SQL with CHASE-SQL methodology
- **AlloyDB Agent** - NL2SQL with MCP Toolbox integration
- **Data Science Agent** - NL2Py with Vertex AI Code Interpreter
- **BQML Agent** - ML training/evaluation with RAG reference guide

### 🏗️ Critical Infrastructure Components

1. **Dataset Configuration System**
   - JSON-based config files (`flights_dataset_config.json`, etc.)
   - Support for multiple data sources (BigQuery, AlloyDB, extensible)
   - Cross-dataset key relationships for joins
   - Runtime dataset switching

2. **NL2SQL Engine**
   - Two methods: Direct Gemini or CHASE-SQL (research-backed)
   - Dynamic schema discovery
   - Query validation and optimization

3. **Code Execution**
   - Vertex AI Code Interpreter extension integration
   - Automatic extension provisioning
   - File/artifact handling (base64 encoding)

4. **RAG Pipeline**
   - Vertex AI RAG Engine integration
   - BQML reference guide ingestion
   - Automatic corpus management

5. **Observability**
   - OpenTelemetry integration
   - OTLP export to W&B Weave
   - Structured logging throughout

6. **Testing Framework**
   - Unit tests for all agents
   - Integration tests
   - Evaluation dataset support
   - pytest configuration

7. **Deployment**
   - Cloud Run configuration
   - Agent Engine deployment scripts
   - Cloud SQL session storage
   - IAM permission setup

### 📊 Sample Datasets

1. **Forecasting Sticker Sales** (BigQuery only)
   - Train/test split for ML
   - Ready for BQML forecasting models

2. **Cymbal Flights** (BigQuery + AlloyDB)
   - Cross-database queries
   - Realistic multi-source scenario
   - Flight history, policies, ticket sales

---

## Adaptation Plan for Orkhon

### Phase 1: Initial Integration (Week 1)

**Goal:** Get data-science agent running alongside existing Orkhon agents

```
backend/adk/agents/
├── root_agent/              # EXISTING - System orchestrator
├── api_coordinators/        # EXISTING - DNB coordinator
│   └── dnb_coordinator/
├── api_agents/              # EXISTING - DNB leaf agents
│   ├── dnb_echo_agent/
│   ├── dnb_statistics_agent/
│   └── dnb_public_register_agent/
└── data_science/            # NEW - From ADK sample via subtree
    ├── agent.py             # Root DS agent
    ├── sub_agents/          # 4 sub-agents
    ├── tools.py
    ├── utils/
    └── pyproject.toml
```

**Tasks:**
1. ✅ Import data-science via git subtree
2. ✅ Update `root_agent/agent.py` to include data_science coordinator
3. ✅ Configure environment variables in `backend/adk/.env`
4. ✅ Test data-science agent in isolation: `adk run data_science`
5. ✅ Test full system: `adk run root_agent`

### Phase 2: BigQuery Integration (Week 2)

**Goal:** Connect data-science agent to Orkhon's BigQuery data warehouse

**Tasks:**
1. ✅ Verify BigQuery datasets exist (from ETL pipelines)
2. ✅ Create dataset config for DNB Statistics data
   ```json
   {
     "datasets": [{
       "type": "bigquery",
       "name": "dnb_statistics",
       "description": "DNB Statistics API data: insurance, pensions, market data"
     }],
     "cross_dataset_relations": {
       "foreign_keys": []
     }
   }
   ```
3. ✅ Create dataset config for DNB Public Register data
4. ✅ Test queries against real DNB data

### Phase 3: Custom Orkhon Dataset Configs (Week 3)

**Goal:** Build Orkhon-specific dataset configurations

**New configs to create:**
- `backend/adk/agents/data_science/orkhon_dnb_statistics_config.json`
- `backend/adk/agents/data_science/orkhon_dnb_public_register_config.json`
- `backend/adk/agents/data_science/orkhon_combined_config.json` (with cross-dataset relations)

**Cross-dataset possibilities:**
```json
{
  "cross_dataset_relations": {
    "foreign_keys": [
      {
        "child": {
          "type": "bigquery",
          "dataset": "dnb_public_register",
          "table": "entities",
          "column": "entity_id"
        },
        "parent": {
          "type": "bigquery",
          "dataset": "dnb_statistics",
          "table": "insurance_companies",
          "column": "entity_id"
        }
      }
    ]
  }
}
```

### Phase 4: MCP Toolbox Integration (Week 4)

**Goal:** Connect data-science AlloyDB agent to Orkhon's existing Toolbox

**Current state:**
- ✅ Orkhon already has GenAI Toolbox running (port 5000)
- ✅ Already configured with DNB APIs as tools
- ✅ Jaeger tracing enabled

**Integration:**
1. ✅ Configure AlloyDB connection in Toolbox
   - Update `backend/toolbox/config/dev/40-alloydb.yaml` (new file)
   - Add AlloyDB credentials to `.env`
2. ✅ Test AlloyDB agent via MCP Toolbox
3. ✅ Enable cross-database queries (BigQuery ↔ AlloyDB)

### Phase 5: Custom Sub-Agents (Ongoing)

**Goal:** Extend data-science with Orkhon-specific capabilities

**Potential new sub-agents:**
- **DNB Insights Agent** - Domain-specific analytics for financial regulation
- **Compliance Agent** - Cross-reference Public Register with Statistics data
- **Forecasting Agent** - Specialized time-series for financial data

**Pattern to follow:**
```python
# backend/adk/agents/data_science/sub_agents/dnb_insights.py

from google.adk.agents import Agent

dnb_insights_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="dnb_insights_agent",
    instruction="""You specialize in Dutch financial regulatory analysis.
    
    You have access to:
    - DNB Public Register (entities, publications)
    - DNB Statistics (insurance, pensions, market data)
    
    Provide insights on regulatory compliance and market trends.""",
    tools=[...]
)
```

---

## Directory Structure After Integration

```
backend/adk/agents/
├── root_agent/
│   ├── __init__.py
│   └── agent.py                # MODIFY: Import data_science coordinator
├── api_coordinators/
│   └── dnb_coordinator/
│       ├── __init__.py
│       └── agent.py
├── api_agents/
│   ├── dnb_echo_agent/
│   ├── dnb_statistics_agent/
│   └── dnb_public_register_agent/
└── data_science/               # NEW: From ADK sample (git subtree)
    ├── __init__.py
    ├── agent.py                # Root DS agent (becomes coordinator)
    ├── pyproject.toml
    ├── README.md
    ├── .env.example
    ├── sub_agents/             # 4 specialized agents
    │   ├── __init__.py
    │   ├── bqml_agent.py
    │   ├── bigquery/
    │   │   ├── agent.py
    │   │   └── tools.py
    │   ├── alloydb/
    │   │   ├── agent.py
    │   │   └── tools.py
    │   └── data_science/
    │       ├── agent.py
    │       └── tools.py
    ├── tools.py
    ├── prompts.py
    ├── utils/
    ├── tests/
    ├── eval/
    ├── deployment/
    ├── orkhon_dnb_statistics_config.json      # NEW: Orkhon-specific
    ├── orkhon_dnb_public_register_config.json # NEW: Orkhon-specific
    └── orkhon_combined_config.json            # NEW: Cross-dataset
```

---

## Environment Variable Setup

### Required Variables (Add to `backend/adk/.env`)

```bash
# ============================================================================
# Data Science Agent Configuration
# ============================================================================

# Dataset configuration
DATASET_CONFIG_FILE='./agents/data_science/orkhon_dnb_statistics_config.json'

# Model backend
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT='your-gcp-project'
GOOGLE_CLOUD_LOCATION='us-central1'

# BigQuery configuration
BQ_DATA_PROJECT_ID='your-gcp-project'
BQ_COMPUTE_PROJECT_ID='your-gcp-project'
BQ_DATASET_ID='dnb_statistics'  # or 'dnb_public_register'

# AlloyDB configuration (optional, for Phase 4)
ALLOYDB_CLUSTER='your-cluster'
ALLOYDB_INSTANCE='your-instance'
ALLOYDB_DATABASE='orkhon_data'
ALLOYDB_HOSTNAME='localhost'  # or instance IP
ALLOYDB_PORT='5432'
ALLOYDB_USER='postgres'
ALLOYDB_PASSWORD='your-password'

# MCP Toolbox (already configured in Orkhon)
MCP_TOOLBOX_HOST='localhost:5000'

# Code Interpreter (optional, created on first run)
CODE_INTERPRETER_EXTENSION_NAME=''

# BQML RAG Corpus (optional, created by setup script)
BQML_RAG_CORPUS_NAME=''

# NL2SQL method: 'BASELINE' (Gemini) or 'CHASE' (CHASE-SQL)
NL2SQL_METHOD='BASELINE'

# Root agent model
ROOT_AGENT_MODEL='gemini-2.0-flash-exp'

# W&B Weave tracing (optional)
WANDB_PROJECT_ID='your-wandb-project'
WANDB_API_KEY='your-wandb-key'
```

---

## Testing Strategy

### 1. Isolated Data Science Agent Test

```powershell
cd backend/adk
uv run adk run agents/data_science
```

**Test queries:**
- "What datasets do you have access to?"
- "Show me the schema for dnb_statistics"
- "Query the top 5 insurance companies by total assets"
- "Create a bar chart of market data trends"

### 2. Integrated System Test

```powershell
cd backend/adk
uv run adk run agents/root_agent
```

**Test queries:**
- "Query DNB Statistics for pension fund data, then create a visualization"
- "Get entity information from Public Register and cross-reference with Statistics data"
- "What are the top insurance trends based on DNB data?"

### 3. Cross-Dataset Test (Phase 4)

**Test query:**
```
"Find all insurance entities in the Public Register, then show their financial 
statistics from the Statistics dataset, and create a comparative analysis chart."
```

This requires:
1. DNB coordinator → Public Register agent (get entity IDs)
2. Data Science coordinator → BigQuery agent (query statistics)
3. Data Science coordinator → Analytics agent (create chart)

---

## Dependencies Management

### Approach: Unified Dependencies

**Decision:** Merge data-science dependencies into root `pyproject.toml`

**Rationale:**
- Simpler development (one virtual environment)
- Easier deployment (single wheel file)
- Consistent dependency resolution

**Steps:**
1. Copy dependencies from `data_science/pyproject.toml` to `backend/adk/pyproject.toml`
2. Run `uv sync` in `backend/adk`
3. Keep `data_science/pyproject.toml` as reference (don't delete)

**Updated `backend/adk/pyproject.toml`:**
```toml
[project]
name = "orkhon-adk"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Existing Orkhon deps
    "google-adk>=1.14",
    "python-dotenv>=1.0.1",
    
    # From data-science sample
    "immutabledict>=4.2.1",
    "sqlglot>=26.10.1",
    "db-dtypes>=1.4.2",
    "regex>=2024.11.6",
    "tabulate>=0.9.0",
    "google-cloud-aiplatform[adk,agent-engines]>=1.93.0",
    "absl-py>=2.2.2",
    "pydantic>=2.11.3",
    "pandas>=2.3.0",
    "numpy>=2.3.1",
    "toolbox-core>=0.3.0",
    "opentelemetry-sdk>=1.36.0",
    "opentelemetry-exporter-otlp-proto-http>=1.36.0",
    "pg8000>=1.31.2",
]

[project.optional-dependencies]
dev = [
    "google-cloud-aiplatform[adk,agent-engines,evaluation]>=1.93.0",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
    "google-adk[eval]>=1.14",
    "black>=25.9.0",
]
```

---

## Maintenance Strategy

### Pulling Upstream Updates

```powershell
# Check for updates in adk-samples
cd C:\Users\rjjaf\_Projects\adk-samples
git pull origin main

# Pull updates into Orkhon (from orkhon root)
cd C:\Users\rjjaf\_Projects\orkhon
git subtree pull --prefix=backend/adk/agents/data_science \
    adk-samples-upstream main:python/agents/data-science \
    --squash
```

### Handling Merge Conflicts

If Orkhon has local customizations:
1. Review conflicts carefully
2. Prefer upstream changes for core logic
3. Keep Orkhon customizations for:
   - Dataset configs (`orkhon_*.json`)
   - Custom sub-agents
   - Environment-specific settings

### Contributing Back Upstream

If Orkhon improvements are generally useful:
```powershell
# Push changes to upstream (create PR)
git subtree push --prefix=backend/adk/agents/data_science \
    adk-samples-upstream feature/orkhon-cross-dataset-improvements
```

---

## Success Metrics

### Phase 1: Integration Complete
- ✅ Data-science agent runs in isolation
- ✅ Root agent delegates to data-science coordinator
- ✅ All 4 sub-agents functional

### Phase 2: BigQuery Integration Complete
- ✅ Queries against DNB Statistics successful
- ✅ Queries against DNB Public Register successful
- ✅ Visualizations generated correctly

### Phase 3: Custom Configs Complete
- ✅ Orkhon dataset configs created
- ✅ Cross-dataset queries working
- ✅ Domain-specific instructions effective

### Phase 4: Full System Integration
- ✅ AlloyDB connected via MCP Toolbox
- ✅ Cross-database queries (BigQuery ↔ AlloyDB)
- ✅ End-to-end workflows (DNB APIs → Analytics)

---

## Risk Mitigation

### Risk 1: Dependency Conflicts
**Mitigation:** Use `uv sync` with lock file, test in clean environment

### Risk 2: Breaking Changes in Upstream
**Mitigation:** Pin to stable ADK versions, test before pulling updates

### Risk 3: Orkhon Customizations Lost
**Mitigation:** Keep customizations in separate files (`orkhon_*.py`, `orkhon_*.json`)

### Risk 4: Performance Issues
**Mitigation:** Monitor with Jaeger, use BigQuery query caching, optimize prompts

---

## Next Steps

1. **Immediate (Today):**
   - Review this plan with team
   - Set up git subtree remote
   - Import data-science agent

2. **This Week (Phase 1):**
   - Get data-science running
   - Update root_agent to include it
   - Test in ADK Web UI

3. **Next Week (Phase 2):**
   - Create Orkhon dataset configs
   - Test BigQuery queries
   - Create first custom workflows

4. **Month 1 (Phases 3-4):**
   - Full MCP Toolbox integration
   - Custom sub-agents
   - Production deployment planning

---

## Questions to Answer

1. **AlloyDB:** Do we need AlloyDB, or is BigQuery sufficient initially?
   - Recommendation: Start with BigQuery only (simpler), add AlloyDB later if needed

2. **Code Interpreter:** Do we need Vertex AI Code Interpreter?
   - Recommendation: Yes, for NL2Py data analysis (plotting, pandas operations)

3. **BQML:** Do we need ML training capabilities?
   - Recommendation: Maybe later, focus on queries/analytics first

4. **W&B Weave:** Do we need this tracing?
   - Recommendation: No, we already have Jaeger (sufficient for now)

---

## Conclusion

The ADK data-science sample provides **immense value** that would take weeks to build from scratch. The git subtree approach lets us leverage this while maintaining Orkhon customizations and staying sync'd with upstream improvements.

**Total Estimated Effort:**
- Phase 1 (Integration): 1-2 days
- Phase 2 (BigQuery): 2-3 days  
- Phase 3 (Custom Configs): 3-5 days
- Phase 4 (Full Integration): 5-7 days

**Total: 2-3 weeks to production-ready data science capabilities** 🚀
