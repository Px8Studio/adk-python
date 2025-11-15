# ADK Web UI Firebase Deployment Plan

**Goal:** Deploy the existing ADK Web UI (Angular app) from `adk-web/` to Firebase Hosting with Cloud Run backend integration.

## 🌐 Your URLs Explained

### What You Control

**Firebase Hosting (Frontend):**
- **Default Firebase URL**: `https://solven-adk-dev.web.app` ✅ **You control this via Firebase project**
- **Alternative URL**: `https://solven-adk-dev.firebaseapp.com` (also available)
- **Custom Domain** (optional): `https://orkhon.yourdomain.com` ⚙️ **You can configure this**

**Cloud Run Backend (API):**
- **Auto-generated URL**: `https://orkhon-adk-backend-[random].run.app` ⚙️ **GCP assigns random suffix**
- **Custom Domain** (optional): `https://api.orkhon.yourdomain.com` ⚙️ **You can configure this**

### What Firebase Handles for You

Firebase Hosting provides:
- ✅ **Global CDN** - Automatic worldwide distribution
- ✅ **SSL Certificate** - Free HTTPS for `.web.app` and `.firebaseapp.com`
- ✅ **Auto-scaling** - No server management needed
- ✅ **Zero-downtime deploys** - Atomic deployments with rollback support
- ✅ **Free tier** - 10GB storage, 360MB/day bandwidth (sufficient for this app)

### Complete Architecture URLs

```
User Browser
    │
    ▼
https://solven-adk-dev.web.app  ← You access the UI here
    │ (Firebase Hosting - CDN)
    │
    ├─ Static Files (HTML/CSS/JS)
    │
    └─ /api/** requests
       │ (Firebase Rewrites)
       ▼
https://orkhon-adk-backend-xyz.run.app
       │ (Cloud Run Backend)
       │
       ├─ /api/v1/agents
       ├─ /api/v1/sessions
       └─ /ws (WebSocket)
```

**Key Point:** Firebase rewrites mean users NEVER see the Cloud Run URL. All requests appear to come from `solven-adk-dev.web.app/api/**`.

## Current State Analysis

### ADK Web Architecture

**Location**: `c:\Users\rjjaf\_Projects\adk-web` (separate repo from Orkhon)

**Framework**: Angular 19.1.0 (Material Design UI)
- Production-ready Google ADK Web UI
- Full agent management, session handling, evaluation UI
- Real-time WebSocket support for agent streaming
- Built-in trace visualization with Jaeger integration

**Build System**: Angular CLI
- **Output**: `dist/agent_framework_web/` (static files)
- **Bundle Size**: ~90-100 MB production build
- **Assets**: `dist/agent_framework_web/assets/config/runtime-config.json` (critical!)

### How You Currently Use It (Orkhon Pattern)

**From Orkhon directory** via `quick-start.ps1`:

```powershell
# This is what you're already doing:
cd c:\Users\rjjaf\_Projects\orkhon\backend\scripts
.\quick-start.ps1  # Starts Toolbox + ADK backend

# Behind the scenes it runs:
adk web --reload_agents --host=0.0.0.0 --port=8000 backend\adk\agents
```

**Result**: ADK Web UI served at `http://localhost:8000` with Orkhon agents loaded

### Key Configuration Files

**package.json** (from `adk-web/`):
```json
{
  "name": "agent-framework-web",
  "scripts": {
    "start": "ng serve",
    "build": "ng build",
    "serve": "npm run clean-config && npm run inject-backend && ng serve --poll 1000"
  }
}
```

**angular.json** (production config):
```json
{
  "configurations": {
    "production": {
      "outputPath": "dist/agent_framework_web",  // ← Correct output path
      "baseHref": "./",
      "deployUrl": "./",
      "outputHashing": "all"
    }
  }
}
```

### Runtime Configuration Pattern

ADK Web uses **runtime configuration injection** instead of build-time environment variables. This is a best practice for single-build, multi-environment deployments.

**How It Works:**

