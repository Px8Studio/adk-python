# Waarom Agentic AI bij DNB – Managementbrief

Doel: Aanbevelen om agentic AI te adopteren in lijn met een Microsoft‑first‑strategie; waarde, risico’s en geschiktheid voor DNB schetsen, met een initiële focus op Verzekeringen en Pensioenfondsen.

Doelgroep: DNB‑leiding, IT, Security, Toezicht, Data & Analytics.

## Managementsamenvatting

- Agentic AI verkort doorlooptijd en overdrachtsmomenten voor toezicht‑ en datataken met volledige auditbaarheid.
- Een initiële high‑value use‑case is een Database‑agent die niet‑technische gebruikers in staat stelt om beheerde data in natuurlijke taal te bevragen; dit kan uitgroeien tot een multi‑agent‑systeem naarmate de behoeften volwassen worden.
- Werkt in vertrouwde kanalen (Teams/Copilot) met enterprise‑identiteit, veiligheid en governance.
- Verwachte resultaten: snellere antwoorden, outputs van hogere kwaliteit met citaten, en betere inzet van analisten.

## Wat is Agentic AI en waarom is het belangrijk

- Definitie: Een agent is een beheerd softwarecomponent dat redeneren met large language models (LLM) gebruikt om te plannen, tools/API’s aan te roepen en taken te coördineren.
- Volwassenheid: Microsoft Agent Framework integreert planning (Semantic Kernel) en multi‑agent‑patronen (AutoGen).
- Geschiktheid: Toezichtsworkflows (cross‑database‑reconciliatie, impact van regelgevingswijzigingen, documentanalyse) vereisen toolgebruik plus beleidscontroles.
- Platform: Azure AI Foundry levert orkestratie, evaluatie, uitrol en identiteitsintegratie.

### Componentniveau versus Systeemniveau

- AI‑agent (enkele actor): Afgebakende taak, minimale planning, lokale status.
- Agentic AI (systeem): Doelgestuurde orkestratie, vertakkingen, retries, verificatie, gedeelde sessiestatus, gecentraliseerd beleid.
- Voorbeeldverschil:
  - Enkelvoudige agent: "Vraag DataLoop op voor rapport X."
  - Systeem: "Vergelijk status van FI X in DataLoop/MEGA/ATM, reconcileer verschillen, stel een met citaten onderbouwde brief op."

### Verschuiving in governance

- Gaat van model‑centrische tests naar validatie van het volledige pad (intentie → plan → toolexecuties → output).
- Foundry‑evaluatie (groundedness, relevantie) plus Content Safety‑gating gaan vooraf aan gevoelige acties.
- Identiteit: Azure Entra ID + Managed Identities voor alle aanroepen; uniforme telemetrie in Application Insights (App Insights) en Azure Log Analytics.

## Microsoft‑first architectuur‑enablers

- Standaard veilige identiteit en toegang (single sign‑on, rolgebaseerde toegang).
- Veiligheids‑ en governance‑controls (content safety, logging, goedkeuringen).
- Integratie met productiviteitstools (Teams/Copilot) voor snelle adoptie.
- Hergebruik van bestaande, beheerde databronnen en dashboards (geen nieuwe platforms vereist bij de pilot).

## Agentencatalogus (Initiële focus: Verzekeringen & Pensioen)

- Root‑orkestrator: Ingang, routing, beleidshandhaving.
- Coördinatoren: Interne services; Externe regulering; Data & Analytics.
- Database‑agent (Nieuw): Conversatietoegang tot beheerde datasets voor niet‑technische gebruikers; zet natuurlijke taal om in veilige, goedgekeurde queries en retourneert antwoorden met citaten.
- Specialisten: DataLoop, MEGA, ATM; Taxonomie (EIOPA RAG); Statistiek; Openbare Registers; Analytics‑naar‑Brief; Documentinname; API‑conciërge; Entiteitsresolutie; Casustriage; Compliance Guard.
- Validatiespecialist: Legt validatielogica uit; ondersteunt het in natuurlijke taal opstellen en reviewen van nieuwe regels met change control (gepositioneerd voor latere fase).
- Guardrails: Identiteit, veiligheidsfilters, evaluatie‑gates, gecentraliseerde tracing.

## Representatieve use‑cases

