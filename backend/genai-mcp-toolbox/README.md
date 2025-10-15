# GenAI Toolbox MCP Server (Google's Implementation)

**Production-ready Model Context Protocol (MCP) server** for DNB APIs and databases, built on [Google's GenAI Toolbox](https://github.com/googleapis/genai-toolbox).

## ⚠️ Important: MCP Protocol Implementations

**This is Google's GenAI Toolbox** implementation of the MCP protocol. Other vendors provide different implementations:

| Implementation | Container Name | Use Case |
|---|---|---|
| **Google GenAI Toolbox** (this) | `orkhon-genai-toolbox-mcp` | Production-ready, observability, DNB APIs |
| Anthropic MCP Servers | `orkhon-anthropic-mcp` | Claude-native tools |
| LangChain MCP | `orkhon-langchain-mcp` | LangChain-specific integrations |

**Why separate containers?** Each vendor's MCP implementation may have:
- Different feature sets (auth methods, tool types)
- Vendor-specific optimizations
- Distinct configuration patterns

---

## What is MCP?

**Model Context Protocol** is an [open standard by Anthropic](https://github.com/modelcontextprotocol) defining how AI agents discover and execute tools:

```
Your Agent → MCP Client SDK → MCP Protocol → MCP Server (Toolbox) → Database/API
```

**GenAI Toolbox** is Google's production-ready MCP server that:
- ✅ Exposes tools via HTTP/SSE on port 5000
- ✅ Handles connection pooling, authentication, rate limiting
- ✅ Built-in OpenTelemetry observability (Jaeger/Cloud Trace)
- ✅ Supports PostgreSQL, MySQL, HTTP APIs (like DNB)

**MCP Toolbox SDKs** connect your agent to this server:
- [Python](https://github.com/googleapis/mcp-toolbox-sdk-python) - `pip install toolbox-langchain`
- [Go](https://github.com/googleapis/mcp-toolbox-sdk-go) - for Genkit agents
- [JavaScript](https://github.com/googleapis/mcp-toolbox-sdk-js) - Node.js/browser

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  Docker Compose Stack                                          │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  GenAI Toolbox :5000 (MCP Server)                        │ │
│  │  • Reads config/tools.yaml                               │ │
│  │  • Manages DNB API connections (dev/prod .env)           │ │
│  │  • Exposes MCP endpoints: /tools, /execute               │ │
│  │  • Sends traces to Jaeger via OTLP                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                 │
│                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Jaeger :16686 (Observability)                           │ │
│  │  • Collects OpenTelemetry traces                         │ │
│  │  • Visualizes request flows                              │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │ MCP Protocol (HTTP/SSE)
                              │
┌────────────────────────────────────────────────────────────────┐
│  Your Agent (Python/Go/JS - separate process)                 │
│  from toolbox_langchain import ToolboxClient                   │
│  client = ToolboxClient("http://localhost:5000")               │
│  tools = await client.aload_toolset()  # MCP discovery         │
└────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Configure Environment Variables

Create `.env` file in this directory:

```bash
# Environment selection (determines which tools.yaml to load)
DNB_ENVIRONMENT=dev  # Change to 'prod' for production

# DEVELOPMENT credentials (loaded when DNB_ENVIRONMENT=dev)
DNB_SUBSCRIPTION_KEY_DEV=b590652c6246466fb08e5418395f8b12
DNB_SUBSCRIPTION_NAME_DEV=dnb-solven-dev

# PRODUCTION credentials (loaded when DNB_ENVIRONMENT=prod)
DNB_SUBSCRIPTION_KEY_PROD=1abbc3f1fe774d94ab09b70597838791
DNB_SUBSCRIPTION_NAME_PROD=dnb-solven

# OpenTelemetry (shared across environments)
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
OTEL_SERVICE_NAME=orkhon-genai-toolbox-mcp
```

**Environment-Based Configuration:**
- `DNB_ENVIRONMENT=dev` → Uses `config/tools.dev.yaml`
- `DNB_ENVIRONMENT=prod` → Uses `config/tools.prod.yaml`
- Docker Compose automatically selects the correct file and API key

### 2. Start the Stack

```bash
# Development mode (default)
docker-compose up -d

# Production mode
echo "DNB_ENVIRONMENT=prod" > .env.local
docker-compose --env-file .env.local up -d
```

### 3. Verify Configuration

```bash
# Check which environment is active
docker-compose exec genai-toolbox-mcp printenv DNB_ENVIRONMENT

# Verify correct tools file is loaded
docker-compose logs genai-toolbox-mcp | grep "tools\..*\.yaml"

# Test connectivity
curl http://localhost:5000/api/tools
```

---

## Environment Switching

**Option A: Edit .env directly**
```bash
# Switch to production
sed -i 's/^DNB_ENVIRONMENT=.*/DNB_ENVIRONMENT=prod/' .env
docker-compose restart genai-toolbox-mcp
```

**Option B: Use environment switcher script**
```powershell
# Windows (PowerShell)
.\scripts\set-env.ps1 -Environment prod

# Linux/Mac
./scripts/set-env.sh prod
```

---

## Configuration Files

```
config/
├── tools.dev.yaml    # Development environment tools (uses DEV subscription key)
└── tools.prod.yaml   # Production environment tools (uses PROD subscription key)
```

**Key Differences:**
- Different `Ocp-Apim-Subscription-Key` headers (via `${DNB_SUBSCRIPTION_KEY_DEV}` / `${DNB_SUBSCRIPTION_KEY_PROD}`)
- Separate rate limits (dev: 30/min, prod: 100/min)
- Different `User-Agent` strings for tracking

---

## Management

### VS Code Tasks (Ctrl+Shift+P → "Run Task")

| Task | Description |
|------|-------------|
| **MCP: Start (Development)** | Start with dev credentials |
| **MCP: Start (Production)** | Start with prod credentials |
| **MCP: Stop All Services** | Stop both containers |
| **MCP: Restart GenAI Toolbox** | Reload config changes |
| **MCP: View Logs (GenAI Toolbox)** | Follow MCP server logs |
| **MCP: View Logs (Jaeger)** | Follow Jaeger logs |
| **MCP: Health Check** | Verify server is running |
| **MCP: List Available Tools** | Show all configured DNB tools |
| **MCP: Open Jaeger UI** | Open tracing dashboard |
| **MCP: Test DNB Echo API** | Quick API connectivity test |

### Command Line

```bash
# View logs
docker-compose logs -f genai-toolbox-mcp
docker-compose logs -f jaeger

# Restart after config changes
docker-compose restart genai-toolbox-mcp

# Stop all services
docker-compose down

# Rebuild image
docker-compose up -d --build

# Check MCP endpoints
curl http://localhost:5000/tools              # List available tools
curl http://localhost:5000/mcp/v1/info        # Server metadata
curl http://localhost:5000/health             # Health status
```

---

## Directory Structure

```
genai-mcp-toolbox/
├── .env                        # Environment variables (DEV/PROD keys)
├── .env.example                # Template for team onboarding
├── .gitignore                  # Excludes .env from git
├── docker-compose.yml          # Multi-container orchestration
├── README.md                   # This file
├── config/
│   └── tools.yaml              # DNB API tool definitions (MCP spec)
└── scripts/
    ├── set-env.sh              # Linux/Mac environment switcher
    └── set-env.ps1             # Windows environment switcher
```

---

## DNB API Configuration Details

### Rate Limits
- **Subscription:** `dnb-solven`
- **Rate limit:** 30 calls/min per subscription
- **Handled by:** Toolbox's `rateLimitPerMinute: 30` in tools.yaml

### API Endpoints

**1. DNB Echo API** (Testing)
- **Path:** `/echo`
- **Purpose:** Validate authentication
- **Tool:** `dnb-echo-test`

**2. Statistics API v2024100101** (Financial Data)
- **Base path:** `/statistics/v2024100101/`
- **Purpose:** Banking sector stats, payment data, financial stability
- **Tools:** 
  - `dnb-statistics-query` - Query datasets
  - `dnb-statistics-metadata` - Get data structure
- **Docs:** Embedded in tool descriptions

**3. Public Register API v1** (Licensing)
- **Base path:** `/public-register/v1/`
- **Purpose:** Search licensed banks, crypto companies, investment firms
- **Tools:**
  - `dnb-public-register-search` - Search by name/type
  - `dnb-public-register-get-org` - Get full organization details
- **External docs:** https://www.dnb.nl/en/public-register/

For full DNB API portal: https://api.portal.dnb.nl/

---

## Observability

### Jaeger Tracing (Local)

**Access UI:** http://localhost:16686

**What you see:**
- End-to-end request flows (Agent → Toolbox → DNB API)
- Latency breakdowns
- Error traces
- Rate limiting events

**Example trace:**
```
Agent Request (100ms)
  └─ Toolbox: dnb-public-register-search (80ms)
      └─ DNB API GET /public-register/v1/organizations (70ms)
```

### Production Observability

**Google Cloud Trace:**
```yaml
# docker-compose.yml (uncomment)
environment:
  - GOOGLE_CLOUD_PROJECT=your-project-id
  - GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json
```

**LangSmith (Agent-level):**
```python
# In your agent code
import os
os.environ["LANGSMITH_API_KEY"] = "your-key"
os.environ["LANGSMITH_PROJECT"] = "orkhon-dnb"
```

---

## Troubleshooting

### Tools Not Loading

```bash
# Validate YAML syntax
docker-compose exec genai-toolbox-mcp cat /config/tools.yaml

# Check environment variables
docker-compose exec genai-toolbox-mcp env | grep DNB

# Verify active environment
docker-compose exec genai-toolbox-mcp printenv DNB_ENVIRONMENT
```

### DNB API Errors

**Authentication failed (401):**
- Verify key at https://api.portal.dnb.nl/ → Profile → Subscriptions
- Check `DNB_ENVIRONMENT` matches key (dev/prod)
- Regenerate key if needed

**Rate limit exceeded (429):**
- DNB allows 30 calls/min per subscription
- Check Jaeger for request volume
- Consider caching responses in your agent

**Connection refused:**
```bash
# Check port availability
netstat -ano | findstr :5000

# Verify Docker network
docker network inspect orkhon-network

# Check container status
docker ps -a | findstr genai-toolbox-mcp
```

### Jaeger Not Receiving Traces

```bash
# Verify OTLP endpoint
docker-compose exec genai-toolbox-mcp printenv OTEL_EXPORTER_OTLP_ENDPOINT

# Check Jaeger health
curl http://localhost:16686

# View Toolbox OTEL logs
docker-compose logs genai-toolbox-mcp | grep -i otel
```

---

## Security Best Practices

1. **Never commit `.env`** - Use `.env.example` for templates
2. **Rotate keys every 6 months** - Set calendar reminder
3. **Use separate dev/prod subscriptions** - Isolate environments
4. **Read-only config mount** - `./config:/config:ro` in docker-compose
5. **Network isolation** - Use dedicated `orkhon-network`

---

## References

### MCP Protocol
- **Spec:** https://github.com/modelcontextprotocol
- **Anthropic Docs:** https://docs.anthropic.com/en/docs/agents-and-tools/mcp

### Google GenAI Toolbox
- **GitHub:** https://github.com/googleapis/genai-toolbox
- **Documentation:** https://googleapis.github.io/genai-toolbox/
- **SDK Python:** https://github.com/googleapis/mcp-toolbox-sdk-python
- **SDK Go:** https://github.com/googleapis/mcp-toolbox-sdk-go
- **SDK JS:** https://github.com/googleapis/mcp-toolbox-sdk-js

### DNB APIs
- **API Portal:** https://api.portal.dnb.nl/
- **Registration:** [My DNB Contact](https://www.dnb.nl/en/contact/)
- **Public Register:** https://www.dnb.nl/en/public-register/
- **Your Subscription:** `dnb-solven`

### Observability
- **OpenTelemetry:** https://opentelemetry.io/
- **Jaeger:** https://www.jaegertracing.io/
- **Google Cloud Trace:** https://cloud.google.com/trace
- **LangSmith:** https://www.langchain.com/langsmith

---

## FAQ

**Q: Can I use this with LangChain's MCP implementation?**  
A: Yes, but run them in separate containers (`orkhon-langchain-mcp` vs `orkhon-genai-toolbox-mcp`) to avoid conflicts.

**Q: How do I switch from dev to prod?**  
A: Use `.\scripts\set-env.ps1 -Environment prod` then restart: `docker-compose restart genai-toolbox-mcp`

**Q: Does this work with Claude Desktop?**  
A: Yes, but use `--stdio` mode instead of HTTP. See [GenAI Toolbox docs](https://googleapis.github.io/genai-toolbox/en/how-to/connect-ide/).

**Q: Can I add custom tools beyond DNB APIs?**  
A: Absolutely! Edit `config/tools.yaml` to add PostgreSQL, MySQL, or other HTTP sources. See [Toolbox tool types](https://googleapis.github.io/genai-toolbox/en/reference/tools/).

---

**Need help?** Open an issue at https://github.com/googleapis/genai-toolbox/issues