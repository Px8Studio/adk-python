# Architecture Documentation Enhancements

**Date**: October 24, 2025  
**Version**: 2.1.0  
**Status**: MVP Implementation Complete (BigQuery + Analytics Agents)

## Overview

This document summarizes the comprehensive enhancements made to `ARCHITECTURE_MERMAID.md` to integrate:
1. **Data Science Multi-Agent System** with BigQuery, AlloyDB, and BQML
2. **Internal DNB Services** hosted on Microsoft Azure (DataLoop, ATM, MEGA)
3. **Multi-Cloud Architecture** distinguishing between Local Development, Docker Containers, Microsoft Azure (internal services), and Google Cloud Platform (data/AI services)

---

## 📋 What's New

### 1. **Internal DNB Services on Microsoft Azure** (NEW)

#### Azure-Hosted Internal Services
- **DNB DataLoop**: Report status communication with financial institutions
- **DNB ATM**: Model access APIs (third-party provided)
- **DNB MEGA**: Validation services (third-party provided)

#### Integration Strategy
- **ADK Built-in OpenAPI Tool**: Direct integration without MCP server
- **Private Network Access**: Secure internal connectivity via Azure Private Endpoints
- **Simplified Architecture**: No external toolbox hop for internal services
- **Lower Latency**: Direct HTTP requests from agents to Azure services

#### Specialist Agents
- `dnb_dataloop_agent`: Handles report status workflows
- `dnb_atm_agent`: Accesses model APIs
- `dnb_mega_agent`: Performs validations

---

### 2. **Data Science Agent Architecture** (NEW SECTION)

#### Multi-Agent Data Analysis System
- **Root Coordination**: `data_coordinator` routes requests to specialized sub-agents
- **Sub-Agents**:
  - `bigquery_agent`: NL2SQL translation for BigQuery using CHASE-SQL or baseline Gemini
  - `alloydb_agent`: NL2SQL for AlloyDB via MCP Toolbox for Databases
  - `analytics_agent`: NL2Py analysis using Code Interpreter extension (Pandas, Matplotlib)
  - `bqml_agent`: BigQuery ML model training with RAG-based reference guide

#### Cross-Dataset Capabilities
- Foreign key relationship configuration (`cross_dataset_relations.json`)
- Cross-dataset joins between BigQuery and AlloyDB
- Dataset configuration files for flexible data source routing

#### Sample Datasets
- **Cymbal Airlines Flights**: Demonstrates cross-dataset queries (BigQuery + AlloyDB)
- **Forecasting Sticker Sales**: BigQuery-only BQML forecasting examples

---

### 3. **Deployment Topology** (ENHANCED - Multi-Cloud)

#### Four-Layer Deployment Model

```
💻 LOCAL DEVELOPMENT
  ├── Python Applications (Host)
  │   ├── ADK Web Server (Port 8000)
  │   ├── Root Agent (.venv)
  │   │   ├── GenAI Toolbox integration (public APIs)
  │   │   └── ADK OpenAPI Tool (internal Azure services)
  │   └── ETL Pipelines (Poetry)
  ├── File System
  │   ├── Bronze Layer (Parquet)
  │   ├── Silver Layer (Cleaned)
  │   └── Gold Layer (Aggregated)
  └── 🐳 Docker Containers
      ├── genai-toolbox-mcp (Port 5000)
      ├── Jaeger All-in-One (Ports 4318, 16686)
      └── PostgreSQL 17 (Port 5432)

☁️ MICROSOFT AZURE (Internal DNB Services)
  ├── Internal Services (Third-party hosted)
  │   ├── DNB DataLoop (Report status)
  │   ├── DNB ATM (Models)
  │   └── DNB MEGA (Validations)
  └── Azure Network
      ├── Virtual Network (VNET)
      └── Private Endpoints (Secure access)

☁️ GOOGLE CLOUD PLATFORM (Data & AI - PLANNED)
  ├── Cloud Run Services
  │   ├── MCP Toolbox (VPC Connector)
  │   └── Data Science Agent (Agent Engine)
  ├── Data & Storage
  │   ├── Cloud Storage (gs://dnb-data/)
  │   ├── BigQuery (dnb_statistics)
  │   ├── AlloyDB (PostgreSQL cluster)
  │   └── Cloud SQL (Session storage)
  └── Vertex AI
      ├── Gemini API
      ├── Code Interpreter Extension
      ├── RAG Engine (BQML reference)
      └── Agent Engine (Reasoning Engine)
```

