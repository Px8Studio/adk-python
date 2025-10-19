# Orkhon Multi-Agent Architecture Analysis & Improvement Plan

## Executive Summary

Based on comprehensive research of ADK documentation and best practices, your Orkhon project has a **solid foundation** but is missing key architectural patterns for scalable multi-agent systems. This document provides a complete roadmap to transform your current structure into a production-ready, extensible multi-agent platform.

---

## 📊 Current State Analysis

### ✅ What You Have (Strengths)

1. **Layered Coordinator Stack**
  - `root_agent/agent.py` routes requests to domain coordinators with
    `sub_agents`.
  - `api_coordinators/dnb_coordinator/agent.py` fans out to
    `dnb_echo`, `dnb_statistics`, and `dnb_public_register` specialists.

2. **Specialized API Agents**
  - `api_agents/dnb_*` modules follow ADK import conventions and encapsulate
    Toolbox toolsets per domain.
  - Public Register agent normalizes casing/pagination and surfaces helpful
    validation errors.

3. **Toolbox & OpenAPI Options**
  - Toolbox-based toolsets remain the default approach.
  - `api_agents/dnb_openapi/agent.py` provides an OpenAPI-driven alternative
    for environments that prefer runtime tool discovery.

4. **Workflow Scaffolds Ready for Use**
  - `workflows/data_pipeline` (SequentialAgent) and
    `workflows/parallel_fetcher` (ParallelAgent) scaffolds are checked in and
    ready to be wired into orchestrations.

### ⚠️ Remaining Gaps (Critical Focus Areas)

#### 1. **Workflow Integration & Deterministic Flows**
  - Workflow scaffolds exist but are not yet invoked by coordinators.
  - Multi-call use cases still rely on LLM reasoning instead of deterministic
    pipelines.

#### 2. **Additional Domain Coordinators**
  - Only the DNB pathway is implemented; Google/data/utility coordinators are
    placeholders.
  - Need a documented pattern for introducing new categories and sharing state
    between them.

#### 3. **A2A Network Readiness**
  - `root_agent/agent.json` exists, but other agents lack cards.
  - No shared `a2a_config.yaml` or automation for starting the A2A server.

#### 4. **Testing & Observability**
  - Smoke tests are manual; no automated coverage for routing paths.
  - Jaeger/telemetry dashboards are not yet curated for the multi-agent view.

---

## 🏗️ Proposed Architecture

### High-Level Structure

```
root_agent (Orkhon Coordinator)
├── api_agents/ (API Integration Category)
│   ├── dnb_coordinator (DNB API Coordinator)
│   │   ├── dnb_echo_agent
│   │   ├── dnb_statistics_agent
│   │   └── dnb_public_register_agent
│   ├── google_search_agent (Future)
│   └── weather_api_agent (Future)
├── data_agents/ (Data Processing Category)
│   ├── data_analyst_agent (Future)
│   └── data_validator_agent (Future)
└── utility_agents/ (Utility Category)
    ├── cache_agent (Future)
    └── logging_agent (Future)
```

### Agent Types & Patterns

#### 1. **Root Coordinator** (`root_agent`)
- **Type:** `LlmAgent`
- **Role:** Top-level request router
- **Pattern:** Coordinator/Dispatcher Pattern
- **Responsibilities:**
  - Route to appropriate category coordinators
  - Maintain conversation context
  - Handle multi-turn interactions
  - Orchestrate complex multi-category workflows

#### 2. **Category Coordinators** (e.g., `dnb_coordinator`)
- **Type:** `LlmAgent` 
- **Role:** Domain-specific routing
- **Pattern:** Coordinator/Dispatcher Pattern
- **Responsibilities:**
  - Route within their domain
  - Aggregate results from specialized agents
  - Handle domain-specific errors

#### 3. **Specialized API Agents** (e.g., `dnb_echo_agent`)
- **Type:** `LlmAgent`
- **Role:** Execute specific API operations
- **Pattern:** Tool-based Agent
- **Responsibilities:**
  - Direct API interaction via ToolboxToolset
  - Schema validation
  - Response formatting

