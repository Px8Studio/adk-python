# Cloud Deployment Guide for Orkhon

This document outlines the recommended approach for deploying Orkhon (ADK agents + Toolbox + ETL + React frontend) to Google Cloud Platform with strong separation of concerns, incremental safety, and production-ready practices.

## Target Cloud Architecture

**Core Components & Recommended GCP Services:**

1. **ADK Agent API / Orkhon Backend** (Python) → Cloud Run (container)
2. **GenAI Toolbox MCP Server** (Go + Postgres + Jaeger)
    - Phase 1: Continue locally with Docker (fast iteration)
    - Phase 2: Migrate to Cloud Run services + Cloud SQL (PostgreSQL) + Managed Jaeger
3. **Frontend** React/Vite App → Firebase Hosting (global CDN)
4. **Authentication** → Firebase Auth (OIDC tokens) or Google Identity Platform
5. **Data Lake / Warehouse** → GCS (raw/parquet) + BigQuery (curated)
6. **Secrets** → Secret Manager (API keys, Gemini/Google API key, DNB subscription key)
7. **Messaging / Async** → Pub/Sub (ETL triggers, long-running workflows)
8. **Monitoring & Tracing** → Cloud Logging, Cloud Trace, Metrics Explorer
9. **CI/CD** → Cloud Build (GitHub triggers) OR GitHub Actions with Workload Identity
10. **Artifact Storage** → Artifact Registry (Python app / Toolbox images)

## Service Topology

```
User Browser
  ↓
Firebase Hosting (HTTPS, static assets)
  ↓
/api/* → Cloud Run (ADK service)
  ↓
  ├─→ Cloud Run (Toolbox) or internal service endpoints
  ├─→ BigQuery (direct)
  ├─→ Cloud Storage (parquet staging)
  ├─→ Secret Manager (env-injected at deploy)
  ├─→ Pub/Sub (async tasks)
  ├─→ Cloud SQL (Toolbox metadata if migrated)
  └─→ External DNB APIs (with key from Secret Manager)
```

## Incremental Migration Plan (Phased)

### Phase 0: Current State
- Local dev: docker-compose for toolbox + local Python for ADK
- Manual environment management

### Phase 1: Lift ADK API
1. Add Dockerfile for ADK web server (production best practices: non-root user, slim base, health endpoint)
2. Create Cloud Run service: `orkhon-adk-dev` (region: europe-west4 or your latency target)
3. Wire service account with least-privilege:
    - Access Secret Manager (read specific secrets)
    - BigQuery Data Viewer / Job User
    - Storage Object Viewer (parquet)
4. Add CORS & `/health` endpoint
5. Deploy manually via `gcloud run deploy` → Then automate with Cloud Build trigger

### Phase 2: Frontend
1. Scaffold React/Vite app
2. Add Firebase Hosting config (`firebase.json`) with rewrite rules:
    - `/api/**` → Cloud Run service `orkhon-adk-dev`
3. Integrate Firebase Auth; issue ID tokens; attach `Authorization: Bearer <id_token>` to backend requests
4. Backend verifies with Google OIDC JWKS
5. Configure environment: `VITE_API_BASE=/api` for relative routing

### Phase 3: Toolbox Cloud Migration
1. Containerize toolbox configuration with generated tool YAML under `/config`
2. Replace local Postgres with Cloud SQL (PostgreSQL) or Firestore
3. Add OpenTelemetry exporter → Cloud Trace
4. Separate dev vs prod config using environment variable `TOOLBOX_ENV`

### Phase 4: Data / ETL
1. Convert ETL pipelines to Cloud Run jobs or Cloud Workflows / Cloud Scheduler
2. Store raw parquet in GCS `gs://orkhon-raw/` and curated in `gs://orkhon-processed/`
3. BigQuery external table or load jobs from curated layer

### Phase 5: Observability & Scale
1. Add structured logging (JSON) in ADK and toolbox containers
2. Install OpenTelemetry Python instrumentation in ADK → export to Cloud Trace
3. Add SLO dashboards (latency p95, error ratio) in Cloud Monitoring

### Phase 6: Production Hardening
1. Set min instances for warm start (ADK if latency-sensitive)
2. Add Cloud Armor policy (rate limit / IP allow if needed)
3. Enforce IAM on Cloud Run (authenticated requests only)
4. Rotate secrets automatically