#### Deployment Comparison Matrix
- Side-by-side comparison of all components across environments
- Clear distinction between local host, Docker, and Cloud Run
- Port mappings and persistence strategies

---

### 3. **BigQuery Deployment Pipeline** (IMPLEMENTED ✅ - Oct 24, 2025)

#### ETL → GCS → BigQuery Flow
```
Bronze Layer (Local Parquet)
  ↓ (Upload Script - upload_to_bigquery.py)
Cloud Storage (gs://dnb-data/bronze/)
  ↓ (BigQuery Load Job)
BigQuery Dataset (dnb_statistics)
  ├── Partitioned by period
  ├── Clustered by business keys
  ├── Schema auto-detected from parquet
  └── Table naming: {category}__{subcategory}__{endpoint}
```

#### Implementation Details

**Core Upload Utilities** (`backend/etl/dnb_statistics/bigquery_upload.py`):
- `generate_table_name()` - Creates BQ table names from folder structure
- `parse_table_path()` - Extracts category/subcategory/endpoint from paths
- `parquet_to_bigquery_schema()` - Auto-detects schema with type mapping
- `upload_to_gcs()` - Uploads parquet to GCS staging bucket
- `create_bigquery_table()` - Creates tables with partitioning/clustering
- `load_parquet_from_gcs()` - Executes BigQuery load jobs
- `upload_parquet_to_bigquery()` - Full pipeline orchestration

**CLI Orchestrator** (`backend/etl/dnb_statistics/upload_to_bigquery.py`):
```powershell
# Upload all tables
python -m backend.etl.dnb_statistics.upload_to_bigquery --all

# Upload specific category
python -m backend.etl.dnb_statistics.upload_to_bigquery --category insurance_pensions

# Upload specific tables
python -m backend.etl.dnb_statistics.upload_to_bigquery --tables exchange_rates_day

# Dry run (preview only)
python -m backend.etl.dnb_statistics.upload_to_bigquery --all --dry-run
```

**VS Code Tasks** (6 new tasks):
- 📊 BigQuery: Upload All DNB Statistics
- 📊 BigQuery: Upload Category (Insurance & Pensions)
- 📊 BigQuery: Upload Category (Market Data)
- 📊 BigQuery: List Available Files
- 📊 BigQuery: Dry Run (Preview Upload)
- 🌐 Open: BigQuery Console

**Configuration** (`.env` file):
```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GCS_BUCKET=dnb-data
BQ_DATASET_ID=dnb_statistics
BQ_PARTITION_FIELD=period
BQ_CLUSTERING_FIELDS=category,subcategory  # optional
```

#### Table Naming Convention
```
{category}__{subcategory}__{endpoint_name}

Examples:
- insurance_pensions__insurers__insurance_corps_balance_sheet_quarter
- market_data__interest_rates__market_interest_rates_day
- macroeconomic__national_accounts__gdp_quarter
```

#### Schema Auto-Detection

Parquet-to-BigQuery type mapping:
- `int64/int32` → `INTEGER`
- `float/double` → `FLOAT`
- `string` → `STRING`
- `bool` → `BOOLEAN`
- `date` → `DATE`
- `timestamp` → `TIMESTAMP`

#### Prerequisites & Setup

See comprehensive guide: `backend/etl/dnb_statistics/BIGQUERY_UPLOAD.md`

