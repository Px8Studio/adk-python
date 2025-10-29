# Orkhon Backend

> **AI Agent Infrastructure for DNB APIs**  
> Build intelligent agents with LangGraph + GenAI Toolbox + DNB APIs

---

## 📋 Overview

The Orkhon backend provides a complete infrastructure for building AI agents that interact with De Nederlandsche Bank (DNB) APIs. It consists of four main components:

```
backend/
├── adk/           # Agent Development Kit - Multi-agent system with ADK
├── open-api-box/  # OpenAPI → Toolbox conversion utilities
├── apis/          # DNB API specifications and OpenAPI specs
├── clients/       # Kiota-generated DNB API clients
├── etl/           # ETL pipelines for DNB data extraction
└── toolbox/       # GenAI Toolbox MCP server (Docker-based)
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    AI Agent Layer (ADK)                      │
│  • LangGraph agents (simple_dnb_agent.py)                   │
│  • Google Gemini LLM integration                             │
│  • Agent Development Kit (ADK) Web UI                        │
└────────────────────┬─────────────────────────────────────────┘
                     │ ToolboxClient
                     ▼
┌──────────────────────────────────────────────────────────────┐
│              Tool Orchestration Layer (Toolbox)              │
│  • GenAI Toolbox MCP Server :5000                           │
│  • 84+ DNB API tools from OpenAPI specs                     │
│  • Tool validation and schema management                     │
│  • OpenTelemetry + Jaeger tracing :16686                    │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                External API Layer (DNB APIs)                 │
│  • Statistics API (v2024100101)                             │
│  • Public Register API (v1)                                  │
│  • Echo API (testing/validation)                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (for toolbox services)
- **Python 3.11+** with `uv` package manager
- **DNB API Key** (set in environment: `DNB_SUBSCRIPTION_KEY_DEV`)

### 1. Start the GenAI Toolbox

```powershell
# Navigate to toolbox directory
cd backend/toolbox

# Start all services (GenAI Toolbox + Jaeger + PostgreSQL)
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker ps --filter name=orkhon-toolbox
```

**Services Available:**
- 🌐 **GenAI Toolbox UI:** http://localhost:5000/ui/
- 📊 **Jaeger Tracing UI:** http://localhost:16686
- 🗄️ **PostgreSQL:** localhost:5432 (for persistent storage)

### 2. Run a Simple Agent

```powershell
# Navigate to ADK directory
cd backend/adk