#### 4. **Workflow Orchestrators** (Future)
- **Type:** `SequentialAgent`, `ParallelAgent`, `LoopAgent`
- **Role:** Deterministic flow control
- **Pattern:** Workflow Pattern
- **Use Cases:**
  - Sequential: Multi-step data pipelines
  - Parallel: Concurrent API calls
  - Loop: Polling, pagination, retries

---

## 📋 Detailed Improvement Recommendations

### Priority 1: Critical (Week 1)

#### 1.1 Rename & Restructure Agents

**Current Structure:**
```
backend/adk/agents/
├── dnb_agent/          # ❌ Unclear role
├── dnb_api_echo/
├── dnb_api_statistics/
└── dnb_api_public_register/
```

**Proposed Structure:**
```
backend/adk/agents/
├── root_agent/                    # NEW: Main coordinator
│   └── agent.py (root_agent)
├── api_coordinators/               # NEW: Category coordinators
│   └── dnb_coordinator/
│       └── agent.py (dnb_coordinator_agent)
├── api_agents/                     # RENAMED: Specialized agents
│   ├── dnb_echo/
│   │   └── agent.py (dnb_echo_agent)
│   ├── dnb_statistics/
│   │   └── agent.py (dnb_statistics_agent)
│   ├── dnb_public_register/
│   │   └── agent.py (dnb_public_register_agent)
│   └── google_search/              # FUTURE
│       └── agent.py (google_search_agent)
└── workflows/                      # NEW: Workflow agents
    ├── data_pipeline/
    └── parallel_fetcher/
```

**Migration Path:**
1. Create new structure alongside old
2. Update imports gradually
3. Test thoroughly
4. Remove old structure
5. Update all documentation

#### 1.2 Create Root Coordinator

**File:** `backend/adk/agents/root_agent/agent.py`

```python
"""
Root Coordinator - Top-level agent for the multi-agent system.

This agent routes requests to specialized category coordinators:
- DNB API operations
- Google Search (future)
- Data processing (future)
"""

from __future__ import annotations

from google.adk.agents import LlmAgent as Agent
from api_coordinators.dnb_coordinator.agent import dnb_coordinator_agent

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    description=(
        "Main coordinator for the Orkhon AI platform. Routes requests to "
        "specialized domain coordinators for API integrations, data processing, "
        "and utility operations."
    ),
    instruction="""You are the Orkhon platform coordinator.

Your role:
1. Understand user requests
2. Route to appropriate domain coordinator:
   - DNB API operations → dnb_coordinator_agent
   - Google searches → google_search_agent (future)
   - Data analysis → data_coordinator_agent (future)
3. Synthesize responses from multiple domains if needed
4. Maintain conversational context

Always be clear about which agent you're delegating to and why.
Provide concise summaries of results.""",
    sub_agents=[
        dnb_coordinator_agent,
        # Future agents will be added here
    ],
)
```

#### 1.3 Refactor DNB Coordinator

**File:** `backend/adk/agents/api_coordinators/dnb_coordinator/agent.py`