1. **Development** (local dev server):
   ```powershell
   cd c:\Users\rjjaf\_Projects\adk-web
   npm run serve --backend=http://localhost:8000
   ```
   - `set-backend.js` writes to `src/assets/config/runtime-config.json`
   - Config: `{ "backendUrl": "http://localhost:8000" }`

2. **Production** (Firebase Hosting):
   - Build Angular app → `dist/agent_framework_web/`
   - Inject backend URL → `dist/agent_framework_web/assets/config/runtime-config.json`
   - Deploy to Firebase → Single build works everywhere!

3. **Frontend reads config at runtime**:
   ```typescript
   // src/utils/runtime-config-util.ts
   static getRuntimeConfig(): RuntimeConfig {
     return (window as any)['runtimeConfig'] as RuntimeConfig;
   }
   
   // src/utils/url-util.ts
   static getApiServerBaseUrl(): string {
     return (window as any)['runtimeConfig']?.backendUrl || '';
   }
   ```

**Why This Matters for Deployment:**
- ✅ Build once, deploy anywhere (dev, staging, prod)
- ✅ No need to rebuild for different backend URLs
- ✅ Easy to switch backends without code changes
- ✅ Supports Firebase rewrites (use empty `backendUrl: ""` for relative URLs)

## Deployment Strategy: Two Options

## Deployment Strategy: Two Options

### Option A: Firebase + Cloud Run (Recommended for Production)

**Best for:** Public internet access, always-on production service

```
User → Firebase Hosting (CDN) → Cloud Run Backend → Toolbox (localhost/cloud)
       https://solven-adk-dev.web.app
```

**Advantages:**
- ✅ Global CDN for fast UI loading
- ✅ Free HTTPS SSL certificate
- ✅ Auto-scaling backend (pay per request)
- ✅ Zero server management
- ✅ Production-grade reliability

**Estimated Cost:**
- Frontend (Firebase): **$0/month** (free tier: 10GB storage, 360MB/day)
- Backend (Cloud Run): **$20-60/month** (depends on usage, can scale to zero)

---

### Option B: Firebase + Local Backend (For Testing/Development)

**Best for:** Testing deployment workflow while keeping backend local

```
User → Firebase Hosting (CDN) → Local Orkhon Backend → Local Toolbox
       https://solven-adk-dev.web.app     (your machine)
```

**Advantages:**
- ✅ Test Firebase deployment workflow
- ✅ Keep existing local backend setup
- ✅ No backend cloud costs
- ⚠️ **Limitation:** Only accessible when your machine is running and reachable

**Estimated Cost:**
- Frontend (Firebase): **$0/month**
- Backend: **$0** (local)

**Note:** This requires exposing your local port 8000 via:
- Ngrok/Cloudflare Tunnel (easiest)
- Your router's port forwarding (if public IP)
- VPN (if accessing from specific networks)

---

## Recommended Approach: Start with Option A

Deploy both frontend AND backend to cloud for best results:

1. **Deploy Backend to Cloud Run** (one-time setup)
2. **Deploy Frontend to Firebase Hosting** (connects to Cloud Run)
3. **Access from anywhere** at `https://solven-adk-dev.web.app`

You can always switch backends later by just updating `runtime-config.json`!

## Prerequisites & Setup

### 1. Firebase CLI & Authentication

**Install Firebase CLI globally:**

```powershell
npm install -g firebase-tools
```

**Login to Firebase:**

```powershell
firebase login
```

**Verify your project exists:**

```powershell
firebase projects:list
# Should show: solven-adk-dev
```

### 2. Required Environment

Already have from Orkhon setup:
- ✅ Node.js 18+ (Angular requirement)
- ✅ npm 9+ (Angular requirement)
- ✅ Python 3.11+ with `uv` (ADK backend)
- ✅ Google Cloud SDK (if deploying backend to Cloud Run)

### 3. Firebase Project Structure

You mentioned you already have `solven-adk-dev` Firebase project. Verify it has:

