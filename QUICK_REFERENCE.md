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

### Google GenAI Toolbox (First) - **Custom Build**
```powershell
cd C:\Users\rjjaf\_Projects\orkhon\backend\genai-toolbox
# Build from sibling clone: C:\Users\rjjaf\_Projects\genai-toolbox
docker-compose -f docker-compose.dev.yml up -d --build
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
cd backend\genai-toolbox
docker-compose -f docker-compose.dev.yml down

# Or stop individual containers:
docker stop genai-toolbox jaeger
```

## 📦 Toolbox Version Management (Custom Build)

```powershell
# Rebuild custom toolbox image
cd backend\genai-toolbox
docker-compose -f docker-compose.dev.yml build genai-toolbox

# Restart with fresh build
docker-compose -f docker-compose.dev.yml up -d --build genai-toolbox
```

## 🔍 Check Status

```powershell
# List running containers
docker ps --filter "name=genai-toolbox" --filter "name=jaeger"

# Check Toolbox health
Invoke-WebRequest http://localhost:5000/api/toolset  # ✅ Correct endpoint

# View Toolbox logs
cd backend\genai-toolbox
docker-compose -f docker-compose.dev.yml logs -f genai-toolbox

# View Jaeger UI
Start-Process http://localhost:16686
```

## 🆘 Common Issues

### Toolbox not responding
```powershell
cd backend\genai-toolbox
docker-compose -f docker-compose.dev.yml restart genai-toolbox
```

### View logs
```powershell
docker-compose -f docker-compose.dev.yml logs -f genai-toolbox
```

---

**Pro Tip:** Keep this file open in a pinned tab for quick reference! 📌