```python
"""
DNB API Coordinator - Routes DNB-specific requests to specialized agents.

Coordinates three DNB API domains:
- Echo API (connectivity & health checks)
- Statistics API (economic data & datasets)
- Public Register API (licenses & registrations)
"""

from __future__ import annotations

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.agent_tool import AgentTool

# Import specialized DNB agents
from api_agents.dnb_echo.agent import dnb_echo_agent
from api_agents.dnb_statistics.agent import dnb_statistics_agent
from api_agents.dnb_public_register.agent import dnb_public_register_agent

dnb_coordinator_agent = Agent(
    name="dnb_coordinator",
    model="gemini-2.0-flash",
    description=(
        "Coordinator for DNB (De Nederlandsche Bank) API operations. "
        "Routes requests to Echo (tests), Statistics (datasets), or "
        "Public Register (licenses/registrations)."
    ),
    instruction="""You coordinate DNB API operations across three domains:

1. **Echo API** (dnb_echo_agent):
   - Connectivity tests (helloworld)
   - API health checks
   - Simple ping operations

2. **Statistics API** (dnb_statistics_agent):
   - Economic datasets
   - Exchange rates
   - Financial sector statistics
   - Balance of payments data

3. **Public Register API** (dnb_public_register_agent):
   - License searches
   - Registration data
   - Regulatory information

Route appropriately based on user intent. If multiple domains are needed,
coordinate sequential or parallel execution. Provide clear summaries.""",
    # Option A: Use sub_agents for LLM-driven delegation (recommended)
    sub_agents=[
        dnb_echo_agent,
        dnb_statistics_agent,
        dnb_public_register_agent,
    ],
    # Option B: Use AgentTool for explicit control (alternative)
    # tools=[
    #     AgentTool(agent=dnb_echo_agent),
    #     AgentTool(agent=dnb_statistics_agent),
    #     AgentTool(agent=dnb_public_register_agent),
    # ],
)
```

### Priority 2: High (Week 2)

**Status:** 🚧 In progress – workflow agent scaffolds live in repo; coordinator
integration and documentation remain.
### Priority 1: Critical (Week 1)

**Status:** ✅ Completed (implemented on `dev`, Oct 2025). Details are retained below
for historical context and onboarding reference.
#### 2.1 Add Workflow Agents

**Example: Parallel API Fetcher**

**Legacy Structure (Jan 2025):**

```python
"""
Parallel API Fetcher - Executes multiple API calls concurrently.

Use when you need to fetch data from multiple sources simultaneously
and aggregate results.
"""
**Resulting Structure (Oct 2025):**
from __future__ import annotations

from google.adk.agents import ParallelAgent, LlmAgent as Agent

# This would be used as a sub-agent in a larger workflow
**Migration Notes:**
1. New structure created alongside the legacy modules (completed Jan 2025).
2. Imports updated to absolute package references under `api_agents`.
3. Smoke testing performed via `adk run root_agent ...` during migration.
4. Legacy `dnb_agent` package removed after validation.
5. Documentation refreshed (this file, summary, diagrams) in Oct 2025.
# Example aggregator
api_aggregator = Agent(
    name="api_aggregator",
    model="gemini-2.0-flash",
    instruction="""Aggregate results from parallel API calls.

Combine data from {api1_result}, {api2_result}, {api3_result}.
Identify patterns, conflicts, or complementary information.
Present a unified summary.""",
)
```

**Example: Data Pipeline (Sequential)**

**File:** `backend/adk/agents/workflows/data_pipeline/agent.py`

```python
"""
Data Pipeline - Sequential data processing workflow.

Implements: Validate → Transform → Analyze → Store
"""

from __future__ import annotations

from google.adk.agents import SequentialAgent, LlmAgent as Agent

validator = Agent(
    name="data_validator",
    model="gemini-2.0-flash",
    instruction="Validate incoming data against schema. Set {validation_status}.",
    output_key="validation_status",
)

transformer = Agent(
    name="data_transformer",
    model="gemini-2.0-flash",
    instruction="Transform data if {validation_status} is 'valid'. Output to {transformed_data}.",
    output_key="transformed_data",
)

analyzer = Agent(
    name="data_analyzer",
    model="gemini-2.0-flash",
    instruction="Analyze {transformed_data} and generate insights. Output to {insights}.",
    output_key="insights",
)

data_pipeline = SequentialAgent(
    name="data_pipeline",
    description="Sequential data processing pipeline",
    sub_agents=[validator, transformer, analyzer],
)
```

#### 2.2 Implement AgentTool Pattern (Alternative Approach)

**When to use AgentTool vs sub_agents:**

- **sub_agents + LLM routing**: For flexible, dynamic delegation (recommended for coordinators)
- **AgentTool**: For explicit, programmatic control (recommended for workflows)

**Example:**

