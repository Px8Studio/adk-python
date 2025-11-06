# Strategy: Adopting ADK Samples in Orkhon

> **Reuse official ADK samples instead of building from scratch**

---

## Philosophy

**Don't Reinvent the Wheel 🚗**

The official [adk-samples](https://github.com/google/adk-samples) repository contains **20+ production-grade agents** across diverse domains. Each represents weeks of engineering effort, testing, and refinement.

**Our approach:**
1. ✅ **Adopt** official samples via git subtree
2. ✅ **Adapt** with Orkhon-specific configs and customizations
3. ✅ **Stay Sync'd** with upstream improvements
4. ✅ **Contribute Back** when we build generally useful features

---

## Git Subtree Strategy

### Why Git Subtree?

| Feature | Git Subtree | Git Submodule | Manual Copy |
|---------|-------------|---------------|-------------|
| **Upstream sync** | ✅ Easy | ⚠️ Complex | ❌ Manual |
| **Local customization** | ✅ Yes | ⚠️ Limited | ✅ Yes |
| **Deployment** | ✅ Self-contained | ❌ Extra steps | ✅ Self-contained |
| **History tracking** | ✅ Clear | ⚠️ Separate | ❌ Lost |
| **Team onboarding** | ✅ Simple | ❌ Confusing | ✅ Simple |

**Decision: Git Subtree** strikes the best balance for our use case.

### Setup (One-Time)

```powershell
cd C:\Users\rjjaf\_Projects\orkhon

# Add adk-samples as remote
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples
```

### Import a Sample

```powershell
# General pattern
git subtree add --prefix=backend/adk/agents/{AGENT_NAME} `
    adk-samples main:python/agents/{AGENT_NAME} `
    --squash

# Example: Import data-science agent
git subtree add --prefix=backend/adk/agents/data_science `
    adk-samples main:python/agents/data-science `
    --squash

# Commit the import
git commit -m "feat(adk): Import {AGENT_NAME} from ADK samples via git subtree"
```

### Pull Updates

```powershell
# Check for upstream changes
cd C:\Users\rjjaf\_Projects\adk-samples
git pull origin main

# Pull updates into Orkhon
cd C:\Users\rjjaf\_Projects\orkhon
git subtree pull --prefix=backend/adk/agents/{AGENT_NAME} `
    adk-samples main:python/agents/{AGENT_NAME} `
    --squash
```

### Handle Conflicts

If you have local customizations:
1. **Review conflicts carefully**
2. **Prefer upstream** for core agent logic
3. **Keep Orkhon customizations** in separate files:
   - `orkhon_*.py` - Custom tools/sub-agents
   - `orkhon_*.json` - Custom configs
   - `orkhon_*.yaml` - Custom prompts

### Contribute Back (Optional)

If Orkhon improvements are generally useful:

```powershell
# Push to feature branch in adk-samples fork
git subtree push --prefix=backend/adk/agents/{AGENT_NAME} `
    adk-samples-fork feature/orkhon-improvements

# Then create PR to upstream adk-samples
```

---

## Directory Structure Convention

### Pattern: Domain-Specific Agent Directories

```
backend/adk/agents/
├── root_agent/                    # L1: System Root
│   └── agent.py
│
├── {DOMAIN}_coordinators/         # L2: Domain Coordinators
│   ├── dnb_coordinator/
│   └── data_coordinator/
│
├── {DOMAIN}_agents/               # L3: Specialists (Leaf Agents)
│   ├── dnb_echo_agent/
│   ├── dnb_statistics_agent/
│   └── dnb_public_register_agent/
│
└── {ADOPTED_SAMPLE}/              # Imported via git subtree
    ├── agent.py                   # Becomes L2 coordinator or L3 specialist
    ├── sub_agents/                # L3 specialists (if multi-agent)
    ├── tools.py
    ├── utils/
    ├── tests/
    ├── eval/
    ├── deployment/
    ├── pyproject.toml
    ├── README.md
    └── orkhon_*.{py,json,yaml}    # Orkhon customizations (separate files)
```

### Integration Pattern

**Every adopted sample becomes either:**
1. **L2 Domain Coordinator** - If it has sub-agents (e.g., `data_science`)
2. **L3 Specialist** - If it's a single-purpose agent (e.g., `blog-writer`)

**Example: Adopting `financial-advisor`**

```
backend/adk/agents/
├── root_agent/
│   └── agent.py                          # ← Import financial_advisor
│
└── financial_advisor/                    # ← Imported via subtree
    ├── agent.py                          # L2 coordinator (has sub-agents)
    ├── sub_agents/
    │   ├── portfolio_agent.py            # L3 specialist
    │   ├── risk_agent.py                 # L3 specialist
    │   └── compliance_agent.py           # L3 specialist
    ├── orkhon_dnb_integration.py         # ← Orkhon-specific: DNB data integration
    └── orkhon_financial_config.json      # ← Orkhon-specific: Dutch regulations
```

**Updated `root_agent/agent.py`:**
```python
from financial_advisor.agent import root_agent as financial_advisor

root = Agent(
    name="root_agent",
    sub_agents=[
        dnb_coordinator,
        data_science_coordinator,
        financial_advisor,  # ← Added
    ]
)
```

---

## Recommended Samples to Adopt

### Tier 1: High Priority (Adopt Now)

| Sample | Value Proposition | Integration Effort |
|--------|-------------------|-------------------|
| **data-science** | Multi-agent system for BigQuery, AlloyDB, NL2SQL, NL2Py, BQML | Medium (2-3 weeks) |
| **financial-advisor** | Financial domain expertise, portfolio analysis, risk assessment | Medium (2 weeks) |
| **customer-service** | Multi-turn conversations, context management, escalation logic | Low (1 week) |

### Tier 2: Medium Priority (Adopt Soon)

| Sample | Value Proposition | Integration Effort |
|--------|-------------------|-------------------|
| **RAG** | Document Q&A with vector search, multiple retrieval strategies | Medium (1-2 weeks) |
| **llm-auditor** | Agent evaluation, monitoring, red-teaming | Low (1 week) |
| **marketing-agency** | Content generation, SEO, campaign planning | Medium (1-2 weeks) |

### Tier 3: Lower Priority (Evaluate Later)

| Sample | Value Proposition | Integration Effort |
|--------|-------------------|-------------------|
| **blog-writer** | Content creation, SEO optimization | Low (3-5 days) |
| **travel-concierge** | Multi-turn planning, tool orchestration patterns | Low (3-5 days) |
| **product-catalog-ad-generation** | E-commerce, ad copy generation | Low (3-5 days) |
| **image-scoring** | Vision capabilities, multimodal agents | Low (3-5 days) |

---

## Customization Patterns

### Pattern 1: Custom Dataset Configs

**For samples that accept dataset configurations (e.g., `data-science`):**

```json
// backend/adk/agents/data_science/orkhon_dnb_config.json
{
  "datasets": [
    {
      "type": "bigquery",
      "name": "dnb_statistics",
      "description": "DNB Statistics API data: insurance, pensions, market trends"
    },
    {
      "type": "bigquery",
      "name": "dnb_public_register",
      "description": "DNB Public Register: entities, publications, compliance data"
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
          "table": "insurance_companies",
          "column": "entity_id"
        }
      }
    ]
  }
}
```

**Set in `.env`:**
```bash
DATASET_CONFIG_FILE='./orkhon_dnb_config.json'
```

### Pattern 2: Custom Sub-Agents

**Add Orkhon-specific capabilities without modifying upstream code:**

```python
# backend/adk/agents/data_science/orkhon_sub_agents/dnb_insights_agent.py