1. **GCP Project Setup**:
   - Enable BigQuery and Storage APIs
   - Create GCS bucket (`gs://dnb-data`)
   - Create BigQuery dataset (`dnb_statistics`)

2. **Authentication**:
   - Service account OR `gcloud auth application-default login`
   - Required roles: `bigquery.dataEditor`, `bigquery.jobUser`, `storage.admin`

3. **Python Dependencies** (in pyproject.toml):
   - `google-cloud-bigquery ^3.28.0`
   - `google-cloud-storage ^2.19.0`
   - `pyarrow ^21.0.0`

---
- insurance_pensions__insurers__insurance_corps_balance_sheet_quarter
- financial_markets__interest_rates__market_interest_rates
- financial_markets__bond_yields__dutch_state_loans
```

---

### 4. **Cloud Run Architecture** (NEW DIAGRAM)

#### Infrastructure Components
- **Cloud Run Services**: Auto-scaling MCP Toolbox and Data Science Agent
- **VPC Network**: Serverless VPC Connector for AlloyDB access
- **Managed Databases**: AlloyDB (8 CPU), Cloud SQL (PostgreSQL 17)
- **Data Storage**: Cloud Storage bucket, BigQuery dataset
- **Vertex AI Services**: Gemini, Code Interpreter, RAG Engine, Agent Engine
- **Security**: Secret Manager, IAM roles, Service Accounts

#### Service Configuration Examples
- MCP Toolbox Cloud Run YAML
- Data Science Agent Cloud Run YAML
- Environment variables and secrets management

---

### 5. **Updated System Overview**

#### Enhanced High-Level Architecture
- Added **Google Cloud Platform** subgraph with GCS, BigQuery, AlloyDB
- New data flow: `Bronze → GCS → BigQuery → Root Agent`
- Color-coded cloud components (distinct from local/external)

#### Updated Agent Orchestration
- Added **Data Science Agents** subgraph with all 4 sub-agents
- New `data_coordinator` routing to BigQuery, AlloyDB, Analytics, BQML agents
- Visual hierarchy showing multi-agent system expansion

---

## 🎯 Key Architectural Principles (Updated)

1. **Multi-Cloud Integration**: Seamless Azure (internal services) + GCP (data/AI) architecture
2. **Modularity**: Clear separation of concerns (agents, tools, ETL, data science)
3. **Type Safety**: Kiota-generated clients, OpenAPI schemas
4. **Observability**: Full tracing from agent → tool → API (local + Azure + GCP)
5. **Extensibility**: Plugin-based tool discovery, new extractors, new agents
6. **Developer Experience**: VS Code tasks, scripts, hot-reload
7. **Cloud-Ready**: Clear migration path from local → Docker → Azure → GCP
8. **Data-Driven**: Medallion architecture (Bronze/Silver/Gold) with cloud integration
9. **Security-First**: Private Endpoints, VPC networking, secure internal service access

---

## 📊 Component Count (Updated)

| Category | Current | Azure (Internal) | GCP (Planned) | Total |
|----------|---------|------------------|---------------|-------|
| **Agents** | 10+ | +3 (DataLoop, ATM, MEGA) | +4 (Data Science) | 17+ |
| **Tools** | 84 (public APIs) | +3 (internal services) | +BQ/AlloyDB tools | 93+ |
| **ETL Extractors** | 23 | 0 | 0 | 23 |
| **API Clients** | 3 Kiota clients | 3 ADK OpenAPI tools | Built-in BQ/AlloyDB | 6+ |
| **Services (Local)** | 3 (Toolbox, Jaeger, Postgres) | 0 | 0 | 3 |
| **Services (Azure)** | 0 | **3 (DataLoop, ATM, MEGA)** | 0 | **3** |
| **Services (GCP)** | 0 | 0 | +6 (Cloud Run, AlloyDB, Cloud SQL, BQ, Vertex AI) | 6 |
| **Data Layers** | 3 (Bronze, Silver, Gold) | 0 | 0 | 3 |
| **Cloud Platforms** | 0 | **1 (Microsoft Azure)** | +1 (Google Cloud) | **2** |

---

## 🔗 Integration Points (Enhanced - Multi-Cloud)

| Component | Protocol | Port | Purpose | Environment |
|-----------|----------|------|---------|-------------|
| ADK Web UI | HTTP/WebSocket | 4200 → Backend | Agent interaction | **Local Host** |
| ADK Agents | HTTP REST | → 5000 | Tool invocation (public) | **Local Host → Docker** |
| **ADK Agents** | **ADK OpenAPI** | **→ Azure** | **Internal services** | **Local Host → Azure** |
| GenAI Toolbox | HTTPS REST | → DNB APIs | External API calls | **Docker → Internet** |
| GenAI Toolbox | OTLP/gRPC | → 4318 | Trace export | **Docker → Docker** |
| Jaeger UI | HTTP | 16686 | Trace visualization | **Browser → Docker** |
| PostgreSQL | PostgreSQL | 5432 | Metadata storage | **Docker (Local)** |
| **DNB DataLoop** | **HTTPS/REST** | **443** | **Report status** | **Azure (Internal)** |
| **DNB ATM** | **HTTPS/REST** | **443** | **Model APIs** | **Azure (Internal)** |
| **DNB MEGA** | **HTTPS/REST** | **443** | **Validations** | **Azure (Internal)** |
| BigQuery | gRPC/REST | 443 | Data warehouse | **GCP (Planned)** |
| AlloyDB | PostgreSQL | 5432 | OLTP database | **GCP (Planned)** |
| Cloud Run | HTTPS | 443 | Agent services | **GCP (Planned)** |
| Vertex AI | gRPC/REST | 443 | AI/ML platform | **GCP (Planned)** |

---

## 📚 New Diagrams Added

### Multi-Cloud System Architecture
1. **Azure Internal Services Integration**: DNB DataLoop, ATM, MEGA on Microsoft stack
2. **OpenAPI Tool Integration Strategy**: MCP Server vs ADK Built-in tool distinction
3. **Multi-Agent Orchestration**: Includes Azure specialists alongside data science agents

### Data Science Agent Architecture
4. **Multi-Agent Data Analysis System**: Root coordinator with 4 specialized sub-agents
5. **Data Science Agent Tools & Technologies**: Mindmap of capabilities
6. **Sample Dataset Configurations**: ERD for Cymbal Airlines dataset
7. **Data Science Agent Interaction Flow**: Sequence diagram for query → SQL → visualization

### Deployment Topology
8. **Four-Layer Deployment Model**: Local → Docker → Azure → GCP comprehensive view
9. **Azure Cloud Architecture**: Internal services with VNET and Private Endpoints
10. **Cloud Run Deployment Architecture**: Full GCP infrastructure with VPC, databases, AI services
11. **Deployment Workflow Comparison**: Multi-cloud environment feature comparison

### BigQuery Integration
12. **BigQuery Deployment Pipeline**: ETL → GCS → BigQuery with table creation
13. **Cross-Dataset Relations**: Foreign key configuration for multi-database joins
14. **BigQuery Upload Architecture** (NEW - Oct 24, 2025): Complete upload workflow with CLI and VS Code tasks

---

## 🚀 Next Steps (Documented Roadmap)

### Implemented ✅
- Multi-agent system with root, coordinators, and specialists
- GenAI Toolbox with 84+ DNB public API tools (MCP Server)
- **Azure internal services integration (DataLoop, ATM, MEGA)** - DOCUMENTED
- **ADK Built-in OpenAPI Tool for internal service access** - DOCUMENTED
- ETL pipeline extracting to Bronze layer (Parquet)
- Docker Compose local development stack
- OpenTelemetry tracing with Jaeger
- **Data Science Multi-Agent System (MVP)** - ✅ **IMPLEMENTED (Oct 24, 2025)**
  - ✅ Root coordinator agent (`data_science_root_agent`)
  - ✅ BigQuery sub-agent with NL2SQL and ADK built-in tools
  - ✅ Analytics sub-agent with Vertex AI Code Interpreter
  - ✅ Dataset configuration system (JSON-based)
  - ✅ Runner script for local testing
  - ✅ Environment configuration template
- **BigQuery Upload Pipeline** - ✅ **IMPLEMENTED (Oct 24, 2025)**
  - ✅ Parquet to BigQuery upload utilities (`bigquery_upload.py`)
  - ✅ CLI orchestrator with --all, --category, --tables options
  - ✅ Auto-schema detection from parquet files
  - ✅ Table naming convention (category__subcategory__endpoint)
  - ✅ GCS staging for efficient load jobs
  - ✅ Partitioning and clustering support
  - ✅ VS Code tasks for upload operations
  - ✅ Comprehensive documentation (BIGQUERY_UPLOAD.md)

### In Progress 🚧
- ~~**Data Integration**: Loading Bronze layer parquet files to BigQuery~~ ✅ **COMPLETED (Oct 24, 2025)**
- **Testing**: Validating data science agent with actual DNB Statistics data
- **BQML Agent**: Implementing BigQuery ML capabilities with RAG reference
- **AlloyDB Agent**: Setting up MCP Toolbox for Databases integration

### Planned 📋

#### 1. Data Science Agents (MVP COMPLETE ✅)
- [x] Implement `data_coordinator` with NL2SQL/NL2Py routing
- [x] Create `bigquery_agent` with baseline Gemini and built-in BQ tools
- [x] Develop `analytics_agent` with Code Interpreter extension
- [ ] **Build `bqml_agent` with RAG-based BQML reference guide** - NEXT
- [ ] **Set up `alloydb_agent` with MCP Toolbox for Databases** - NEXT
- [ ] **Implement CHASE-SQL** for advanced BigQuery NL2SQL

#### 2. Azure Internal Services (DOCUMENTED - Implementation Pending)
- [ ] Implement `dnb_dataloop_agent` with ADK OpenAPI Tool
- [ ] Implement `dnb_atm_agent` with ADK OpenAPI Tool
- [ ] Implement `dnb_mega_agent` with ADK OpenAPI Tool
- [ ] Configure Azure Private Endpoint connections
- [ ] Set up secure authentication for Azure services

#### 3. Cloud Deployment (GCP)
- [ ] Deploy GenAI Toolbox to Cloud Run with VPC connector
- [ ] Set up AlloyDB cluster with Auth Proxy
- [ ] Create Cloud SQL instance for session storage
- [ ] Configure Vertex AI Code Interpreter extension
- [ ] Build RAG corpus for BQML documentation
- [ ] Set up Private Link from GCP to Azure (if needed)

#### 4. Data Pipeline
- [ ] Implement Bronze → GCS upload scripts
- [ ] Create BigQuery dataset with partitioned tables
- [ ] Develop Silver layer transformation logic
- [ ] Build Gold layer aggregation views
- [ ] Set up Cloud Scheduler for automated ETL

#### 5. Advanced Features
- [ ] Cross-dataset join capabilities (BigQuery ↔ AlloyDB)
- [ ] Dataset configuration files for flexible data source routing
- [ ] BQML model training workflows (ARIMA, forecasting)
- [ ] Performance optimization for large-scale analytics
- [ ] Multi-cloud observability (Azure + GCP traces in Jaeger)

---

## 📝 Documentation Standards

All diagrams follow these conventions:

### Color Coding
- **Local Python**: Orange (#fff3e0)
- **Local Data**: Purple (#f3e5f5)
- **Docker Containers**: Blue (#e3f2fd) - Thick border (3px)
- **Azure Internal Services**: Blue (#bbdefb) - Microsoft stack
- **Azure Network**: Blue-grey (#cfd8dc) - VNET infrastructure
- **Cloud Run**: Green (#e8f5e9) - Thick border (3px)
- **GCP Data Services**: Light Blue (#e1f5fe)
- **Vertex AI**: Pink (#fce4ec)
- **Security**: Teal (#e0f2f1)

### Diagram Types
- **Graph TB/LR**: System architecture, deployment topology
- **Flowchart**: Workflows, processes
- **Sequence Diagram**: Interaction flows
- **Mindmap**: Technology stacks, capabilities
- **ERD**: Data models, dataset relationships

---

## 🔍 Visual Distinctions

### Local Development
- **Python apps run on host** (.venv isolation)
- **Data stored on local filesystem** (data/1-bronze/, etc.)
- **Services run in Docker containers** (toolbox, jaeger, postgres)
- **Browser accesses localhost ports** (4200, 5000, 16686)

### Azure Cloud (Internal Services)
- **DNB internal services on Microsoft Azure** (DataLoop, ATM, MEGA)
- **Accessed via ADK Built-in OpenAPI Tool** (no MCP server)
- **Secure internal network** (VNET + Private Endpoints)
- **Private authentication** (Azure credentials)

### GCP Cloud (Data & AI - Planned)
- **Services run on Cloud Run** (auto-scaling, serverless)
- **Data stored in GCP** (Cloud Storage, BigQuery, AlloyDB)
- **AI services via Vertex AI** (Gemini, Code Interpreter, RAG)
- **Secrets managed by Secret Manager**
- **Networking via VPC connectors**
- **Private Link to Azure** (if cross-cloud access needed)

---

## 📖 References

- **ADK Samples**: `adk-samples/python/agents/data-science/`
- **Deploy Guide**: `_archive/deploy_dnb_data_to_bigquery.md`
- **Original Architecture**: `ARCHITECTURE_MERMAID.md` (v1.0.0)
- **This Document**: `ARCHITECTURE_ENHANCEMENTS.md` (v2.0.0)

---

## 🎉 Impact Summary

### Documentation Coverage
- **13 new/enhanced Mermaid diagrams** added across 4 major sections
- **500+ lines** of new architecture documentation
- **Multi-cloud deployment topology** (Local → Docker → Azure → GCP)
- **Data science agent system** fully documented **AND IMPLEMENTED (MVP)**
- **Azure internal services integration** documented (DataLoop, ATM, MEGA)
- **OpenAPI tool strategy** clarified (MCP vs ADK Built-in)

### Developer Benefits
- Clear understanding of what runs where (local vs Docker vs Azure vs GCP)
- Tool integration strategy for public vs internal services
- Step-by-step deployment paths for each component
- Visual roadmap from current state to multi-cloud deployment
- Sample configurations and table structures
- Security architecture for internal Azure access
- **Working data science agent scaffolding ready for data integration**

### Multi-Cloud Architecture Achievements
- ✅ **Azure integration**: 3 internal services with Private Endpoint networking (documented)
- ✅ **GCP planning**: Data warehouse + AI/ML platform documented
- ✅ **Tool strategy**: MCP for public APIs, ADK OpenAPI for internal services
- ✅ **Security**: Private network access, secure authentication patterns
- ✅ **Observability**: Extended tracing across multi-cloud components
- ✅ **Data Science MVP**: BigQuery + Analytics agents fully implemented

### Implementation Progress (Oct 24, 2025)
- ✅ **Data Science Root Coordinator**: Renamed to `data_science_root_agent` for clarity
- ✅ **System Root Agent**: Updated to include `data_science_root_agent` as sub-agent
- ✅ **BigQuery Agent**: NL2SQL with schema-aware query generation
- ✅ **Analytics Agent**: NL2Py with Vertex AI Code Interpreter
- ✅ **Configuration System**: JSON-based dataset definitions
- ✅ **Development Tooling**: Runner script, environment templates, README
- ✅ **Three-Level Hierarchy**: System Root → Domain Coordinators → Specialists

### Data Science Agent File Structure

```
backend/adk/agents/data_science/
├── __init__.py                           # Module exports (data_science_root_agent)
├── agent.py                              # Data science coordinator (140 lines)
├── prompts.py                            # Coordinator instructions (80 lines)
├── tools.py                              # Coordination tools (30 lines)
├── dnb_statistics_dataset_config.json    # Dataset config
├── .env.example                          # Environment template
├── README.md                             # Comprehensive documentation
└── sub_agents/
    ├── __init__.py
    ├── bigquery/
    │   ├── __init__.py
    │   ├── agent.py                      # BigQuery NL2SQL (95 lines)
    │   ├── prompts.py                    # Query instructions (50 lines)
    │   └── tools.py                      # Query utilities
    └── analytics/
        ├── __init__.py
        ├── agent.py                      # Analytics NL2Py (95 lines)
        └── prompts.py                    # Analytics instructions (50 lines)

