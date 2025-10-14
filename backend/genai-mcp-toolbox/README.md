# MCP Server for Databases (Toolbox)

Local instance of [Google's GenAI Toolbox](https://github.com/googleapis/genai-toolbox) providing MCP-compatible database and HTTP tools.

## Quick Start

1. **Set environment variables** (root `.env`):
   ```bash
   DNB_SUBSCRIPTION_KEY=your-dnb-key
   ```

2. **Start the server**:
   ```bash
   # From this directory
   docker-compose up -d
   
   # Or use VS Code task: "Start MCP Toolbox"
   ```

3. **Verify it's running**:
   ```bash
   curl http://localhost:5000/health
   ```

## Configuration

- **Tools**: Edit `config/tools.yaml` to add/modify tools and sources
- **Logs**: `docker-compose logs -f toolbox`
- **Stop**: `docker-compose down`

## Directory Structure

```
mcp-server-databases/
├── config/
│   └── tools.yaml          # Tool and source definitions
├── docker-compose.yml      # Container orchestration
└── README.md               # This file
```

## DNB API Integration

Your subscription: **dnb-solven**  
Rate limit: 30 calls/min  
Headers required: `Ocp-Apim-Subscription-Key`

See [DNB API Services.MD](../apis/mijn-dnb/DNB API Services.MD) for full docs.

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