```powershell
# Check project details
firebase projects:describe solven-adk-dev

# Check if Hosting is enabled (should auto-enable on first deploy)
firebase deploy --only hosting --dry-run
```

## Step-by-Step Deployment Guide

### Phase 1: Initialize Firebase in ADK Web Project (One-Time Setup)

**Navigate to ADK Web directory:**

```powershell
cd c:\Users\rjjaf\_Projects\adk-web
```

**Initialize Firebase Hosting:**

```powershell
firebase init hosting
```

**Answer the prompts:**
- `? What do you want to use as your public directory?` → **`dist/agent_framework_web`**
- `? Configure as a single-page app (rewrite all urls to /index.html)?` → **`Yes`**
- `? Set up automatic builds and deploys with GitHub?` → **`No`**
- `? File dist/agent_framework_web/index.html already exists. Overwrite?` → **`No`**

**What this creates:**
- `firebase.json` - Hosting configuration
- `.firebaserc` - Project selection (points to `solven-adk-dev`)

---

### Phase 2: Configure Firebase Hosting

**Create `firebase.json`** in `c:\Users\rjjaf\_Projects\adk-web\firebase.json`:

```json
{
  "hosting": {
    "public": "dist/agent_framework_web",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "orkhon-adk-backend",
          "region": "us-central1"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css|map)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "assets/**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=86400"
          }
        ]
      },
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "DENY"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          }
        ]
      }
    ]
  }
}
```

**Key configuration explained:**
- `"public": "dist/agent_framework_web"` - Where your Angular build outputs
- `/api/**` rewrite - Routes API calls to Cloud Run backend (optional, see Phase 4)
- `**` rewrite - SPA routing (all routes go to index.html)
- Headers - CDN caching + security headers

**Create `.firebaserc`** in `c:\Users\rjjaf\_Projects\adk-web\.firebaserc`:

```json
{
  "projects": {
    "default": "solven-adk-dev"
  }
}
```

---

### Phase 3: Create Runtime Config Injection Script

**Create `inject-firebase-config.js`** in `c:\Users\rjjaf\_Projects\adk-web\inject-firebase-config.js`:

```javascript
/**
 * Injects Firebase production backend URL into runtime-config.json
 * Run this after building for production, before deploying
 */

const fs = require('fs');
const path = require('path');

const distPath = './dist/agent_framework_web/assets/config/runtime-config.json';
const backendUrl = process.env.BACKEND_URL;

if (backendUrl === undefined) {
    console.error('ERROR: BACKEND_URL environment variable not set');
    console.error('Usage: $env:BACKEND_URL="https://your-backend.run.app"; node inject-firebase-config.js');
    console.error('   OR: $env:BACKEND_URL=""; node inject-firebase-config.js  # For Firebase rewrites');
    process.exit(1);
}

const config = {
    backendUrl: backendUrl
};

// Ensure directory exists
const dir = path.dirname(distPath);
if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
}

fs.writeFileSync(distPath, JSON.stringify(config, null, 2));

console.log('✅ Firebase runtime config injected successfully');
console.log(`   Backend URL: ${backendUrl || '(empty - using Firebase rewrites)'}`);
console.log(`   Config file: ${distPath}`);
```

**Update `package.json`** scripts in `c:\Users\rjjaf\_Projects\adk-web\package.json`:

Add these scripts:

```json
{
  "scripts": {
    "build:firebase": "ng build --configuration production",
    "inject-config": "node inject-firebase-config.js",
    "deploy:firebase": "npm run build:firebase && firebase deploy --only hosting",
    "serve:firebase": "firebase serve --only hosting"
  }
}
```

---

### Phase 4A: Deploy Frontend Only (Local Backend)

**Use this if:** You want to test Firebase deployment while keeping your local Orkhon backend running.

**Steps:**

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# 1. Build production Angular app
npm run build:firebase

# 2. Get your local machine's IP address
ipconfig
# Look for "IPv4 Address" under your active network adapter
# Example: 192.168.1.100

