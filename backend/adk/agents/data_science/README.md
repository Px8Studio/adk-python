# Orkhon Data Science Coordinator Agent

A domain-level coordinator for data science operations within the Orkhon multi-agent system.

## Overview

This agent coordinates between specialized sub-agents for:
- BigQuery database access (NL2SQL)
- Python analytics and visualization (NL2Py with Code Interpreter)

**Integration Pattern:** This agent is a sub-agent of the Orkhon `root_agent`. It exists as part of the integrated multi-domain system, not as a standalone service.

### Architecture

```
root_agent (System Orchestrator)
├── dnb_coordinator (DNB API Domain)
└── data_science_coordinator (Data Science Domain) ← THIS AGENT
    ├── bigquery_agent (Database Queries)
    └── analytics_agent (Python Analysis)
```

## Usage

### Production Integration (Primary Pattern)

```python
from adk.agents.root_agent import root_agent
from google.adk.runners import Runner

# The data_science_coordinator is already integrated in root_agent
runner = Runner(root_agent)
runner.run("Show me trends in the pension fund data")
```

### Development Testing (Testing Only)

For isolated development/testing of data science features:

```powershell
# Run test script (bypasses root_agent for faster iteration)
python backend/adk/run_data_science_agent.py --query "What data do you have?"
```

**⚠️ Note:** The `run_data_science_agent.py` script is a development tool only. Production usage should always go through the integrated `root_agent`.

## Quick Start

### Prerequisites

- Python 3.12+
- Google Cloud Project with Vertex AI and BigQuery enabled
- DNB Statistics dataset loaded in BigQuery

### Installation

1. **Install dependencies**:
   ```powershell
   cd backend
   poetry install
   ```

2. **Configure environment**:
   ```powershell
   cp backend/adk/agents/data_science/.env.example backend/adk/agents/data_science/.env
   # Edit .env with your GCP project settings
   ```

3. **Load data to BigQuery** (see [Data Setup](#data-setup) below)

### Running the Agent

**Production:** Use the integrated system via root_agent
```powershell
python backend/adk/run_root_agent.py
# or
adk web --agents-dir backend/adk/agents
```

**Development:** Use the test script for faster iteration
```powershell
python backend/adk/run_data_science_agent.py
```

## Integration Patterns

### Pattern 1: System Integration (Production)

```python
# backend/adk/agents/root_agent/agent.py
from google.adk.agents.llm_agent import Agent
from adk.agents.api_coordinators import get_dnb_coordinator_agent
from adk.agents.data_science import data_science_coordinator

root_agent = Agent(
    name="root_agent",
    sub_agents=[
        get_dnb_coordinator_agent(),
        data_science_coordinator,  # Integrated here
    ],
)
```

**Routing Logic:** The root_agent automatically routes:
- "Get exchange rates" → `dnb_coordinator`
- "Show trends in pension data" → `data_science_coordinator`
- "Get stats and analyze trends" → Sequential coordination

### Pattern 2: Development Testing (Non-Production)

```python
# backend/adk/run_data_science_agent.py
from google.adk.runners import Runner
from adk.agents.data_science import data_science_coordinator

# Direct access for faster development iteration
runner = Runner(data_science_coordinator)
runner.run("Test query")
```

**Purpose:** Bypass root_agent routing for faster development cycles when working on data science features in isolation.

### Module Structure

```
backend/adk/agents/data_science/
├── __init__.py              # Exports: data_science_coordinator
├── agent.py                 # Defines coordinator agent
└── sub_agents/
    ├── bigquery/
    │   └── agent.py         # BigQuery sub-agent
    └── analytics/
        └── agent.py         # Analytics sub-agent
```

## Project Structure

```
backend/adk/agents/data_science/
├── __init__.py                           # Module exports
├── agent.py                              # Coordinator agent
├── prompts.py                            # Agent instructions
├── tools.py                              # Agent tools
├── dnb_statistics_dataset_config.json    # Dataset configuration
├── .env.example                          # Environment template
├── README.md                             # This file
└── sub_agents/
    ├── bigquery/                         # Database queries
    └── analytics/                        # Python analysis
```

## Configuration

### Dataset Configuration

The agent uses `dnb_statistics_dataset_config.json`:

```json
{
  "datasets": [
    {
      "type": "bigquery",
      "name": "dnb_statistics",
      "description": "DNB Statistics dataset..."
    }
  ]
}
```

### Environment Variables

Key variables in `.env`:

```bash
# Google Cloud
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery
BQ_DATA_PROJECT_ID=your-project-id
BQ_DATASET_ID=dnb_statistics

# Models (optional)
DATA_SCIENCE_AGENT_MODEL=gemini-2.0-flash-exp
```

## Development

### Testing the Agent

**Integrated Testing:**
```powershell
python backend/adk/run_root_agent.py
You: Analyze pension fund trends
```

**Isolated Testing:**
```powershell
python backend/adk/run_data_science_agent.py --query "What tables exist?"
```

### Debugging

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logs.

## Data Setup

### Load DNB Statistics to BigQuery

```powershell
# Create dataset
bq mk --location=us-central1 --dataset your-project-id:dnb_statistics

# Load parquet files
bq load --source_format=PARQUET `
  dnb_statistics.insurance_corps_balance_sheet_quarter `
  backend/data/1-bronze/insurance_corps_balance_sheet_quarter.parquet
```

## References

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Data Science Sample](https://github.com/google/adk-samples/tree/main/python/agents/data-science)
- [Orkhon Architecture](../../../ARCHITECTURE_ENHANCEMENTS.md)

## License

Copyright 2025 Google LLC - Apache License 2.0

---

**Status:** ✅ Integrated Domain Coordinator - Part of Orkhon Multi-Agent System