```python
from google.adk.tools.agent_tool import AgentTool

coordinator = Agent(
    name="coordinator",
    tools=[
        AgentTool(
            agent=specialized_agent,
            # Optional: customize how agent is invoked
        ),
    ],
)
```

### Priority 3: Medium (Week 3-4)

**Status:** ⚠️ Not started – root agent card exists, but broader A2A work is not
yet in the codebase.

#### 3.1 Add A2A Network Preparation

**Goal:** Enable agent-to-agent communication across network boundaries.

**Step 1: Create Agent Cards**

**File:** `backend/adk/agents/root_agent/agent.json`

```json
{
  "name": "root_agent",
  "description": "Main coordinator for Orkhon AI platform",
  "version": "1.0.0",
  "capabilities": {
    "supports_streaming": true,
    "supports_artifacts": true,
    "supports_tools": true
  },
  "sub_agents": [
    "dnb_coordinator_agent"
  ],
  "metadata": {
    "domain": "multi-domain",
    "vendor": "Orkhon",
    "contact": "team@orkhon.dev"
  }
}
```

**Step 2: Configure A2A Server**

**File:** `backend/adk/a2a_config.yaml`

```yaml
# A2A Server Configuration
server:
  host: "0.0.0.0"
  port: 8001
  
agents:
  - name: "root_agent"
    module: "root_agent.agent"
    agent_var: "root_agent"
    enabled: true
    
  - name: "dnb_coordinator"
    module: "api_coordinators.dnb_coordinator.agent"
    agent_var: "dnb_coordinator_agent"
    enabled: true
    expose_externally: true  # Allow external A2A calls

telemetry:
  enabled: true
  jaeger_endpoint: "http://localhost:4318"
```

**Step 3: Start A2A Server**

```python
# backend/adk/start_a2a_server.py
from a2a.server import A2AServer
from google.adk.agents.loader import load_agent

def main():
    server = A2AServer(config_path="a2a_config.yaml")
    
    # Register agents
    root_agent = load_agent("root_agent.agent", "root_agent")
    server.register_agent("root_agent", root_agent)
    
    dnb_coordinator = load_agent("api_coordinators.dnb_coordinator.agent", "dnb_coordinator_agent")
    server.register_agent("dnb_coordinator", dnb_coordinator)
    
    server.start()

if __name__ == "__main__":
    main()
```

#### 3.2 Implement State Management Best Practices

**Use session state for inter-agent communication:**

```python
# In specialized agent
agent = Agent(
    name="data_fetcher",
    output_key="fetched_data",  # Saves result to session.state['fetched_data']
    instruction="Fetch data and save it.",
)

# In consuming agent
processor = Agent(
    name="data_processor",
    instruction="Process the data from {fetched_data}.",  # Reads from state
)
```

#### 3.3 Add Extensibility for Future Agents

**File:** `backend/adk/agents/api_agents/google_search/agent.py` (Placeholder)

```python
"""
Google Search Agent - Performs web searches via Google Custom Search API.

[PLACEHOLDER - To be implemented]
"""

from __future__ import annotations

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

# Future implementation
google_search_agent = Agent(
    name="google_search",
    model="gemini-2.0-flash",
    description="Performs web searches and retrieves information from Google",
    instruction="You help users search the web and find information.",
    tools=[
        # ToolboxToolset for Google Custom Search API tools
    ],
)
```

### Priority 4: Low (Future)

**Status:** ⏳ Planned – placeholders exist (`google_search`), implementation
will follow once upstream APIs are prioritised.

#### 4.1 Advanced Patterns

1. **Loop Agent for Pagination**
2. **Custom Agents for Complex Logic**
3. **Callback-based Guardrails**
4. **Memory Service Integration**
5. **Artifact Management**

---

## 🎯 Agent Types Summary

### ADK Agent Types You Should Use

| Type | When to Use | Example in Orkhon |
|------|-------------|-------------------|
| **LlmAgent** | Intelligent routing, NL understanding, tool usage | `root_agent`, `dnb_coordinator`, all API agents |
| **SequentialAgent** | Multi-step pipelines, ordered processing | Data pipeline, validate→process→store |
| **ParallelAgent** | Concurrent operations, multiple API calls | Parallel DNB statistics + public register queries |
| **LoopAgent** | Iterative tasks, pagination, polling | Future: Paginate through large datasets |
| **Custom Agent** | Unique logic, special integrations | Future: Rate limiting, caching layers |