from google.adk.agents import Agent

dnb_insights_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="dnb_insights_agent",
    instruction="""You specialize in Dutch financial regulatory analysis.
    
    You have access to:
    - DNB Public Register (entities, publications)
    - DNB Statistics (insurance, pensions, market data)
    
    Provide insights on:
    - Regulatory compliance trends
    - Market concentration analysis
    - Entity risk profiling
    - Cross-dataset correlation analysis
    """,
    tools=[...]  # Custom Orkhon tools
)
```

**Integrate in upstream agent:**
```python
# backend/adk/agents/data_science/agent.py

# Add at top
import os
if os.path.exists("orkhon_sub_agents"):
    from orkhon_sub_agents.dnb_insights_agent import dnb_insights_agent
    ORKHON_SUB_AGENTS = [dnb_insights_agent]
else:
    ORKHON_SUB_AGENTS = []

# Add to agent definition
def get_root_agent() -> LlmAgent:
    agent = LlmAgent(
        name="data_science_root_agent",
        sub_agents=[
            bqml_agent,
            bigquery_agent,
            alloydb_agent,
            analytics_agent,
            *ORKHON_SUB_AGENTS,  # ← Add Orkhon custom agents
        ],
        ...
    )
    return agent
```

### Pattern 3: Custom Tools

**Add Orkhon-specific tools for adopted agents:**

```python
# backend/adk/agents/financial_advisor/orkhon_tools.py

