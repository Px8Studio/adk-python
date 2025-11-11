# Why We're Recommending Agentic AI at DNB – Management Brief

Purpose: We're recommending the adoption of agentic AI aligned with our Microsoft-first strategy. This brief outlines the value we see, the risks we've identified, and how it fits DNB's needs, with our initial focus on Insurance and Pension funds.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics teams.

## Executive Summary

- We believe agentic AI will reduce cycle time and handoffs for our supervisory and data tasks while maintaining full auditability.
- Our initial high-value use case is a Database Agent that lets non‑technical users query governed data in natural language. We can expand this into a multi‑agent system as our needs mature.
- We'll work in familiar channels (Teams/Copilot) with enterprise identity, safety, and governance baked in.
- We expect: faster answers, higher-quality cited outputs, and better leverage of our analyst time.

## What Is Agentic AI and Why We Think It Matters

- Definition: We define an agent as a governed software component using large language model (LLM) reasoning to plan, invoke tools/APIs, and coordinate tasks.
- Maturity: Microsoft's Agent Framework integrates planning (Semantic Kernel) and multi‑agent patterns (AutoGen), which we can leverage.
- Fit: Our supervisory workflows (cross-database reconciliation, regulatory change impact, document analysis) require tool use plus policy controls—exactly what agentic AI provides.
- Platform: We'll use Azure AI Foundry for orchestration, evaluation, deployment, and identity integration.
- Multi‑agent system: When we have multiple agents working together autonomously, each independently responsible for a specific focus area, we create a multi‑agent system that can handle our larger organizational purposes.

### Component-Level vs System-Level

- AI agent (single actor): We use this for bounded tasks with minimal planning and local state.
- Agentic AI (system): We're building this for goal-driven orchestration with branching, retries, verification, shared session state, and centralized policies. This becomes our multi‑agent system.
- Example difference we see:
  - Single agent: "Query DataLoop for report X."
  - System: "Compare FI X status across DataLoop/MEGA/ATM, reconcile differences, draft cited brief for us."

### Governance Shift We're Making

- We're moving from model-centric testing to full path validation (intent → plan → tool executions → output).
- We'll use Foundry evaluation (groundedness, relevance) plus Content Safety gating before any sensitive actions.
- Identity: We're implementing Azure Entra ID + Managed Identities across all calls, with unified telemetry in Application Insights and Azure Log Analytics.

## Why We're Building on Microsoft-First Architecture

- We get secure-by-default identity and access (single sign-on, role-based access).
- We inherit safety and governance controls (content safety, logging, approvals).
- We integrate with our existing productivity tools (Teams/Copilot) for fast adoption.
- We reuse our existing, governed data sources and dashboards (no new platforms required for our pilot).

## Why We Chose Azure AI Foundry Over Copilot Studio

- TL;DR: We're using Copilot Studio for lightweight, M365-first experiences and citizen-development. We're using Azure AI Foundry for our governed, multi-agent, tool-heavy backends that require private networking, managed identity, evaluation gates, and CI/CD.

Key differences we considered:
- Scope and target:
  - Copilot Studio: Rapid M365-centric copilots that we could build quickly.
  - AI Foundry: Our engineering platform for agentic backends (Prompt Flow/Semantic Kernel), any channel we need (including Teams), any model/provider, custom tools/APIs.
- Identity, networking, and data perimeter:
  - Copilot Studio: Strong for user-delegated access to M365 and Power Platform connectors.
  - AI Foundry: We get end-to-end Entra ID with Managed Identities, Key Vault, private networking/VNet, private endpoints across our LLM, APIs, and databases.
- Orchestration and multi-agent:
  - Copilot Studio: Prompts, plugins, and actions; limited branching/planning for our complex tool use.
  - AI Foundry: We get first-class orchestration (Prompt Flow, SK), retries/branching, multi-agent patterns, evaluation gates before sensitive actions.
- Tools and internal APIs:
  - Copilot Studio: Connector-first approach.
  - AI Foundry: We can use direct SDK/OpenAPI/MCP tools, database access with MI, standardized tool schemas that we reuse across agents/services.
- Evaluation, safety, and observability:
  - Copilot Studio: Responsible AI features for M365 experiences.
  - AI Foundry: We implement offline/online evaluations (groundedness/relevance), policy gates, lineage and tracing (App Insights/Log Analytics), A/B testing, canary deployments, rollbacks.
- DevOps and portability:
  - Copilot Studio: ALM via Power Platform solutions.
  - AI Foundry: We use Projects/Hubs, infra-as-code (Bicep/Terraform), versioned flows, multi-environment CI/CD, model/provider portability.
