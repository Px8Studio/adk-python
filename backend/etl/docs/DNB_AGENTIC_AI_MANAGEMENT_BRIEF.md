# Why Agentic AI at DNB – Management Brief

Purpose: Explain why DNB should adopt agentic AI now, how it aligns with our Microsoft-first strategy, the business value, risks, and a 90‑day path to production pilots.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics.

## Executive Summary

- Agentic AI turns static chat into reliable work execution: agents plan, call tools/APIs, and orchestrate multi-step tasks with guardrails.
- DNB’s Microsoft-first stack is ready: Azure AI Foundry for orchestration and governance; Microsoft Agent Framework (preview) unifying Semantic Kernel + AutoGen; GitHub Copilot as our default model; enterprise security via Entra ID, Managed Identities, Key Vault, and Content Safety.
- Initial DNB use cases show 30–60% productivity gains in supervision research, cross-system lookups, and reporting preparation, with strong auditability.
- This brief outlines what is possible on the Microsoft stack today and the agent types we can deploy first in Insurance & Pension with a clear checklist of questions to answer before implementation.

## What Is Agentic AI (and Why It Matters)

- Definition: An “agent” is an LLM-enabled software component that can reason about a goal, plan steps, call tools/APIs, and coordinate with other agents—reliably and auditable.
- Why now:
  - Maturity: Microsoft Agent Framework (preview) blends Semantic Kernel (skills/tools, planning) and AutoGen (multi-agent patterns).
  - Platform fit: Azure AI Foundry provides Prompt Flow, evaluation, deployment, and governance integrated with DNB’s Azure.
  - DNB context: Cross-database queries, regulatory checks, and document analysis benefit from tool-using, policy‑aware automation.

### AI agent vs Agentic AI — what’s the difference?

- AI agent (component-level)
  - Scope: Single actor that calls tools/APIs to complete a bounded task.
  - Interaction: Often single-turn or short multi-turn; minimal planning.
  - State: Typically stateless or local, narrow context window.
  - Governance: Unit-level logging and RBAC.
  - Microsoft fit: One Prompt Flow or a Semantic Kernel skill; often hosted as a single Azure Container App.

- Agentic AI (system-level)
  - Scope: Goal-driven system that plans, branches, and coordinates multiple agents/tools.
  - Interaction: Multi-step Reason-Act loops with retries, verification, and reflection.
  - State: Shared memory/session across steps and agents; evaluation gates.
  - Governance: System policies, safety filters, observability, approvals (human-in-the-loop).
  - Microsoft fit: Prompt Flow for orchestration + Microsoft Agent Framework (preview) to compose multi-agent patterns (Semantic Kernel + AutoGen), monitored via Application Insights and governed in Azure AI Foundry.

- In practice at DNB
  - AI agent: “Query DataLoop for report X” (one tool call with IAM).
  - Agentic AI: “Compare FI X status across DataLoop/MEGA/ATM, reconcile discrepancies, and draft a cited brief” (parallel fetch, synthesis, verification, and guardrails).

- Governance implications
  - Move from testing a model to validating end-to-end behavior (tools, plans, decisions).
  - Use Foundry evaluation (groundedness, relevance) and Content Safety gates before actions.
  - Enforce Entra ID RBAC and Managed Identities across all agent calls; centralize traces in App Insights/Log Analytics.

## Microsoft-First Architecture Enablers

- Azure AI Foundry (formerly AI Studio)
  - Visual orchestration (Prompt Flow), evaluation/groundedness checks, safe deployment to Azure Container Apps, built-in versioning and monitoring.
- Microsoft Agent Framework (preview)
  - Combines Semantic Kernel and AutoGen to build dependable single- and multi-agent systems with planning, memory, and tool use.
  - Repo: https://github.com/microsoft/agent-framework
- Models: GitHub Copilot (primary) with Azure OpenAI fallback for large-context tasks.
- Security & Compliance by design
  - Identity: Azure Entra ID, Managed Identities (no secrets in code), RBAC.
  - Safety: Azure AI Content Safety for PII and jailbreak protection.
  - Data: Private networking, Customer-Managed Keys, audit via Application Insights + Log Analytics.
- Data & Insights
  - Microsoft Fabric (Lakehouse/Warehouse) and Power BI integrate seamlessly for analytics-driven agents.

## Agent Catalog for Insurance & Pension (expandable DNB-wide)

- Root Orchestrator
  - Role: Entry point, routing, synthesis, policy enforcement.
  - Microsoft fit: Prompt Flow orchestration + Agent Framework patterns; App Insights traces.

- Domain Coordinators
  - Internal Services Coordinator: DataLoop, MEGA, ATM routing; IAM-aware.
  - External Regulatory Coordinator: EIOPA/EBA/ECB public sources (begin with EIOPA).
  - Data & Analytics Coordinator: Fabric Lakehouse, Power BI, change detection.
  - Microsoft fit: Router + sub-flows in Prompt Flow; SK/AutoGen for multi-agent.

- Internal Specialists (systems we already use)
  - DataLoop Specialist: Report status, lineage notes (Azure SQL, Managed Identity).
  - MEGA Specialist: Validation rules lookup and explanations (Azure SQL).
  - ATM Specialist: Model metadata and checks (Azure PostgreSQL).