from google.adk.tools import tool

@tool
def query_dnb_entity_info(entity_id: str) -> dict:
    """Query DNB Public Register for entity information.
    
    Args:
        entity_id: The DNB entity identifier
        
    Returns:
        Entity details including regulatory status, publications, etc.
    """
    # Use Orkhon's ToolboxClient to call DNB Public Register API
    from backend.adk.utils.toolbox_client import ToolboxClient
    
    client = ToolboxClient()
    result = client.invoke_tool(
        "dnb_public_register_api_publicregister_entities_search",
        {"EntityId": entity_id}
    )
    return result

@tool
def query_dnb_statistics(entity_id: str, metric: str) -> dict:
    """Query DNB Statistics for entity metrics.
    
    Args:
        entity_id: The DNB entity identifier
        metric: The metric to retrieve (e.g., 'total_assets', 'risk_weighted_assets')
        
    Returns:
        Statistical data for the entity
    """
    # Implementation using BigQuery or Statistics API
    ...
```

**Integrate:**
```python
# backend/adk/agents/financial_advisor/agent.py

import os
if os.path.exists("orkhon_tools.py"):
    from .orkhon_tools import query_dnb_entity_info, query_dnb_statistics
    ORKHON_TOOLS = [query_dnb_entity_info, query_dnb_statistics]
else:
    ORKHON_TOOLS = []

def get_root_agent():
    agent = LlmAgent(
        name="financial_advisor",
        tools=[
            *existing_tools,
            *ORKHON_TOOLS,  # ← Add Orkhon tools
        ],
        ...
    )
    return agent
```

### Pattern 4: Custom Prompts

**Override or extend upstream prompts:**

```python
# backend/adk/agents/customer_service/orkhon_prompts.py

def get_orkhon_escalation_prompt() -> str:
    """Custom escalation prompt for Dutch financial regulations."""
    return """
    When escalating to human support, follow DNB compliance guidelines:
    
    1. **GDPR Compliance**: Never share personal data without consent
    2. **MiFID II**: For investment advice, escalate to licensed advisor
    3. **Wft**: For insurance matters, escalate to AFM-certified agent
    4. **DNB Supervision**: For complaints, provide DNB contact information
    
    Dutch Financial Supervisory Contact:
    - De Nederlandsche Bank (DNB): 0800 - 020 1068
    - Autoriteit Financiële Markten (AFM): 0800 - 540 0540
    """

