## Orkhon Frontend: What To Do Next

You have the hosting + proxy scaffolding. Finish the React/Vite app, wire CI/CD, and deploy. This checklist walks you through dev → staging → prod for a full-stack agentic AI app (ADK now, LangGraph later).

### 1. Scaffold Vite React (TypeScript)

If you haven’t finished the interactive prompt yet, run from repo root:

```powershell
npm create vite@latest frontend -- --template react-ts
```

Skip if the Vite files already exist (main.tsx, App.tsx, index.html). The folder currently only has custom config we added.

Then install deps:

```powershell
cd frontend
npm install
```

Add required packages for quality (optional but recommended):

```powershell
npm install -D @types/node eslint typescript
```

### 2. Verify Local Dev Works

Start backends (your quick-start script or separate terminals) so FastAPI (ADK) runs on 8000 and Toolbox on 5000. Then:

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173 and confirm requests to `/api/...` and `/toolbox/...` proxy correctly (network tab should show 200 responses).

### 3. Add First API Call

In `src/App.tsx` (after scaffold) consume the helper:

```tsx
import { useEffect, useState } from 'react';
import { apiFetch } from './lib/api';

export function App() {
  const [info, setInfo] = useState<string>('loading...');
  useEffect(() => {
    apiFetch('/health').then(r => setInfo(JSON.stringify(r))).catch(e => setInfo(e.message));
  }, []);
  return <pre>{info}</pre>;
}
```

Ensure your ADK API exposes a `/health` or similar; adapt path as needed.

### 4. Firebase Hosting Setup

Files already added:
- `firebase.json` (rewrites /api and /toolbox)
- `.firebaserc` (dev/prod aliases)

Login and target dev project:

```powershell
firebase login
firebase use dev
```

### 5. Build & Local Preview

```powershell
cd frontend
npm run build
firebase emulators:start --only hosting
```

Navigate to the emulator URL (printed in console). Rewrites won’t work unless you also run backends locally. Emulator tests CDN behavior, not Cloud Run.

### 6. Deploy to Dev

First deploy when Cloud Run services exist (replace serviceIds in firebase.json if different):

```powershell
firebase deploy --only hosting -P dev
```

### 7. Promote to Prod

```powershell
firebase use prod
firebase deploy --only hosting -P prod
```

### 8. GitHub Actions (CI/CD)

Create `.github/workflows/firebase-hosting.yml` (we can add this automatically) to:
1. Install Node deps
2. Build frontend
3. Deploy to dev on push to `dev`, prod on tagged release or merge to `main`

Use a Firebase CI token stored as `FIREBASE_TOKEN` secret.

### 9. Auth Strategy (Forward-Looking)

Single-origin through Hosting simplifies:
- Using Firebase Auth or Identity Platform: grab ID token → send `Authorization: Bearer <token>` from `api.ts`
- Avoids CORS complexity; tighten CORS in FastAPI to only allow Hosting domain.

### 10. Observability & Tracing

You already send OpenTelemetry spans (WANDB). Frontend integration optional: Add OTLP exporter in browser (caution: large volume). Prefer backend tracing only initially.

### 11. Introducing LangGraph Later

When adding a LangGraph service, deploy to Cloud Run, then extend `firebase.json`:

```json
{
  "source": "/graph/**",
  "run": { "serviceId": "orkhon-langgraph", "region": "europe-west4" }
}
```

Frontend calls `fetch('/graph/execute', ...)` — same pattern; no extra environment variables needed unless you want feature flags.

### 12. Cache & Performance Notes

- `assets/**` immutable caching; ensure hashed filenames (Vite does this in production build).
- Consider adding `Link` headers for font preloading later if needed.
- Lighthouse: run against prod URL after first deploy.

### 13. Testing Frontend/Backend Contract

Add a script:

```powershell
curl https://<dev-hosting-domain>/api/health
curl https://<dev-hosting-domain>/toolbox/api/toolset/
```

Both should return JSON without CORS errors.

### 14. Common Pitfalls

- Missing Cloud Run IAM: make sure services allow unauthenticated access OR you handle identity tokens in fetch.
- Stale Hosting cache: deploying new `index.html` invalidates shell; ensure no aggressive caching on HTML.
- Wrong serviceId region mismatch → 404 in rewrites.

