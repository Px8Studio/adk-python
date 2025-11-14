I'll analyze the ADK Web deployment situation by examining the codebase and clarifying the architecture. 

Searched codebase for "ADK web server FastAPI adk web command hosting deployment", 20 results

Searched for regex `adk web|adk_web_server|AadkWebServer` (`**/*.py`), 20 results

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/src/google/adk/cli/adk_web_server.py)

Now let me check how the ADK Web UI is packaged and served: 

Searched for regex `adk-web|web.*assets|package.*data` (`**/pyproject.toml`), no results

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/pyproject.toml#1-1), lines 1 to 101

Searched for files matching `**/web_assets/**`, no matches

Searched for regex `web_assets_dir|WEB_ASSETS|importlib.*resources` (`**/*.py`), 11 results

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/src/google/adk/cli/fast_api.py#1-1), lines 1 to 81

Searched for regex `ANGULAR_DIST_PATH|importlib|resources|web.*ui|adk.*web` (`**/fast_api.py`), 10 results

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/src/google/adk)

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/src/google/adk/cli/fast_api.py#195-195), lines 195 to 235

Searched for files matching `**/browser/**`, 10 matches

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/src/google/adk/cli)

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-python/src/google/adk/cli/browser/assets/config/runtime-config.json)

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-web/src/assets/config/runtime-config.json)