## ADK Web UI vs Custom React Frontend

| Aspect | ADK Web UI (existing) | Custom React/Vite (planned) |
|--------|----------------------|---------------------------|
| **Purpose** | Developer debugging, agent iteration | Production user experience, auth, multi-tenant |
| **Auth** | None built-in | Full Firebase Auth / role-based model |
| **Extensibility** | Limited without forking ADK | Total control: dashboards, metrics, billing |
| **Risk if public** | Exposes raw agent/control surface | Enforces strict API contracts |
| **Time-to-cloud** | Very fast (containerize & deploy) | Moderate (weeks for robust UX) |

### Recommendation

1. **Deploy ADK Web UI early but restrict access (internal-only)** using one of:
    - Cloud Run with `--no-allow-unauthenticated` + IAM (developer group only)
    - Identity-Aware Proxy (IAP) in front of Cloud Run
    - Private Cloud Run + Cloud VPN / Serverless VPC Access (network isolation)

2. **Do NOT expose ADK Web UI publicly** — it lacks per-user isolation and rate limits

3. **Begin React/Vite build in parallel** once agent API stabilizes (Phase 2)

### Hardening ADK Web UI (Minimum)
Add lightweight reverse-proxy layer or FastAPI middleware that:
- Validates JWT (Firebase / Identity Platform)
- Injects `X-User-Id` into session creation calls
- Enforces per-user session scoping (namespaced session IDs)

## Authentication & Session Strategy

### Phased Auth Model

1. **Internal (Phase 1):** IAM-only Cloud Run (developers call via gcloud auth / IAP)
2. **Early external pilot (Phase 2):** Firebase Auth (OIDC); Cloud Run verifies ID tokens (JWKS). Map `sub` → `user_id`
3. **Multi-tenant (Phase 3):** Introduce `users` table (Cloud SQL or Firestore) for roles (admin, analyst, viewer). Add quota fields
4. **Advanced (Phase 4):** Usage metering & billing integration (export metrics to BigQuery)

### Session Mapping (ADK)
- Key = `user_id:session_uuid` to guarantee isolation
- Store minimal metadata (created_at, active_agents) in Redis (future) or Firestore
- Expire idle sessions automatically (cleanup job / TTL index)

## A2A Protocol Integration

The A2A (Agent-to-Agent) protocol becomes useful when:
- You need cross-domain agents (e.g., financial compliance agent calls analytics agent hosted separately)
- External partners integrate their own agent endpoints (B2B scenario)
- You want capability discovery beyond static tool definitions

**Do NOT rush A2A during initial single-tenant development.** Adopt once you have stable internal agent interactions you wish to externalize.

### A2A Adoption Phases

1. **Design Contracts:** Define allowed message types (REQUEST, RESPONSE, EVENT), security (signed tokens, optional mutual TLS)
2. **Gateway Layer:** Implement `/a2a/bridge` FastAPI router translating internal agent tasks → A2A messages
3. **Identity & Trust:** Use service accounts or signed JWTs referencing agent identity; store trusted issuer list
4. **External Agent Registration:** Admin UI to register remote agent endpoints + capabilities (persist in Firestore/Cloud SQL)
5. **Observability:** Tag traces with `a2a.remote_agent` and `a2a.message_type`
6. **Scaling:** Introduce rate limiting and circuit breakers per external agent

### a2a-inspector Role
Bring in `a2a-inspector` once Phase 2 of A2A begins:
- Run inspector in staging to visualize message flows and detect schema mismatches
- Integrate OpenTelemetry exporters to augment Cloud Trace view
- Do not deploy inspector publicly—treat it like an internal dev tool

## Component Start Timeline

| Component | Start Phase | Trigger Condition |
|-----------|-------------|-------------------|
| ADK Web UI (internal) | Phase 1 | Need cloud test & latency benchmark |
| React/Vite Frontend | Phase 2 | Defined API contract & auth decision |
| Basic Auth (Firebase) | Phase 2 | External user testing or pilot needed |
| Multi-tenant Session Model | Phase 3 | >5 external users or role differentiation |
| A2A Protocol | Phase 4 | Need remote agents / partner integration |
| a2a-inspector | Phase 4 | At least one external A2A integration in staging |
| Usage Metering / Quotas | Phase 5 | Monetization / fairness controls |

