# DNB API MCP Generation Scripts

This directory contains automation scripts for generating MCP (Model Context Protocol) servers from OpenAPI specifications.

## 🎯 Overview

These scripts use [cnoe-io/openapi-mcp-codegen](https://github.com/cnoe-io/openapi-mcp-codegen) to automatically generate:
- Complete MCP servers with tools for each API endpoint
- LangGraph React agents ready to use
- Evaluation and testing frameworks
- Proper authentication handling
- Type-safe Pydantic models

## 📁 Scripts

### 1. `generate_mcp_from_openapi.py`
Main generation script - converts OpenAPI specs to MCP servers

**Usage:**
```bash
# Generate for specific API
python generate_mcp_from_openapi.py echo
python generate_mcp_from_openapi.py statistics
python generate_mcp_from_openapi.py public-register

# Generate all APIs
python generate_mcp_from_openapi.py --all

# Generate without agent or evaluation
python generate_mcp_from_openapi.py echo --no-agent --no-eval

# Clean generated files
python generate_mcp_from_openapi.py --clean echo
python generate_mcp_from_openapi.py --clean-all

# List available APIs
python generate_mcp_from_openapi.py --list
```

**Output:**
```
backend/apis/dnb/generated/
├── dnb_echo_mcp/
│   ├── mcp_echo/
│   │   ├── api/          # HTTP client
│   │   ├── models/       # Pydantic models
│   │   ├── tools/        # Generated tools
│   │   └── server.py     # MCP server
│   ├── agent/
│   │   └── agent.py      # LangGraph agent
│   ├── pyproject.toml
│   └── README.md
├── dnb_statistics_mcp/
└── dnb_public_register_mcp/
```

### 2. `compare_manual_vs_generated.py`
Validation script - compares manual GenAI Toolbox config with generated MCP server

**Usage:**
```bash
# Compare Echo API
python compare_manual_vs_generated.py echo

# Compare with production config
python compare_manual_vs_generated.py echo --env prod

# Compare Statistics API
python compare_manual_vs_generated.py statistics
```

**What it checks:**
- ✅ Endpoint coverage (all manual endpoints have generated equivalents)
- ✅ Authentication configuration
- ✅ Parameter mappings
- ✅ Response handling

### 3. `watch_and_regenerate.py`
Automation script - watches OpenAPI specs for changes and auto-regenerates

**Usage:**
```bash
# Watch all APIs (checks every 5 seconds)
python watch_and_regenerate.py

# Watch specific API
python watch_and_regenerate.py --api echo

# Custom check interval
python watch_and_regenerate.py --interval 10

# Generate once and exit (for CI/CD)
python watch_and_regenerate.py --once
```

**Use cases:**
- Development: Auto-regenerate when spec changes
- CI/CD: Validate specs and regenerate in pipeline
- Testing: Ensure generated code stays in sync with specs

## 🚀 Quick Start

### Prerequisites
```bash
# Install uv (includes uvx)
pip install uv

# Or use system package manager
# Windows (winget): winget install astral-sh.uv
# macOS (brew): brew install uv
# Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Generate Your First MCP Server

```bash
# 1. Navigate to scripts directory
cd c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb\scripts

# 2. Generate Echo API MCP server
python generate_mcp_from_openapi.py echo

# 3. Test the generated server
cd ../generated/dnb_echo_mcp
poetry install
poetry run mcp_echo

# 4. Try the LangGraph agent
cd agent
poetry install
# Configure .env with your credentials
poetry run python agent.py
```

### Validate Against Manual Config

```bash
# Compare generated vs manual configuration
python compare_manual_vs_generated.py echo
```

### Set Up Auto-Regeneration

```bash
# Start watching for spec changes
python watch_and_regenerate.py

# In another terminal, edit the OpenAPI spec
# The script will auto-detect changes and regenerate
```

## 📖 Generated MCP Server Usage

After generation, each MCP server can be used in multiple ways:

### As MCP Server (stdio)
```python
from toolbox_langchain import ToolboxClient
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent

# Load tools from MCP server
async with ToolboxClient("http://localhost:5000") as client:
    tools = await client.aload_toolset("dnb-tools")
    
    # Create agent
    llm = ChatVertexAI(model="gemini-2.0-flash-001")
    agent = create_react_agent(llm, tools)
    
    # Use agent
    response = await agent.ainvoke({
        "messages": [("user", "Test the DNB API connection")]
    })
```

### As LangGraph Agent (generated)
```python
# Use the auto-generated agent
from agent.agent import create_agent

agent = await create_agent()
response = await agent.ainvoke({
    "messages": [("user", "Get banking statistics for 2024")]
})
```

### Direct Tool Invocation
```python
# Import generated tools directly
from mcp_echo.tools.helloworld import retrieve_resource

result = await retrieve_resource()
print(result)  # {"helloWorld": "DNB API Services"}
```

## 🔧 Configuration

### API Definitions

APIs are configured in `generate_mcp_from_openapi.py`:

```python
APIS = {
    "echo": {
        "spec": "openapi3-echo-api.yaml",
        "output": "dnb_echo_mcp",
        "description": "DNB Echo API - Test endpoint"
    },
    "statistics": {
        "spec": "openapi3_statisticsdatav2024100101.yaml",
        "output": "dnb_statistics_mcp",
        "description": "DNB Statistics API"
    },
    "public-register": {
        "spec": "openapi3_publicdatav1.yaml",
        "output": "dnb_public_register_mcp",
        "description": "DNB Public Register API"
    }
}
```

### Environment Variables

Generated servers use these environment variables (see generated `.env.example`):

```bash
# API Authentication
DNB_API_URL=https://api.dnb.nl
DNB_TOKEN=your_subscription_key_here

# MCP Server
MCP_MODE=stdio  # or 'web' for HTTP
MCP_PORT=8000   # if using web mode

# LangGraph Agent
OPENAI_API_KEY=your_key  # or other LLM provider
LANGFUSE_PUBLIC_KEY=your_key  # for observability (optional)
```

## 🧪 Testing Generated Servers

### Run MCP Server Tests
```bash
cd generated/dnb_echo_mcp
poetry install
poetry run pytest
```

### Run Agent Evaluations
```bash
cd generated/dnb_echo_mcp/agent
poetry install

# Interactive evaluation
poetry run python -m eval.interactive

# Automated evaluation
poetry run python -m eval.evaluate
```

### Manual Testing
```bash
# Test with MCP Inspector
cd generated/dnb_echo_mcp
npx @modelcontextprotocol/inspector poetry run mcp_echo
```

## 📊 CI/CD Integration

### GitHub Actions Example
```yaml
name: Regenerate MCP Servers

on:
  push:
    paths:
      - 'backend/apis/dnb/specs/*.yaml'

jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: pip install uv
      
      - name: Regenerate MCP servers
        run: |
          cd backend/apis/dnb/scripts
          python watch_and_regenerate.py --once
      
      - name: Validate generated code
        run: |
          python compare_manual_vs_generated.py echo
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add backend/apis/dnb/generated/
          git commit -m "chore: regenerate MCP servers from OpenAPI specs"
          git push
```

## 🐛 Troubleshooting

### uvx not found
```bash
# Install uv
pip install uv

# Or use installer
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
```

### Generation fails
```bash
# Check OpenAPI spec is valid
uvx openapi-spec-validator backend/apis/dnb/specs/openapi3-echo-api.yaml

# Check uvx can access repository
uvx --from git+https://github.com/cnoe-io/openapi-mcp-codegen.git openapi_mcp_codegen --help
```

### Generated server won't run
```bash
# Install dependencies
cd generated/dnb_echo_mcp
poetry install --no-root

# Check Python version (requires 3.13+)
python --version

# View logs
poetry run mcp_echo --verbose
```

## 📚 Additional Resources

- [cnoe-io/openapi-mcp-codegen](https://github.com/cnoe-io/openapi-mcp-codegen) - Generator documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent framework
- [DNB API Documentation](../docs/dnb_api_services.md) - Our API docs

## 🤝 Contributing

To add a new DNB API:

1. Add OpenAPI spec to `backend/apis/dnb/specs/`
2. Update `APIS` dict in `generate_mcp_from_openapi.py`
3. Run generation: `python generate_mcp_from_openapi.py <new-api>`
4. Add comparison logic to `compare_manual_vs_generated.py`
5. Update documentation

## 📝 Notes

- Generated code is **not** checked into git (in `.gitignore`)
- Regenerate whenever OpenAPI specs change
- Use `compare_manual_vs_generated.py` to validate changes
- Generated servers are production-ready but review before deploying