# Integrate in agent instruction
def get_orkhon_instruction():
    base_instruction = get_base_instruction()  # From upstream
    escalation_prompt = get_orkhon_escalation_prompt()
    
    return f"""
    {base_instruction}
    
    <ORKHON_ESCALATION_POLICY>
    {escalation_prompt}
    </ORKHON_ESCALATION_POLICY>
    """
```

---

## Dependency Management

### Approach: Unified Dependencies

**Decision:** Merge adopted sample dependencies into root `pyproject.toml`

```toml
# backend/adk/pyproject.toml

[project]
name = "orkhon-adk"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Core Orkhon
    "google-adk>=1.14",
    "python-dotenv>=1.0.1",
    
    # From data-science sample
    "pandas>=2.3.0",
    "numpy>=2.3.1",
    "sqlglot>=26.10.1",
    "db-dtypes>=1.4.2",
    "toolbox-core>=0.3.0",
    
    # From financial-advisor sample
    "yfinance>=0.2.0",
    "alpha-vantage>=2.3.0",
    
    # From customer-service sample
    "sentence-transformers>=2.0.0",
    
    # ... etc
]

[project.optional-dependencies]
dev = [
    "google-adk[eval]>=1.14",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
    "black>=25.9.0",
]
```

**After adopting each sample:**
```powershell
cd backend\adk

# Merge dependencies from sample's pyproject.toml
uv add {dependencies from sample}

# Or manually edit pyproject.toml, then:
uv sync
```

---

## Testing Strategy

### Pattern: Isolated + Integrated Testing

**1. Test adopted agent in isolation:**
```powershell
cd backend\adk
uv run adk run agents/{ADOPTED_SAMPLE}
```

**2. Test integrated with root agent:**
```powershell
uv run adk run agents/root_agent
```

**3. Run sample's test suite:**
```powershell
cd agents/{ADOPTED_SAMPLE}
uv run pytest tests/
```

**4. Create Orkhon integration tests:**
```python
# backend/adk/tests/integration/test_data_science_integration.py

import pytest
from google.adk.agents import Runner
from agents.root_agent.agent import root_agent

@pytest.mark.integration
def test_dnb_data_science_workflow():
    """Test end-to-end DNB data → Data Science workflow."""
    runner = Runner(agent=root_agent)
    
    # Query should route: root → data_science → bigquery_agent
    result = runner.run(
        "Query the DNB Statistics dataset for top 10 insurance companies by assets"
    )
    
    assert "insurance" in result.lower()
    assert "assets" in result.lower()
    
@pytest.mark.integration
def test_cross_domain_workflow():
    """Test workflow across DNB coordinator and Data Science coordinator."""
    runner = Runner(agent=root_agent)
    
    # Should route: root → dnb_coordinator → data_science → visualization
    result = runner.run(
        "Get entity list from DNB Public Register, query their financial metrics, "
        "and create a bar chart visualization"
    )
    
    assert "chart" in result.lower() or "visualization" in result.lower()
```

---

## Maintenance Checklist

### Monthly Sync (First Monday of Each Month)

```powershell
# 1. Check for upstream updates
cd C:\Users\rjjaf\_Projects\adk-samples
git pull origin main
git log --oneline --since="1 month ago" python/agents/

# 2. For each adopted sample, pull updates
cd C:\Users\rjjaf\_Projects\orkhon
git subtree pull --prefix=backend/adk/agents/{SAMPLE} `
    adk-samples main:python/agents/{SAMPLE} `
    --squash

# 3. Resolve conflicts (prefer upstream for core logic)

# 4. Update dependencies
cd backend\adk
uv sync

# 5. Run tests
uv run pytest tests/

