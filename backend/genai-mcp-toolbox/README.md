# MCP Server for Databases (GenAI Toolbox)

Local instance of [Google's GenAI Toolbox](https://github.com/googleapis/genai-toolbox) - a **Model Context Protocol (MCP) server** that provides standardized access to databases, HTTP APIs, and other tools.

## What is MCP?

**Model Context Protocol** is an [open standard by Anthropic](https://github.com/modelcontextprotocol) that defines how AI agents discover and execute tools:

```
Your Agent → MCP Client SDK → MCP Protocol → MCP Server (Toolbox) → Database/API
```

**GenAI Toolbox** is Google's production-ready MCP server implementation that:
- Exposes tools via HTTP/SSE on port 5000
- Handles connection pooling, authentication, rate limiting
- Provides built-in observability (OpenTelemetry)
- Supports databases (PostgreSQL, MySQL, etc.) and HTTP sources

**MCP Toolbox SDKs** are client libraries that connect to Toolbox:
- [Python](https://github.com/googleapis/mcp-toolbox-sdk-python) - `pip install toolbox-langchain`
- [Go](https://github.com/googleapis/mcp-toolbox-sdk-go) - for Genkit agents
- [JavaScript](https://github.com/googleapis/mcp-toolbox-sdk-js) - Node.js/browser

### How Everything Fits Together

```
┌─────────────────────────────────────────────────────────────┐
│  MCP Protocol (Anthropic's open standard)                   │
│  https://github.com/modelcontextprotocol                    │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ implements
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  genai-toolbox (Google's MCP Server Implementation)         │
│  - Runs as HTTP/SSE server on port 5000                     │
│  - Exposes tools via MCP protocol                           │
│  - Handles DB connections, HTTP calls, auth                 │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ consumed by
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  mcp-toolbox-sdk-* (MCP Client SDKs)                        │
│  - Python/JS/Go clients                                     │
│  - Connect to Toolbox server via MCP protocol               │
│  - Convert MCP tools → LangChain/Genkit/custom tools        │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ used by
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Your Agent Code (LangGraph, Genkit, etc.)                  │
│  - Loads tools via SDK                                      │
│  - Executes agent logic                                     │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  This Container (MCP Server)                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  GenAI Toolbox :5000                                   │  │
│  │  • Reads config/tools.yaml                             │  │
│  │  • Manages DNB API connections (via .env)              │  │
│  │  • Exposes MCP endpoints: /tools, /execute             │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                     ▲
                     │ MCP Protocol (HTTP/SSE)
                     │
┌──────────────────────────────────────────────────────────────┐
│  Your Agent (separate process)                               │
│  from toolbox_langchain import ToolboxClient                 │
│  client = ToolboxClient("http://localhost:5000")             │
│  tools = await client.aload_toolset()  # MCP discovery       │
└──────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Configure Environment Variables

Create `.env` file in **this directory**:

```bash
# DNB API Keys (get from https://api.portal.dnb.nl/)
DNB_SUBSCRIPTION_KEY=your-primary-key
DNB_SUBSCRIPTION_KEY_SECONDARY=your-secondary-key
DNB_SUBSCRIPTION_NAME=dnb-solven

# Optional: Observability
# OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
```

**Why two keys?**
- **Primary**: Production use
- **Secondary**: Dev/staging or zero-downtime rotation
- **Rotation strategy**: Regenerate primary → update .env → regenerate secondary

### 2. Start the MCP Server

```bash
# Option 1: Docker Compose (recommended)
docker-compose up -d

# Option 2: VS Code Task
# Press Ctrl+Shift+P → "Run Task" → "Start MCP Toolbox"

# Verify it's running
curl http://localhost:5000/health
```

### 3. Configure Tools

Edit `config/tools.yaml` to define your data sources and tools:

```yaml
sources:
  dnb-http:
   kind: http
   baseUrl: https://api.portal.dnb.nl
   headers:
     Ocp-Apim-Subscription-Key: ${DNB_SUBSCRIPTION_KEY}
     X-Subscription-Name: ${DNB_SUBSCRIPTION_NAME}
   timeout: 30s

tools:
  dnb-query:
   kind: http
   source: dnb-http
   method: GET
   path: /your/endpoint
   description: Query DNB public data
   parameters:
     query:
      type: string
      description: Search query
   queryParams:
     q: ${query}
```

### 4. Connect Your Agent

```python
# Install client SDK
pip install toolbox-langchain

# In your agent code
from toolbox_langchain import ToolboxClient

async with ToolboxClient("http://localhost:5000") as client:
   # MCP protocol: discover all tools from tools.yaml
   tools = await client.aload_toolset()
   
   # Use with LangChain/LangGraph
   from langgraph.prebuilt import create_react_agent
   agent = create_react_agent(llm, tools)
```

## Directory Structure

```
mcp-server-databases/
├── .env                    # Environment variables (KEEP SECRET!)
├── .gitignore              # Excludes .env from git
├── docker-compose.yml      # Container orchestration
├── README.md               # This file
└── config/
   └── tools.yaml          # Tool and source definitions (MCP spec)
```

## Management Commands

```bash
# View logs
docker-compose logs -f toolbox

# Restart after config changes
docker-compose restart

# Stop server
docker-compose down

# Rebuild image
docker-compose up -d --build

# Check MCP endpoints
curl http://localhost:5000/tools          # List available tools
curl http://localhost:5000/mcp/v1/info    # Server metadata
```

## DNB API Integration

**Your subscription:** `dnb-solven`  
**Rate limit:** 30 calls/min  
**Base URL:** https://api.portal.dnb.nl  
**Auth header:** `Ocp-Apim-Subscription-Key`

For full DNB API docs, see [../apis/mijn-dnb/DNB API Services.MD](../apis/mijn-dnb/DNB API Services.MD)

## Observability

Toolbox has **built-in OpenTelemetry** support:

```yaml
# docker-compose.yml
environment:
  - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
  - OTEL_SERVICE_NAME=orkhon-mcp-toolbox
```

**Viewing traces:**
- **Local:** Run Jaeger (`docker run -p 16686:16686 jaegertracing/all-in-one`)
- **Cloud:** Google Cloud Trace, Datadog, Honeycomb
- **LangSmith:** Works with any framework for agent-level observability

## Troubleshooting

**Tools not loading:**
```bash
# Validate YAML syntax
docker-compose exec toolbox cat /config/tools.yaml

# Check environment variables
docker-compose exec toolbox env | grep DNB
```

**DNB API errors:**
- Verify key in .env matches your subscription at https://api.portal.dnb.nl/
- Check rate limit (30 calls/min per subscription)
- Ensure `Ocp-Apim-Subscription-Key` header is set in tools.yaml

**Connection refused:**
- Ensure port 5000 isn't in use: `netstat -ano | findstr :5000`
- Check Docker network: `docker network ls`

## References

- **MCP Protocol Spec:** https://github.com/modelcontextprotocol
- **GenAI Toolbox:** https://github.com/googleapis/genai-toolbox
- **MCP Python SDK:** https://github.com/googleapis/mcp-toolbox-sdk-python
- **Toolbox Docs:** https://googleapis.github.io/genai-toolbox/