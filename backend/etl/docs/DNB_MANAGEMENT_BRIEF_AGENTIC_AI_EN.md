# Why Agentic AI at DNB – Management Brief

Purpose: Recommend adoption of agentic AI aligned with Microsoft-first strategy; outline value, risks, and fit for DNB, with an initial focus on Insurance and Pension funds.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics.

## Executive Summary

- Agentic AI reduces cycle time and handoffs for supervisory and data tasks with full auditability.
- An initial high-value use case is a Database Agent that lets non‑technical users query governed data in natural language; this can expand into a multi‑agent system as needs mature.
- Works in familiar channels (Teams/Copilot) with enterprise identity, safety, and governance.
- Expected outcomes: faster answers, higher-quality, cited outputs, and better analyst leverage.

## What Is Agentic AI and Why It Matters

- Definition: An agent is a governed software component using large language
  model (LLM) reasoning to plan, invoke tools/APIs, and coordinate tasks.
- Maturity: Microsoft Agent Framework integrates planning (Semantic Kernel) and multi‑agent patterns (AutoGen).
- Fit: Supervisory workflows (cross-database reconciliation, regulatory change impact, document analysis) require tool use plus policy controls.
- Platform: Azure AI Foundry supplies orchestration, evaluation, deployment, identity integration.

### Component-Level vs System-Level

- AI agent (single actor): Bounded task, minimal planning, local state.
- Agentic AI (system): Goal-driven orchestration, branching, retries, verification, shared session state, centralized policies.
- Example difference:
  - Single agent: “Query DataLoop for report X.”
  - System: “Compare FI X status across DataLoop/MEGA/ATM, reconcile differences, draft cited brief.”

### Governance Shift

- Moves from model-centric testing to full path validation (intent → plan →
  tool executions → output).
- Foundry evaluation (groundedness, relevance) plus Content Safety gating
  precede sensitive actions.
- Identity: Azure Entra ID + Managed Identities across all calls; unified
  telemetry in Application Insights (App Insights) and Azure Log Analytics.

## Microsoft-First Architecture Enablers

- Secure-by-default identity and access (single sign-on, role-based access).
- Safety and governance controls (content safety, logging, approvals).
- Integration with productivity tools (Teams/Copilot) for fast adoption.
- Reuse existing, governed data sources and dashboards (no new platforms required at pilot).

## Agent Catalog (Initial Focus: Insurance & Pension)

- Root Orchestrator: Entry, routing, policy enforcement.
- Coordinators: Internal Services; External Regulatory; Data & Analytics.
- Database Agent (New): Conversational access to governed datasets for non‑technical users; turns natural language into safe, approved queries and returns cited answers.
- Specialists: DataLoop, MEGA, ATM; Taxonomy (EIOPA RAG); Statistics; Public Registers; Analytics‑to‑Brief; Document Ingestion; API Concierge; Entity Resolution; Case Triage; Compliance Guard.
- Validation Specialist: Explains validation logic; assists natural‑language authoring and review of new rules with change control (positioned for later phase).
- Guardrails: Identity, safety filters, evaluation gates, centralized tracing.

## Representative Use Cases

1) Supervision Report Status Assistant – Consolidate status + validation notes with sources.  
2) Taxonomy Agent – Detect taxonomy deltas, propose mapping changes.  
3) Policy & Market Intelligence – Macro trends + cited data.  
4) Internal API Concierge – Locate authoritative endpoints and auth method.  
5) Analytics‑to‑Brief – Summarize material dashboard shifts.  
6) Entity Resolution – Canonical ID with confidence + lineage.  
7) Case Triage – Classify, enrich, and route with audit metadata.  
8) Database Q&A (New) – Ask questions in natural language and get cited answers from governed datasets without writing SQL.  
9) Validation Authoring & Coverage (Later) – NL→Validation authoring, proposal and review with change control.

All responses are source‑grounded; human‑in‑the‑loop (HITL) for sensitive outputs.

## Business Value and Key Performance Indicators (KPIs)

- Productivity: 30–60% cycle time reduction on targeted tasks.
- Quality: Cited, policy‑aligned outputs.
- Adoption: Weekly active users and repeat usage in Teams/Copilot.
- Satisfaction: CSAT ≥4.2/5.

KPIs:
- Time‑to‑answer vs baseline (by use case).
- Citation/grounding rate ≥0.8 (sampled reviews).
- Manual correction rate <10% after week 8.
- Analyst hours shifted from collection to judgment.

## Risks & Mitigations

- Incorrect actions: Tool‑first prompting, verification steps, HITL for sensitive flows.
- Data leakage / PII: Safety gating, redaction, private networking, no training on DNB data.
- Access control gaps: Role‑based access, least privilege, approvals.
- Drift: Versioned flows, canary rollout, telemetry and feedback loops.

## Readiness Checklist (Pre-Build)

