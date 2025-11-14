# ADK Web UI Firebase Deployment Plan

Deploy the existing ADK Web UI (Angular app) to Firebase Hosting for `solven-adk-dev.web.app` with backend API integration.

## Current State Analysis

### ADK Web Architecture
- **Location**: `c:\Users\rjjaf\_Projects\adk-web`
- **Framework**: Angular 19.1.0 (Material Design UI)
- **Build System**: Angular CLI
- **Output**: `dist/adk_web/` (static files)
- **Bundle Size**: ~90-100 MB production build

### Key Configuration Files

**package.json:**
```json
{
  "name": "adk-web",
  "scripts": {
    "start": "ng serve",
    "build": "ng build",
    "serve": "npm run clean-config && npm run inject-backend && ng serve"
  }
}
```

**angular.json (production config):**
```json
{
  "configurations": {
    "production": {
      "outputPath": "dist/adk_web",
      "baseHref": "./",
      "deployUrl": "./",
      "outputHashing": "all"
    }
  }
}
```

### Runtime Configuration Pattern

ADK Web uses **runtime configuration injection** instead of build-time environment variables:

1. **Development** (`npm run serve --backend=http://localhost:8000`):
   - `set-backend.js` writes to `src/assets/config/runtime-config.json`
   - Config includes: `{ "backendUrl": "http://localhost:8000" }`

2. **Production** (deployed):
   - `runtime-config.json` must be present in `dist/adk_web/assets/config/`
   - Frontend reads backend URL from this file at runtime
   - Allows single build to work across environments

3. **Access in code**:
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

## Deployment Requirements

### Prerequisites

1. **Firebase Project Created**: ✅ You mentioned you already have this
2. **Firebase CLI Installed**:
   ```powershell
   npm install -g firebase-tools
   ```

3. **Firebase Login**:
   ```powershell
   firebase login
   ```

4. **Node.js & npm**: Already available (Angular requires it)

### Required Tools

- Node.js 18+ ✅
- npm 9+ ✅
- Angular CLI 19+ ✅
- Firebase CLI ✅ (install if missing)

## Step-by-Step Deployment Guide

### Step 1: Initialize Firebase in ADK Web Project

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# Initialize Firebase (select Hosting only)
firebase init hosting

# When prompted:
# ? What do you want to use as your public directory? dist/agent_framework_web
# ? Configure as a single-page app (rewrite all urls to /index.html)? Yes
# ? Set up automatic builds and deploys with GitHub? No
# ? File dist/agent_framework_web/index.html already exists. Overwrite? No
```

This creates:
- `firebase.json` - Hosting configuration
- `.firebaserc` - Project selection

### Step 2: Configure Firebase Hosting

**Create/Update `firebase.json`** in `c:\Users\rjjaf\_Projects\adk-web\firebase.json`:

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
        "source": "/dev-ui/**",
        "destination": "/index.html"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
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
      }
    ]
  }
}
```

**Create `.firebaserc`** in `c:\Users\rjjaf\_Projects\adk-web\.firebaserc`:

```json
{
  "projects": {
    "default": "solven-adk-dev"
  }
}
```

### Step 3: Create Runtime Config Injection Script

**Create `inject-firebase-config.js`** in `c:\Users\rjjaf\_Projects\adk-web\inject-firebase-config.js`:

```javascript
/**
 * Injects Firebase production backend URL into runtime-config.json
 * Run this after building for production, before deploying
 */

const fs = require('fs');
const path = require('path');

const distPath = './dist/agent_framework_web/assets/config/runtime-config.json';
const backendUrl = process.env.BACKEND_URL || '';

if (!backendUrl) {
    console.error('ERROR: BACKEND_URL environment variable not set');
    console.error('Usage: BACKEND_URL=https://your-backend.run.app node inject-firebase-config.js');
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
console.log(`   Backend URL: ${backendUrl}`);
console.log(`   Config file: ${distPath}`);
```

### Step 4: Update package.json Scripts

**Add to `package.json` scripts**:

