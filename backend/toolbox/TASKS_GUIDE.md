# 🎯 VS Code Tasks Guide for Orkhon Toolbox

This guide explains all available VS Code tasks for managing and testing the GenAI Toolbox MCP server.

## 📋 How to Run Tasks

### Method 1: Command Palette
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Tasks: Run Task"
3. Select the task you want to run

### Method 2: Terminal Menu
1. Go to **Terminal → Run Task...**
2. Select your task

### Method 3: Keyboard Shortcut (Optional)
You can add keyboard shortcuts in **File → Preferences → Keyboard Shortcuts** by searching for "Tasks: Run Task"

---

## 🔧 Available Tasks

### 🚀 Server Management - Development

#### **MCP: Start Dev Server**
Starts the development Docker containers (Toolbox + Jaeger)
```bash
docker-compose -f docker-compose.dev.yml up -d
```
- ✅ Use this when starting your development session
- ✅ Runs in detached mode (-d)
- ✅ Opens in a shared panel

#### **MCP: Stop Dev Server**
Stops and removes the development containers
```bash
docker-compose -f docker-compose.dev.yml down
```
- ✅ Use this when you're done developing
- ✅ Cleans up networks and volumes

#### **MCP: Restart Dev Server**
Restarts only the GenAI Toolbox container (not Jaeger)
```bash
docker-compose -f docker-compose.dev.yml restart genai-toolbox-mcp
```
- ✅ Use this after changing configuration files
- ✅ Faster than full stop/start
- ⚠️ Only restarts the toolbox, not Jaeger

#### **MCP: Rebuild & Start Dev Server**
Rebuilds the Docker image and starts containers
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```
- ✅ Use when you've updated the Dockerfile
- ✅ Forces a rebuild of the image
- ⚠️ Takes longer than a regular start

---

### 📊 Server Management - Production

#### **MCP: Start Prod Server**
Starts the production Docker containers
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### **MCP: Stop Prod Server**
Stops and removes the production containers
```bash
docker-compose -f docker-compose.prod.yml down
```

---

### 🔍 Monitoring & Debugging

#### **MCP: View Dev Logs (Live)**
Shows live logs from the GenAI Toolbox container only
```bash
docker-compose -f docker-compose.dev.yml logs -f genai-toolbox-mcp
```
- ✅ Updates in real-time (follow mode)
- ✅ Filtered to toolbox container only
- ⚠️ Press `Ctrl+C` to stop

#### **MCP: View All Logs (Live)**
Shows live logs from ALL containers (Toolbox + Jaeger)
```bash
docker-compose -f docker-compose.dev.yml logs -f
```
- ✅ See everything happening
- ✅ Useful for debugging networking issues
- ⚠️ Press `Ctrl+C` to stop

#### **MCP: Check Container Status**
Shows status of all Orkhon Toolbox containers
```bash
docker ps --filter name=orkhon-toolbox
```
- ✅ Quick health check
- ✅ Shows port mappings
- ✅ Shows container uptime

---

### 🌐 Web UI Shortcuts

#### **MCP: Open Toolbox Web UI**
Opens the Toolbox web interface in your browser
- **URL:** `http://localhost:5000/ui/`
- ✅ Browse and test tools
- ✅ View toolsets
- ✅ Interactive tool invocation

#### **MCP: Open Jaeger Tracing UI**
Opens the Jaeger tracing dashboard
- **URL:** `http://localhost:16686`
- ✅ View request traces
- ✅ Monitor performance
- ✅ Debug slow queries

#### **MCP: Open Statistics OpenAPI Spec**
Opens the DNB Statistics API OpenAPI specification in VS Code
- **File:** `openapi3_statisticsdatav2024100101.yaml`
- ✅ View API documentation
- ✅ Test endpoints (with OpenAPI extension)

#### **MCP: Open Public Register OpenAPI Spec**
Opens the DNB Public Register API OpenAPI specification
- **File:** `openapi3_publicdatav1.yaml`
- ✅ View API documentation
- ✅ Search institutions

---

### 🧪 API Testing

#### **DNB: Test Echo API (Direct)**
Tests the DNB Echo API directly (bypassing Toolbox)
```bash
curl -i -H "Ocp-Apim-Subscription-Key: $DNB_SUBSCRIPTION_KEY_DEV" \
  https://api.dnb.nl/echo-api/helloworld
```
- ✅ Verifies your DNB API key works
- ✅ Tests direct connectivity to DNB
- ⚠️ Requires `DNB_SUBSCRIPTION_KEY_DEV` environment variable

#### **DNB: Test Echo API (via Toolbox)**
Tests the DNB Echo API through the Toolbox MCP server
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/tool/dnb-echo-helloworld/invoke" \
  -Method POST -ContentType "application/json" -Body '{}'
