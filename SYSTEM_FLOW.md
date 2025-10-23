# Orkhon Quick-Start: Complete System Flow

This document outlines the complete system flow for the Orkhon project, from a single startup command to a fully operational, multi-service development environment.

## 🎯 One Command to Start Everything

The entire stack can be launched with a single command from your PowerShell terminal.

```powershell
.\backend\scripts\quick-start.ps1
```

This script automates diagnostics, Docker setup, service health checks, and launching the ADK web server.

## 🏛️ Conceptual Architecture: The "Tools-First" Approach

Before diving into the operational flow, it's important to understand the "why" behind Orkhon's design. GenAI Toolbox sits at the centre of Orkhon’s “tools-first” agent architecture. Think of it as the contract between language models, tool/business logic, and surrounding infrastructure. Here is how the major ecosystems connect.

### Core Building Blocks

- **OpenAPI → Toolbox → Agents:** Domain APIs (e.g., DNB) live as OpenAPI specs. `openapi-mcp-codegen` or ADK’s `OpenAPIToolset` converts them into structured tools. The generated YAML under `config/` defines each tool’s HTTP method, params, authentication, and docs. ADK agents then import those toolsets and expose them to the LLM.

- **Model Context Protocol (MCP):** GenAI Toolbox is an MCP server. MCP is a model/tool interop standard backed by Google, LangChain, Microsoft, and others. MCP defines capabilities (tools, resources, prompts) and communications. Toolbox implements the protocol so any MCP-aware agent (ADK, LangChain, Semantic Kernel, etc.) can auto-discover and call tools without bespoke glue code.

- **ADK Agents:** Google’s Agent Development Kit (ADK) wraps Gemini models, prompt instructions, memory, and tool orchestration. In Orkhon, the root agent routes requests, coordinator agents choose between “standard” toolbox tools or experimental OpenAPI tools, and API-specific agents invoke the DNB toolsets. The ADK runtime handles function-calling, structured responses, retries, logging, and evaluation hooks.

### Where the Big Players Show Up

- **Google:** Supplies Gemini models and ADK (agents, runners, OpenAPI ingestion). `google.adk` packages in `.venv` are used everywhere – from the FastAPI web server under `adk` to the ETL pipelines referencing ADK’s tooling.

- **LangChain:** While Orkhon isn’t running LangChain pipelines directly, MCP is equally supported by LangChain’s LangGraph/LCEL stack. That means the same Toolbox server you use with ADK could be consumed by a LangChain agent simply by registering an MCP client. This is how the ecosystems align: tooling is shared even if orchestration differs.

- **Microsoft:** MCP grew out of the VS Code Copilot ecosystem. VS Code now treats MCP servers as “tool providers” that Copilot or inline chats can call. Microsoft’s Semantic Kernel is adding MCP support too. So Orkhon’s toolbox can be plugged into both Gemini-based agents (ADK) and Microsoft-first stacks (Copilot, Semantic Kernel) with no new adapters.

### Why This Partnership Matters

- **Shared standards** mean you describe a tool once (OpenAPI → YAML) and reuse it everywhere. Gemini/ADK, LangChain, Copilot, or custom agents can all call the same MCP endpoint.
- **Authentication and rate-limiting are centralized.** Toolbox inserts headers like `Ocp-Apim-Subscription-Key` and enforces retry/backoff policies so individual agents don’t need bespoke code.
- **Observability comes for free.** Every call passes through Toolbox, giving you Jaeger traces, logs, and metrics regardless of which LLM client triggered it.

## 📊 System Startup Flow

The `quick-start.ps1` script executes the following sequence to bring the full stack online.