### Decision Checklist Before A2A
1. Do we have repeated cross-service calls that could become standardized agent messages?
2. Are external parties requesting direct orchestration integration?
3. Do we have secure auth & session isolation already in place?
4. Is observability mature (traces, metrics)? If not—delay A2A.

## Security & Authentication

### Approach
Firebase Auth issues ID tokens; Cloud Run validates them.

### Backend Steps
1. Enable Identity Platform or use Google public certs to verify Firebase tokens
2. Middleware verifying Authorization header using PyJWT + Google JWKS endpoint
3. Map user identity to agent session (session service key: user_id or email)
4. Provide multi-tenant isolation at session layer

### Service-to-Service Auth (Optional)
ADK ↔ Toolbox using IAM: Toolbox Cloud Run requires authenticated invocations; ADK service account granted `roles/run.invoker`

## Environment Variables & Secrets

### Secret Manager (names)
- `gemini_api_key` (projects/<id>/secrets/gemini_api_key)
- `dnb_api_key_dev`
- `bigquery_dataset` (could be plain env)
- `gcs_bucket_raw`
- `gcs_bucket_curated`

### Cloud Run Environment Wiring
```bash
--set-secrets=GEMINI_API_KEY=gemini_api_key:latest,DNB_SUBSCRIPTION_KEY_DEV=dnb_api_key_dev:latest
--update-env-vars=BIGQUERY_DATASET=orkhon_ds,GCS_BUCKET_RAW=orkhon-raw,GCS_BUCKET_CURATED=orkhon-curated
```

## CI/CD Options

### Option A: Cloud Build Triggers
GitHub push to dev branch triggers build:
1. Build & push image → Artifact Registry
2. Deploy Cloud Run service with `--allow-unauthenticated` (dev) or restricted (prod)
3. Substitute secrets via `--set-secrets`
4. Separate trigger for prod (tag push vX.Y.Z)

### Option B: GitHub Actions + Workload Identity
Reusable workflow: build, push (using `gcloud auth login --workload-identity`), deploy

## Data & ETL Patterns

### Data Layers
- **Bronze (raw parquet)** → GCS
- **Silver (cleaned)** → GCS curated prefix
- **Gold (analytics)** → BigQuery partitioned tables

### Loading Strategy
Cloud Run job (Python) triggered daily by Cloud Scheduler hitting Pub/Sub:
1. Add Dockerfile (root service, not just sample agent).  
2. Add `backend/adk/serve.py` launching ADK web + health check.  
3. Create `cloudbuild.yaml` at repo root for ADK deployment.  
4. Create `infra/terraform/` directory (optional) for declarative: Artifact Registry, Cloud Run service, secrets.  
5. Add README section `DEPLOYMENT.md` documenting build → deploy → test.  
6. Draft `firebase.json` and `.firebaserc` in frontend.

I can implement initial Dockerfile + serve.py + cloudbuild.yaml for you next if you want—just say “create deployment scaffolding” and I’ll proceed.

## Environment & Secrets Matrix

Secret Manager (names):
- gemini_api_key (projects/<id>/secrets/gemini_api_key)
- dnb_api_key_dev
- bigquery_dataset (could be plain env)
- gcs_bucket_raw
- gcs_bucket_curated

Cloud Run env wiring:
--set-secrets=GEMINI_API_KEY=gemini_api_key:latest,DNB_SUBSCRIPTION_KEY_DEV=dnb_api_key_dev:latest
--update-env-vars=BIGQUERY_DATASET=orkhon_ds,GCS_BUCKET_RAW=orkhon-raw,GCS_BUCKET_CURATED=orkhon-curated

## Risks & Mitigations

Risk: Cold start latency for LLM calls.
Mitigation: min-instances=1 + region selection + caching tool metadata.

Risk: Secret leakage in logs.
Mitigation: Redact sensitive values; never print env variables.

Risk: BigQuery costs if queries unbounded.
Mitigation: Limit row fetch in agent tools; enforce query cost guardrail (dry-run before execute).

Risk: Schema drift parquet ↔ BigQuery.
Mitigation: Maintain schema definition file; add validation step in ETL job.

## Todo List Delta

Completed: Assess backend readiness.
In Progress: Architecture proposal (this answer).
Pending: Containerization, CI/CD, frontend rewrites, secrets, migration doc.