### 15. Rapid Iteration Workflow

1. Run backend quick-start script.
2. `npm run dev` in frontend.
3. Commit & push → CI builds, deploys dev site.
4. Smoke test dev site → tag release → prod deploy.

### Summary

You now have: unified path rewrites, proxy parity dev/prod, environment isolation, future extensibility for additional agent frameworks. Next critical step: generate the scaffold (if not already), add the CI workflow, then deploy.

---
If you’d like, ask for an automatic GitHub Actions workflow and I’ll add it next.
Searched codebase for "#codebase considering the app context we are building in orkhon, with currently gogole adkk built samples, and in the future with langgraph built agents... what is the right way to integrate firebae hosting react app compiled  with vite , what is the right setup guide me and explain why behind the reocmemndations, remember we are building a full stack agentic ai app.. 

(true) PS C:\Users\rjjaf\_Projects\orkhon> npm create vite@latest frontend -- --template react
npm warn "react" is being parsed as a normal command line argument.
npm warn Unknown cli config "--template". This will stop working in the next major version of npm.
Need to install the following packages:
create-vite@8.0.2
Ok to proceed? (y) y


> npx
> create-vite frontend react

│
◇  Select a framework:
│  React
│
◆  Select a variant:
│  ● TypeScript
│  ○ TypeScript + React Compiler
│  ○ TypeScript + SWC
│  ○ JavaScript
│  ○ JavaScript + React Compiler
│  ○ JavaScript + SWC
│  ○ React Router v7 ↗
│  ○ TanStack Router ↗
│  ○ RedwoodSDK ↗
│  ○ RSC ↗
└
", 29 results

Created 6 todos

Gathering current frontend structure and locating Vite config to tailor Firebase Hosting and proxy setup.

