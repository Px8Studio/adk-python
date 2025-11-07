# ADK Samples Integration Guide

## TL;DR: Git Subtree Strategy

**Use git subtree to import official ADK samples into Orkhon.**

✅ **Advantages:**
- Seamless upstream sync (pull updates easily)
- Self-contained (no external dependencies in deployment)
- Clear history (see what came from upstream vs local changes)
- Local customization (modify without breaking sync)

❌ **Not submodules** (deployment complexity, team confusion)  
❌ **Not manual copy** (lost history, no sync path)

---

## Quick Start: Adopt `data-science` Agent

### 1. Import via Git Subtree

```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\backend\scripts\adopt-adk-sample.ps1 -SampleName "data-science"
```

This imports the entire `data-science` agent from [google/adk-samples](https://github.com/google/adk-samples) to:
```
C:\Users\rjjaf\_Projects\orkhon\backend\adk\agents\data-science\
```

### 2. Configure for Orkhon

```powershell
cd backend\adk\agents\data-science

# Copy example environment
copy .env.example .env

# Edit with Orkhon-specific values
notepad .env
```

**Critical settings for Orkhon:**
```bash
# Vertex AI Backend
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=orkhon-dev
GOOGLE_CLOUD_LOCATION=europe-west1

# BigQuery Configuration
BQ_DATA_PROJECT_ID=orkhon-dev
BQ_COMPUTE_PROJECT_ID=orkhon-dev
BQ_DATASET_ID=dnb_statistics  # Or flights_dataset for sample data

# Dataset Configuration
DATASET_CONFIG_FILE=./orkhon_dnb_config.json  # Create this (see below)

# NL2SQL Method
NL2SQL_METHOD=BASELINE  # Options: BASELINE or CHASE

# Skip AlloyDB for now (DNB data is all in BigQuery)
# (Leave AlloyDB settings blank unless you need cross-database queries)
```

### 3. Create Orkhon Dataset Configuration

```powershell
# Create custom config for DNB datasets
@"
{
  "datasets": [
    {
      "type": "bigquery",
      "dataset_id": "dnb_statistics",
      "description": "DNB Statistics API data: insurance companies, pensions, market data, financial indicators. Contains detailed financial metrics and regulatory compliance data for Dutch financial institutions."
    },
    {
      "type": "bigquery",
      "dataset_id": "dnb_public_register",
      "description": "DNB Public Register: regulated entities, publications, supervisory actions. Contains entity information, registration details, and published regulatory documents."
    }
  ],
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
          "table": "insurance_statistics",
          "column": "entity_id"
        }
      }
    ]
  }
}
"@ | Out-File -FilePath agents\data-science\orkhon_dnb_config.json -Encoding utf8
```

### 4. Install Dependencies

```powershell
cd backend\adk

# Sync all dependencies (includes data-science requirements)
uv sync
```

### 5. Test the Agent

```powershell
# Test in isolation first
cd backend\adk
.\.venv\Scripts\Activate.ps1
adk run agents/data-science
```

**Try these queries:**
```
What datasets do you have access to?

Query the dnb_statistics dataset for the top 10 insurance companies by total assets

Create a bar chart showing the asset distribution
```

### 6. Integrate with Root Agent

```powershell
notepad agents\root_agent\agent.py
```

**Add these lines:**

```python
# At the top (with other imports)
from ..data_science.agent import get_root_agent as get_data_science_agent

# Create instance
data_science_agent = get_data_science_agent()

# In root_agent definition, add to sub_agents:
root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are the Orkhon Root Agent...""",
    sub_agents=[
        dnb_coordinator,
        data_science_agent,  # ← Add this
        # ... other sub-agents
    ]
)
```

### 7. Test Integrated System

```powershell
adk run agents/root_agent
```

**Try cross-domain queries:**
```
Get a list of all insurance entities from DNB Public Register, 
then query their total assets from DNB Statistics, 
and create a visualization showing the top 15 by assets

Query dnb_statistics for trends in pension fund assets over time,
then create a line chart showing the trend
```

### 8. Commit the Integration

```powershell
git add .
git commit -m "feat(adk): Integrate data-science agent from ADK samples

- Import via git subtree for easy upstream sync
- Configure for dnb_statistics and dnb_public_register datasets
- Integrate with root_agent for unified query interface
- Add Orkhon-specific dataset configuration"

git push origin dev
```

---

## Directory Structure After Adoption

```
backend/adk/agents/
├── root_agent/
│   ├── agent.py                    # Modified: imports data-science agent
│   └── __init__.py
│
├── api_coordinators/               # Orkhon custom
│   └── dnb_coordinator/
│
├── api_agents/                     # Orkhon custom
│   ├── dnb_echo_agent/
│   ├── dnb_statistics_agent/
│   └── dnb_public_register_agent/
│
└── data_science/                   # ← Imported via git subtree
    ├── agent.py                    # Upstream: Multi-agent coordinator
    ├── data_science/               # Upstream: Sub-agents (BQ, BQML, Analytics)
    │   ├── __init__.py
    │   ├── agents/
    │   │   ├── bigquery_agent.py
    │   │   ├── bqml_agent.py
    │   │   ├── ds_agent.py
    │   │   └── alloydb_agent.py (skip if not using AlloyDB)
    │   └── utils/
    ├── tests/                      # Upstream: Agent tests
    ├── eval/                       # Upstream: Evaluation suite
    ├── deployment/                 # Upstream: Deployment scripts
    ├── pyproject.toml              # Upstream: Dependencies
    ├── README.md                   # Upstream: Documentation
    ├── .env.example                # Upstream: Config template
    ├── .env                        # Local: Your config (gitignored)
    └── orkhon_dnb_config.json      # Local: Orkhon dataset config
```

**Key Points:**
- **Upstream files:** Don't modify unless absolutely necessary (breaks sync)
- **Orkhon customizations:** Prefix with `orkhon_*` (e.g., `orkhon_dnb_config.json`)
- **Configuration:** Use `.env` and `orkhon_*.json` for local settings

---

## Customization Patterns

### Pattern 1: Custom Dataset Configuration

**Create `orkhon_dnb_config.json` in the agent directory:**

```json
{
  "datasets": [
    {
      "type": "bigquery",
      "dataset_id": "dnb_statistics",
      "description": "Detailed description for LLM context..."
    }
  ]
}
```

**Reference in `.env`:**
```bash
DATASET_CONFIG_FILE=./orkhon_dnb_config.json
```

### Pattern 2: Custom Sub-Agents (Optional)

If you need Orkhon-specific capabilities:

```python
# Create: agents/data_science/orkhon_sub_agents/dnb_insights_agent.py

from google.adk.agents import Agent

dnb_insights_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="dnb_insights_agent",
    instruction="""You specialize in Dutch financial regulatory analysis...""",
    tools=[...]
)
```

**Import conditionally in `agent.py`:**
```python
# At top of agents/data_science/agent.py
import os
if os.path.exists("orkhon_sub_agents"):
    from orkhon_sub_agents.dnb_insights_agent import dnb_insights_agent
    ORKHON_SUB_AGENTS = [dnb_insights_agent]
else:
    ORKHON_SUB_AGENTS = []

# Add to agent
def get_root_agent():
    agent = LlmAgent(
        sub_agents=[
            bigquery_agent,
            bqml_agent,
            ds_agent,
            *ORKHON_SUB_AGENTS,  # ← Custom agents
        ],
        ...
    )
    return agent
```

### Pattern 3: Custom Tools via Toolbox

**Best approach:** Use Orkhon's existing toolbox infrastructure instead of modifying the agent.

The `data-science` agent's BigQuery sub-agent can already query any dataset you configure. Your DNB datasets are just additional BigQuery datasets.

**No code changes needed!** Just configure the dataset in `orkhon_dnb_config.json`.

---

## Maintenance: Monthly Sync

**First Monday of each month:**

```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\backend\scripts\sync-adk-samples.ps1
```

This pulls upstream updates while preserving your Orkhon customizations.

**If conflicts occur:**
1. Review the conflict
2. **Prefer upstream** for core agent logic
3. **Keep Orkhon changes** for `orkhon_*` files
4. Re-test after resolving

---

## Why Git Subtree Over Alternatives?

### Git Subtree vs Submodule

| Feature | Git Subtree (✅ Recommended) | Git Submodule (❌ Avoid) |
|---------|------------------------------|--------------------------|
| Deployment | Self-contained (no extra steps) | Requires `git submodule update --init --recursive` |
| Upstream sync | `git subtree pull` (simple) | `git submodule update --remote` (confusing) |
| Local changes | ✅ Full control | ⚠️ Detached HEAD issues |
| Team onboarding | ✅ Simple (just `git clone`) | ❌ Complex (submodule commands) |
| History tracking | ✅ Clear (squashed commits) | ⚠️ Separate (hidden in submodule) |

### Git Subtree vs Manual Copy

| Feature | Git Subtree (✅ Recommended) | Manual Copy (❌ Avoid) |
|---------|------------------------------|------------------------|
| Upstream sync | ✅ `git subtree pull` | ❌ Manual re-copy |
| History | ✅ Tracked | ❌ Lost |
| Attribution | ✅ Clear source | ⚠️ Unclear origin |
| Contribution back | ✅ `git subtree push` | ❌ Manual diff |

**Decision: Git Subtree** is the clear winner for our use case.

---

## Other Recommended Samples to Adopt

### Tier 1: High Value (Adopt Soon)

| Sample | Use Case | Integration Effort |
|--------|----------|-------------------|
| **financial-advisor** | Portfolio analysis, risk assessment, Dutch regulations | Medium (2 weeks) |
| **customer-service** | Multi-turn conversations, escalation logic | Low (1 week) |
| **RAG** | Document Q&A with vector search | Medium (1-2 weeks) |

### Tier 2: Evaluate Later

| Sample | Use Case | Integration Effort |
|--------|----------|-------------------|
| **llm-auditor** | Agent evaluation, red-teaming | Low (1 week) |
| **marketing-agency** | Content generation, SEO | Medium (1-2 weeks) |
| **blog-writer** | Content creation | Low (3-5 days) |

---

## Troubleshooting

### "Sample not found in adk-samples"

```powershell
# Verify remote
git remote -v | Select-String "adk-samples"

# Re-add if missing
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples

# List available samples
git ls-tree -r adk-samples/main --name-only python/agents/
```

### "Conflicts during sync"

```powershell
# 1. Review conflicts
git status

# 2. Manually resolve conflicts in files
# - Keep upstream changes for core logic
# - Keep Orkhon changes for orkhon_* files

# 3. Complete the merge
git add .
git commit -m "merge: Sync data-science agent with upstream (resolve conflicts)"
```

### "Dependencies conflict"

```powershell
cd backend\adk

# Try resolving to latest compatible versions
uv sync --resolution=highest

# Or manually edit pyproject.toml to adjust version constraints
uv sync
```

### "Agent not working after integration"

```powershell
# 1. Test agent in isolation
adk run agents/data-science

# 2. Check environment variables
cat agents\data-science\.env | Select-String "GOOGLE_CLOUD_PROJECT|BQ_DATASET_ID|DATASET_CONFIG_FILE"

# 3. Verify dataset config
cat agents\data-science\orkhon_dnb_config.json

# 4. Test with verbose logging
adk run agents/data-science --verbose
```

---

## Success Checklist

After adopting a sample agent:

- [ ] Agent imported via `git subtree add`
- [ ] `.env` file configured with Orkhon values
- [ ] Custom `orkhon_*.json` config created (if needed)
- [ ] Dependencies installed (`uv sync`)
- [ ] Agent tested in isolation (`adk run agents/{name}`)
- [ ] Agent integrated with root_agent
- [ ] Integration tested with cross-domain queries
- [ ] Changes committed and pushed
- [ ] Documentation updated (this file)

---

## Key Takeaways

🎯 **Git subtree is the right choice** for Orkhon's use case

🎯 **Adopt don't build** - Reuse official samples instead of reinventing

🎯 **Customize in separate files** - Use `orkhon_*` prefix for local changes

🎯 **Sync monthly** - Pull upstream updates regularly

🎯 **Test thoroughly** - Isolation → Integration → Production

---

## Resources

- **Official ADK Samples:** https://github.com/google/adk-samples
- **Data Science Sample Docs:** https://github.com/google/adk-samples/tree/main/python/agents/data-science
- **ADK Documentation:** https://google.github.io/adk-docs
- **Orkhon Adoption Strategy:** `backend/adk/ADOPTION_STRATEGY.md`

---

**Questions? Issues?** See `ADOPTION_STRATEGY.md` for detailed rationale and decision matrix.