backend/adk/agents/root_agent/
├── __init__.py                           # System root exports
├── agent.py                              # System orchestrator (integrates coordinators)
└── instructions.txt                      # System routing logic

backend/adk/run_data_science_agent.py     # Standalone CLI runner (180 lines)
```

**Total**: ~850 lines of production-ready code across 15 files

### Key Features Implemented

1. **Modular Architecture**
   - Clean separation between coordinator and sub-agents
   - Type-safe with Python type hints
   - Follows ADK best practices from official samples

2. **Schema-Aware Query Generation**
   - Automatic BigQuery schema introspection
   - Schema information passed to agent context
   - Reduces hallucination in SQL generation

3. **Stateful Code Execution**
   - Vertex AI Code Interpreter with persistent state
   - Data passed between agents via context
   - Supports multi-step analysis workflows

4. **Configuration-Driven**
   - JSON-based dataset definitions
   - Environment-based model selection
   - Easy to extend with new datasets

5. **Developer Experience**
   - Comprehensive README with examples
   - Interactive and single-query modes
   - Detailed error messages and logging
   - Environment variable validation

### Usage Examples

```powershell
# Interactive mode
python backend/adk/run_data_science_agent.py

# Single query mode
python backend/adk/run_data_science_agent.py --query "What tables are available?"

