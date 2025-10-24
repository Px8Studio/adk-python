# Orkhon Data Science Multi-Agent System

A multi-agent architecture for sophisticated data analysis, integrating BigQuery database access, Python analytics with Code Interpreter, and future support for AlloyDB and BigQuery ML.

## Overview

This implementation follows the ADK samples pattern for data science agents, adapted for the Orkhon project's DNB Statistics dataset. The system coordinates between specialized sub-agents to handle different aspects of data analysis.

### Architecture

```
data_science_root_agent (Coordinator)
├── bigquery_agent (NL2SQL)
│   ├── BigQuery Built-in Tools (execute_sql)
│   └── Schema-aware query generation
└── analytics_agent (NL2Py)
    └── Vertex AI Code Interpreter
        ├── pandas, numpy, matplotlib
        └── Stateful execution
```

### Current Features (MVP)

- ✅ **Root Coordinator Agent**: Routes queries to appropriate sub-agents
- ✅ **BigQuery Agent**: Natural language to SQL translation and execution
- ✅ **Analytics Agent**: Python data analysis and visualization via Code Interpreter
- ✅ **Dataset Configuration**: JSON-based dataset definition system
- ✅ **Schema Awareness**: Automatic schema loading for query generation

### Planned Features

- ⏳ **AlloyDB Agent**: PostgreSQL database access via MCP Toolbox
- ⏳ **BQML Agent**: BigQuery ML model training with RAG-based reference
- ⏳ **Cross-Dataset Joins**: Query coordination across BigQuery and AlloyDB
- ⏳ **CHASE-SQL**: Advanced NL2SQL method for complex queries

## Quick Start

### Prerequisites

- Python 3.12+
- Google Cloud Project with:
  - Vertex AI API enabled
  - BigQuery API enabled
  - DNB Statistics dataset loaded in BigQuery
- Poetry or uv for dependency management

### Installation

1. **Install dependencies**:
   ```powershell
   # Using Poetry (recommended for Orkhon)
   cd backend
   poetry install
   
   # Or using uv
   uv sync
   ```

2. **Configure environment**:
   ```powershell
   # Copy the example env file
   cp backend/adk/agents/data_science/.env.example backend/adk/agents/data_science/.env
   
   # Edit .env and fill in your values
   # Required variables:
   # - GOOGLE_CLOUD_PROJECT
   # - BQ_DATA_PROJECT_ID
   # - BQ_DATASET_ID
   ```

3. **Verify BigQuery dataset**:
   ```powershell
   # Ensure your BigQuery dataset exists
   bq ls --project_id=your-project-id dnb_statistics
   ```

### Running the Agent

#### Interactive CLI Mode

```powershell
# From project root
python backend/adk/run_data_science_agent.py
```

This starts an interactive session where you can ask questions about your data.

#### Single Query Mode

```powershell
# Run a single query and exit
python backend/adk/run_data_science_agent.py --query "What data do you have?"
```

#### ADK Web UI (Coming Soon)

```powershell
# Start ADK web server
adk web --agents-dir backend/adk
```

### Example Interactions

```
You: What data do you have access to?

Agent: I have access to the DNB Statistics dataset in BigQuery, which contains
Dutch financial and economic data including insurance & pensions, financial
markets, balance of payments, and monetary statistics.

---

You: Show me the top 5 records from the insurance_corps_balance_sheet_quarter table

Agent: [Executes BigQuery query and displays results]

---

You: Create a visualization showing trends over time for that data

Agent: [Generates Python code via Code Interpreter and displays chart]
```

## Project Structure

```
backend/adk/agents/data_science/
├── __init__.py                           # Module initialization
├── agent.py                              # Root coordinator agent
├── prompts.py                            # Root agent instructions
├── tools.py                              # Root agent tools (call_bigquery_agent, call_analytics_agent)
├── dnb_statistics_dataset_config.json    # Dataset configuration
├── .env.example                          # Environment template
├── README.md                             # This file
└── sub_agents/
    ├── __init__.py
    ├── bigquery/
    │   ├── __init__.py
    │   ├── agent.py                      # BigQuery sub-agent
    │   ├── prompts.py                    # BigQuery instructions
    │   └── tools.py                      # BigQuery utilities
    └── analytics/
        ├── __init__.py
        ├── agent.py                      # Analytics sub-agent
        └── prompts.py                    # Analytics instructions
```

## Configuration

### Dataset Configuration

The agent uses `dnb_statistics_dataset_config.json` to define available datasets:

```json
{
  "datasets": [
    {
      "type": "bigquery",
      "name": "dnb_statistics",
      "description": "DNB Statistics dataset..."
    }
  ],
  "cross_dataset_relations": {
    "foreign_keys": []
  }
}
```

### Environment Variables

See `.env.example` for all available configuration options. Key variables:

```bash
# Google Cloud
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery
BQ_DATA_PROJECT_ID=your-project-id
BQ_DATASET_ID=dnb_statistics

# Models (optional, defaults to gemini-2.0-flash-exp)
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
BIGQUERY_AGENT_MODEL=gemini-2.0-flash-exp
ANALYTICS_AGENT_MODEL=gemini-2.0-flash-exp
```

## Development

### Adding a New Sub-Agent

1. Create a new directory under `sub_agents/`
2. Implement `agent.py`, `prompts.py`, and any needed `tools.py`
3. Add the agent to the root agent's configuration in `agent.py`
4. Update the dataset configuration if needed

### Testing

```powershell
# Run tests (when implemented)
pytest tests/

# Test specific functionality
python backend/adk/run_data_science_agent.py --query "test query"
```

### Debugging

Set log level to DEBUG in your `.env`:

```bash
LOG_LEVEL=DEBUG
```

## Integration with Orkhon

This data science agent is part of the larger Orkhon project:

- **ETL Pipeline**: Bronze/Silver/Gold layers feed into BigQuery
- **API Integration**: Works alongside DNB public API agents
- **Tracing**: Will integrate with Jaeger for observability
- **Deployment**: Future Cloud Run deployment planned

## Next Steps

1. **Load Data**: Upload your Bronze layer parquet files to BigQuery
2. **Test Queries**: Verify the agent can access and query your data
3. **Add BQML Agent**: Implement machine learning capabilities
4. **Add AlloyDB Agent**: Enable PostgreSQL database access
5. **Cross-Dataset Queries**: Implement joins across BigQuery and AlloyDB

## References

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Data Science Sample](https://github.com/google/adk-samples/tree/main/python/agents/data-science)
- [BigQuery Built-in Tools](https://google.github.io/adk-docs/tools/built-in-tools/#bigquery)
- [Vertex AI Code Interpreter](https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-execution)

## License

Copyright 2025 Google LLC - Apache License 2.0

---

**Status**: 🚧 MVP Implementation Complete - Ready for Data Integration