# 3. Inject local backend URL
$env:BACKEND_URL = "http://192.168.1.100:8000"
npm run inject-config

# 4. Test locally before deploying
npm run serve:firebase
# Opens http://localhost:5000 (Firebase local emulator)
# Test that it connects to your local backend

# 5. Deploy to Firebase
firebase deploy --only hosting

# 6. Access your deployed app
# URL: https://solven-adk-dev.web.app
```

**Important Notes:**
- ⚠️ Your local backend must be running (`quick-start.ps1` in Orkhon)
- ⚠️ Your machine must be reachable from the internet (router port forwarding or ngrok)
- ⚠️ Update firewall rules to allow port 8000 access

**CORS Configuration Required** in Orkhon backend:

```python
# backend/adk/run_dnb_openapi_agent.py (or wherever CORS is configured)
allow_origins = [
    "https://solven-adk-dev.web.app",
    "https://solven-adk-dev.firebaseapp.com",
    "http://localhost:4200",  # For local Angular dev
    "http://localhost:5000",  # For Firebase emulator
]
```

---

### Phase 4B: Deploy Frontend + Backend to Cloud (Recommended)

**Use this for:** Production deployment accessible from anywhere.

#### Step 1: Deploy Backend to Cloud Run

```powershell
cd c:\Users\rjjaf\_Projects\orkhon\backend

# Build and deploy ADK backend to Cloud Run
gcloud run deploy orkhon-adk-backend `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS=https://solven-adk-dev.web.app `
  --set-env-vars TOOLBOX_BASE_URL=http://localhost:5000 `
  --set-secrets=GEMINI_API_KEY=gemini-api-key:latest `
  --min-instances=0 `
  --max-instances=10 `
  --memory=2Gi `
  --cpu=2 `
  --port=8000 `
  --timeout=300

# Get the deployed URL
$backendUrl = gcloud run services describe orkhon-adk-backend --region us-central1 --format 'value(status.url)'
Write-Host "Backend deployed at: $backendUrl"
```

**Create Dockerfile** in `c:\Users\rjjaf\_Projects\orkhon\backend\Dockerfile` if not exists:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies
RUN uv pip install --system -e .

# Copy application code
COPY adk/ ./adk/

# Expose port
EXPOSE 8000

# Run ADK web server
CMD ["adk", "web", "--host=0.0.0.0", "--port=8000", "--reload_agents", "adk/agents"]
```

#### Step 2: Deploy Frontend to Firebase

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# 1. Build production Angular app
npm run build:firebase

# 2. Use Firebase rewrites (empty backend URL)
$env:BACKEND_URL = ""
npm run inject-config

# 3. Deploy to Firebase
firebase deploy --only hosting

# 4. Access your deployed app
# URL: https://solven-adk-dev.web.app
```

**With Firebase rewrites**, API calls work like this:

```
User browser makes: GET https://solven-adk-dev.web.app/api/v1/agents
                         ↓
Firebase rewrites to:   GET https://orkhon-adk-backend-xyz.run.app/api/v1/agents
                         ↓
Cloud Run backend responds
                         ↓
User sees response from: https://solven-adk-dev.web.app/api/v1/agents
```

**Advantages:**
- ✅ No CORS issues (same origin for user)
- ✅ Backend URL hidden from users
- ✅ Easy to switch backends (just update `firebase.json`)

---

### Phase 5: Verify Deployment

```powershell
# Open deployed site
firebase open hosting:site

# Or manually visit
Start-Process "https://solven-adk-dev.web.app"
```

**Manual Testing Checklist:**

- [ ] **Homepage loads** - No blank screen, no 404s
- [ ] **Runtime config accessible** - Check `https://solven-adk-dev.web.app/assets/config/runtime-config.json`
- [ ] **Agent list loads** - Can see available agents
- [ ] **Agent chat works** - Can send messages and get responses
- [ ] **Sessions persist** - Refresh page, session continues
- [ ] **Evaluation runs** - Can run evaluation sets
- [ ] **Traces display** - Can view agent execution traces
- [ ] **WebSocket connects** - Real-time streaming works
- [ ] **No console errors** - Check browser DevTools console