```
- ✅ Verifies Toolbox → DNB API connection
- ✅ Tests tool configuration
- ✅ Shows JSON response

#### **DNB: Get Statistics Metadata**
Retrieves metadata about available DNB statistical datasets
```bash
curl -H "Ocp-Apim-Subscription-Key: $DNB_SUBSCRIPTION_KEY_DEV" \
  -H "Accept: application/json" \
  https://api.dnb.nl/statistics/v2024100101/metadata | jq .
```
- ✅ Lists available datasets
- ✅ Shows data structure
- ⚠️ Requires `jq` for JSON formatting

#### **DNB: Query Statistics Sample**
Retrieves a sample of DNB statistics data (5 records)
```bash
curl -H "Ocp-Apim-Subscription-Key: $DNB_SUBSCRIPTION_KEY_DEV" \
  -H "Accept: application/json" \
  https://api.dnb.nl/statistics/v2024100101/data?limit=5 | jq .
```
- ✅ Quick data preview
- ✅ Verifies statistics API works

#### **Toolbox: List All Tools**
Lists all tools configured in the Toolbox
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/toolset/" | ConvertTo-Json -Depth 10
```
**Sample Output:**
```json
{
  "serverVersion": "0.17.0+container.dev.linux.amd64",
  "tools": {
    "dnb-echo-helloworld": {
      "description": "Test DNB API connectivity by calling the echo endpoint",
      "parameters": []
    },
    "dnb-get-metadata": {
      "description": "Retrieve metadata about available statistical datasets from DNB",
      "parameters": []
    },
    "dnb-query-statistics": {
      "description": "Query Dutch banking statistics data with optional filters",
      "parameters": [...]
    }
  }
}
```

#### **Toolbox: List DNB Toolset**
Lists only the DNB toolset configuration
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/toolset/dnb-tools" | ConvertTo-Json -Depth 10
```
- ✅ Shows DNB-specific tools
- ✅ View tool parameters

---

### ⚡ Quick Actions

#### **🚀 Full Restart: Stop → Start → Open UI**
Composite task that:
1. Stops the dev server
2. Starts it fresh
3. Opens the Toolbox Web UI

- ✅ One-click complete refresh
- ✅ Useful after config changes
- ✅ Opens UI automatically

---

## 🎨 Task Presentation Settings

All tasks use optimized presentation settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `reveal` | `always` | Shows terminal output immediately |
| `panel` | `shared` | Reuses terminal panel (less clutter) |
| `clear` | `true` | Clears previous output |
| `close` | `false` | Keeps terminal open after completion |

---

## 🔧 Troubleshooting

### Task doesn't appear in the list?
- Reload VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"
- Check that `tasks.json` is in `.vscode/` folder

### Environment variable not found?
Tasks use `${env:VARIABLE_NAME}` syntax. Ensure your `.env` file is loaded:
```bash
# In your shell profile or .env file
export DNB_SUBSCRIPTION_KEY_DEV="your-key-here"
```

### Docker command not found?
Ensure Docker Desktop is installed and running.

### Port 5000 already in use?
Check if another application is using port 5000:
```bash
netstat -ano | findstr :5000
```

---

## 📚 Related Files

- **Tasks Configuration:** `.vscode/tasks.json`
- **Docker Dev Config:** `backend/toolbox/docker-compose.dev.yml`
- **Docker Prod Config:** `backend/toolbox/docker-compose.prod.yml`
- **Tools Config:** `backend/toolbox/config/tools.dev.yaml`
- **Environment Variables:** `backend/toolbox/.env`

---

## 🎯 Recommended Workflow

1. **Start your day:**
   - Run: `MCP: Start Dev Server`
   - Run: `MCP: Open Toolbox Web UI`

2. **During development:**
   - Use: `MCP: View Dev Logs (Live)` in a separate terminal
   - Test with: `DNB: Test Echo API (via Toolbox)`

3. **After config changes:**
   - Run: `MCP: Restart Dev Server`
   - Or use: `🚀 Full Restart: Stop → Start → Open UI`

4. **End your day:**
   - Run: `MCP: Stop Dev Server`

---

## 💡 Tips & Best Practices

- **Use keyboard shortcuts:** Set up custom shortcuts for frequently used tasks
- **Monitor logs:** Keep a terminal with live logs running during development
- **Check status first:** Run `MCP: Check Container Status` before starting
- **Clear cache:** Use rebuild task if experiencing strange Docker issues
- **Environment variables:** Always verify your `.env` file is up to date

---

## 📖 Additional Resources

- [GenAI Toolbox Documentation](https://googleapis.github.io/genai-toolbox/)
- [Jaeger Tracing Guide](https://www.jaegertracing.io/docs/)
- [DNB API Portal](https://api.portal.dnb.nl/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**Last Updated:** October 16, 2025