- Cost and scaling:
  - Copilot Studio: Fast time-to-value for M365 scenarios; simpler cost model.
  - AI Foundry: We get more control for our data/compute-heavy backends, explicit cost attribution, scale-out patterns.

When we use which:
- We choose Copilot Studio when:
  - Our experience is primarily in M365 (Teams/Outlook/SharePoint) with user-delegated access and simple actions.
  - We want citizen developers to maintain the solution and connector breadth is sufficient.
- We choose AI Foundry when:
  - Our workflows invoke internal APIs/databases under Managed Identity with private networking and audit needs.
  - We need multi-agent orchestration, evaluation gates, rollouts, and platform-level observability/traceability.
  - We want model/provider portability or non-M365 channels.

Our coexistence pattern (recommended):
- Frontend: We use Copilot/Teams (Copilot Studio for UX where helpful).
- Backend: We build our agentic services in AI Foundry (Prompt Flow/SK) with tools, evaluations, and governance.
- Integration: We expose our backend APIs to Copilot via secure plugins/actions, keeping our Teams UX while centralizing orchestration, identity, and audit in Foundry.

## Our Agent Catalog (Initial Focus: Insurance & Pension)

We're building:
- Root Orchestrator: Our entry point, routing, and policy enforcement.
- Coordinators: Internal Services; External Regulatory; Data & Analytics teams.
- Database Agent (New): We're starting here—conversational access to our governed datasets for non‑technical users. We turn natural language into safe, approved queries and return cited answers.
- Specialists: DataLoop, MEGA, ATM; Taxonomy (EIOPA RAG); Statistics; Public Registers; Analytics‑to‑Brief; Document Ingestion; API Concierge; Entity Resolution; Case Triage; Compliance Guard.
- Validation Specialist: We plan this for later—explains validation logic; assists natural‑language authoring and review of new rules with change control.
- Guardrails: We enforce identity, safety filters, evaluation gates, centralized tracing across all our agents.

## Representative Use Cases We're Targeting

1) Supervision Report Status Assistant – We consolidate status + validation notes with sources.  
2) Taxonomy Agent – We detect taxonomy deltas and propose mapping changes.  
3) Policy & Market Intelligence – We surface macro trends + cited data.  
4) Internal API Concierge – We help locate authoritative endpoints and auth methods.  
5) Analytics‑to‑Brief – We summarize material dashboard shifts for our team.  
6) Entity Resolution – We provide canonical ID with confidence + lineage.  
7) Case Triage – We classify, enrich, and route with audit metadata.  
8) Database Q&A (New) – We let users ask questions in natural language and get cited answers from our governed datasets without writing SQL.  
9) Validation Authoring & Coverage (Later) – We'll support NL→Validation authoring, proposal and review with change control.

All our responses are source‑grounded; we use human‑in‑the‑loop (HITL) for sensitive outputs.

## Business Value and Key Performance Indicators (KPIs) We're Tracking

We're targeting:
- Productivity: 30–60% cycle time reduction on our targeted tasks.
- Quality: We deliver cited, policy‑aligned outputs.
- Adoption: We measure weekly active users and repeat usage in Teams/Copilot.
- Satisfaction: We aim for CSAT ≥4.2/5.

