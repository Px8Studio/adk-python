# Orkhon Backend

> **AI Agent Infrastructure for DNB APIs**  
> Build intelligent agents with LangGraph + GenAI Toolbox + DNB APIs

---

## 📋 Overview

The Orkhon backend provides a complete infrastructure for building AI agents that interact with De Nederlandsche Bank (DNB) APIs. It consists of four main components:

```
backend/
├── adk/           # Agent Development Kit - LangGraph agents
├── agentbox/      # OpenAPI → Toolbox conversion utilities
├── apis/          # DNB API specifications and generated code
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

Contains LangGraph-based AI agents that use the GenAI Toolbox.

**Key Files:**
- `simple_dnb_agent.py` - Example agent using DNB tools
- `simple_agent.ipynb` - Jupyter notebook for interactive development
- `scripts/` - Helper scripts for agent development

**Learn More:** See [Agent Development Guide](adk/README.md)

---

### 🔧 `/agentbox` - OpenAPI Conversion Tools

Utilities to convert OpenAPI specifications into GenAI Toolbox tool definitions.

**Key Features:**
- Converts OpenAPI 3.x specs → `tools.yaml` format
- Generates 84+ tools from DNB API specifications
- Validates tool schemas and parameters

**Usage:**
```powershell
cd backend/agentbox
python openapi_to_toolbox.py convert --all
```

**Output:** Generated tools are placed in `backend/toolbox/config/dev/` and `backend/toolbox/config/prod/`

**Learn More:** See [OpenAPI Conversion Guide](agentbox/README.md)

---

### 🌐 `/apis/dnb` - DNB API Integration

DNB (De Nederlandsche Bank) API specifications, documentation, and generated clients.

**Structure:**
```
apis/dnb/
├── specs/              # OpenAPI 3.x specifications
│   ├── openapi3_statisticsdatav2024100101.yaml
│   ├── openapi3_publicdatav1.yaml
│   └── openapi3_echoapi.yaml
├── generated/          # Auto-generated Python clients
├── docs/               # API documentation
├── scripts/            # Code generation scripts
└── tests/              # API integration tests
```

**Quick Start:**
- 📖 [DNB API Services Overview](apis/dnb/DNB%20API%20Services.MD)
- 🚀 [Quick Start Guide](apis/dnb/QUICKSTART.md)

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
├── tools.dev.yaml      # Development tool definitions
├── tools.prod.yaml     # Production tool definitions
├── dev/                # Generated DNB tool configs (dev)
└── prod/               # Generated DNB tool configs (prod)
```

**Management Tasks:**

Use VS Code tasks (Ctrl+Shift+P → "Tasks: Run Task"):
- `MCP: Start Dev Server` - Start all services
- `MCP: Stop Dev Server` - Stop all services
- `MCP: View Dev Logs (Live)` - Monitor logs in real-time
- `MCP: Open Toolbox Web UI` - Open http://localhost:5000/ui/
- `MCP: Open Jaeger Tracing UI` - Open http://localhost:16686

**Learn More:**
- 📖 [Toolbox Configuration Guide](toolbox/config/QUICK_ANSWER.md)
- 📊 [Jaeger Tracing Documentation](toolbox/docs/Jaeger%20UI.md)

---

## 🔄 Development Workflow

### Typical Development Flow:

```
1. Update OpenAPI Specs
   └─> apis/dnb/specs/*.yaml

2. Generate Tool Definitions
   └─> Run: python agentbox/openapi_to_toolbox.py convert --all
   └─> Output: toolbox/config/dev/*.yaml

3. Restart Toolbox
   └─> Run: docker-compose -f toolbox/docker-compose.dev.yml restart

4. Test Tools in Toolbox UI
   └─> Open: http://localhost:5000/ui/

5. Build/Update Agent
   └─> Edit: adk/simple_dnb_agent.py
   └─> Run: python adk/simple_dnb_agent.py

6. Monitor with Jaeger
   └─> Open: http://localhost:16686
   └─> View traces and performance metrics
```

### Quick Restart Flow (VS Code Task):

Run task: **"🔄 Convert & Restart: Convert APIs → Restart Server → Open UI"**

This executes:
1. OpenAPI → Toolbox conversion
2. Restarts GenAI Toolbox server
3. Opens Web UI for testing

---

## 🌐 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| **GenAI Toolbox UI** | http://localhost:5000/ui/ | Browse and test tools |
| **Toolbox API** | http://localhost:5000/api/ | Programmatic tool access |
| **Jaeger UI** | http://localhost:16686 | Distributed tracing & monitoring |
| **PostgreSQL** | localhost:5432 | Tool metadata storage |

---

## 📚 Documentation

### Component Documentation:
- **[ADK - Agent Development](adk/README.md)** - Build LangGraph agents
- **[AgentBox - OpenAPI Conversion](agentbox/README.md)** - Convert APIs to tools
- **[DNB APIs - Integration Guide](apis/dnb/DNB%20API%20Services.MD)** - DNB API documentation
- **[Toolbox - Configuration](toolbox/config/QUICK_ANSWER.md)** - Tool configuration guide

### Monitoring & Observability:
- **[Jaeger Tracing Guide](toolbox/docs/Jaeger%20UI.md)** - Understand distributed tracing

---

## 🛠️ Troubleshooting

### Common Issues:

**1. Docker services won't start:**
```powershell
# Check Docker Desktop is running
docker --version

# View service logs
cd backend/toolbox
docker-compose -f docker-compose.dev.yml logs
```

**2. Tools not appearing in Toolbox:**
```powershell
# Validate tool configuration
cd backend/toolbox
python validate_config.py

# Restart with fresh build
docker-compose -f docker-compose.dev.yml up -d --build
```

**3. DNB API authentication errors:**
```powershell
# Verify API key is set
echo $env:DNB_SUBSCRIPTION_KEY_DEV

# Test direct API access
curl -H "Ocp-Apim-Subscription-Key: $env:DNB_SUBSCRIPTION_KEY_DEV" `
     https://api.dnb.nl/echo-api/helloworld
```

**4. Agent can't connect to Toolbox:**
- Ensure Toolbox is running: http://localhost:5000/api/toolset/
- Check `ToolboxClient` configuration in your agent
- Review Jaeger traces for connection errors

---

## 🤝 Contributing

When contributing to the backend:

1. **API Changes:** Update OpenAPI specs in `apis/dnb/specs/`
2. **Tool Definitions:** Regenerate with `openapi_to_toolbox.py`
3. **Agent Code:** Follow LangGraph patterns in `adk/`
4. **Documentation:** Update relevant README files

---

## 📄 License

See [LICENSE](../LICENSE) in project root.

---

## 🔗 Related Projects

- **[GenAI Toolbox](https://github.com/GoogleCloudPlatform/genai-toolbox)** - Upstream MCP server
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Agent framework
- **[OpenTelemetry](https://opentelemetry.io/)** - Observability standards
- **[Jaeger](https://www.jaegertracing.io/)** - Distributed tracing platform