1) Assistent Toezichtsrapportstatus – Consolideer status + validatie‑notities met bronnen.  
2) Taxonomie‑agent – Detecteert taxonomiewijzigingen, stelt mapping‑aanpassingen voor.  
3) Beleid & Marktintel – Macrotrends + geciteerde data.  
4) Interne API‑conciërge – Lokaliseer gezaghebbende endpoints en auth‑methode.  
5) Analytics‑naar‑Brief – Vat materiële dashboardverschuivingen samen.  
6) Entiteitsresolutie – Canonieke ID met confidence + herkomst (lineage).  
7) Casustriage – Classificeer, verrijk en routeer met auditmetadata.  
8) Database Q&A (Nieuw) – Stel vragen in natuurlijke taal en ontvang met citaten onderbouwde antwoorden uit beheerde datasets, zonder SQL te schrijven.  
9) Validatie‑authoring & dekking (Later) – NL→Validatie‑authoring, voorstel en review met change control.

Alle antwoorden zijn bron‑gegrond; human‑in‑the‑loop (HITL) voor gevoelige outputs.

## Zakelijke waarde en KPI’s

- Productiviteit: 30–60% reductie van doorlooptijd op gerichte taken.
- Kwaliteit: Met citaten onderbouwde, beleidsconforme outputs.
- Adoptie: Wekelijks actieve gebruikers en hergebruik in Teams/Copilot.
- Tevredenheid: CSAT ≥4,2/5.

KPI’s:
- Time‑to‑answer vs baseline (per use‑case).
- Citaties/grounding‑ratio ≥0,8 (steekproefsgewijze reviews).
- Handmatige correctieratio <10% na week 8.
- Analistenuren verschuiven van verzamelen naar oordeelsvorming.

## Risico’s & mitigaties

- Onjuiste acties: Tool‑first prompting, verificatiestappen, HITL voor gevoelige flows.
- Datalekken/PII: Safety‑gating, redactie, private networking, geen training op DNB‑data.
- Toegangscontrolegaten: Rolgebaseerde toegang, least privilege, goedkeuringen.
- Drift: Geversioneerde flows, canary‑uitrol, telemetrie en feedbackloops.

## Gereedheidschecklist (pre‑build)

- Heldere uitkomsten en beslisrechten (adviserend vs handelend; HITL‑punten).
- Gezaghebbende databronnen, actualiteit en citaatverwachtingen.
- Identiteitsscopes, dataresidency en retentie.
- Veiligheidsclassificatie, PII‑afhandeling, auditomvang en reviewcadans.
- Kanalen en change management (Teams/Copilot, ACA), kostenkader.
- Herbruikbare patronen en governance (goedkeuringen, logging, uitrolgates).

## Referenties

- Azure AI Foundry (orkestratie, evaluatie, uitrol).
- Microsoft Copilot (eindgebruikerskanaal).
- Governance: GDPR, NIS2, DORA via identiteit, veiligheid, encryptie en audit.

## Open vragen voor DNB‑architectuur en ‑operaties

- Organisatie & samenwerking
  - Centrale eigenaar(s): Wie vormt het centrale team dat Agentic AI leidt
    (sponsor, product/eigenaar, platform)? Waar landt dit organisatorisch?
  - Samenwerkingsmodel: Hoe werken we samen met toezicht‑domeinen en IT
    (cadans, werkafspraken, Teams‑kanaal, besluitvormingsforum)?
  - Rollen en bezetting (pilot → opschaling): Welke rollen zijn nodig en in
    welke inzet? (Product Owner, Solution Architect, Agent Engineer(s),
    Data Engineer, Tool/API‑owner(s), Security, Compliance/Privacy,
    Platform/DevOps, Evaluator/QA, Change & Adoption lead,
    Juridisch/Inkoop‑liaison).
  - Capaciteit & tijdlijn (indicatief): Discovery 2–3 weken; pilot build 6–8
    weken; hardening/uitrol 2 weken. Beschikbaarheid per rol (gemiddeld):
    PO 0,3–0,5 FTE; Eng 2–3 FTE; Data Eng 0,5–1 FTE; Security/Compliance
    0,2 FTE elk; Evaluator 0,3 FTE.
  - Artefacten: RACI, roadmap/backlog, Definition of Done/acceptatiecriteria,
    beslislog, risico‑/mitigatie‑register.
  - Werkwijze: PR‑gebaseerde change control, wekelijkse demo’s, design reviews,
    incident/DR‑oefeningen.

