# Orkhon Quick Reference Card

## 🚀 One-Command Start
```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\quick-start.ps1
```

## 🎯 Quick URLs
- **ADK Web UI:** http://localhost:8000
- **Toolbox UI:** http://localhost:5000/ui/
- **Jaeger Tracing:** http://localhost:16686

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

# Stop Toolbox:
cd backend\toolbox
docker-compose -f docker-compose.dev.yml down
```

## 🔍 Check Status
```powershell
# Check containers
docker ps --filter "name=orkhon-toolbox"

# Check Toolbox health
Invoke-WebRequest http://localhost:5000/ui/

# Check ADK Web (when running)
Invoke-WebRequest http://localhost:8000
```

## 📝 Test Queries for dnb_agent
```
"What tools do you have available?"
"Get the hello world message from DNB"
"Show me available exchange rates"
"List pension fund statistics"
```

## 📚 Documentation
- **SUCCESS.md** - Complete success guide
- **START_GUIDE.md** - Detailed startup instructions
- **SYSTEM_STATUS.md** - Current system status

## 🆘 Common Issues

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
