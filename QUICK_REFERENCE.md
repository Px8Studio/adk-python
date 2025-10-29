# Orkhon Quick Reference Card

## 🚀 One-Command Start (Full Stack)
```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\backend\scripts\quick-start.ps1
```

**This starts:**
- ✅ Docker network (orkhon-network)
- ✅ GenAI Toolbox MCP Server (port 5000)
- ✅ Jaeger Tracing (port 16686)
- ✅ ADK Web Server (port 8000)
- ✅ Opens Web UIs automatically

**Advanced Options:**
```powershell
# Skip diagnostics
.\backend\scripts\quick-start.ps1 -SkipDiagnostics

# Force recreate Docker containers
.\backend\scripts\quick-start.ps1 -ForceRecreate

# Don't open web UIs automatically
.\backend\scripts\quick-start.ps1 -OpenUIs:$false

# Increase wait time for services (default 60s)
.\backend\scripts\quick-start.ps1 -WaitSeconds 120

# Restart existing containers (default if already running)
# This ensures latest tool configurations are loaded
.\backend\scripts\quick-start.ps1 -RestartToolbox
```

## 🎯 Quick URLs
- **ADK Web UI:** http://localhost:8000
- **Toolbox UI:** http://localhost:5000/ui/
- **Jaeger Tracing:** http://localhost:16686
- **Toolbox API:** http://localhost:5000/api/toolsets
- **Toolbox Health:** http://localhost:5000/health

## ⌨️ VS Code Tasks (Ctrl+Shift+P → Tasks: Run Task)
- `🚀 Quick Start: Full Orkhon Stack` - Start everything
- `ADK: Start Web Server Only` - Just ADK Web
- `🌐 Open: ADK Web UI` - Open in browser
- `MCP: Start Dev Server` - Start Toolbox only
- `MCP: Stop Dev Server` - Stop Toolbox
- `🔍 Diagnostics: Check System Status` - Run diagnostics

## 📦 Manual Start

### Toolbox (First)
```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\toolbox
docker-compose -f docker-compose.dev.yml up -d
```

### ADK Web (Second)
```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\.venv\Scripts\Activate.ps1
adk web --reload_agents --host=0.0.0.0 --port=8000 backend\adk\agents
```

## 🛑 Stop Everything
```powershell
# Stop ADK Web: Ctrl+C in its terminal

# Stop all Docker services:
cd backend\toolbox
docker-compose -f docker-compose.dev.yml down

# Or stop individual containers:
docker stop orkhon-genai-toolbox-mcp orkhon-jaeger
```

## 🔍 Check Status
```powershell
# Check all Orkhon containers
docker ps --filter "name=orkhon-"

# Check container logs
cd backend\toolbox
docker-compose -f docker-compose.dev.yml logs -f

# Check specific service logs
docker logs orkhon-genai-toolbox-mcp --tail=50
docker logs orkhon-jaeger --tail=50

# Check Toolbox health
Invoke-WebRequest http://localhost:5000/health

# Restart Toolbox to reload configurations
cd backend\toolbox
docker-compose -f docker-compose.dev.yml restart genai-toolbox

# Check ADK Web (when running)
Invoke-WebRequest http://localhost:8000

# Run diagnostics
.\backend\scripts\diagnose-setup.ps1
```

## 📝 Test Queries for Multi-Agent System

**Testing Agent Hierarchy:**

```
# Test System Root (L1)
"What can you help me with?"

# Test DNB Coordinator (L2) → Specialists (L3)
"Get the hello world message from DNB"              → dnb_echo_agent
"Show me available exchange rates"                  → dnb_statistics_agent
"Search for financial institutions in public register" → dnb_public_register_agent

# Test Data Science Coordinator (L2) → Specialists (L3)
"What data do you have access to?"                  → bigquery_agent
"Create a chart showing pension trends over time"   → analytics_agent

# Test Multi-Domain Coordination
"Get latest interest rates from DNB and create a trend visualization"
  → dnb_coordinator → dnb_statistics_agent (fetch)
  → data_science_coordinator → analytics_agent (visualize)
```

**Agent Hierarchy (3 Levels):**
```
L1 (System):     root_agent
L2 (Coordinators): dnb_coordinator, data_science_coordinator
L3 (Specialists):  dnb_echo_agent, dnb_statistics_agent, dnb_public_register_agent,
                   bigquery_agent, analytics_agent
```

Run with:
```powershell
# Via ADK Web (recommended)
.\backend\scripts\quick-start.ps1

# Via CLI runner
python backend\adk\run_dnb_openapi_agent.py

# Data science standalone
python backend\adk\run_data_science_agent.py
```

## 📚 Documentation
- **[Current Architecture](backend/etl/docs/ARCHITECTURE_CURRENT.md)** - 3-level hierarchy (8 agents)
- **[Future Architecture](backend/etl/docs/ARCHITECTURE_DNB_FUTURE.md)** - DNB IT deployment (Azure)
- **[System Flow](SYSTEM_FLOW.md)** - Complete startup sequence + agent routing
- **[Backend README](backend/README.md)** - Component overview + agent structure
- **[Toolbox Config](backend/toolbox/config/QUICK_ANSWER.md)** - Tool setup guide

## 🆘 Common Issues

### Missing Google AI/Vertex credentials
If you see an error like:

> Missing key inputs argument! To use the Google AI API, provide (api_key). To use the Google Cloud API, provide (vertexai, project & location).

Set one of the following in a local .env file (copy .env.example to .env):

Option A: Google AI API key

```powershell
# .env
GOOGLE_API_KEY=your_api_key_here
```

Option B: Vertex AI (Application Default Credentials)

```powershell
# .env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Authenticate once in a terminal
gcloud auth application-default login
```

Option B (service account file):

```powershell
# .env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
```

Then re-run Quick Start or the ADK Web task.

### Port 8000 in use
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Toolbox not responding
```powershell
cd backend\toolbox
docker-compose -f docker-compose.dev.yml restart genai-toolbox-mcp
```

### View logs
```powershell
docker-compose -f docker-compose.dev.yml logs -f genai-toolbox-mcp
```

---

**Pro Tip:** Keep this file open in a pinned tab for quick reference! 📌