- External/Knowledge Specialists
  - Taxonomy Agent (EIOPA RAG): Conversational access to XBRL/taxonomy updates, delta diffs, mapping suggestions; sources cited.
    - Microsoft fit: Azure AI Search vector index + Prompt Flow; governance via Content Safety.
  - DNB Statistics Agent: Economic indicators with citations.
  - Public Registers Agent: Fetch entity/regulatory data with source links.

- Data & Reporting Specialists
  - Analytics-to-Brief Agent: Summarize dashboard shifts and anomalies (Fabric/Power BI).
  - Document Ingestion/Extraction Agent: Parse filings, extract key fields, flag gaps.

- Platform/Enablement Agents
  - API Concierge: Find the right internal API/data set, auth steps, example calls.
  - Entity Resolution Agent: Harmonize FI identities across DataLoop/MEGA/ATM.
  - Case Triage Agent: Classify, enrich, and route queries with audit notes.
  - Compliance Guard: PII checks, policy tagging, retention hints on outputs.

Microsoft guardrails for all: Entra ID + Managed Identity, private networking, Content Safety, App Insights/Log Analytics, Foundry evaluation.

## Representative DNB Use Cases (Insurance & Pension first, DNB-wide later)

1) Supervision Report Status Assistant (DataLoop/MEGA/ATM)
   - Task: “What is the latest status and validation notes for FI X across report types Y/Z?”
   - Actions: IAM-authenticated SQL/API calls; consolidate; cite sources.

2) Taxonomy Agent (EIOPA RAG)
   - Task: “What changed in the latest EIOPA taxonomy relevant to pensions? Propose mapping deltas and highlight impacts.”
   - Actions: Retrieve, chunk, embed EIOPA resources; answer with citations; generate suggested deltas.

3) Policy & Market Intelligence Copilot
   - Task: “Summarize macro trends relevant to pension funds; attach DNB statistics, link to sources.”
   - Actions: Call DNB Statistics API and internal docs where permitted; produce a cited brief.

4) Internal API Concierge
   - Task: “Which internal source gives me validation rule outcomes for report Y?”
   - Actions: Query internal API registry/docs; return method/schema/auth; examples.

5) Analytics-to-Brief (Fabric + Power BI)
   - Task: “Summarize weekly changes for dashboard ABC; list material deviations vs prior period.”
   - Actions: Query Fabric/Power BI; detect changes; produce a concise brief.

6) Entity Resolution & Data Harmonization
   - Task: “Unify FI X across DataLoop/MEGA/ATM; return canonical ID and confidence.”
   - Actions: Deterministic + heuristic matching; return matches with confidence and lineage.

7) Case Triage & Routing
   - Task: “Route this inquiry to the right domain specialist and attach required context.”
   - Actions: Classify, enrich, tag, and forward with audit metadata.

Notes
- All answers grounded with sources; HITL for sensitive actions.
- Built on Azure AI Foundry + Agent Framework (preview), with Content Safety and IAM.

## Business Value and KPIs

- Productivity: 30–60% time saved on repetitive cross-system lookups and synthesis.
- Quality: Source-grounded, policy-aligned answers with audit trails and citations.
- Speed: Minutes to insights instead of hours/days, improving supervisory responsiveness.
- Talent leverage: Analysts focus on judgment and escalation, not data wrangling.

Measure:
- Cycle time per query/task (baseline vs. pilot)
- Groundedness/citation score (>=0.8 target in Foundry eval)
- Manual correction rate (<10% target after week 8)
- User satisfaction (CSAT >=4.2/5)

## Risk, Compliance, and Mitigations

- Hallucination/incorrect actions
  - Mitigate with tool-first prompts, source grounding, evaluation pipelines in Foundry, and human-in-the-loop for sensitive actions.
- Data leakage/PII handling
  - Enforce Content Safety, redaction, private networking, and data residency; no training on DNB data; CMK encryption.
- Access control
  - Entra ID, Managed Identities, per‑role RBAC; least-privilege for databases and APIs.
- Model/Framework drift
  - Versioned flows, canary releases, monitoring; Agent Framework is open and aligned with Microsoft ecosystem to reduce lock-in risk.

## Readiness Questions Before Building a Use Case

- Outcome and decision rights
  - What decision does the agent support? Is it advisory or can it act? Where is HITL required?
- Data and sources of truth
  - Which systems are authoritative? What joins are required? Any latency or freshness constraints?
- Identity, access, and boundaries
  - Which Managed Identities, roles, and resource scopes are needed? Any data residency limits?
- Safety and compliance
  - What PII or sensitive content may appear? Redaction policy? Retention and classification?
- Grounding and quality
  - What sources must be cited? Target groundedness/relevance; acceptable error thresholds?
- Observability and audit
  - What needs to be logged and for how long? Who reviews traces and when?
- Cost, SLOs, and scale
  - Expected volumes, response times, concurrency, and cost caps?
- Deployment and rollout
  - Channel (Teams, web), environment (ACA), change management, and support model?
- Reuse and standardization
  - Which tools/connectors should be shared across agents? Patterns we standardize on?

## References

- Azure AI Foundry: evaluation, Prompt Flow, deployment to Azure Container Apps
- Microsoft Agent Framework (preview, Semantic Kernel + AutoGen): https://github.com/microsoft/agent-framework
- DNB compliance context: GDPR, NIS2, DORA; enforce via Entra ID, Managed Identities, Content Safety, CMK, private networking.

## (Removed) 90‑Day Plan and Deliverables
- The time-bound plan was removed to keep this as a general overview focused on capabilities, candidate agents, and the readiness questions needed before any build.