# Custom environment file
python backend/adk/run_data_science_agent.py --env-file /path/to/.env
```

### Integration Points

| Component | Integration Method | Status |
|-----------|-------------------|--------|
| BigQuery | ADK Built-in BigQueryToolset | ✅ Implemented |
| Code Interpreter | Vertex AI Extension | ✅ Implemented |
| Schema Introspection | google-cloud-bigquery client | ✅ Implemented |
| Dataset Config | JSON file loading | ✅ Implemented |
| Logging | Python logging module | ✅ Implemented |
| Environment | python-dotenv | ✅ Implemented |
| AlloyDB | MCP Toolbox (planned) | 📋 Ready to add |
| BQML | RAG + BQ ML API (planned) | 📋 Ready to add |

### Next Implementation Steps

1. **Data Integration** (Immediate)
   - Upload Bronze layer parquet to BigQuery
   - Verify table schemas and data quality
   - Test queries against actual DNB Statistics

2. **BQML Agent** (Next Sprint)
   - Implement RAG corpus for BigQuery ML reference docs
   - Create BQML-specific agent with model training tools
   - Add BQML examples to dataset config

3. **AlloyDB Agent** (Next Sprint)
   - Set up MCP Toolbox for Databases
   - Configure AlloyDB connection via toolbox
   - Implement cross-dataset query planning

4. **CHASE-SQL** (Future Enhancement)
   - Integrate CHASE-SQL methodology
   - Compare performance vs baseline Gemini
   - Make selectable via environment variable

---

*This enhancement sets the foundation for implementing the data science multi-agent system and cloud deployment strategy. The MVP implementation (Oct 24, 2025) provides a working BigQuery + Analytics agent system ready for data integration and further expansion.*
