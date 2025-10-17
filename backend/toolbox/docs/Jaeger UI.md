# Jaeger UI - Distributed Tracing Guide

> **Observability and Performance Monitoring for GenAI Toolbox**  
> Understand request flows, debug issues, and optimize performance

---

## 🔍 What is Jaeger UI?

**Jaeger** is an **open-source distributed tracing system** that runs alongside your GenAI Toolbox. It provides real-time observability into every request flowing through your system.

**Access:** http://localhost:16686

### Key Capabilities:
- ⏱️ **Performance Monitoring** - Track request latency and bottlenecks
- 🔗 **Request Journey Visualization** - See the complete flow from agent → toolbox → DNB API
- ❌ **Error Detection** - Identify failures in real-time
- 📈 **Service Dependencies** - Understand system architecture through traces

---

## 📊 Jaeger UI - The Observability Dashboard

### **What It Does:**
Jaeger **traces every request** that flows through your GenAI Toolbox and visualizes:
- ⏱️ **How long each API call takes** (performance monitoring)
- 🔗 **The complete request journey** (from your agent → toolbox → DNB API)
- ❌ **Errors and failures** in real-time
- 📈 **Service dependencies** and bottlenecks

### **Where It Comes From:**
```yaml
# In your docker-compose.dev.yml
jaeger:
  image: jaegertracing/all-in-one:latest  # ← Official Jaeger container
  ports:
    - "16686:16686"  # ← UI port (what you see in browser)
    - "4318:4318"    # ← OTLP collector (receives traces from toolbox)
```

**Configuration:**
Your GenAI Toolbox is configured to send OpenTelemetry data to Jaeger via environment variables:
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318` - Collector endpoint
- `OTEL_SERVICE_NAME=orkhon-genai-toolbox-mcp` - Service identifier in traces

---

## 🎯 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ Your Agent (Python/Go)                                      │
│ client.invoke("dnb-echo-helloworld", {})                    │
└────────────────┬────────────────────────────────────────────┘
                 │ 1. HTTP Request
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ GenAI Toolbox :5000                                         │
│ • Receives request                                          │
│ • Sends TRACE to Jaeger (start: "tool invoke")             │
│ • Calls DNB API                                             │
│ • Sends TRACE to Jaeger (end: "tool invoke", duration)     │
└────────────────┬────────────────────────────────────────────┘
                 │ 2. Telemetry data (OpenTelemetry format)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Jaeger :4318 (OTLP Collector)                               │
│ • Stores traces in memory                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Jaeger UI :16686 (What you see in browser)                  │
│ • Visualizes traces                                         │
│ • Shows request timeline                                    │
│ • Displays errors and latency                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Using Jaeger UI

### **1. View Recent Requests**
Go to: http://localhost:16686/search

**You'll see:**
- **Service dropdown** → Select `orkhon-genai-toolbox-mcp` (or whatever `${OTEL_SERVICE_NAME}` is set to)
- **Operation dropdown** → Shows all traced operations:
  - `toolbox/server/tool/invoke` (when you call a tool)
  - `toolbox/server/toolset/get` (when you list tools)
  - `toolbox/server/tool/get` (when you inspect a tool)
- **Traces** → Click to see the full request journey

### **2. What You Can See:** 

Ran terminal command: curl.exe -X POST http://localhost:5000/api/tool/dnb-echo-helloworld/invoke -H "Content-Type: application/json" -d "{}"