- Identiteit & Toegang
  - Hoe authenticeren agents naar Azure SQL/PostgreSQL (Managed Identity vs door gebruiker gedelegeerde tokens)? Is per‑gebruiker‑attributie nodig in downstream query‑audittrails?
  - Welke RBAC‑rollen zijn vereist per agent en per tool? Hoe wordt least privilege afgedwongen en periodiek herzien?
  - Hoe wordt cross‑tenant‑ of gasttoegang afgehandeld, indien nodig, voor inter‑agency samenwerking?

- Dataresidency, retentie en privacy
  - Bevestig EU‑regio(’s), customer‑managed keys (CMK) en encryptiestatus voor alle services (Cosmos DB, Log Analytics, AI‑services).
  - Welke retentie‑ en verwijderingsbeleid gelden voor chats, eventlogs, artifacts en tussentijdse data? Hoe wordt PII‑redactie toegepast op logs?

- Netwerken & connectiviteit
  - Welke services vereisen private endpoints/VNet‑integratie (ACA, databases, Key Vault, OpenAI‑endpoints)? Zijn er egress‑beperkingen of proxyvereisten?
  - DNS, firewallregels en IP‑allowlists voor interne API’s en databases.

- Secrets, sleutels en credentials
  - Kunnen we volledig met Managed Identities werken, of zijn er secrets nodig? Hoe worden rotatie en toegangsreviews afgedwongen via Key Vault?

- Veiligheid & compliance
  - Welke Content Safety‑drempels (PII, jailbreak, haat/misbruik) moeten toolexecutie afschermen? Waar zijn human‑in‑the‑loop‑goedkeuringen vereist?
  - Hoe registreren we veiligheidsbeslissingen zonder gevoelige payloads op te slaan?

- Observeerbaarheid & audit
  - Welk App Insights/Log Analytics‑schema, sampling en correlatie‑ID’s hanteren we voor end‑to‑end tracing (gebruiker → agent → tool → DB/API)?
  - Welke KQL‑queries en dashboards zijn nodig voor security‑onderzoeken en compliancerapportage?

- Modellen & orkestratie
  - Baseline‑modelkeuze (Azure OpenAI GPT‑4/Copilot) en fallbacks. Welke evaluatiemetrics (groundedness, relevantie) definiëren acceptabele kwaliteit?
  - Criteria voor keuze Prompt Flow vs Semantic Kernel per agent. Hoe worden versies en uitrol gecontroleerd?

- Tools & interne API’s
  - Inventaris van gezaghebbende API’s met OpenAPI‑specs. Zijn rate limits, paginering en foutcontracten consistent?
  - Hoe worden toolschema’s (inputs/outputs) gestandaardiseerd en hergebruikt over agents?

- Databases & datawarehouse
  - Catalogus van beheerde datasets (DataLoop, MEGA, ATM, Synapse/Fabric). Welke row‑level security en masking‑policies gelden?
  - Hebben we querykost‑controles, caching of gesynthetiseerde datasets nodig voor evaluaties/smoke‑tests?

- Teams/Copilot‑integratie
  - Welke kanalen (Teams‑bot, message extensions, Copilot‑plugins) vallen in scope? Hoe worden gebruikersidentiteit en autorisatie per verzoek afgedwongen?

- Agent‑to‑Agent (A2A) interacties
  - Hebben we A2A nu of later nodig? Wat is het agentkaart‑formaat, de registry‑locatie en het auth‑model voor afdelingsoverstijgende aanroepen?
  - Hoe auditen en rate‑limiten we cross‑org‑aanroepen?

- Kosten & operatie
  - Kostenattributie‑tags, budgetten en alerts. Verwachte concurrency, autoscaling‑drempels en cold‑start‑mitigatie voor ACA.
  - Quotabeheer voor model‑ en dataservices.

- Change management & governance
  - PR‑gebaseerde change control voor prompts, tools en flows; vereiste reviewers; canary‑ en rollbackstrategieën.
  - Incidentrespons‑runbooks, DR‑strategie (RTO/RPO) en backup/restore‑dekking.

- Juridisch & inkoop
  - Data Processing Agreements en EU‑databoundary‑vereisten voor modelproviders.
  - Licentiebeperkingen voor connectors, SDK’s en eventuele third‑party‑componenten.

Opmerking: Deze lijst kadert de discovery om adoptierisico’s te reduceren; ze kan worden aangescherpt naarmate systemen en stakeholders worden geïnventariseerd.