**Debugging Commands:**

```powershell
# View Firebase Hosting logs
firebase hosting:channel:list

# View Cloud Run logs (if using Cloud Run backend)
gcloud run services logs read orkhon-adk-backend --region us-central1 --limit 50

# Check deployment status
firebase deploy --only hosting --debug

# Check runtime config
Invoke-WebRequest https://solven-adk-dev.web.app/assets/config/runtime-config.json
```

---

## Complete Deployment Workflow (Copy-Paste Ready)

### Option 1: Production Deployment (Firebase + Cloud Run)

**Full cloud deployment - accessible from anywhere.**

```powershell
### Step 1: One-time setup (Firebase configuration)
cd c:\Users\rjjaf\_Projects\adk-web
firebase login
firebase init hosting  # Select dist/agent_framework_web as public directory

### Step 2: Deploy backend to Cloud Run
cd c:\Users\rjjaf\_Projects\orkhon\backend
gcloud run deploy orkhon-adk-backend `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS=https://solven-adk-dev.web.app `
  --min-instances=0 `
  --memory=2Gi `
  --cpu=2 `
  --port=8000

### Step 3: Build and deploy frontend
cd c:\Users\rjjaf\_Projects\adk-web
npm run build:firebase
$env:BACKEND_URL = ""  # Use Firebase rewrites
npm run inject-config
firebase deploy --only hosting

### Step 4: Access your app
Start-Process "https://solven-adk-dev.web.app"
```

**Result:** Your app is live at `https://solven-adk-dev.web.app` with Cloud Run backend!

---

### Option 2: Testing Deployment (Firebase + Local Backend)

**Test Firebase deployment while keeping backend local.**

```powershell
### Step 1: Start local Orkhon stack
cd c:\Users\rjjaf\_Projects\orkhon\backend\scripts
.\quick-start.ps1  # Starts Toolbox + ADK backend on localhost:8000

### Step 2: Get your machine's IP
ipconfig  # Look for IPv4 Address (e.g., 192.168.1.100)

### Step 3: Build and deploy frontend
cd c:\Users\rjjaf\_Projects\adk-web
npm run build:firebase
$env:BACKEND_URL = "http://YOUR_IP:8000"  # Replace with your IP
npm run inject-config
firebase deploy --only hosting

### Step 4: Access your app
Start-Process "https://solven-adk-dev.web.app"
```

**Note:** Your local backend must be reachable from the internet (port forwarding or ngrok).

---

### Option 3: Quick Update (Frontend Only)

