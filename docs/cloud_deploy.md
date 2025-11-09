# Orkhon Cloud Architecture and Agent Strategy (Unified Guide)

This single document is the authoritative playbook for Orkhon’s multi‑agent platform: cloud architecture, deployment practices, and the curated set of ADK sample agents we’ll build on. It’s written to be actionable, production‑minded, and compatible with adding non‑ADK agents (LangChain/LangGraph) later.

## What we’re building

- Backend: Python ADK service on Cloud Run (multi‑agent orchestration, tools, sessions)
- Toolbox: GenAI Toolbox MCP server (dev: local Docker; prod: Cloud Run + Cloud SQL)
- Frontend: React + Vite hosted on Firebase Hosting (public UI)
- Auth: Firebase Auth (OIDC) → ID token verified by Cloud Run backend
- Data: BigQuery + GCS (curated and raw)
- Secrets: Secret Manager → injected at deploy
- Observability: Cloud Logging + Cloud Trace (OpenTelemetry), optional Jaeger locally

Service topology:
```
Browser (Firebase Hosting)
  → /api/* → Cloud Run (ADK backend)
      ├─→ Cloud Run (Toolbox) / internal services
      ├─→ BigQuery / GCS
      ├─→ Secret Manager
      ├─→ Pub/Sub (optional)
      └─→ External APIs (DNB, etc.)
```

---
## Core agents to adopt first (foundation)

We’ll start with a focused set that covers analytics, verification, retrieval, ops, safety, and research flows. Treat each as a persona integrated into the Orkhon backend, not as standalone public UIs.

| Agent | Role | Why it’s in | Patterns to reuse |
|------|------|-------------|-------------------|
| Data Science (multi‑agent) | NL2SQL, analytics, BQML | Mature orchestration; cross‑dataset config; code+SQL blend | Dataset config JSON; DB/BQML/DS sub‑agents |
| MLE‑STAR | Automated ML refinement | Iterative targeted code block refinement + search | Inner/outer loops; isolated workspace |
| LLM Auditor | Fact checking & compliance | Lightweight critic/reviser pipeline | Post‑generation audit step |
| RAG (Docs Retrieval) | Internal knowledge grounding | Clean retrieval with citations | Retrieval gating; tool‑use expectations |
| Software Bug Assistant | Internal ops triage | DB + MCP + search + ext sources | MCP toolbox integration; mixed routing |
| Safety Plugins | Global guardrails | Hooks on user/tool/model | Runner‑level plugins; policy surface |
| Gemini Fullstack | Research + HITL planning | Plan→Approve→Iterate→Compose | Workflow graph; components reused in backend |

Secondary/later: Customer Service (multimodal), Data Engineering (Dataform focus), Incident/Order Processing (Application Integration), Real‑Time Conversational.

---
## Where Gemini Fullstack fits (clarification)

Gemini Fullstack is a blueprint for a research workflow with a React frontend and an ADK/FastAPI backend. It’s not a requirement to be your primary user interface. Use it in two ways:

1) Backend capability (recommended now): import its planning/research/critique/compose agents into Orkhon as a “Research & Synthesis” persona. Expose via our Orkhon API; keep ADK Web UI internal for dev only.

2) Frontend reference (optional later): borrow UI patterns (timeline, HITL plan approval) for the Orkhon React app on Firebase. Don’t deploy its separate frontend alongside ours unless there’s a compelling reason.

No conflict with ADK Web UI: the ADK Web UI remains an internal developer console; Gemini Fullstack’s frontend is a sample app. Our public UI is the Orkhon React app on Firebase.

Practical guidance:
- Treat Gemini Fullstack’s backend agents as a module; register them in our agent registry.
- Migrate only UI pieces we want (plan approval, research timeline) into our Firebase app.
- Keep a single public frontend to avoid fragmented UX.

---
## Phased plan (execution order)

Phase 0.1 – Agent inventory & registry
- Create `docs/agents_inventory.md` with names, roles, env vars, maturity.
- Adopt single‑service packaging initially (one Cloud Run service hosting multiple agents).

Phase 1 – Lift ADK backend to Cloud Run (internal auth only)
- Containerize backend (non‑root, slim base, `/healthz`).
- Cloud Run `orkhon-adk-dev` with IAM/IAP; inject secrets from Secret Manager.
- Enable BigQuery/Storage access; add CORS.

Phase 2 – Public frontend on Firebase Hosting
- Build Orkhon React/Vite app; wire Firebase Auth.
- Hosting rewrites `/api/** → Cloud Run`.
- Backend verifies OIDC tokens (Google JWKS) and maps `sub → user_id`.

Phase 3 – Toolbox to Cloud Run
- Containerize Toolbox with `/config/tools.yaml` from Secret Manager.
- Use Cloud SQL Postgres where needed; add OTEL exporter → Cloud Trace.

Phase 4 – Observability & scale
- Structured JSON logs; OTEL for spans (tool calls, LLM calls, agent steps).
- SLO dashboards (p95 latency, error ratio) and basic rate limits.