Our KPIs:
- Time‑to‑answer vs our baseline (by use case).
- Citation/grounding rate ≥0.8 (we'll do sampled reviews).
- Manual correction rate <10% after week 8.
- Analyst hours we shift from collection to judgment.

## Risks & Our Mitigations

We've identified:
- Incorrect actions: We mitigate with tool‑first prompting, verification steps, HITL for sensitive flows.
- Data leakage / PII: We apply safety gating, redaction, private networking, no training on DNB data.
- Access control gaps: We enforce role‑based access, least privilege, approvals.
- Drift: We use versioned flows, canary rollout, telemetry and feedback loops.

## Our Readiness Checklist (Pre-Build)

Before we build, we need:
- Clear outcomes and decision rights (advisory vs action; our HITL points).
- Our authoritative data sources, freshness expectations, and citation requirements.
- Identity scopes, residency, and retention policies we'll enforce.
- Safety classification, PII handling, audit scope and our review cadence.
- Our channels and change management approach (Teams/Copilot, ACA), cost envelope.
- Reusable patterns and governance we'll standardize (approvals, logging, rollout gates).

## References We're Using

- Azure AI Foundry (our orchestration, evaluation, deployment platform).
- Microsoft Copilot (our end‑user channel).
- Governance: We're addressing GDPR, NIS2, DORA via identity, safety, encryption, and audit.

## Open Questions We Need to Answer with DNB Architecture and Operations

- Organization & Collaboration
  - Central ownership: Which central team should lead our Agentic AI initiative (sponsor, product owner, platform)? Where should we sit organizationally?
  - Collaboration model: How should we work with our supervision domains and IT (our cadence, working agreements, Teams channel, decision forum)?
  - Roles and staffing (pilot → scale): Which roles do we need and at what allocation? (Product Owner, Solution Architect, Agent Engineer(s), Data Engineer, Tool/API owner(s), Security, Compliance/Privacy, Platform/DevOps, Evaluator/QA, Change & Adoption lead, Legal/Procurement liaison).
  - Capacity & timeline (indicative): We estimate Discovery 2–3 weeks; our pilot build 6–8 weeks; hardening/deployment 2 weeks. Our typical availability per role: PO 0.3–0.5 FTE; Eng 2–3 FTE; Data Eng 0.5–1 FTE; Security/Compliance 0.2 FTE each; Evaluator 0.3 FTE.
  - Artifacts we'll create: RACI, our roadmap/backlog, Definition of Done/acceptance criteria, decision log, risk/mitigation register.
  - Our ways of working: PR‑based change control, our weekly demos, design reviews, incident/DR exercises.

- Identity & Access
  - How will our agents authenticate to Azure SQL/PostgreSQL (Managed Identity vs user-delegated tokens)? Do we need per-user attribution in our downstream query audit trails?
  - What RBAC roles do we require per agent and per tool? How will we enforce and review least privilege?
  - How will we handle cross-tenant or guest access, if we need it, for inter-agency collaboration?

- Data Residency, Retention, and Privacy
  - We need to confirm our EU region(s), customer-managed keys (CMK), and encryption posture for all our services (Cosmos DB, Log Analytics, AI services).
  - What retention and deletion policies should we apply to our chats, event logs, artifacts, and intermediate data? How will we apply PII redaction to our logs?

- Networking & Connectivity
  - Which of our services require private endpoints/VNet integration (ACA, databases, Key Vault, OpenAI endpoints)? Do we have any egress restrictions or proxy requirements?
  - We need to define DNS, firewall rules, and IP allowlists for our internal APIs and databases.

- Secrets, Keys, and Credentials
  - Can we operate fully with Managed Identities, or do we need any secrets? How will we enforce rotation and access reviews via Key Vault?

- Safety & Compliance
  - What Content Safety thresholds (PII, jailbreak, hate/abuse) should we use to gate tool execution? Where do we require human-in-the-loop approvals?
  - How should we record our safety decisions without storing sensitive payloads?

- Observability & Audit
  - What App Insights/Log Analytics schema, sampling, and correlation IDs will we adopt for our end-to-end tracing (user → agent → tool → DB/API)?
  - Which KQL queries and dashboards do we need for our security investigations and compliance reporting?

- Models & Orchestration
  - Our baseline model choice (Azure OpenAI GPT-4/Copilot) and fallbacks. What evaluation metrics (groundedness, relevance) define acceptable quality for us?
  - Our criteria for selecting Prompt Flow vs Semantic Kernel for specific agents. How will we control versions and rollouts?

- Tools & Internal APIs
  - We need an inventory of our authoritative APIs with OpenAPI specs. Are our rate limits, pagination, and error contracts consistent?
  - How will we standardize and reuse tool schemas (inputs/outputs) across our agents?

- Databases & Data Warehouse
  - Our catalog of governed datasets (DataLoop, MEGA, ATM, Synapse/Fabric). What row-level security and masking policies do we apply?
  - Do we need query cost controls, caching, or synthesized datasets for our evaluations/smoke tests?

- Teams/Copilot Integration
  - Which channels are in our scope (Teams bot, message extensions, Copilot plugins)? How will we enforce user identity and authorization per request?

- Agent-to-Agent (A2A) Interactions
  - Do we need A2A now or later? What should our agent card format be, where's our registry location, and what's our auth model for cross-department calls?
  - How will we audit and rate-limit our cross-org calls?

- Cost & Operations
  - We need cost attribution tags, budgets, and alerts. What's our expected concurrency, autoscaling thresholds, and cold start mitigation for ACA?
  - How do we manage quota for our model and data services?

- Change Management & Governance
  - Our PR-based change control for prompts, tools, and flows; our required reviewers; our canary and rollback strategies.
  - Our incident response runbooks, DR strategy (RTO/RPO), and backup/restore coverage.

- Legal & Procurement
  - What Data Processing Agreements and EU data boundary requirements do we have for our model providers?
  - What licensing constraints do we face for connectors, SDKs, and any third-party components we use?

