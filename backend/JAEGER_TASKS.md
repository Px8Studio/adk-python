# 🔬 Jaeger Tasks - Quick Summary

## What We Added

### New Jaeger Management Tasks

1. **Jaeger: Restart Container**
   - Restarts only Jaeger (not Toolbox)
   - Clears all in-memory traces
   - Useful when Jaeger becomes unresponsive

2. **Jaeger: View Logs (Live)**
   - Shows real-time Jaeger logs
   - Monitor trace ingestion
   - Debug OTLP connection issues

3. **Jaeger: Check Health Status**
   - Quick health verification
   - Returns: `healthy`, `unhealthy`, or `starting`
   - Useful for troubleshooting

4. **Jaeger: Test OTLP Endpoint**
   - Tests OpenTelemetry Protocol receiver
   - Verifies port 4318 is accepting connections
   - Returns HTTP status code (200 = working)

5. **Jaeger: Clear All Traces**
   - Same as restart, but clearer intent
   - Use for fresh testing sessions
   - All traces permanently deleted

---

## Why These Tasks Matter

### 🎯 Problem They Solve

**Before:**
- ❌ No easy way to manage Jaeger separately
- ❌ Had to restart entire stack to clear traces
- ❌ Difficult to debug why traces aren't appearing
- ❌ No quick health check for Jaeger

**After:**
- ✅ Manage Jaeger independently
- ✅ Clear traces without affecting Toolbox
- ✅ Quick diagnostics with health check
- ✅ Test OTLP endpoint directly

---

## 🧪 Testing Results

| Task | Status | Output |
|------|--------|--------|
| **Jaeger: Check Health Status** | ✅ Working | `healthy` |
| **Jaeger: View Logs** | ✅ Working | Shows OTLP on :4317 & :4318 |
| **Jaeger: Restart Container** | ✅ Working | Restarts in ~2 seconds |

---

## 🔍 Understanding Jaeger Ports

Jaeger runs on multiple ports for different purposes:

| Port | Protocol | Purpose |
|------|----------|---------|
| **4317** | gRPC | OTLP gRPC endpoint (binary protocol) |
| **4318** | HTTP | OTLP HTTP endpoint (JSON/protobuf) |
| **14250** | gRPC | Jaeger native collector gRPC |
| **14268** | HTTP | Jaeger native collector HTTP |
| **16686** | HTTP | **Jaeger UI** (what you see in browser) |
| **16685** | gRPC | Jaeger Query gRPC |

**Most Important:**
- **:4318** - Where Toolbox sends traces (OTLP HTTP)
- **:16686** - Where you view traces (Jaeger UI)

---

## 🎓 Common Use Cases

### 1. Traces Not Appearing?
```
Step 1: Run "Jaeger: Check Health Status"
  → Should return: healthy

Step 2: Run "Jaeger: Test OTLP Endpoint"  
  → Should return: 200

Step 3: Run "Jaeger: View Logs (Live)"
  → Look for trace ingestion messages

Step 4: Check Toolbox logs
  → Run "MCP: View Dev Logs (Live)"
  → Look for telemetry errors
```

### 2. Want Fresh Start for Testing?
```
Run: "Jaeger: Clear All Traces"
  → Restarts Jaeger
  → Clears all in-memory traces
  → Ready for clean testing
```

### 3. Jaeger Unresponsive or Slow?
```
Run: "Jaeger: Restart Container"
  → Quick 2-second restart
  → Doesn't affect Toolbox
  → Clears any stuck traces
```

### 4. Debugging OTLP Connection?
```
Run: "Jaeger: Test OTLP Endpoint"
  → Tests :4318 directly
  → Confirms receiver is working
  → Returns 200 if healthy
```

---

## 📊 Jaeger Log Interpretation

### What to Look For:

✅ **Good Signs:**
```
"msg":"OTLP receiver status change","status":"StatusStarting"
"msg":"Starting GRPC server","endpoint":":4317"
"msg":"Starting HTTP server","endpoint":":4318"
"msg":"Query server started","http_addr":"[::]:16686"
"msg":"Health Check state change","status":"ready"
```

❌ **Warning Signs:**
```
"level":"error" - Something failed
"failed to upload metrics" - Metrics endpoint issue (can be ignored)
"connection refused" - Can't reach backend
"port already in use" - Port conflict
```

---

## 🔧 Troubleshooting

### Jaeger Container Not Healthy?

**Check 1: Container Status**
```bash
docker ps --filter name=jaeger
```
Look for `(healthy)` or `(unhealthy)` in STATUS column

**Check 2: Detailed Health**
```bash
docker inspect orkhon-toolbox-dev-jaeger-1 --format='{{json .State.Health}}' | jq .
```
Shows health check history

**Check 3: Container Logs**
```bash
docker logs orkhon-toolbox-dev-jaeger-1 --tail 50
```
See what went wrong during startup

### OTLP Endpoint Returns Error?

**Possible Causes:**
1. Jaeger container not fully started (wait 10 seconds)
2. Port 4318 blocked by firewall
3. Another service using port 4318
4. Jaeger crashed during startup

**Solution:**
```bash
# Restart Jaeger
Run: "Jaeger: Restart Container"

# Wait 10 seconds

# Test again
Run: "Jaeger: Test OTLP Endpoint"
```

---

## 💡 Pro Tips

1. **Monitor traces during development:**
   - Keep Jaeger UI open in browser
   - Refresh after each API call
   - Look for slow spans (red/orange)

2. **Use clear traces strategically:**
   - Before each test session
   - When traces become cluttered
   - When debugging specific flows

3. **Combine with Toolbox logs:**
   - Run both log viewers side-by-side
   - Correlate errors across services
   - Use Jaeger trace IDs to find logs

4. **Understand trace lifecycle:**
   - Traces take ~5-30 seconds to appear
   - In-memory storage = lost on restart
   - Max traces limited by memory

5. **Health check regularly:**
   - Add to morning routine
   - Check after Docker restarts
   - Verify after system updates

---

## 📚 Additional Resources

- [Jaeger Official Docs](https://www.jaegertracing.io/docs/)
- [OpenTelemetry OTLP Spec](https://opentelemetry.io/docs/specs/otlp/)
- [Jaeger Architecture](https://www.jaegertracing.io/docs/architecture/)
- [OTLP HTTP Protocol](https://opentelemetry.io/docs/specs/otlp/#otlphttp)

---

**Last Updated:** October 16, 2025