- Clear outcomes and decision rights (advisory vs action; HITL points).
- Authoritative data sources, freshness, and citation expectations.
- Identity scopes, residency, and retention.
- Safety classification, PII handling, audit scope and review cadence.
- Channels and change management (Teams/Copilot, ACA), cost envelope.
- Reusable patterns and governance (approvals, logging, rollout gates).

## References

- Azure AI Foundry (orchestration, evaluation, deployment).
- Microsoft Copilot (end‑user channel).
- Governance: GDPR, NIS2, DORA via identity, safety, encryption, and audit.

## Open Questions for DNB Architecture and Operations

- Organization & Collaboration
  - Central ownership: Which central team leads Agentic AI (sponsor,
    product/owner, platform)? Where does it sit organizationally?
  - Collaboration model: How do we work with supervision domains and IT
    (cadence, working agreements, Teams channel, decision forum)?
  - Roles and staffing (pilot → scale): Which roles are needed and at what
    allocation? (Product Owner, Solution Architect, Agent Engineer(s),
    Data Engineer, Tool/API owner(s), Security, Compliance/Privacy,
    Platform/DevOps, Evaluator/QA, Change & Adoption lead,
    Legal/Procurement liaison).
  - Capacity & timeline (indicative): Discovery 2–3 weeks; pilot build 6–8
    weeks; hardening/deployment 2 weeks. Typical availability per role:
    PO 0.3–0.5 FTE; Eng 2–3 FTE; Data Eng 0.5–1 FTE; Security/Compliance
    0.2 FTE each; Evaluator 0.3 FTE.
  - Artifacts: RACI, roadmap/backlog, Definition of Done/acceptance criteria,
    decision log, risk/mitigation register.
  - Ways of working: PR‑based change control, weekly demos, design reviews,
    incident/DR exercises.

- Identity & Access
  - How will agents authenticate to Azure SQL/PostgreSQL (Managed Identity vs user-delegated tokens)? Do we need per-user attribution in downstream query audit trails?
  - What RBAC roles are required per agent and per tool? How will least privilege be enforced and reviewed?
  - How will cross-tenant or guest access be handled, if needed, for inter-agency collaboration?

- Data Residency, Retention, and Privacy
  - Confirm EU region(s), customer-managed keys (CMK), and encryption posture for all services (Cosmos DB, Log Analytics, AI services).
  - What retention and deletion policies apply to chats, event logs, artifacts, and intermediate data? How will PII redaction be applied to logs?

- Networking & Connectivity
  - Which services require private endpoints/VNet integration (ACA, databases, Key Vault, OpenAI endpoints)? Any egress restrictions or proxy requirements?
  - DNS, firewall rules, and IP allowlists for internal APIs and databases.

- Secrets, Keys, and Credentials
  - Can we operate fully with Managed Identities, or are any secrets required? How will rotation and access reviews be enforced via Key Vault?

- Safety & Compliance
  - What Content Safety thresholds (PII, jailbreak, hate/abuse) should gate tool execution? Where are human-in-the-loop approvals required?
  - How do we record safety decisions without storing sensitive payloads?

- Observability & Audit
  - What App Insights/Log Analytics schema, sampling, and correlation IDs will we adopt for end-to-end tracing (user → agent → tool → DB/API)?
  - Which KQL queries and dashboards are needed for security investigations and compliance reporting?

- Models & Orchestration
  - Baseline model choice (Azure OpenAI GPT-4/Copilot) and fallbacks. What evaluation metrics (groundedness, relevance) define acceptable quality?
  - Criteria for selecting Prompt Flow vs Semantic Kernel for specific agents. How will versions and rollouts be controlled?

- Tools & Internal APIs
  - Inventory of authoritative APIs with OpenAPI specs. Are rate limits, pagination, and error contracts consistent?
  - How will tool schemas (inputs/outputs) be standardized and reused across agents?

- Databases & Data Warehouse
  - Catalog of governed datasets (DataLoop, MEGA, ATM, Synapse/Fabric). What row-level security and masking policies apply?
  - Do we need query cost controls, caching, or synthesized datasets for evaluations/smoke tests?

- Teams/Copilot Integration
  - Which channels (Teams bot, message extensions, Copilot plugins) are in scope? How will user identity and authorization be enforced per request?

- Agent-to-Agent (A2A) Interactions
  - Do we need A2A now or later? What is the agent card format, registry location, and auth model for cross-department calls?
  - How will we audit and rate-limit cross-org calls?

- Cost & Operations
  - Cost attribution tags, budgets, and alerts. Expected concurrency, autoscaling thresholds, and cold start mitigation for ACA.
  - Quota management for model and data services.

- Change Management & Governance
  - PR-based change control for prompts, tools, and flows; required reviewers; canary and rollback strategies.
  - Incident response runbooks, DR strategy (RTO/RPO), and backup/restore coverage.

- Legal & Procurement
  - Data Processing Agreements and EU data boundary requirements for model providers.
  - Licensing constraints for connectors, SDKs, and any third-party components.