**Rebuild and redeploy just the frontend (assumes backend hasn't changed).**

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# Build
npm run build:firebase

# Inject config (use existing backend URL)
$env:BACKEND_URL = ""  # Or your Cloud Run URL
npm run inject-config

# Deploy
firebase deploy --only hosting
```

---

## Configuration Files Reference

1. **firebase.json** - Hosting configuration with rewrites
2. **.firebaserc** - Firebase project selection (`solven-adk-dev`)
3. **inject-firebase-config.js** - Runtime config injection script
4. **.gitignore updates** - Add Firebase files:
   ```
   # Firebase
   .firebase/
   firebase-debug.log
   firebase-debug.*.log
   ```

### Files to Modify

1. **package.json** - Add `build:firebase` and `deploy:firebase` scripts
2. **angular.json** - Already configured correctly with `baseHref: "./"` for production

## Environment-Specific Configurations

### Development (Local)
```json
// src/assets/config/runtime-config.json (local dev)
{
  "backendUrl": "http://localhost:8000"
}
```

Command: `npm run serve --backend=http://localhost:8000`

### Staging/Testing (Firebase + Local Backend)
```json
// dist/agent_framework_web/assets/config/runtime-config.json
{
  "backendUrl": "http://YOUR_LOCAL_IP:8000"
}
```

Deployment: Build + inject local IP + deploy to Firebase

### Production (Firebase + Cloud Run)
```json
// dist/agent_framework_web/assets/config/runtime-config.json
{
  "backendUrl": ""
}
```

Deployment: Build + inject empty URL + deploy (uses Firebase rewrites)

## Complete Deployment Commands

### Initial Setup (One-time)

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# Install dependencies
npm install

# Install Firebase CLI globally
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase Hosting
firebase init hosting
```

### Every Deployment

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# Build production bundle
npm run build

# Inject backend configuration
# Option 1: Use Firebase rewrites (recommended)
$env:BACKEND_URL = ""
node inject-firebase-config.js

# Option 2: Use Cloud Run URL directly
# $env:BACKEND_URL = "https://orkhon-adk-backend-xyz.run.app"
# node inject-firebase-config.js

# Deploy to Firebase Hosting
firebase deploy --only hosting

# View deployed site
firebase open hosting:site
```

### One-Command Deployment (after setup)

```powershell
# Add to package.json
{
  "scripts": {
    "deploy:prod": "npm run build && cross-env BACKEND_URL='' node inject-firebase-config.js && firebase deploy --only hosting"
  }
}

# Then just run:
npm run deploy:prod
```

## Testing Checklist

Before considering deployment successful:

- [ ] ADK Web UI loads at `https://solven-adk-dev.web.app`
- [ ] Homepage displays correctly (no 404s for assets)
- [ ] Runtime config loads: Check `/assets/config/runtime-config.json`
- [ ] Backend connectivity works (can list agents)
- [ ] WebSocket connections establish for real-time updates
- [ ] Agent chat interface functions correctly
- [ ] Session management persists across page refreshes
- [ ] Evaluation runs complete successfully
- [ ] Artifacts display correctly
- [ ] Trace visualization renders properly
- [ ] Mobile responsive design works
- [ ] No CORS errors in browser console
- [ ] API calls route through Firebase rewrites (if using)
- [ ] Error handling displays user-friendly messages

## Troubleshooting

### Issue: 404 on Assets

**Symptom**: CSS/JS files not loading, 404 errors in console

**Fix**: Check `baseHref` and `deployUrl` in `angular.json`:
```json
{
  "configurations": {
    "production": {
      "baseHref": "./",
      "deployUrl": "./"
    }
  }
}
```

### Issue: Backend API Calls Fail

**Symptom**: "CORS error" or "Failed to fetch" in console

**Fix 1**: Verify CORS on backend allows Firebase domain
```python
allow_origins = ["https://solven-adk-dev.web.app"]
```

**Fix 2**: Check `runtime-config.json` backend URL is correct
```powershell
# Download and inspect deployed config
Invoke-WebRequest https://solven-adk-dev.web.app/assets/config/runtime-config.json
```

### Issue: Blank Page After Deployment

**Symptom**: White screen, no content

**Fix**: Check browser console for errors
- Missing `index.html`? → Ensure `public: dist/agent_framework_web` in firebase.json
- Module loading error? → Verify build completed successfully
- Base href issue? → Check `baseHref: "./"` in angular.json

### Issue: WebSocket Connection Fails

**Symptom**: Real-time updates don't work, WS errors in console

**Fix**: Firebase Hosting supports WebSocket pass-through but requires:
1. Cloud Run backend with WebSocket support enabled
2. HTTP/1.1 upgrade headers allowed
3. Check `url-util.ts` WebSocket URL construction

### Issue: Runtime Config Not Found

**Symptom**: `GET /assets/config/runtime-config.json 404`

**Fix**: Ensure injection script ran after build:
```powershell
# Check if file exists in build output
Test-Path dist\agent_framework_web\assets\config\runtime-config.json

# If missing, run injection again
$env:BACKEND_URL = ""
node inject-firebase-config.js
```

## Production Optimizations

### Enable CDN Caching

Already configured in `firebase.json` headers:
- Static assets (JS/CSS): 1 year cache
- Dynamic assets: 1 day cache

### Prerendering (Optional)

For better SEO and initial load:
```json
{
  "hosting": {
    "cleanUrls": true,
    "trailingSlash": false
  }
}
```

### Custom Domain (Optional)

```powershell
# Add custom domain
firebase hosting:sites:create solven-adk-dev
firebase target:apply hosting adk-web solven-adk-dev
firebase deploy --only hosting:adk-web
```

### Security Headers

Add to `firebase.json`:
```json
{
  "hosting": {
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "DENY"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          }
        ]
      }
    ]
  }
}
```

## Cost Estimates

**Firebase Hosting (solven-adk-dev.web.app):**
- Free tier: 10 GB storage, 360 MB/day transfer
- ADK Web build: ~100 MB
- Estimated cost: **$0/month** (well within free tier)

**Cloud Run Backend** (if needed):
- See main deployment plan for backend costs
- Estimated: $45-60/month for always-on instance

**Total cost**: $0-60/month depending on backend choice

## Next Steps After Initial Deployment

1. **Set up CI/CD** (GitHub Actions):
   ```yaml
   # .github/workflows/firebase-deploy.yml
   - name: Build and Deploy
     run: |
       npm ci
       npm run build
       BACKEND_URL=${{ secrets.BACKEND_URL }} node inject-firebase-config.js
       firebase deploy --only hosting --token ${{ secrets.FIREBASE_TOKEN }}
   ```

2. **Configure custom domain** for `solven-adk-dev.com` (if desired)

3. **Set up monitoring**:
   - Firebase Performance Monitoring
   - Google Analytics
   - Error tracking (Sentry or Cloud Error Reporting)

4. **Create second deployment** for `solven.web.app` (production frontend)

5. **Implement authentication** (Firebase Auth) if needed

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│           Firebase Hosting                              │
│       https://solven-adk-dev.web.app                    │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │   ADK Web UI (Angular SPA)                     │     │
│  │   - Static HTML/CSS/JS                         │     │
│  │   - 100 MB bundle                              │     │
│  │   - Cached on CDN                              │     │
│  └────────────────┬───────────────────────────────┘     │
└────────────────────┼───────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │   API Request           │
        │   /api/v1/agents        │
        └────────────┬────────────┘
                     │
         ┌───────────▼──────────────┐
         │  Firebase Rewrites       │
         │  (configured in          │
         │   firebase.json)         │
         └───────────┬──────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Cloud Run Backend                          │
│      https://orkhon-adk-backend-xyz.run.app             │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │   ADK Web Server (FastAPI)                     │     │
│  │   - Multi-agent orchestration                  │     │
│  │   - Session management                         │     │
│  │   - WebSocket support                          │     │
│  └────────────┬───────────────────────────────────┘     │
└────────────────┼───────────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
┌───────────┐      ┌─────────────────┐
│ Toolbox   │      │  BigQuery/GCS   │
│ (MCP)     │      │  Secret Manager │
└───────────┘      └─────────────────┘
```

## Summary

**Deploying ADK Web UI to Firebase Hosting requires:**

1. ✅ **Build the Angular app** → `dist/agent_framework_web/`
2. ✅ **Configure Firebase Hosting** → `firebase.json`, `.firebaserc`
3. ✅ **Inject runtime config** → Backend URL for production
4. ✅ **Deploy static files** → `firebase deploy --only hosting`
5. ✅ **Configure backend CORS** → Allow Firebase domain
6. ⚠️ **Backend must be hosted separately** → Cloud Run or local server

**Key advantages of this approach:**
- Frontend is fully static (fast CDN delivery)
- Single build works across environments (runtime config)
- Firebase Hosting rewrites provide seamless backend integration
- No need to manage frontend infrastructure
- Auto-scaling and global CDN included

**The ADK Web UI is production-ready and can be deployed immediately** once you:
1. Create the Firebase configuration files
2. Build the production bundle
3. Inject the backend URL
4. Deploy to Firebase Hosting

This approach is significantly simpler than the Orkhon React frontend (which needs to be built from scratch) because ADK Web is already a complete, production-ready Angular application.
