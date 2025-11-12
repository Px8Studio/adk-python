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
# In docker-compose.dev.yml
jaeger:
  image: jaegertracing/all-in-one:latest  # Official Jaeger container
  ports:
    - "16686:16686"  # UI port (what you see in browser)
    - "4318:4318"    # OTLP collector (receives traces from toolbox)
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

### **2. Analyze a Trace**

After invoking a tool (e.g., `dnb-echo-helloworld`), refresh Jaeger and click "Find Traces" to see:

```
Trace Timeline:
├─ toolbox/server/tool/invoke (200ms total)
   ├─ HTTP call to DNB API (150ms)
   ├─ JSON parsing (5ms)
   └─ Response formatting (2ms)
```

**Example:** Test a tool invocation:
```powershell
curl.exe -X POST http://localhost:5000/api/tool/dnb-echo-helloworld/invoke `
  -H "Content-Type: application/json" `
  -d "{}"
```

Then in Jaeger UI:
1. Select service: `orkhon-genai-toolbox-mcp`
2. Select operation: `toolbox/server/tool/invoke`
3. Click "Find Traces"
4. Click on a trace to see detailed timeline

---

## 🆚 Jaeger vs GenAI Toolbox Web UI

| **Jaeger UI** (`:16686`) | **GenAI Toolbox UI** (`:5000`) |
|---|---|
| **Purpose:** Performance monitoring & debugging | **Purpose:** Browse and test tools |
| Shows request traces, timings, errors | Shows tool schemas, parameters, invoke UI |
| From: `jaegertracing/all-in-one` container | From: GenAI Toolbox built-in server |
| **For DevOps/Monitoring** | **For Development/Testing** |

---

## 📊 Key Features

### **1. Trace Search**
- Filter by service, operation, tags, duration
- Time range selection (last 1h, 2h, custom)
- Find traces matching specific criteria

### **2. Trace Details**
Each trace shows:
- **Span Timeline** - Visual representation of operation duration
- **Service Calls** - Which services were involved
- **Tags & Logs** - Metadata and debug information
- **Error Information** - Stack traces for failures

### **3. Service Dependencies**
View the **System Architecture** tab to see:
- Service dependency graph
- Request flow between services
- Performance metrics per service

### **4. Compare Traces**
- Select multiple traces
- Compare performance side-by-side
- Identify regression patterns

---

## 🎓 When to Use Jaeger

### **Use Jaeger (`:16686`)** when:
- ✅ **Investigating slow requests** - "Why did this take 10 seconds?"
- ✅ **Debugging errors** - "Where did this fail in the request chain?"
- ✅ **Monitoring production health** - Real-time observability
- ✅ **Understanding request flow** - See the complete journey through multiple services
- ✅ **Performance optimization** - Identify bottlenecks and optimize

### **Don't Use Jaeger for:**
- ❌ Testing if tools work (use Toolbox UI instead)
- ❌ Browsing available tools (use Toolbox UI instead)
- ❌ Checking tool parameters (use Toolbox UI instead)

---

## 🔧 Common Tasks

### **Task 1: Find Slow Requests**
1. Go to Search tab
2. Set "Min Duration" filter (e.g., > 1000ms)
3. Click "Find Traces"
4. Analyze spans to identify bottleneck

### **Task 2: Debug Failed Requests**
1. In Search, add tag filter: `error=true`
2. Find traces with errors
3. Click trace → Look for red spans
4. Check "Logs" tab for error details

### **Task 3: Monitor DNB API Performance**
1. Search for operation: `toolbox/server/tool/invoke`
2. Filter by time range (last 1 hour)
3. Sort by duration (longest first)
4. Identify problematic API calls

### **Task 4: Clear All Traces**
Jaeger stores traces in memory by default. To clear:
```powershell
cd backend/toolbox
docker-compose -f docker-compose.dev.yml restart jaeger
```

Or use VS Code task: **"Jaeger: Clear All Traces (Restart Container)"**

---

## 🛠️ Troubleshooting

### **Problem: No traces appearing**

**Solution:**
1. Check Jaeger is running:
   ```powershell
   docker ps --filter name=jaeger
   ```

2. Verify Toolbox is sending traces:
   ```powershell
   docker-compose -f docker-compose.dev.yml logs genai-toolbox-mcp | grep -i otel
   ```

3. Check OTLP endpoint is reachable:
   ```powershell
   curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:4318/v1/traces `
     -H 'Content-Type: application/json' -d '{"resourceSpans":[]}'
   ```
   Expected: `200`

### **Problem: Traces are incomplete**

**Cause:** Toolbox may not be configured to send all span data.

**Solution:** Check environment variables in `docker-compose.dev.yml`:
```yaml
OTEL_EXPORTER_OTLP_ENDPOINT: "http://jaeger:4318"
OTEL_SERVICE_NAME: "orkhon-genai-toolbox-mcp"
```

### **Problem: Jaeger UI is slow**

**Cause:** Too many traces in memory.

**Solution:** Restart Jaeger to clear traces:
```powershell
docker-compose -f docker-compose.dev.yml restart jaeger
```

---

## 📚 Related Documentation

- **[Backend README](../../README.md)** - Overall backend architecture
- **[Toolbox Configuration](../config/QUICK_ANSWER.md)** - Tool configuration guide
- **[Docker Compose](../docker-compose.dev.yml)** - Service configuration

---

## 🔗 External Resources

- **[Jaeger Documentation](https://www.jaegertracing.io/docs/)** - Official Jaeger docs
- **[OpenTelemetry](https://opentelemetry.io/)** - Observability standard
- **[Distributed Tracing](https://www.jaegertracing.io/docs/1.50/architecture/)** - Architecture concepts

---

## 💡 Tips & Best Practices

1. **Tag your operations** - Add custom tags to traces for better filtering
2. **Set appropriate sampling** - In production, use sampling to reduce overhead
3. **Archive important traces** - Take screenshots or export JSON for debugging sessions
4. **Monitor regularly** - Check Jaeger daily to catch performance regressions early
5. **Use trace IDs** - Share trace IDs with your team when reporting issues

---

## 🚀 Quick Start Checklist

- [ ] Start Toolbox with Jaeger: `docker-compose -f docker-compose.dev.yml up -d`
- [ ] Open Jaeger UI: http://localhost:16686
- [ ] Invoke a test tool (e.g., `dnb-echo-helloworld`)
- [ ] Search for traces in Jaeger
- [ ] Analyze trace timeline
- [ ] Explore service dependencies

**You're now ready to monitor and optimize your GenAI Toolbox!** 🎉