Phase 5 – Hardening & multi‑tenant
- Namespaced sessions `user_id:session_uuid` with TTL cleanup.
- Quotas per user; usage metering exported to BigQuery.
- Optional: Cloud Armor for rate limiting/IP policies.

Phase 6 – A2A (later, when needed)
- Add `/a2a/bridge` for trusted external agents; signed JWTs; registry.
- Use `a2a-inspector` in staging only.

---
## Packaging & registry (multi‑agent)

- Start with one container hosting multiple agents; expose agent IDs via a registry endpoint. Keep heavy persona candidates listed for future isolation (second Cloud Run service) based on load.
- Directory convention: each agent folder must contain `__init__.py` importing `.agent` and an `agent.py` with `root_agent` or `app`.

---
## Auth, sessions, and safety

- Public UX: Firebase Auth; Cloud Run verifies tokens → `user_id` scoping.
- Session key format: `user_id:session_uuid` with per‑user isolation.
- Global safety: enable Safety Plugins at Runner level across hooks (user message, before/after tool, model output).
- LLM Auditor as a post‑generation audit where required; can rewrite responses.

---
## Data and costs

- Guardrails on BigQuery: limit row counts, use dry‑run estimates, and cache NL2SQL schema context.
- Separate compute vs storage projects if needed; prefer curated datasets for agent access.

---
## Observability

- Emit spans for: routing decisions, tool calls (name, duration, status), LLM calls (model, tokens, latency), and sub‑agent boundaries.
- Redact sensitive values; include correlation IDs across services.

---
## CI/CD

- Either Cloud Build triggers or GitHub Actions (Workload Identity):
  1) Lint/tests → 2) Build/push to Artifact Registry → 3) Deploy Cloud Run with `--set-secrets`.
- Separate dev/prod triggers; tags drive prod deploys.

---
## Environment & secrets

Secret Manager names (examples):
- `gemini_api_key`, `dnb_api_key_dev`
- `bigquery_dataset` (or plain env)
- `gcs_bucket_raw`, `gcs_bucket_curated`

Cloud Run flags (concept):
```
--set-secrets=GEMINI_API_KEY=gemini_api_key:latest,DNB_SUBSCRIPTION_KEY_DEV=dnb_api_key_dev:latest
--update-env-vars=BIGQUERY_DATASET=orkhon_ds,GCS_BUCKET_RAW=orkhon-raw,GCS_BUCKET_CURATED=orkhon-curated
```

---
## Risks & mitigations

- Cold starts → `min-instances=1` for latency‑sensitive services; pick region close to users.
- Secret leakage → strict redaction in logs; never print env values.
- BigQuery cost runaways → query limits, dry‑run budgeting, and caching.
- Schema drift parquet↔BQ → schema validation gate in ETL.

---
## How we’ll integrate the core agents (playbook)

1) Data Science: point to Orkhon datasets; remove sample loaders; enforce cost guards; log structured outputs.
2) MLE‑STAR: sandbox code execution; limit web search; cache results.
3) LLM Auditor: wire as post‑processing step; add policy taxonomy labels.
4) RAG: point to internal corpus; unify citation format; add freshness score.
5) Software Bug Assistant: map to Orkhon incident schema; secure MCP with IAM; consider vector search over logs.
6) Safety Plugins: enable globally; track blocked/allowed metrics.
7) Gemini Fullstack: register planner/research/critic/composer as a single persona; optionally reuse timeline UI patterns in our React app.

---
## Quick start checklist (operator view)

- [ ] Cloud project + Artifact Registry + Secret Manager
- [ ] Dockerize ADK backend (health, non‑root)
- [ ] Cloud Run deploy (internal) + IAM/IAP
- [ ] Firebase Hosting app with Auth; rewrites to `/api` (Cloud Run)
- [ ] Enable Safety Plugins; add LLM Auditor where needed
- [ ] Wire OTEL tracing; basic dashboards
- [ ] Plan Toolbox migration to Cloud Run + Cloud SQL

---
## FAQ: Gemini Fullstack vs ADK Web UI vs Orkhon React

- Is Gemini Fullstack “the interface”? No. It’s a sample fullstack app. Our interface is the Orkhon React app on Firebase.
- Will it conflict with ADK Web UI? No—ADK Web UI is an internal dev console only.
- Why integrate Gemini Fullstack at all? To reuse its backend workflow (plan→approve→iterate→compose) and optionally its UI patterns. It accelerates “research‑grade” flows.
- Can we deploy Gemini Fullstack as‑is? You could, but it fragments UX. Prefer importing its capabilities into Orkhon’s single frontend and backend.

---
## Next actions (you can ask me to implement any of these)

1) Create deployment scaffolding (Dockerfile + serve.py + cloudbuild.yaml)
2) Add auth middleware skeleton (Firebase OIDC verification)
3) Register Data Science + LLM Auditor + RAG personas in backend
4) Add Safety Plugins at Runner level
5) Extract Gemini Fullstack backend agents and register as a “Research & Synthesis” persona
6) Bootstrap Firebase app sections (timeline UI, evaluation harness page)

This doc supersedes separate “cloud_deploy.md” and “agents_recommendations.md” split guidance.