Let me know if you’d like me to:
- Generate the Dockerfile + serve.py now
- Add cloudbuild.yaml
- Provide Terraform stubs

Just specify which, and I’ll implement directly.

## Quick Validation Commands (Optional)

```powershell
# (After Dockerfile creation)
docker build -t orkhon-adk:dev backend/adk
docker run -p 8080:8080 -e GEMINI_API_KEY=$env:GEMINI_API_KEY orkhon-adk:dev
curl http://localhost:8080/healthz
```

## Summary

You’ll run ADK on Cloud Run fronted by Firebase Hosting for the React app, with secrets managed via Secret Manager, data pipelines migrating to Cloud Run jobs + BigQuery, toolbox eventually containerized with Cloud SQL, and proper observability via OpenTelemetry. This phased approach minimizes risk and gives you production hygiene early. Ready to scaffold the deployment pieces when you say the word.

What would you like me to create first? Dockerfile + serve.py + cloudbuild.yaml, or start with Terraform skeleton?

---

## ADK Web UI vs Custom React Frontend

| Aspect | ADK Web UI (existing) | Custom React/Vite (planned) |
|--------|-----------------------|------------------------------|
| Purpose | Developer debugging, agent iteration | Production user experience, auth, multi-tenant features |
| Auth | None built-in (no user model) | Full Firebase Auth / role-based model |
| Extensibility | Limited without forking ADK | Total control: dashboards, usage metrics, billing |
| Risk if public | Exposes raw agent/control surface | Can enforce strict API contracts |
| Time-to-cloud | Very fast (containerize & deploy) | Moderate (weeks for robust UX) |

Recommendation:
1. Deploy ADK Web UI early but restrict access (internal-only) using one of:
   - Cloud Run with `--no-allow-unauthenticated` + IAM (developer group only)
   - Identity-Aware Proxy (IAP) in front of Cloud Run
   - Private Cloud Run + Cloud VPN / Serverless VPC Access (if you require network isolation)
2. Do NOT expose ADK Web UI publicly—it lacks per-user isolation and rate limits.
3. Begin React/Vite build in parallel once agent API stabilizes (Phase 2). Use the ADK Web UI as a reference for endpoints and flows.

### Hardening ADK Web UI (Minimum)
Add a lightweight reverse-proxy layer or FastAPI middleware that:
* Validates JWT (Firebase / Identity Platform)
* Injects `X-User-Id` into session creation calls
* Enforces per-user session scoping (namespaced session IDs)

If you decide to extend instead of replace, wrap the `adk web` invocation in a custom launcher that adds authentication middleware before mounting static assets.

## Authentication & Session Strategy

Phased auth model:
1. Internal (Phase 1): IAM-only Cloud Run (developers call via gcloud auth / IAP).
2. Early external pilot (Phase 2): Firebase Auth (OIDC); Cloud Run verifies ID tokens (JWKS). Map `sub` → `user_id`.
3. Multi-tenant (Phase 3): Introduce a `users` table (Cloud SQL or Firestore) for roles (admin, analyst, viewer). Add quota fields (daily tool invokes, max parallel agents).
4. Advanced (Phase 4): Usage metering & billing integration (export metrics to BigQuery; scheduled aggregation job; dashboard in React).

Session Mapping (ADK):
* Key = `user_id:session_uuid` to guarantee isolation.
* Store minimal metadata (created_at, active_agents) in Redis (future) or Firestore.
* Expire idle sessions automatically (cleanup job / TTL index).

## Introducing A2A Protocol (a2a-python)

The A2A (Agent-to-Agent) protocol becomes useful when:
* You need **cross-domain agents** (e.g., financial compliance agent calls analytics agent hosted separately).
* External partners integrate their own agent endpoints (third-party or B2B scenario).
* You want **capability discovery** beyond static tool definitions.

Do NOT rush A2A during initial single-tenant development; adopt once you have stable internal agent interactions you wish to externalize.

### A2A Adoption Phases
1. Design Contracts: Define allowed message types (REQUEST, RESPONSE, EVENT), security (signed tokens, optional mutual TLS).
2. Gateway Layer: Implement small `/a2a/bridge` FastAPI router in your ADK service translating internal agent tasks → A2A messages.
3. Identity & Trust: Use service accounts or signed JSON Web Tokens referencing agent identity; store trusted issuer list.
4. External Agent Registration: Admin UI to register remote agent endpoints + capabilities (persist in Firestore/Cloud SQL).
5. Observability: Tag traces with `a2a.remote_agent` and `a2a.message_type`.
6. Scaling: Introduce rate limiting and circuit breakers per external agent.