---

## 🗺️ Migration Roadmap

### Phase 1: Foundation (Week 1)
- [x] Research ADK patterns
- [ ] Create new directory structure
- [ ] Implement `root_agent` agent
- [ ] Refactor `dnb_coordinator`
- [ ] Update imports
- [ ] Test basic routing

### Phase 2: Enhancement (Week 2)
- [ ] Add workflow agents (Sequential, Parallel)
- [ ] Implement AgentTool patterns where appropriate
- [ ] Add state management examples
- [ ] Create developer documentation

### Phase 3: Network (Week 3-4)
- [ ] Generate agent cards
- [ ] Configure A2A server
- [ ] Test inter-agent communication
- [ ] Document A2A patterns

### Phase 4: Expansion (Future)
- [ ] Add Google Search agent
- [ ] Add data processing agents
- [ ] Implement custom agents
- [ ] Add advanced features (memory, callbacks)

---

## 💡 Key Insights from ADK Documentation

### 1. **Coordinator Pattern is Correct**
✅ Your current `dnb_agent` is using the coordinator pattern correctly with `sub_agents`.

### 2. **LLM vs Workflow Agents**
⚠️ You're using LLM agents for everything. Consider:
- **Workflow agents** for deterministic flows (cheaper, faster, predictable)
- **LLM agents** for intelligent routing (flexible, context-aware)

### 3. **AgentTool vs sub_agents**
- `sub_agents`: LLM decides when to transfer (`transfer_to_agent()`)
- `AgentTool`: LLM treats agent as a function call tool
- **Best practice:** Use `sub_agents` for coordinators, `AgentTool` for explicit invocations

### 4. **State Management**
✅ Use `output_key` to save agent results
✅ Use `{variable}` in instructions to read from state
✅ Pass state between agents in workflows

### 5. **A2A Network**
📡 Prepare for distributed agents:
- Agent cards for discovery
- A2A server for remote calls
- Proper error handling

---

## 📚 Naming Conventions (ADK Best Practices)

### Agent Names

```python
# ✅ GOOD: Clear, descriptive, role-based
root_agent = Agent(name="root_agent", ...)
coordinator = Agent(name="dnb_coordinator", ...)
specialist = Agent(name="dnb_statistics_agent", ...)

# ❌ BAD: Ambiguous, technical details in name
agent = Agent(name="dnb_agent", ...)  # What role?
api_agent = Agent(name="dnb_api_stats", ...)  # Inconsistent pattern
```

### Directory Structure

```
✅ GOOD:
agents/
  root_agent/           # Top-level coordinator
  api_coordinators/      # Category coordinators
    dnb_coordinator/
  api_agents/            # Specialized agents
    dnb_echo/
    dnb_statistics/
  workflows/             # Workflow agents
    data_pipeline/

❌ BAD:
agents/
  dnb_agent/            # Unclear role
  dnb_api_echo/         # Inconsistent naming
```

### Variable Names

```python
# ✅ GOOD: Explicit about role
root_agent = Agent(...)
dnb_coordinator_agent = Agent(...)
dnb_echo_agent = Agent(...)

# ❌ BAD: Generic
agent = Agent(...)
dnb = Agent(...)
```

---

## 🔍 Comparison: Before vs After

### Before (Current)

```
dnb_agent (Coordinator)
├── dnb_api_echo (API Agent)
├── dnb_api_statistics (API Agent)
└── dnb_api_public_register (API Agent)
```

**Issues:**
- ❌ Not extensible (DNB-centric naming)
- ❌ Single-level hierarchy
- ❌ No workflow agents
- ❌ No A2A preparation

### After (Proposed)

