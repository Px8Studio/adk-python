# ADK Web Setup Guide

## Overview

This guide will help you set up and run ADK Web UI locally to interact with your DNB agent through GenAI Toolbox.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   ADK Web UI    │─────▶│  ADK API Server  │─────▶│  GenAI Toolbox  │
│  (localhost:4200│      │  (localhost:8000)│      │  (localhost:5000│
└─────────────────┘      └──────────────────┘      └─────────────────┘
   Angular Frontend         Python FastAPI            MCP Server
                                  │
                                  ▼
                          ┌──────────────────┐
                          │   Vertex AI      │
                          │  (Gemini Models) │
                          └──────────────────┘
```

## Prerequisites Checklist

- [x] Node.js and npm installed
- [x] Angular CLI installed (`npm install -g @angular/cli`)
- [x] Python 3.10+ with ADK installed
- [x] GenAI Toolbox running on port 5000
- [x] Google Cloud project with Vertex AI enabled
- [x] DNB API subscription keys configured

## Step-by-Step Setup

### 1. Install ADK Web Dependencies

```powershell
cd C:\Users\rjjaf\_Projects\adk-web
npm install
```

### 2. Configure Vertex AI (One-time setup)

```powershell
# Set your Google Cloud project
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"
$env:GOOGLE_GENAI_USE_VERTEXAI = "True"

# Authenticate with Google Cloud
gcloud auth application-default login
gcloud config set project your-project-id
```

### 3. Start GenAI Toolbox (if not already running)

```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\toolbox
docker-compose -f docker-compose.dev.yml up -d
```

Verify it's running:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/toolsets" | ConvertTo-Json
```

### 4. Start ADK API Server

```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\adk

# Activate your virtual environment first
.\.venv\Scripts\Activate.ps1

# Start the API server
adk api_server --allow_origins=http://localhost:4200 --host=0.0.0.0 --port=8000 agents
```

You should see:
```
+-----------------------------------------------------------------------------+
| ADK API Server started                                                      |
|                                                                             |
| For local testing, access at http://0.0.0.0:8000.                          |
+-----------------------------------------------------------------------------+
```

### 5. Start ADK Web UI

In a **new terminal**:

```powershell
cd C:\Users\rjjaf\_Projects\adk-web

# Start the web UI (it will connect to the API server at localhost:8000)
npm run serve --backend=http://localhost:8000
```

You should see Angular compilation output and:
```
Backend URL injected: http://localhost:8000
...
** Angular Live Development Server is listening on localhost:4200 **
```

### 6. Access ADK Web

Open your browser to: **http://localhost:4200**

You should see the ADK Web UI with:
- Your `dnb_agent` available in the agent selector
- A chat interface to interact with the agent
- Tabs for Events, State, Traces, Artifacts, etc.

## Testing Your Setup

### Test 1: Agent Discovery

In ADK Web:
1. Select `dnb_agent` from the agent dropdown
2. The agent should load without errors

### Test 2: Echo API

Try this message:
```
Test the DNB Echo API
```

The agent should:
1. Use the `dnb-echo-helloworld` tool
2. Return a successful response from the DNB API

### Test 3: Statistics Query

Try this message:
```
What statistics are available from the DNB API?
```

The agent should:
1. Query the DNB Statistics API
2. Return available datasets and metadata

## Troubleshooting

### Issue: "adk command not found"

**Solution**: Install ADK Python or activate your virtual environment
```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\.venv\Scripts\Activate.ps1
```

### Issue: "CORS error" in browser console

**Solution**: Ensure API server was started with `--allow_origins` flag:
```powershell
adk api_server --allow_origins=http://localhost:4200 --host=0.0.0.0 --port=8000 agents
```

### Issue: "No agents found"

**Solution**: Verify agent structure:
```
backend/adk/agents/
  └── dnb_agent/
      ├── __init__.py
      ├── agent.py
      └── README.md
```

Each agent folder must have `__init__.py` and `agent.py`.

### Issue: "Toolbox connection failed"

**Solution**: Verify Toolbox is running:
```powershell
curl http://localhost:5000/api/toolsets
```

If not running:
```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\toolbox
docker-compose -f docker-compose.dev.yml up -d
```

### Issue: Vertex AI authentication errors

**Solution**: 
1. Check your environment variables:
   ```powershell
   $env:GOOGLE_CLOUD_PROJECT
   $env:GOOGLE_GENAI_USE_VERTEXAI
   ```
2. Re-authenticate:
   ```powershell
   gcloud auth application-default login
   ```

## Development Workflow

### Quick Start (All Services)

**Terminal 1** - Toolbox:
```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\toolbox
docker-compose -f docker-compose.dev.yml up
```

**Terminal 2** - ADK API Server:
```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\adk
.\.venv\Scripts\Activate.ps1
adk api_server --allow_origins=http://localhost:4200 --host=0.0.0.0 agents
```

**Terminal 3** - ADK Web UI:
```powershell
cd C:\Users\rjjaf\_Projects\adk-web
npm run serve --backend=http://localhost:8000
```

### Making Changes to Your Agent

1. Edit `backend/adk/agents/dnb_agent/agent.py`
2. The API server should auto-reload (if started with `--reload` flag)
3. In ADK Web, create a new session or refresh to see changes

### Hot Reload (Auto-reload on changes)

Start API server with reload enabled:
```powershell
adk web --reload_agents --host=0.0.0.0 --port=8000 agents
```

This combines API server + Web UI with auto-reload!

## Useful Commands

### Check Service Status
```powershell
# Toolbox
curl http://localhost:5000/health

# API Server
curl http://localhost:8000/health

# Web UI
curl http://localhost:4200
```

### View Logs
```powershell
# Toolbox logs
cd C:\Users\rjjaf\_Projects\orkhon\backend\toolbox
docker-compose -f docker-compose.dev.yml logs -f

# Jaeger traces
Start-Process "http://localhost:16686"
```

### Stop All Services
```powershell
# Stop Toolbox
cd C:\Users\rjjaf\_Projects\orkhon\backend\toolbox
docker-compose -f docker-compose.dev.yml down

# Stop API Server: Ctrl+C in terminal
# Stop Web UI: Ctrl+C in terminal
```

## Next Steps

1. **Explore ADK Web Features**:
   - Session management
   - Event tracing
   - Artifact viewing
   - State inspection

2. **Add More Agents**:
   - Create new folders under `agents/`
   - Follow the same structure as `dnb_agent`

3. **Customize Tools**:
   - Add more toolsets to Toolbox
   - Configure in `agent.py` with different `toolset_name`

4. **Deploy to Cloud**:
   - Use `adk deploy cloud_run` for production
   - See ADK documentation for deployment options

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Samples](https://github.com/google/adk-samples)
- [ADK Python Repo](https://github.com/google/adk-python)
- [ADK Web Repo](https://github.com/google/adk-web)
- [GenAI Toolbox Docs](https://github.com/google/genai-toolbox)

## Support

For issues:
1. Check the troubleshooting section above
2. Review ADK logs in terminal output
3. Check Jaeger traces at http://localhost:16686
4. Consult ADK documentation

Happy agent building! 🚀