```
┌─────────────────────────────────────────────────────────────┐
│                     USER COMMAND                            │
│              .\backend\scripts\quick-start.ps1             │
└────────────────────────┬────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: System Diagnostics (diagnose-setup.ps1)          │
│  • Docker CLI installed?                                   │
│  • docker-compose.dev.yml exists?                          │
│  • Python venv ready?                                      │
│  • Ports available? (8000, 5000, 16686, 4318)            │
│  • Docker network exists?                                  │
└────────────────────────┬────────────────────────────────────┘
                                           │ [OK] All checks passed
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Docker Network Management                         │
│  • Check if orkhon-network exists                          │
│  • Create if missing                                       │
│  • Verify connectivity                                     │
└────────────────────────┬────────────────────────────────────┘
                                           │ [OK] Network ready
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Start Docker Stack                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  docker-compose -f docker-compose.dev.yml up -d     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│         ┌───────────────┴───────────────┐                  │
│         ▼                               ▼                  │
│  ┌─────────────┐                 ┌─────────────┐          │
│  │   Jaeger    │                 │  Toolbox    │          │
│  │  :16686     │◄────OTLP────────│  :5000      │          │
│  │  :4318      │                 │             │          │
│  └─────────────┘                 └─────────────┘          │
│         │                               │                  │
│         │ Health Check                  │ Health Check     │
│         │ (10s retries)                 │ (multi-probe)    │
│         ▼                               ▼                  │
│    [HEALTHY]                        [READY]                │
└────────────────────────┬────────────────────────────────────┘
                                           │ [OK] All services ready
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Open Web UIs (Automatic)                          │
│  • Opens: http://localhost:5000/ui/  (Toolbox)            │
│  • Opens: http://localhost:16686     (Jaeger)             │
└────────────────────────┬────────────────────────────────────┘
                                           │ [OK] UIs opened
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Verify Python Environment                         │
│  • Check .venv/Scripts/Activate.ps1 exists                │
│  • Prepare for ADK Web startup                             │
└────────────────────────┬────────────────────────────────────┘
                                           │ [OK] Environment ready
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Start ADK Web Server                              │
│  • Load .env configuration                                 │
│  • Activate Python virtual environment                     │
│  • Run: adk web --reload_agents --port 8000               │
│  • Listen on 0.0.0.0:8000                                  │
└────────────────────────┬────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│              🎉 FULL STACK RUNNING                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  ADK Web:     http://localhost:8000                 │  │
│  │  Toolbox UI:  http://localhost:5000/ui/             │  │
│  │  Jaeger UI:   http://localhost:16686                │  │
│  │  Toolbox API: http://localhost:5000/api/toolset/    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  User can now:                                              │
│  ✅ Build AI agents with ADK                                │
│  ✅ Use 82 DNB API tools via Toolbox                        │
│  ✅ Monitor traces in Jaeger                                │
│  ✅ Test tools in Toolbox UI                                │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow During Operation

Once running, a typical request flows through the system as follows:

```
┌──────────────┐
│   User       │
│  (Browser)   │
└──────┬───────┘
          │ HTTP Request
          ▼
┌──────────────────────────┐
│   ADK Web Server         │
│   http://localhost:8000  │
│                          │
│   • LangGraph Agents     │
│   • Tool Orchestration   │
│   • Session Management   │
└──────┬───────────────────┘
          │ Tool Invocation
          │ (via ToolboxClient)
          ▼
┌───────────────────────────────────────┐
│   GenAI Toolbox MCP Server            │
│   http://localhost:5000               │
│                                       │
│   • 82 DNB API Tools                  │
│   • 4 Toolsets                        │
│   • Request validation                │
│   • OpenTelemetry tracing             │
└──────┬────────────────────┬───────────┘
          │                    │
          │ API Calls          │ Traces (OTLP)
          │                    │
          ▼                    ▼
┌──────────────┐    ┌──────────────────┐
│  DNB APIs    │    │  Jaeger          │
│              │    │  http://16686    │
│  • Statistics│    │                  │
│  • Public    │    │  • Trace storage │
│    Register  │    │  • UI rendering  │
│  • Echo      │    │  • Query API     │
└──────────────┘    └──────────────────┘
```

## 🎛️ Health Check Mechanism

The startup script actively probes services to ensure they are ready before proceeding.

```
┌────────────────────────────────────────┐
│   backend\scripts\quick-start.ps1      │
│   Step 3: Service Health Checks        │
└────────────────┬───────────────────────┘
                             │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
┌────────────────┐  ┌──────────────────┐
│   Jaeger       │  │   Toolbox        │
│                │  │                  │
│  Probes:       │  │  Probes:         │
│  • /           │  │  • /health       │
│  • /search     │  │  • /api/toolsets │
│                │  │  • /api/toolset/ │
│                │  │  • /ui/          │
└────┬───────────┘  └────┬─────────────┘
        │                   │
        │ HTTP GET          │ HTTP GET
        │ (2s timeout)      │ (2s timeout)
        │                   │
        ▼                   ▼
┌─────────┐         ┌──────────┐
│ 200 OK  │         │  200 OK  │
└────┬────┘         └────┬─────┘
        │                   │
        └─────────┬─────────┘
                        │
                        ▼
        [OK] All services ready!
```

## 📈 Startup Timeline

A typical startup sequence takes approximately 30-60 seconds.

```
Time    Step    Action                          Status
────────────────────────────────────────────────────────
0:00    1       Run diagnostics                 Checking...
0:05    1       ✓ Docker detected               [OK]
0:05    1       ✓ Ports available               [OK]
0:06    1       ✓ Network exists                [OK]
0:06    1       ✓ All checks passed             [OK]

0:06    2       Verify Docker network           Checking...
0:07    2       ✓ orkhon-network exists         [OK]