```json
{
  "scripts": {
    "build:firebase": "ng build --configuration production",
    "deploy:firebase": "npm run build:firebase && firebase deploy --only hosting",
    "inject-firebase-config": "node inject-firebase-config.js"
  }
}
```

### Step 5: Build and Deploy Workflow

#### Option A: Deploy with Local Backend (Testing)

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# 1. Build production
npm run build:firebase

# 2. Inject local backend URL (for testing)
$env:BACKEND_URL = "http://localhost:8000"
node inject-firebase-config.js

# 3. Test locally before deploying
firebase serve

# 4. Deploy to Firebase Hosting
firebase deploy --only hosting
```

**Note**: This will work but frontend will try to connect to localhost:8000 (won't work for remote users).

#### Option B: Deploy with Cloud Run Backend (Production)

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# 1. Build production
npm run build:firebase

# 2. Inject Cloud Run backend URL
$env:BACKEND_URL = "https://orkhon-adk-backend-xyz.run.app"
node inject-firebase-config.js

# 3. Test locally with Cloud Run backend
firebase serve

# 4. Deploy to Firebase Hosting
firebase deploy --only hosting
```

#### Option C: Use Firebase Hosting Rewrites (Recommended)

With Firebase Hosting rewrites configured in `firebase.json`, the frontend can use **relative URLs** (`/api/*`) that Firebase automatically routes to Cloud Run.

**Modify runtime-config.json injection**:

```javascript
// inject-firebase-config.js (modified for rewrites)
const config = {
    backendUrl: ''  // Empty = use relative URLs (Firebase rewrites handle routing)
};
```

**Frontend will make calls to**:
- `/api/v1/agents` → Firebase rewrites to → `https://orkhon-adk-backend.run.app/api/v1/agents`

**Build & Deploy**:

```powershell
cd c:\Users\rjjaf\_Projects\adk-web

# 1. Build
npm run build:firebase

# 2. Inject empty backend URL (use rewrites)
$env:BACKEND_URL = ""
node inject-firebase-config.js

# 3. Deploy
firebase deploy --only hosting
```

### Step 6: Verify Deployment

```powershell
# Check deployment status
firebase hosting:sites:list

# Open deployed site
firebase open hosting:site
```

**Manual verification**:
1. Go to `https://solven-adk-dev.web.app`
2. Open browser DevTools → Network tab
3. Check that API calls route correctly
4. Verify runtime-config.json loads: `https://solven-adk-dev.web.app/assets/config/runtime-config.json`

## Backend Integration Requirements

### For Local Development Backend

**Start ADK backend** (in Orkhon project):

```powershell
cd c:\Users\rjjaf\_Projects\orkhon\backend
adk web --reload_agents --host=0.0.0.0 --port=8000 --allow_origins=https://solven-adk-dev.web.app adk\agents
```

**CORS Configuration** (add to backend):
```python
# Backend CORS must allow Firebase domain
allow_origins = [
    "https://solven-adk-dev.web.app",
    "https://solven-adk-dev.firebaseapp.com",
    "http://localhost:4200"  # For local Angular dev
]
```

### For Cloud Run Backend (Production)

**Deploy Orkhon backend to Cloud Run** (from earlier plan):

```powershell
cd c:\Users\rjjaf\_Projects\orkhon\backend

gcloud run deploy orkhon-adk-backend `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS=https://solven-adk-dev.web.app `
  --set-secrets=GOOGLE_API_KEY=gemini-api-key:latest `
  --min-instances=1 `
  --memory=2Gi `
  --cpu=2
```

**Get Cloud Run URL**:
```powershell
$backendUrl = gcloud run services describe orkhon-adk-backend --region us-central1 --format 'value(status.url)'
Write-Host "Backend URL: $backendUrl"
```

**Update firebase.json rewrites** with actual service name:
```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "orkhon-adk-backend",
          "region": "us-central1"
        }
      }
    ]
  }
}
```

## Configuration Files Summary

### Files to Create in `c:\Users\rjjaf\_Projects\adk-web\`

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