### a2a-inspector Role
Bring in the `a2a-inspector` once Phase 2 of A2A begins:
* Run inspector in staging to visualize message flows and detect schema mismatches.
* Integrate OpenTelemetry exporters so inspector augments your Cloud Trace view.
* Do not deploy inspector publicly—treat it like an internal dev tool similar to ADK Web UI.

## When to Start Each Component

| Component | Start Phase | Trigger Condition |
|-----------|-------------|-------------------|
| ADK Web UI (internal) | Phase 1 | Need quick cloud test & agent latency benchmark |
| React/Vite Frontend | Phase 2 | Defined API contract & initial auth decision |
| Basic Auth (Firebase) | Phase 2 | External user testing or pilot needed |
| Multi-tenant Session Model | Phase 3 | >5 external users or role differentiation |
| A2A Protocol | Phase 4 | Need remote agents / partner integration |
| a2a-inspector | Phase 4 | At least one external A2A integration in staging |
| Usage Metering / Quotas | Phase 5 | Monetization / fairness controls |

## Decision Checklist Before A2A
1. Do we have repeated cross-service calls that could become standardized agent messages?
2. Are any external parties requesting direct orchestration integration?
3. Do we have secure auth & session isolation already in place?
4. Is observability mature (traces, metrics)? If not—delay A2A.

## Minimal Implementation Examples (Conceptual)

FastAPI Auth Middleware (concept sketch):
```python
from fastapi import Request, HTTPException
import httpx, jwt

JWKS_URL = "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com"

class FirebaseAuthMiddleware:
  def __init__(self):
    self.jwks = httpx.get(JWKS_URL).json()
  async def __call__(self, request: Request, call_next):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
      raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ",1)[1]
    # (Resolve key, verify signature, audience, issuer)
    payload = jwt.decode(token, options={"verify_aud": False}, algorithms=["RS256"], key=self._resolve_key(token))
    request.state.user_id = payload.get("sub")
    return await call_next(request)
```

Internal A2A Bridge Handler (pseudo):
```python
@router.post("/a2a/bridge")
async def bridge(msg: A2AMessage):
  # Validate signature & remote agent trust
  # Translate A2A payload to internal agent invocation
  result = runner.invoke_agent(msg.target_agent, msg.payload)
  return A2AResponse(correlation_id=msg.correlation_id, data=result)
```

## Risks of Using ADK Web UI as Public Interface
* No builtin rate limiting → possible cost runaways (LLM calls).
* Sessions not isolated per user by default → data leakage risk.
* Lacks production-grade instrumentation for multi-tenant auditing.

Mitigation: Keep it internal, start custom frontend early for anything user-facing.

## Next Concrete Actions (If You Agree)
1. Mark ADK Web UI for internal Cloud Run deployment now (internal-only).
2. Add auth middleware skeleton (even before React) to future-proof.
3. Begin React scaffold (`frontend/`) with API boundary layer (typed client + error handling).
4. Defer A2A until at least 2 internal domains argue for externalization.
5. Schedule observability uplift before A2A (traces + structured logs).

---

Searched codebase for "#codebase do you think we could start with deploying the already existing adk web ui as the appp interface? thinking forward where we will want to have user authentication, management etc.. will we be able to already make use of such thing or not? and what about the a2a-python and ui tool inspector, are these for later add ons, or should we already start setting these up as wlel and integrating? when do we actuall start with integrating the a2a protocol? how would that translate to our app context of orkhon?", 26 results

Adding tasks to cover ADK Web UI deployment evaluation, auth strategy, and A2A integration, then checking for cloud_deploy.md so I can document phased plan.

Completed (2/11) *Propose target GCP architecture*

I'm going to open the cloud deployment documentation file to see if it exists and what it contains so I can update it with a phased plan for ADK Web UI, auth, and A2A integration.

