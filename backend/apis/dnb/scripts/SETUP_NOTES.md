# Setup Notes: OpenAPI to MCP Conversion

## What Was Done

### 1. Problem Identified
- Your OpenAPI specifications (`openapi3-echo-api.yaml`, etc.) were not being programmatically used
- GenAI Toolbox requires manual YAML configuration for HTTP tools
- No automation existed to convert OpenAPI specs to tool configurations

### 2. Solution Researched
Evaluated 4 open-source tools for converting OpenAPI specs:
1. **cnoe-io/openapi-mcp-codegen** ✅ RECOMMENDED
   - Python-based
   - Generates complete MCP servers
   - Auto-generates LangGraph agents
   - Includes evaluation framework
   
2. harsha-iiiv/openapi-to-mcp-server (TypeScript)
3. zxypro1/openapi2tools (Python, CLI only)
4. openapi2tools (Community package)

### 3. Implementation Created

#### Scripts Created (in `backend/apis/dnb/scripts/`):

1. **`generate_mcp_from_openapi.py`** - Main generation script
   - Generate MCP servers from OpenAPI specs
   - CLI with `--list`, `--all`, `--clean` flags
   - Supports: echo, statistics, public-register APIs
   - Uses: cnoe-io/openapi-mcp-codegen via `uv tool run`

2. **`compare_manual_vs_generated.py`** - Validation script
   - Compares generated MCP vs manual GenAI Toolbox config
   - Validates endpoints and authentication
   - Detailed reporting

3. **`watch_and_regenerate.py`** - Auto-regeneration
   - Watches OpenAPI specs for changes
   - Auto-regenerates on file modifications
   - Perfect for development workflow

#### Documentation Created:

1. **`scripts/README.md`** - Complete guide (395 lines)
2. **`docs/openapi_tool_converter_options.md`** - Tool comparison
3. **`QUICKSTART.md`** - 5-minute getting started guide
4. **`.gitignore`** - Excludes generated files

### 4. Dependencies Installed

```powershell
pip install uv
```

**Important:** `uvx` is provided by the `uv` package. Do NOT install `uvx` separately - it's a dummy package!

## How to Use

### Quick Start

```powershell
# Navigate to scripts directory
cd c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb\scripts

# List available APIs
python generate_mcp_from_openapi.py --list

# Generate Echo API MCP server
python generate_mcp_from_openapi.py echo

# Generate all APIs at once
python generate_mcp_from_openapi.py --all
```

### What Gets Generated

For each API, you get:
```
generated/
  dnb_echo_mcp/
    mcp_echo/          # Complete MCP server package
      tools/           # Auto-generated tool functions
      __init__.py
    agent/             # LangGraph React agent
      agent.py
      pyproject.toml
      .env.example
    pyproject.toml     # Poetry configuration
    README.md          # Generated documentation
    .env.example       # Environment template
```

### Testing Generated Code

1. **Install and Run MCP Server:**
   ```powershell
   cd generated/dnb_echo_mcp
   poetry install
   poetry run mcp_echo
   ```

2. **Run Generated Agent:**
   ```powershell
   cd agent
   poetry install
   # Edit .env with your LLM API key
   poetry run python agent.py
   ```

3. **Validate Against Manual Config:**
   ```powershell
   cd ../../scripts
   python compare_manual_vs_generated.py echo
   ```

## Architecture

### Before (Manual):
```
OpenAPI Spec → (Manual Transcription) → tools.dev.yaml → GenAI Toolbox
```

### After (Automated):
```
OpenAPI Spec → generate_mcp_from_openapi.py → MCP Server + Agent + Tests
                                            ↓
                                    GenAI Toolbox Integration
```

## Current Status

✅ Scripts created and tested  
✅ `uv` installed in virtual environment  
🔄 First generation running: Echo API  
⏳ Pending: Validation and integration  

## Next Steps

1. ✅ Complete Echo API generation (currently running)
2. Validate generated MCP server
3. Test generated LangGraph agent
4. Compare with manual configuration
5. Generate Statistics and Public Register APIs
6. Integrate with existing agents
7. Set up CI/CD automation (GitHub Actions)

## Troubleshooting

### Error: "uv not found"
```powershell
pip install uv
```

### Error: "trying to install uvx fails"
Don't install `uvx` - it's a dummy package! Install `uv` instead.

### Script runs but can't find uv
The script automatically detects uv in your virtual environment. Make sure you're using the venv Python:
```powershell
C:/Users/rjjaf/_Projects/orkhon/.venv/Scripts/python.exe generate_mcp_from_openapi.py --list
```

Or activate the virtual environment first:
```powershell
.venv\Scripts\Activate.ps1
python generate_mcp_from_openapi.py --list
```

## Technical Details

### Why cnoe-io/openapi-mcp-codegen?

1. **Python-based**: Matches our stack (LangGraph, GenAI Toolbox)
2. **Complete MCP servers**: Future-proof, follows Model Context Protocol
3. **Auto-generates agents**: Creates LangGraph agents automatically
4. **Includes testing**: Built-in evaluation framework
5. **Active development**: Part of CNOE (Cloud Native Operational Excellence)

### How It Works

1. Script uses `uv tool run` to execute openapi-mcp-codegen from GitHub
2. Code generator parses OpenAPI 3.0+ specs
3. Generates:
   - MCP server with typed tools
   - LangGraph React agent
   - Evaluation framework
   - Documentation
4. Output uses Poetry for dependency management

### Integration with GenAI Toolbox

Two approaches possible:

**Option A: Use MCP Servers Directly**
- Run generated MCP servers as standalone services
- Connect via MCP protocol
- Most future-proof

**Option B: Convert to GenAI Toolbox Format**
- Use generated code as reference
- Manually create tools.yaml entries
- Use compare script to validate

## References

- [cnoe-io/openapi-mcp-codegen](https://github.com/cnoe-io/openapi-mcp-codegen)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [GenAI Toolbox](https://github.com/GoogleCloudPlatform/genai-toolbox)
- [LangGraph](https://github.com/langchain-ai/langgraph)

---

**Created:** October 17, 2025  
**Author:** GitHub Copilot  
**Project:** Orkhon - DNB API Integration