# Run the DNB agent
python simple_dnb_agent.py
```

---

## 📁 Component Details

### 🤖 `/adk` - Agent Development Kit

Contains Google ADK-based multi-agent system that uses the GenAI Toolbox.

**Key Files:**
- `agents/root_agent/` - Root coordinator agent
- `agents/api_coordinators/` - Domain-specific coordinators (DNB, etc.)
- `agents/api_agents/` - Specialized API agents (echo, statistics, public register)
- `simple_dnb_agent.py` - Standalone LangGraph example using DNB tools
- `run_dnb_openapi_agent.py` - Script to run the multi-agent system
- `simple_agent.ipynb` - Jupyter notebook for interactive development

**Learn More:** See Agent Implementation docs in `adk/AGENT_*.md` files

---

### 🔧 `/open-api-box` - OpenAPI Conversion Tools

Utilities to convert OpenAPI specifications into GenAI Toolbox tool definitions.

**Key Features:**
- Converts OpenAPI 3.x specs → YAML tool format
- Generates 87+ tools from DNB API specifications
- Validates tool schemas and parameters
- Supports both dev and prod environments

**Usage:**
```powershell
cd backend/open-api-box
python openapi_toolbox.py convert --all
```

**Output:** Generated tools are placed in:
- `backend/toolbox/config/dev/` (numbered YAML files like `10-dnb-echo.generated.yaml`)
- `backend/toolbox/config/prod/` (same structure for production)

**Learn More:** Uses the upstream `openapi-mcp-codegen` project for conversion logic

---

### 🌐 `/apis` - DNB API Specifications

OpenAPI 3.x specifications for all DNB APIs.

**Structure:**
```
apis/dnb/
├── specs/              # OpenAPI 3.x specifications
│   ├── openapi3_statisticsdatav2024100101.yaml
│   ├── openapi3_publicdatav1.yaml
│   └── openapi3-echo-api.yaml
└── docs/               # API documentation
```

**Quick Start:**
- 📖 [DNB API Services Overview](apis/dnb/DNB%20API%20Services.MD)
- 🚀 [Quick Start Guide](apis/dnb/QUICKSTART.md)

---

### 📦 `/clients` - Kiota-Generated API Clients

Python HTTP clients generated using Microsoft's Kiota tool.

**Structure:**
```
clients/
├── dnb-echo/              # DNB Echo API client
├── dnb-public-register/   # Public Register API client
├── dnb-statistics/        # Statistics API client
├── echo_client.py         # Wrapper for Echo client
├── statistics_client.py   # Wrapper for Statistics client
└── public_register_client.py  # Wrapper for Public Register client
```

**Learn More:** See [Clients README](clients/README.md)

---

### 📊 `/etl` - ETL Pipelines

Extract-Transform-Load pipelines for DNB data.

**Structure:**
```
etl/
├── dnb_statistics/     # Statistics API ETL (17+ extractors)
├── dnb_public_register/  # Public Register ETL (6 extractors)
├── run_dnb_stats_etl.py  # Statistics ETL runner
└── run_dnb_pr_etl.py     # Public Register ETL runner
```

**Features:**
- Automated data extraction from DNB APIs
- Parquet file output (Bronze layer)
- Configurable extractors per endpoint

---

### 🐳 `/toolbox` - GenAI Toolbox MCP Server

Docker-based Model Context Protocol (MCP) server that exposes DNB APIs as tools for AI agents.

**Key Components:**
- **GenAI Toolbox** - Go-based MCP server from [Google Cloud GenAI Toolbox](https://github.com/GoogleCloudPlatform/genai-toolbox)
- **Jaeger** - Distributed tracing for observability
- **PostgreSQL** - Tool metadata and configuration storage

**Configuration:**
```
toolbox/config/
├── tools.dev.yaml      # Development environment root config
├── tools.prod.yaml     # Production environment root config
├── dev/                # Generated DNB tool configs (dev)
│   ├── 00-base.yaml    # Base configuration (sources, auth)
│   ├── 10-dnb-echo.generated.yaml
│   ├── 20-dnb-statistics.generated.yaml
│   └── 30-dnb-public-register.generated.yaml
└── prod/               # Generated DNB tool configs (prod)
    └── (same structure as dev)
```

**Management Tasks:**

Use VS Code tasks (Ctrl+Shift+P → "Tasks: Run Task"):
- `🚀 Quick Start: Full Orkhon Stack` - Start everything (includes MCP restart)
- `MCP: Start Dev Server` - Start all services
- `MCP: Stop Dev Server` - Stop all services
- `MCP: View Dev Logs (Live)` - Monitor logs in real-time
- `MCP: Open Toolbox Web UI` - Open http://localhost:5000/ui/
- `MCP: Open Jaeger Tracing UI` - Open http://localhost:16686

**Learn More:**
- 📖 [Toolbox Configuration Guide](toolbox/config/QUICK_ANSWER.md)
- 📊 [Jaeger Tracing Documentation](toolbox/docs/Jaeger%20UI.md)
- 🏗️ [Current Architecture (What We Built)](etl/docs/ARCHITECTURE_CURRENT.md)
- 🔮 [Future DNB IT Architecture (Planned)](etl/docs/ARCHITECTURE_DNB_FUTURE.md)

---

## 🤝 Contributing

When contributing to the backend:

1. **API Changes:** Update OpenAPI specs in `apis/dnb/specs/`
2. **Tool Definitions:** Regenerate with `open-api-box/openapi_toolbox.py`
3. **Agent Code:** Follow ADK multi-agent patterns in `adk/agents/`
   - **DNB Coordinators:** `adk/agents/api_coordinators/`
   - **DNB Specialists:** `adk/agents/api_agents/`
   - **Data Science:** `adk/agents/data_science/`
4. **ETL Changes:** Update extractors in `etl/`
5. **Documentation:** Update relevant README and markdown files

**Current Agent Count:**
- Root: 1 (root_agent)
- Coordinators: 2 (dnb_coordinator, data_science_agent)
- Specialists: 5 (3 DNB API + 2 Data Science)
- **Total: 8 agents implemented** ✅

---

## 📄 License

See [LICENSE](../LICENSE) in project root.

---

## 🔗 Related Projects

- **[GenAI Toolbox](https://github.com/GoogleCloudPlatform/genai-toolbox)** - Upstream MCP server
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Agent framework
- **[OpenTelemetry](https://opentelemetry.io/)** - Observability standards
- **[Jaeger](https://www.jaegertracing.io/)** - Distributed tracing platform