Read [](file:///c%3A/Users/rjjaf/_Projects/adk-web/set-backend.js)

Perfect! Now I understand the complete picture. Let me explain everything clearly:

## **The Complete ADK Web Architecture Explained**

### **What You're Running Locally (Quick Start Task)**

When you run the `🚀 Quick Start: Full Orkhon Stack` task, here's what happens:

1. **Python Backend** (`adk web`) starts:
   - FastAPI server on `http://localhost:8000`
   - Serves **pre-built Angular static files** from `adk-python/src/google/adk/cli/browser/`
   - Mounts these at `/dev-ui/` endpoint
   - Also provides REST API endpoints (`/run`, `/run_sse`, `/list-apps`, etc.)

2. **The Frontend Files Are Bundled in the Python Package**:
   - The `adk-web` Angular app is built **during ADK Python package creation**
   - Output goes to `adk-python/src/google/adk/cli/browser/` 
   - This gets packaged **inside** the `google-adk` Python wheel
   - When you `pip install google-adk`, you get the frontend too!

### **Key Difference: Runtime vs Build-time Configuration**

This is the crucial part you asked about:

#### **Build-time (Traditional Environment Variables)**
```javascript
// ❌ NOT used in ADK Web
export const environment = {
  backendUrl: 'http://localhost:8000'  // Baked into build
};
```
- Requires rebuilding Angular app for different backends
- Different builds for dev/staging/production

#### **Runtime Configuration (ADK Web's Approach)**
```javascript
// ✅ ADK Web uses this pattern
// File: runtime-config.json (loaded at browser runtime)
{
  "backendUrl": "http://localhost:8000"
}
```
- **One build works everywhere** - no rebuild needed!
- Backend URL configured when server starts
- Browser loads config at startup from runtime-config.json

### **How Runtime Config Works**

**On the Python backend** (adk_web_server.py):
```python
def _setup_runtime_config(self, web_assets_dir: str):
    runtime_config_path = os.path.join(
        web_assets_dir, "assets", "config", "runtime-config.json"
    )
    runtime_config = {"backendUrl": self.url_prefix if self.url_prefix else ""}
    
    # Write config file that browser will load
    with open(runtime_config_path, "w") as f:
        json.dump(runtime_config, f)
```

**On the Angular frontend** (`runtime-config-util.ts`):
```typescript
static getRuntimeConfig(): RuntimeConfig {
  return (window as any)['runtimeConfig'] as RuntimeConfig;
}

static getApiServerBaseUrl(): string {
  return (window as any)['runtimeConfig']?.backendUrl || '';
}
```

### **Development vs Production Workflow**

#### **Local Development** (your current setup):
```bash
# Terminal 1: ADK backend serves everything
adk web --port=8000 backend/adk/agents

# Browser: http://localhost:8000
# → Backend dynamically writes runtime-config.json
# → Serves pre-built Angular from browser/ folder
# → Angular reads runtime-config.json at startup
```

#### **Separate Frontend Development** (ADK Web repo):
```bash
# Terminal 1: Backend only
adk api_server --allow_origins=http://localhost:4200 --port=8000

# Terminal 2: Live Angular dev server
cd adk-web
npm run serve --backend=http://localhost:8000
# → set-backend.js writes src/assets/config/runtime-config.json
# → ng serve hot-reloads on http://localhost:4200
```

### **Firebase Hosting Compatibility**

**Yes, ADK Web is compatible with Firebase Hosting!** Here's why:

1. **Static Build Output**: Angular produces static HTML/CSS/JS
2. **Single-Page App**: Uses client-side routing
3. **Runtime Config**: Works perfectly with Firebase rewrites

**BUT** - You have **two deployment options**:

#### **Option A: Integrated Deployment (Current ADK Design)**
```
┌─────────────────────────────────────────┐
│   Cloud Run (single container)         │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  FastAPI (Python)               │   │
│  │  - Serves frontend at /dev-ui/  │   │
│  │  - Provides backend API         │   │
│  │  - Writes runtime-config.json   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**This is the official ADK recommended approach** because:
- ✅ **Zero CORS issues** (same origin)
- ✅ **Simpler deployment** (one service)
- ✅ **Runtime config automatic** (Python writes it)
- ✅ **Better for agent execution** (backend needs resources)

#### **Option B: Separate Frontend (Firebase) + Backend (Cloud Run)**
```
┌──────────────────────┐        ┌────────────────────────┐
│ Firebase Hosting     │        │  Cloud Run Backend     │
│ (Static Frontend)    │  API   │  (FastAPI Python)      │
│                      │───────→│                        │
│ https://solven-adk   │  CORS  │  https://backend.run   │
│   -dev.web.app       │        │       .app             │
└──────────────────────┘        └────────────────────────┘
```

This requires:
- ⚠️ **Manual CORS configuration** on backend
- ⚠️ **Separate deployment** (two services)
- ⚠️ **Manual runtime config injection** before deploy
- ⚠️ **Backend must scale for agent workloads**

### **Best Practice: Which Approach to Use?**

#### **For Orkhon Project:**

**Recommended: Hybrid Approach**

```bash
# Your local development copy structure
orkhon/
├── backend/
│   ├── adk/agents/          # Your custom agents
│   └── toolbox/             # MCP toolbox
└── .venv/                   # Has google-adk installed
    └── lib/python3.11/site-packages/google/adk/cli/browser/
        # Pre-built ADK Web UI (from pip install)

# Upstream sync (separate repos):
adk-python/                  # Fork/track upstream
adk-web/                     # Fork/track upstream  
```

**Why this works:**
1. ✅ **No file duplication** - Frontend is in the Python package
2. ✅ **Easy updates** - `pip install --upgrade google-adk`
3. ✅ **Clean separation** - Your agents in Orkhon, ADK framework in venv
4. ✅ **Upstream sync** - Use separate repos to track Google's changes
5. ✅ **Local customization** - Edit your agents, not the framework

**Deployment:**
```bash
# Deploy to Cloud Run (integrated backend + frontend)
cd orkhon/backend
gcloud run deploy orkhon-adk \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

The Cloud Run container will:
- Install `google-adk` (includes frontend in `browser/`)
- Run `adk web backend/adk/agents`
- Serve UI at `/dev-ui/` 
- Serve API at `/run`, `/list-apps`, etc.

### **Summary**

**Key Points:**
1. **Frontend is bundled in Python package** - No need to copy `adk-web` files
2. **Runtime config = one build for all environments** - No rebuild needed
3. **Official ADK approach = integrated deployment** - Backend serves frontend
4. **Firebase Hosting is possible but not recommended** - Adds complexity
5. **Your Orkhon setup is correct** - Keep agents in Orkhon, ADK in venv

**Answer to your original question:**
> "What is the official recommended advice from the builder of ADK Web in terms of deploying and hosting?"

**Answer:** Deploy the **integrated FastAPI + Angular** to **Cloud Run** as a single service. The frontend is designed to be served by the Python backend, not separately. Firebase Hosting is technically compatible but goes against the ADK design pattern.