Read [](file:///c%3A/Users/rjjaf/_Projects/orkhon/docs/cloud_deploy.md)

Using "Apply Patch"


```

```
Good call—let’s make this practical. We’ll use the existing ADK Web UI as an internal, developer-facing console now, while we build a proper React/Vite app for end users. I’ve added concrete guidance and a phased plan directly into cloud_deploy.md so you’ve got a living playbook in-repo.

Here’s the short version, tailored to Orkhon.

## Should we deploy the ADK Web UI as the app interface?

- Yes, but only as an internal tool. It’s perfect for agent development and debugging, but it’s not designed for public, multi-tenant use.
- Put it behind Cloud Run with restricted access:
  - Cloud Run “authenticated invocations only” with IAM (dev group only), or
  - Identity-Aware Proxy (IAP), or
  - Private Cloud Run exposed only over VPN if you want stricter isolation.
- Don’t expose it to the public internet as-is. There’s no built-in user model, rate limits, or multi-tenant isolation.

What it’s great for now:
- Iterating on ADK agents and tools.
- Testing new flows and verifying LLM/tool performance in the cloud environment.

What it’s not for:
- End-user UI, multi-tenant usage, account management, or billing.

## What about authentication and user management?

- Near-term (Phase 1): Keep ADK Web UI internal-only, protected by IAM/IAP. No user management needed yet.
- Public app (Phase 2): Use Firebase Auth (OIDC). Your React/Vite app will obtain an ID token and forward it to your Cloud Run backend. The backend verifies it using Google JWKS and maps sub → user_id. That’s your session isolation key.
- Multi-tenant (Phase 3): Add roles and quotas in a small users table (Firestore or Cloud SQL), and scope sessions by user_id in your agent/session layer.

Tip: Even before the React app, add a thin auth middleware to your backend API so you’re ready to accept Firebase tokens later without refactoring.

## A2A (a2a-python) and a2a-inspector—when and how?

- Don’t rush A2A for the first cut. Introduce it when:
  - You need cross-domain agents (e.g., external partner’s agent, or separate analytical agent cluster).
  - You want capability discovery and standardized remote agent messaging.
- Translate to Orkhon:
  - Implement a small “A2A bridge” endpoint in your ADK backend later that converts A2A messages into internal agent invocations.
  - Use signed JWTs or service accounts for trust; keep a registry of trusted remote agents (Firestore/Cloud SQL).
- a2a-inspector is an internal dev tool. Start using it in staging once you wire your first external A2A integration; it’s not meant for end users.

## What to do now vs later

Now (Phase 1):
- Deploy ADK Web UI to Cloud Run as internal-only (IAM/IAP).
- Keep Toolbox local for dev iteration, or begin planning a move to Cloud Run + Cloud SQL.
- Add a minimal health endpoint and prepare a basic auth middleware skeleton (even if it’s only used later).
- Define secrets in Secret Manager (GEMINI_API_KEY, DNB key, etc.).

Next (Phase 2):
- Start the React/Vite app hosted on Firebase.
- Configure Firebase Hosting rewrites to proxy /api to Cloud Run.
- Implement Firebase Auth in the frontend and token verification in the backend.

Later (Phase 3+):
- Introduce multi-tenant sessions, quotas, and usage logging.
- Migrate Toolbox to Cloud Run with Cloud SQL + OpenTelemetry to Cloud Trace.
- Adopt A2A when you have real cross-agent or partner integrations.

## Actions taken

- I expanded cloud_deploy.md with:
  - A clear decision framework: ADK Web UI vs React/Vite app
  - Auth & session strategy (IAM/IAP → Firebase Auth → multi-tenant)
  - A2A adoption phases and how it maps to Orkhon (including the role of a2a-inspector)
  - Risks of using ADK Web UI publicly and mitigations
  - Concrete next steps checklist

## What’s next (pick one and I’ll implement)

- Create deployment scaffolding for ADK Web UI to Cloud Run (Dockerfile + serve.py health check + cloudbuild.yaml).
- Add a minimal auth middleware to the backend to verify Firebase tokens (kept disabled until frontend is ready).
- Scaffold the React/Vite frontend with Firebase Hosting config (rewrites to Cloud Run) and Firebase Auth.

Todo status update
- Completed: Architecture proposal
- Completed: Evaluated ADK Web UI as interim interface (documented in docs/cloud_deploy.md)
- Pending: Containerize ADK backend, CI/CD, frontend rewrites, secrets wiring, step-by-step migration

Tell me which artifact you want me to create first, and I’ll add the files and wire them up.

Made changes.