```
root_agent (Root Coordinator)
├── dnb_coordinator (Category Coordinator)
│   ├── dnb_echo_agent (Specialized Agent)
│   ├── dnb_statistics_agent (Specialized Agent)
│   └── dnb_public_register_agent (Specialized Agent)
├── google_search_agent (Future Specialized Agent)
├── data_pipeline (Sequential Workflow)
│   ├── validator
│   ├── transformer
│   └── analyzer
└── parallel_fetcher (Parallel Workflow)
```

**Benefits:**
- ✅ Extensible (easy to add non-DNB agents)
- ✅ Clear hierarchy with proper roles
- ✅ Workflow agents for efficiency
- ✅ A2A-ready architecture
- ✅ Follows ADK best practices

---

## 🎓 Learning Resources

1. **ADK Documentation**
   - Multi-Agent Systems: `/adk-docs/docs/agents/multi-agents.md`
   - LLM Agents: `/adk-docs/docs/agents/llm-agents.md`
   - Workflow Agents: `/adk-docs/docs/agents/workflow-agents/`
   - A2A: `/adk-docs/docs/a2a/`

2. **Sample Agents**
   - Financial Advisor: `/adk-samples/python/agents/financial-advisor/`
   - Travel Concierge: `/adk-samples/python/agents/travel-concierge/`
   - Data Science: `/adk-samples/python/agents/data-science/`

3. **Contributing Samples**
   - Workflow Triage: `/adk-python/contributing/samples/workflow_triage/`
   - A2A Basic: `/adk-python/contributing/samples/a2a_basic/`

---

## ✅ Action Items Checklist

### Immediate (This Week)
- [ ] Review this architecture document with team
- [ ] Decide on migration strategy (gradual vs clean slate)
- [ ] Create new directory structure
- [ ] Implement `root_agent` agent
- [ ] Refactor `dnb_coordinator`
- [ ] Test basic routing

### Short-term (Next 2 Weeks)
- [ ] Add Sequential workflow for data pipeline
- [ ] Add Parallel workflow for concurrent API calls
- [ ] Update all documentation
- [ ] Create migration guide for existing code

### Medium-term (Next Month)
- [ ] Prepare A2A infrastructure
- [ ] Add placeholder for Google Search agent
- [ ] Implement state management examples
- [ ] Create developer onboarding guide

### Long-term (Future)
- [ ] Implement custom agents
- [ ] Add memory service integration
- [ ] Add callback-based guardrails
- [ ] Expand to other API categories

---

## 🤔 Decision Points

### 1. Migration Strategy
**Option A: Gradual (Recommended)**
- Create new structure alongside old
- Migrate one category at a time
- Maintain backward compatibility
- Lower risk, longer timeline

**Option B: Clean Slate**
- Remove old structure entirely
- Implement all at once
- Breaking changes acceptable
- Higher risk, faster transformation

**Recommendation:** Option A with clear deprecation warnings

### 2. Workflow Agent Usage
**Question:** When should we use Workflow Agents vs LLM Agents?

**Answer:**
- **SequentialAgent**: When you have a fixed pipeline (validate → transform → store)
- **ParallelAgent**: When you need concurrent execution (multiple API calls)
- **LoopAgent**: When you have iteration (pagination, polling)
- **LlmAgent**: When you need intelligent routing and decision-making

### 3. AgentTool vs sub_agents
**Question:** Should we use AgentTool or sub_agents pattern?

**Answer:**
- **sub_agents**: For coordinators (let LLM decide when to transfer)
- **AgentTool**: For workflows (explicit, programmatic control)

---

## 📞 Support & Next Steps

1. **Review this document thoroughly**
2. **Discuss with team**
3. **Prioritize phases**
4. **Start with Phase 1**
5. **Iterate based on feedback**

**Questions?** Reference:
- ADK Docs: `adk-docs/` folder
- ADK Samples: `adk-samples/python/agents/`
- This guide: `AGENT_ARCHITECTURE_ANALYSIS.md`

---

*Last Updated: 2025-10-19*
*Author: AI Architecture Assistant*
*Version: 1.1*