0:07    3       Start Jaeger container          Starting...
0:10    3       Start Toolbox container         Starting...
0:12    3       Wait for Jaeger health          Waiting...
0:15    3       ✓ Jaeger healthy                [OK]
0:17    3       Wait for Toolbox ready          Probing...
0:20    3       ✓ Toolbox ready                 [OK]

0:20    4       Open Toolbox UI                 Opening...
0:21    4       Open Jaeger UI                  Opening...
0:22    4       ✓ UIs opened                    [OK]

0:22    5       Check Python venv               Checking...
0.22    5       ✓ venv found                    [OK]

0:22    6       Load .env config                Loading...
0:23    6       Activate venv                   Activating...
0:24    6       Start ADK Web                   Starting...
0:30    6       ✓ ADK Web listening on :8000    [OK]

0:30    ✓       FULL STACK RUNNING              [READY]
────────────────────────────────────────────────────────
Total Time: ~30-60 seconds (depending on system)
```

## 🛑 Shutdown Flow

```
User presses Ctrl+C
          │
          ▼
┌──────────────────┐
│  ADK Web Server  │──► Stops immediately
└──────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  Docker Services Continue Running   │
│  • GenAI Toolbox: still at :5000    │
│  • Jaeger: still at :16686          │
└─────────────────────────────────────┘
          │
          │ User can:
          ├─► Restart ADK Web: .\backend\scripts\quick-start.ps1
          ├─► Stop Docker: cd backend\toolbox
          │                docker-compose down
          └─► View logs:   docker logs <container>
```

## 🔧 Service Dependencies

```
┌──────────────────┐
│  Docker Desktop  │ (Must be running first)
└────────┬─────────┘
               │
               ▼
┌──────────────────┐
│  Docker Network  │ (orkhon-network)
└────────┬─────────┘
               │
       ┌────┴────┐
       ▼         ▼
┌────────┐  ┌────────────┐
│ Jaeger │  │  Toolbox   │ (Both start in parallel)
└────┬───┘  └─────┬──────┘
        │            │
        │◄───OTLP────┤ (Toolbox sends traces to Jaeger)
        │            │
        └─────┬──────┘
                 │ Both must be healthy before...
                 ▼
        ┌──────────┐
        │ ADK Web  │ (Connects to Toolbox via HTTP)
        └──────────┘
```

## 🎯 Success Indicators

### Terminal Output
You'll know the system is ready when you see this banner in your terminal:
```powershell
========================================================
                     ADK Web Server Starting...

  Full Stack Running:
  • ADK Web:     http://localhost:8000
  • Toolbox UI:  http://localhost:5000/ui/
  • Jaeger UI:   http://localhost:16686

  Press CTRL+C to stop the ADK server
  (Toolbox services will continue running in Docker)
========================================================
```

### Docker Status
You can verify the backend services are running with `docker ps`:
```powershell
PS> docker ps --filter "name=orkhon-"
NAMES                                    STATUS
orkhon-toolbox-dev-genai-toolbox-mcp-1  Up 2 minutes
orkhon-toolbox-dev-jaeger-1             Up 2 minutes (healthy)
```

### Service Health
All primary UIs should return a `200 OK` status:
```powershell
✓ http://localhost:8000      → ADK Web (200 OK)
✓ http://localhost:5000/ui/  → Toolbox UI (200 OK)
✓ http://localhost:16686     → Jaeger UI (200 OK)
```

## 🚀 Ready to Build!

Once you see the "Full Stack Running" message, you can:

1.  **Browse Toolbox UI** → http://localhost:5000/ui/
       - See all 82 DNB tools
       - Test tools interactively
       - View tool schemas

2.  **Access ADK Web** → http://localhost:8000
       - Interact with AI agents
       - Run agent workflows
       - Test agent capabilities

3.  **Monitor Traces** → http://localhost:16686
       - View distributed traces
       - Analyze performance
       - Debug tool invocations

### Tips for Deeper Development

1.  **Define once, reuse widely.** Keep specs in `apis/`, run `openapi-mcp-codegen` to refresh YAML, and immediately get the new tool in Toolbox, ADK, or LangChain clients.
2.  **Use MCP clients for cross-ecosystem use.** Want to test with LangChain or Copilot? Point them to the Toolbox MCP endpoint (`http://localhost:5000`) and they’ll see the same tool catalog ADK uses.
3.  **Handle rate limits early.** Build backoff/retry policies into Toolbox (or your generated clients) and surface friendly errors from agents. That keeps conversational flows from collapsing on 429 responses.
4.  **Trace everything.** With Jaeger already wired, tag your tool configs and agent flows so you can inspect every request end-to-end when something fails.
5.  **Leverage ADK’s abstractions.** Use runner decorators, evaluation hooks, or memory providers to extend the agents. ADK is designed for those integrations and plays nicely with MCP.

---

**🎉 Everything is automated. Just run `.\backend\scripts\quick-start.ps1` and you're ready to build!**
