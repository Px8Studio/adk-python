# Why Agentic AI at DNB – Management Brief

Purpose: Recommend adoption of agentic AI aligned with Microsoft-first strategy; outline value, risks, and 90‑day path to pilots.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics.

## Executive Summary

- Agentic AI operationalizes multi-step supervisory and data tasks with auditability.
- Azure AI Foundry, Microsoft Agent Framework (preview), GitHub Copilot, Entra ID, Managed Identities, Key Vault, and Content Safety provide required foundation.
- Pilot use cases show 30–60% productivity improvement in supervision research, cross‑system lookups, and reporting prep.
- Initial deployment should focus on Insurance & Pension domain with governed expansion path.

## What Is Agentic AI and Why It Matters

- Definition: An agent is a governed software component using LLM reasoning to plan, invoke tools/APIs, and coordinate tasks.
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

- Moves from model-centric testing to full path validation (intent → plan → tool executions → output).
- Foundry evaluation (groundedness, relevance) plus Content Safety gating precede sensitive actions.
- Identity: Entra ID + Managed Identities across all calls; unified telemetry in App Insights / Log Analytics.

## Microsoft-First Architecture Enablers

- Azure AI Foundry: Prompt Flow orchestration, evaluation, versioning, governed deployment.
- Microsoft Agent Framework (preview): Planning, memory, multi-agent composition.
- Models: GitHub Copilot primary; Azure OpenAI fallback for large-context tasks.
- Security: Entra ID, Managed Identities, Content Safety, private networking, CMK encryption.
- Data Integration: Fabric Lakehouse/Warehouse and Power BI for analytics-driven automation.

## Agent Catalog (Initial Focus: Insurance & Pension)

- Root Orchestrator: Entry, routing, policy enforcement.
- Coordinators: Internal Services; External Regulatory; Data & Analytics.
- Specialists: DataLoop, MEGA, ATM; Taxonomy (EIOPA RAG); Statistics; Public Registers; Analytics-to-Brief; Document Ingestion; API Concierge; Entity Resolution; Case Triage; Compliance Guard.
- Guardrails: Identity, safety filters, evaluation gates, centralized tracing.

## Representative Use Cases

1) Supervision Report Status Assistant – Consolidate status + validation notes with sources.  
2) Taxonomy Agent – Detect taxonomy deltas, propose mapping changes.  
3) Policy & Market Intelligence – Macro trends + cited data.  
4) Internal API Concierge – Locate authoritative endpoints and auth method.  
5) Analytics-to-Brief – Summarize material dashboard shifts.  
6) Entity Resolution – Canonical ID with confidence + lineage.  
7) Case Triage – Classify, enrich, and route with audit metadata.  

All responses are source-grounded; human review for sensitive outputs.

## Business Value & KPIs

- Productivity: 30–60% cycle time reduction.
- Quality: Cited, policy-aligned outputs.
- Responsiveness: Faster supervisory insight generation.
- Analyst Leverage: Shift from data collection to judgment.

KPIs:
- Task cycle time delta (baseline vs pilot).
- Groundedness/citation score ≥0.8 (Foundry eval).
- Manual correction rate <10% after week 8.
- User CSAT ≥4.2/5.

## Risks & Mitigations

- Incorrect actions: Tool-first prompting, verification steps, evaluation gating, HITL for sensitive flows.
- Data leakage / PII: Content Safety, redaction, private networking, no model training on DNB data.
- Access control gaps: Entra ID RBAC, Managed Identities, least privilege database roles.
- Framework/model drift: Versioned flows, canary deploy, telemetry anomaly alerts.

## Readiness Checklist (Pre-Build)

- Outcome & decision rights (advisory vs action; HITL points).
- Authoritative data sources / joins / freshness.
- Identity scopes and residency constraints.
- Safety classification, PII handling, retention.
- Grounding sources and acceptable error thresholds.
- Audit scope, retention period, review cadence.
- Volume, SLO, concurrency, cost envelope.
- Deployment channel (Teams/web) and change management.
- Reusable tool/connectors and standard patterns.

## References

- Azure AI Foundry (Prompt Flow, evaluation, deployment).
- Microsoft Agent Framework (preview).
- Compliance: GDPR, NIS2, DORA via identity, safety, encryption, private networking.

