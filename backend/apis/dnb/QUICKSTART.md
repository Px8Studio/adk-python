# 🚀 Quick Start: Generate Your First MCP Server

This guide will walk you through generating an MCP server from the DNB Echo API OpenAPI specification.

## ⏱️ Time Required: 5 minutes

## Prerequisites

First, ensure Docker Desktop is running and `uv` is installed:

```powershell
# Check Docker is running
docker --version

# Check if uv is installed
uv --version

# If not installed, install it:
pip install uv
```

**Note:** The `quick-start.ps1` script will automatically start/restart MCP Toolbox as needed.

## Step 1: Start Full Stack (Recommended)

```powershell
# Navigate to project root
cd c:\Users\rjjaf\_Projects\orkhon

# Run the full stack quick-start (includes MCP Toolbox)
.\backend\scripts\quick-start.ps1
```

This will:
1. ✅ Check system prerequisites
2. ✅ Start/restart Docker services (MCP Toolbox, Jaeger, Postgres)
3. ✅ Open Web UIs automatically
4. ✅ Start ADK Web server

## Step 2: Navigate to Scripts Directory

```powershell
cd c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb\scripts
```

## Step 3: Generate MCP Server for Echo API

```powershell
python generate_mcp_from_openapi.py echo
```

**Expected output:**
```
✅ uvx is available
======================================================================
🚀 Generating MCP Server: ECHO
======================================================================
📄 Spec: openapi3-echo-api.yaml
📁 Output: c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb\generated\dnb_echo_mcp
📝 Description: DNB Echo API - Test endpoint for API connectivity
🤖 Agent: YES
🧪 Evaluation: YES

⏳ Running code generation...
...
✅ Generation successful!

📦 Generated files in: c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb\generated\dnb_echo_mcp
```

## Step 4: Explore Generated Files

```powershell
cd ..\generated\dnb_echo_mcp
dir
```

**You should see:**
```
mcp_echo/          # MCP server package
agent/             # LangGraph agent
pyproject.toml     # Poetry configuration
README.md          # Generated documentation
.env.example       # Environment variables template
```

## Step 5: Install Dependencies

```powershell
# Install using Poetry
poetry install
```

## Step 6: Configure Environment

```powershell
# Copy .env template
copy .env.example .env

# Edit .env and add your DNB API key
notepad .env
```

Add your API key:
```env
DNB_API_URL=https://api.dnb.nl
DNB_TOKEN=your_subscription_key_here
```

## Step 7: Run the MCP Server

```powershell
# Run in stdio mode (default)
poetry run mcp_echo
```

## Step 8: Test with the Generated Agent

```powershell
cd agent
poetry install

# Edit .env to add LLM credentials
copy .env.example .env
notepad .env

# Add your LLM API key (OpenAI, Anthropic, or Gemini)
# Example for OpenAI:
# OPENAI_API_KEY=sk-...

# Run the agent
poetry run python agent.py
```

## Step 9: Compare with Manual Configuration

```powershell
cd ..\..\scripts
python compare_manual_vs_generated.py echo
```

This validates that the generated MCP server matches your manual GenAI Toolbox configuration.

## Next Steps

### Option 1: Use in Your Agent
```python
# In your existing agent code
from mcp_echo.tools.helloworld import retrieve_resource

result = await retrieve_resource()
print(result)  # {"helloWorld": "DNB API Services"}
```

### Option 2: Generate for Other APIs
```powershell
# Generate Statistics API
python generate_mcp_from_openapi.py statistics

# Generate Public Register API
python generate_mcp_from_openapi.py public-register

# Generate all at once
python generate_mcp_from_openapi.py --all
```

### Option 3: Enable Auto-Regeneration
```powershell
# Watch for changes to OpenAPI specs
python watch_and_regenerate.py

# In another terminal, edit the spec
# The watcher will auto-detect and regenerate
```

## 🐛 Troubleshooting

### Error: "uvx not found"
```powershell
pip install uv
```

### Error: "OpenAPI spec not found"
Check that you're in the correct directory:
```powershell
cd c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb\scripts
```

### Error: "Poetry not found"
```powershell
pip install poetry
```

### Generated server won't run
Check Python version (requires 3.13+):
```powershell
python --version
```

## 📚 More Information

- Full documentation: [scripts/README.md](./README.md)
- Tool options: [docs/openapi_tool_converter_options.md](../docs/openapi_tool_converter_options.md)
- DNB API docs: [docs/dnb_api_services.md](../docs/dnb_api_services.md)

## ✅ Success!

You've successfully generated your first MCP server! 🎉

The generated code includes:
- ✅ Complete MCP server with typed tools
- ✅ LangGraph React agent
- ✅ Evaluation framework
- ✅ Proper error handling and logging
- ✅ Authentication support

Now you can integrate it with your existing agents or use it as a standalone service.
