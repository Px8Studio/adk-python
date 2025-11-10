# Why Agentic AI at DNB – Management Brief

Purpose: Recommend adoption of agentic AI aligned with Microsoft-first strategy; outline value, risks, and 90‑day path to pilots.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics.

## Executive Summary

- Agentic AI reduces cycle time and handoffs for supervisory and data tasks with full auditability.
- Start simple: launch a Database Agent pilot that lets non‑technical users query governed data in natural language; then expand to a full multi‑agent system.
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

## Phased Rollout (90 Days)

- Weeks 1–2: Align scope, success metrics, and priority datasets; enable access and governance.
- Weeks 3–6: Pilot Database Agent in Teams; measure time‑to‑answer and quality; collect feedback.
- Weeks 7–10: Add routing to internal services and simple specialists; expand coverage to top use cases.
- Weeks 11–12: Preview Validation Specialist (advisory only); define change control path.

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