# 6. Test in ADK Web UI
uv run adk web agents
```

### Quarterly Review (First Monday of Each Quarter)

- **Review adopted samples** - Are they still needed?
- **Evaluate new samples** - Are there new official samples worth adopting?
- **Assess customizations** - Can any be contributed back upstream?
- **Update documentation** - Reflect changes in README and integration plans

---

## Decision Matrix: Adopt vs Build

**When to ADOPT an official sample:**
- ✅ Sample solves 80%+ of your use case
- ✅ Sample has comprehensive tests and documentation
- ✅ Sample is actively maintained by Google
- ✅ Time savings > 2 weeks of development effort

**When to BUILD custom:**
- ✅ Highly specialized Orkhon-specific logic (e.g., DNB API coordinators)
- ✅ Simple single-purpose agents (<100 LOC)
- ✅ No official sample exists for the domain
- ✅ Need full control over implementation

**Hybrid approach (recommended):**
- Adopt official sample as foundation
- Add Orkhon customizations in separate files (`orkhon_*.py`)
- Contribute generally useful features back upstream

---

## Success Metrics

### Adoption Success
- ✅ Agent runs without errors in isolation
- ✅ Agent integrates with root_agent successfully
- ✅ All sample tests pass
- ✅ Custom Orkhon integrations work
- ✅ Documentation updated

### Long-Term Success
- ✅ Regularly sync with upstream (monthly)
- ✅ Contribute improvements back (quarterly)
- ✅ Team understands how to customize without breaking upstream sync
- ✅ Deployment to production successful

---

## Example: Full Adoption Workflow

### Step-by-Step: Adopting `financial-advisor`

```powershell
# 1. Import via git subtree
cd C:\Users\rjjaf\_Projects\orkhon
git subtree add --prefix=backend/adk/agents/financial_advisor `
    adk-samples main:python/agents/financial-advisor `
    --squash
git commit -m "feat(adk): Import financial-advisor from ADK samples"

# 2. Install dependencies
cd backend\adk
# Copy deps from financial_advisor/pyproject.toml to root pyproject.toml
uv sync

# 3. Configure environment
copy agents\financial_advisor\.env.example agents\financial_advisor\.env
notepad agents\financial_advisor\.env
# Set GCP project, API keys, etc.

# 4. Test in isolation
uv run adk run agents/financial_advisor
# Query: "What's the current price of AAPL?"

# 5. Create Orkhon customizations
New-Item -ItemType File agents\financial_advisor\orkhon_tools.py
New-Item -ItemType File agents\financial_advisor\orkhon_dnb_integration.py

# Edit orkhon_tools.py to add DNB data integration
# Edit orkhon_dnb_integration.py to add Dutch regulations

# 6. Integrate with root agent
notepad agents\root_agent\agent.py
# Add: from financial_advisor.agent import root_agent as financial_advisor
# Add to sub_agents: [dnb_coordinator, data_science_coordinator, financial_advisor]

# 7. Test integrated system
uv run adk run agents/root_agent
# Query: "Get financial metrics for DNB entity 12345 and provide investment advice"

# 8. Create integration tests
New-Item -ItemType File tests\integration\test_financial_advisor_integration.py
# Write tests for DNB + financial advisor workflows

# 9. Update documentation
notepad README.md
# Document the new financial_advisor integration

# 10. Commit everything
git add .
git commit -m "feat(adk): Integrate financial-advisor with DNB data sources"
git push origin dev
```

---

## Conclusion

**Key Principles:**
1. **Reuse** - Don't build what already exists in adk-samples
2. **Customize** - Adapt with Orkhon-specific configs in separate files
3. **Sync** - Regularly pull upstream updates (monthly)
4. **Contribute** - Push generally useful features back to adk-samples

**Expected Outcomes:**
- **Faster development** - Weeks saved per adopted sample
- **Higher quality** - Production-tested code from Google
- **Easier maintenance** - Upstream improvements flow automatically
- **Better collaboration** - Contribute to open-source ADK ecosystem

**Next Steps:**
1. Start with `data-science` (highest ROI for Orkhon)
2. Add `financial-advisor` (domain expertise)
3. Evaluate `customer-service` and `RAG` for future adoption

🚀 **Let's build on the shoulders of giants!**