Read [](file:///c%3A/Users/rjjaf/_Projects/orkhon/frontend)

Searched for files matching `**/frontend/vite.config.*`, 2 matches

Created [](file:///c%3A/Users/rjjaf/_Projects/orkhon/firebase.json)

Using "Apply Patch"


```

```


Created [](file:///c%3A/Users/rjjaf/_Projects/orkhon/.firebaserc)

Created [](file:///c%3A/Users/rjjaf/_Projects/orkhon/frontend/vite.config.ts)

Created [](file:///c%3A/Users/rjjaf/_Projects/orkhon/frontend/.env.development)

Created [](file:///c%3A/Users/rjjaf/_Projects/orkhon/frontend/.env.production)

Created [](file:///c%3A/Users/rjjaf/_Projects/orkhon/frontend/src/lib/api.ts)

Completed (1/6) *Explain target architecture and choices*

Using "Apply Patch"


```

```
You’re wiring up a Vite/React frontend and want it cleanly hosted on Firebase while talking to your ADK/Toolbox services now (and LangGraph later); I’ll set up a simple, stable pattern that works locally and in prod, and explain the “why” behind each choice.

## What “good” looks like

- Frontend: Vite + React served by Firebase Hosting (CDN, HTTP/2/3, cache).
- Backends (now and future):
  - ADK API (FastAPI) on Cloud Run (or similar container target).
  - Toolbox (MCP) on Cloud Run.
  - Future LangGraph agents on Cloud Run (same contract).
- Single origin in prod: Hosting rewrites route /api/**, /toolbox/** to the right Cloud Run services. This avoids CORS, enables secure cookies, consistent auth, and clean URLs.
- Local dev: Vite dev server proxies /api and /toolbox to localhost (ports 8000 and 5000), so your UI code doesn’t change between dev and prod.

Why this setup
- Firebase Hosting + rewrites keeps the browser talking to one origin and lets you front multiple backends without exposing raw URLs.
- Cloud Run is the best fit for Python backends (ADK) and containerized MCP servers. It scales to zero, supports CPUs/GPUs, and is easy to deploy.
- Using path-based routing (/api, /toolbox) means your UI is environment-agnostic and portable to future stacks (e.g., LangGraph services).

## Actions taken (files created)

- firebase.json at repo root: Hosting config + cache headers + SPA fallback + rewrites to Cloud Run for /api and /toolbox.
- .firebaserc at repo root: project aliases (dev/prod) to keep environments clean.
- vite.config.ts: Vite dev proxy to ADK (8000) and Toolbox (5000).
- .env.development and `.env.production`: consistent base URLs (`/api`, `/toolbox`).
- api.ts: tiny fetch helper that centralizes base URLs and auth header.

Notes:
- Replace placeholders in firebase.json with your real Cloud Run service IDs and region.
- Lint errors in the new TS files will go away after you finish scaffolding the Vite app and install dependencies.

## Files changed

- firebase.json (new): Hosting config
- .firebaserc (new): project mapping (dev/prod)
- vite.config.ts (new): dev proxy config for Vite
- .env.development (new): Vite env for dev
- .env.production (new): Vite env for prod
- api.ts (new): typed helper for API calls

## How it works

- Dev (no CORS pain): Vite proxies `/api` → `http://localhost:8000` (ADK), `/toolbox` → `http://localhost:5000` (Toolbox).
- Prod (single origin): Firebase Hosting rewrites:
  - `/api/**` → Cloud Run service `orkhon-api` (region `europe-west4` in the example)
  - `/toolbox/**` → Cloud Run service `orkhon-toolbox`
  - `**` → `index.html` (SPA fallback)
- Caching: long TTL for `assets/**` (immutable), no-cache for `index.html` (fresh deploys).

## Why these recommendations

- Stable API contract: UI always calls relative paths (`/api`, `/toolbox`). Rewrites handle environment specifics, so no code changes as you move from local → staging → prod. This scales cleanly when you introduce LangGraph services (add another rewrite like `/graph/**` → Cloud Run).
- Security: Single origin simplifies Auth (e.g., Firebase Auth/Identity Platform), cookies, and CSRF risk. You can forward bearer tokens to backends.
- Performance: Firebase CDN + immutable assets yields excellent Lighthouse scores.
- Simplicity: Avoids SSR/Functions until you actually need them; your ADK backend stays in the environment best suited for it (Cloud Run).

## What you still need to do

- Finish the Vite app scaffold in frontend (you started that flow already).
- Install frontend deps in frontend so the linting errors go away.
- Set real values in firebase.json:
  - `"site"`: your Hosting site name
  - `run.serviceId` and `region` for each backend
- Ensure your ADK/Toolbox are deployed to Cloud Run (or temporarily disable rewrites until you’re ready).
- CORS (backend): if you run backends on a different origin (only in early dev), allow `http://localhost:5173`. In prod, single origin through Hosting means you can tighten CORS.
- Auth: if you plan to use Firebase Auth, forward the ID token as `Authorization: Bearer <token>` from `api.ts` and verify it server-side (FastAPI dependency or middleware).

## Optional reference commands (PowerShell)

- Frontend dev (after `npm create vite@latest frontend -- --template react-ts`):
  - cd frontend
  - npm install
  - npm run dev
- Firebase CLI:
  - npm i -g firebase-tools
  - firebase login
  - firebase use orkhon-web-dev
  - firebase deploy --only hosting
- Cloud Run (high-level):
  - Build and deploy ADK API container -> `orkhon-api` (europe-west4)
  - Build and deploy Toolbox container -> `orkhon-toolbox` (europe-west4)
- Emulators (optional for team dev):
  - firebase emulators:start --only hosting

## A quick word on LangGraph later

- Add another backend (e.g., `orkhon-graph`) in Cloud Run, then extend firebase.json:
  - `"rewrites": [{ "source": "/graph/**", "run": { "serviceId": "orkhon-graph", "region": "europe-west4" } }]`
- In UI, call `fetch('/graph/something')`—no code changes apart from paths.
- Keep each service small and focused; let Hosting handle composition at the edge.

## Small gotcha you hit

The npm warning you saw (“Unknown cli config --template”) is from newer npm parsing, but `npm create vite@latest frontend -- --template react-ts` still works. You can also run `npm create vite@latest frontend` and pick TypeScript in the prompts (which you did).

## Done and next steps

- I created Hosting + Vite proxy config in your repo so you can keep moving without CORS headaches.
- Replace placeholders in firebase.json and finish the Vite scaffold in frontend.
- If you want, I can add a GitHub Actions workflow for Firebase Hosting deploy (dev and prod), and a small FastAPI CORS tightening for prod.

Made changes.