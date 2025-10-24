# Orkhon Backend Architecture (Mermaid Diagrams)

> **Visual Architecture Documentation**  
> Comprehensive Mermaid diagrams illustrating the Orkhon backend system components, data flows, and interactions

---

## 📖 Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Agent Orchestration](#agent-orchestration)
- [Tool Integration](#tool-integration)
- [ETL Pipeline](#etl-pipeline)
- [Data Flow Patterns](#data-flow-patterns)
- [Data Science Agent Architecture](#data-science-agent-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Deployment Topology](#deployment-topology)

---

## System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph Frontend["🖥️ Frontend Layer"]
        ADK_UI["ADK Web UI<br/>(Angular SPA)<br/>Port: 4200"]
        Jaeger_UI["Jaeger Tracing UI<br/>(Observability)<br/>Port: 16686"]
    end

    subgraph Agents["🤖 Agent Orchestration Layer ✅ IMPLEMENTED"]
        direction TB
        Root["Root Agent<br/>(ADK LlmAgent)"]
        DNB_Coord["DNB Coordinator<br/>(Toolbox Path)"]
        DNB_OpenAPI_Coord["DNB OpenAPI Coordinator<br/>(OpenAPI Path)"]
        
        subgraph API_Agents["API Specialists ✅ WORKING"]
            Echo["Echo Agent"]
            Stats["Statistics Agent"]
            PR["Public Register Agent"]
        end
    end

    subgraph Tools["🔧 Tool Orchestration Layer ✅ IMPLEMENTED"]
        Toolbox["GenAI Toolbox<br/>MCP Server<br/>Port: 5000"]
        ToolConfig["Tool Configurations<br/>(YAML Definitions)<br/>84+ DNB Tools"]
        OTel["OpenTelemetry<br/>(Tracing)"]
    end

    subgraph External["🌐 External DNB Services (Public APIs) ✅ CONNECTED"]
        DNB_Echo["DNB Echo API<br/>(Testing)"]
        DNB_Stats["DNB Statistics API<br/>(v2024100101)"]
        DNB_PR["DNB Public Register API<br/>(v1)"]
        Jaeger["Jaeger Backend<br/>(Trace Storage)"]
    end

    subgraph Azure["☁️ Microsoft Azure (Internal DNB Services) 📋 PLANNED"]
        subgraph Azure_DB["🗄️ Databases (PRIMARY ACCESS)"]
            DataLoop_DB["DataLoop DB<br/>(SQL Server)<br/>IAM Auth"]
            ATM_DB["ATM DB<br/>(PostgreSQL)<br/>IAM Auth"]
            MEGA_DB["MEGA DB<br/>(SQL Server)<br/>IAM Auth"]
        end
        subgraph Azure_API["🔌 APIs (SECONDARY)"]
            DNB_DataLoop["DNB DataLoop API<br/>(Report Status)"]
            DNB_ATM["DNB ATM API<br/>(Models)"]
            DNB_MEGA["DNB MEGA API<br/>(Validations)"]
        end
        Azure_IAM["Azure IAM<br/>(Role-Based Access)"]
    end

    subgraph Build["🛠️ Development Tools"]
        OpenAPIBox["OpenAPI-Box<br/>(OpenAPI → Toolbox Converter)"]
        OpenAPI_Specs["OpenAPI 3.0 Specs<br/>(APIs/DNB/Specs)"]
    end

    subgraph ETL["📊 ETL Pipeline ✅ IMPLEMENTED"]
        Stats_ETL["Statistics ETL<br/>(17+ Extractors)"]
        PR_ETL["Public Register ETL<br/>(6 Extractors)"]
        Bronze["Bronze Layer<br/>(Parquet Files)"]
    end

    subgraph Cloud["☁️ Google Cloud Platform 📋 PLANNED"]
        GCS["Cloud Storage<br/>(Staging Bucket)"]
        BQ["BigQuery<br/>(Data Warehouse)"]
        AlloyDB["AlloyDB<br/>(PostgreSQL)"]
    end

    %% Connections - Implemented
    ADK_UI -.HTTP/WebSocket.-> Root
    Root --> DNB_Coord
    Root --> DNB_OpenAPI_Coord
    DNB_Coord --> API_Agents
    DNB_OpenAPI_Coord --> API_Agents
    API_Agents -.HTTP REST.-> Toolbox
    Toolbox --> ToolConfig
    Toolbox -.HTTPS.-> DNB_Echo
    Toolbox -.HTTPS.-> DNB_Stats
    Toolbox -.HTTPS.-> DNB_PR
    Toolbox -.OTLP/gRPC.-> OTel
    OTel --> Jaeger
    Jaeger_UI -.Query.-> Jaeger
    
    %% Connections - Planned (Azure Database Access)
    Toolbox -.IAM Auth.-> Azure_IAM
    Azure_IAM -.SQL Connection.-> DataLoop_DB
    Azure_IAM -.SQL Connection.-> ATM_DB
    Azure_IAM -.SQL Connection.-> MEGA_DB
    DataLoop_DB -.Backed by.-> DNB_DataLoop
    ATM_DB -.Backed by.-> DNB_ATM
    MEGA_DB -.Backed by.-> DNB_MEGA
    
    %% Build tools
    OpenAPIBox -.Generates.-> ToolConfig
    OpenAPI_Specs -.Input.-> OpenAPIBox
    
    Stats_ETL -.Extract.-> DNB_Stats
    PR_ETL -.Extract.-> DNB_PR
    Stats_ETL --> Bronze
    PR_ETL --> Bronze
    
    Bronze -.Upload.-> GCS
    GCS -.Load.-> BQ
    BQ -.Query.-> Root

    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef agent fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef tool fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef external fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef build fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef etl fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef cloud fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef azure fill:#bbdefb,stroke:#0d47a1,stroke-width:3px

    class ADK_UI,Jaeger_UI frontend
    class Root,DNB_Coord,DNB_OpenAPI_Coord,Echo,Stats,PR agent
    class Toolbox,ToolConfig,OTel tool
    class DNB_Echo,DNB_Stats,DNB_PR,Jaeger external
    class OpenAPIBox,OpenAPI_Specs build
    class Stats_ETL,PR_ETL,Bronze etl
    class GCS,BQ,AlloyDB cloud
    class DNB_DataLoop,DNB_ATM,DNB_MEGA azure
```

**Key Components:**
- **Frontend**: Angular-based UI for agent interaction ✅ **IMPLEMENTED**
- **Agents**: Multi-agent system built with Google ADK ✅ **IMPLEMENTED**
- **Tools**: MCP server managing 84+ public DNB API tools ✅ **IMPLEMENTED**
- **ETL**: Data extraction pipelines for analytics ✅ **IMPLEMENTED**
- **External**: Public DNB APIs and observability backend ✅ **CONNECTED**
- **Azure**: Internal DNB services with **database access (PRIMARY)** 📋 **PLANNED**
  - Database access granted FIRST via Azure IAM
  - API access as secondary option
  - Role-based access control required
- **Cloud**: GCP services for data warehouse and analytics 📋 **PLANNED**

---

## Azure Database Integration Architecture 📋 PLANNED

### Database-First Access Pattern

```mermaid
graph TB
    subgraph DNB_Infra["🏢 DNB Internal Infrastructure"]
        subgraph Agents_DNB["Agents (Copilot-based)"]
            DNB_Agent["Internal DNB Agents<br/>Model: GitHub Copilot<br/>Deployment: Azure Container Apps"]
        end
        
        subgraph IAM["🔐 Azure IAM"]
            RBAC["Role-Based Access Control"]
            ServicePrincipal["Service Principals"]
            ManagedIdentity["Managed Identities"]
        end
        
        subgraph Databases["🗄️ Primary Data Access"]
            DataLoop_DB_Detail["DataLoop Database<br/>Type: SQL Server<br/>Auth: Azure AD IAM<br/>Tables: Reports, Statuses, FI Data"]
            ATM_DB_Detail["ATM Database<br/>Type: PostgreSQL<br/>Auth: Azure AD IAM<br/>Tables: Models, Predictions"]
            MEGA_DB_Detail["MEGA Database<br/>Type: SQL Server<br/>Auth: Azure AD IAM<br/>Tables: Validations, Rules"]
        end
        
        subgraph APIs_Secondary["🔌 Secondary API Access"]
            DataLoop_API_Detail["DataLoop REST API<br/>OpenAPI 3.0<br/>HTTPS/JSON"]
            ATM_API_Detail["ATM REST API<br/>OpenAPI 3.0<br/>HTTPS/JSON"]
            MEGA_API_Detail["MEGA REST API<br/>OpenAPI 3.0<br/>HTTPS/JSON"]
        end
        
        subgraph A2A_Server["🔄 A2A Protocol Server"]
            A2A_Endpoint["A2A JSON-RPC Endpoint<br/>Agent Cards Published<br/>Cross-Org Communication"]
        end
    end
    
    %% IAM Authentication Flow
    DNB_Agent -->|1. Request Access| RBAC
    RBAC -->|2. Validate Role| ServicePrincipal
    ServicePrincipal -->|3. Grant Token| ManagedIdentity
    
    %% Primary Database Access
    ManagedIdentity -->|4. SQL Connection| DataLoop_DB_Detail
    ManagedIdentity -->|4. SQL Connection| ATM_DB_Detail
    ManagedIdentity -->|4. SQL Connection| MEGA_DB_Detail
    
    %% Secondary API Access
    DNB_Agent -.Optional.-> DataLoop_API_Detail
    DNB_Agent -.Optional.-> ATM_API_Detail
    DNB_Agent -.Optional.-> MEGA_API_Detail
    
    %% A2A Integration
    DNB_Agent -->|Expose via A2A| A2A_Endpoint
    
    classDef dnb_agent fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    classDef iam fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef database fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef api fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef a2a fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class DNB_Agent dnb_agent
    class RBAC,ServicePrincipal,ManagedIdentity iam
    class DataLoop_DB_Detail,ATM_DB_Detail,MEGA_DB_Detail database
    class DataLoop_API_Detail,ATM_API_Detail,MEGA_API_Detail api
    class A2A_Endpoint a2a
```

**Access Pattern Priority:**
1. **PRIMARY**: Direct database connections via Azure IAM (SQL Server/PostgreSQL)
2. **SECONDARY**: REST API access as fallback or for specific operations
3. **A2A Protocol**: Required for cross-organization agent communication

**IAM Requirements:**
- Service Principals for agent authentication
- Managed Identities for Azure resource access
- Role-Based Access Control (RBAC) for database permissions
- Token-based authentication with refresh

**Model Configuration:**
- **Local/External Deployment**: Google Gemini (gemini-2.5-flash, gemini-2.5-pro)
- **DNB Infrastructure**: GitHub Copilot (required by DNB policy)
- Configuration via environment variables

**A2A Protocol Requirements:**
- Agent cards (.well-known/agent.json) for each internal agent
- JSON-RPC 2.0 endpoints for agent-to-agent communication
- Authentication schemes for secure cross-org communication
- Task management and streaming support

---

## Component Architecture

### Directory Structure

```mermaid
graph LR
    subgraph Backend["backend/"]
        ADK["📁 adk/<br/>Agent Development Kit<br/>• Root Agent<br/>• API Coordinators<br/>• API Specialists<br/>• Workflows"]
        APIs["📁 apis/<br/>API Specifications<br/>• OpenAPI 3.0 Specs<br/>• Generated Docs<br/>• API Tests"]
        OpenAPIBox["📁 open-api-box/<br/>OpenAPI Converter<br/>• openapi_toolbox.py<br/>• Schema Validator"]
        Toolbox["📁 toolbox/<br/>MCP Server<br/>• Docker Compose<br/>• Tool Configs<br/>• Health Checks"]
        Clients["📁 clients/<br/>Kiota Clients<br/>• dnb-echo/<br/>• dnb-statistics/<br/>• dnb-public-register/"]
        ETL["📁 etl/<br/>ETL Pipelines<br/>• Statistics ETL<br/>• Public Register ETL<br/>• Orchestrators"]
        Scripts["📁 scripts/<br/>Automation<br/>• start-adk-web.ps1<br/>• generate-clients.ps1<br/>• diagnose-setup.ps1"]
        Data["📁 data/<br/>Data Layers<br/>• 1-bronze/ (Raw)<br/>• 2-silver/ (Cleaned)<br/>• 3-gold/ (Aggregated)"]
    end

    ADK -.Uses.-> Toolbox
    ADK -.Uses.-> Clients
    OpenAPIBox -.Generates.-> Toolbox
    APIs -.Input To.-> OpenAPIBox
    APIs -.Input To.-> Clients
    ETL -.Uses.-> Clients
    ETL -.Writes.-> Data

    classDef primary fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    classDef secondary fill:#c5e1a5,stroke:#558b2f,stroke-width:2px
    classDef utility fill:#ffccbc,stroke:#e64a19,stroke-width:2px
    
    class ADK,Toolbox primary
    class APIs,Clients,ETL secondary
    class OpenAPIBox,Scripts,Data utility
```

**Component Responsibilities:**
- **adk/**: AI agent logic and orchestration
- **apis/**: OpenAPI specs and documentation
- **open-api-box/**: Tool generation automation
- **clients/**: Kiota-generated API clients
- **etl/**: Data extraction pipelines
- **toolbox/**: Runtime tool execution
- **clients/**: Type-safe API clients (Kiota-generated)
- **etl/**: Data extraction and transformation
- **scripts/**: Development and deployment automation
- **data/**: Medallion architecture (Bronze/Silver/Gold layers)

---

## Agent Orchestration

### Multi-Agent Hierarchy

```mermaid
graph TB
    subgraph Root["🎯 Root Agent (gemini-2.0-flash)"]
        RA["root_agent<br/>Main System Coordinator<br/>Routes to Specialists"]
    end

    subgraph Coordinators["🎛️ Coordinator Layer"]
        DNB_Coord["dnb_coordinator<br/>(Toolbox Path)<br/>Routes to MCP Tools"]
        OpenAPI_Coord["dnb_openapi_coordinator<br/>(OpenAPI Path)<br/>Runtime Tool Generation"]
        Google_Coord["google_coordinator<br/>(COMING SOON)<br/>Google API Integration"]
        Data_Coord["data_coordinator<br/>(COMING SOON)<br/>Data Workflows"]
    end

    subgraph Specialists["🔧 Specialist Agents ✅ IMPLEMENTED"]
        direction LR
        Echo_TB["dnb_echo_agent<br/>ToolboxToolset<br/>• Connectivity Tests<br/>• Health Checks"]
        Stats_TB["dnb_statistics_agent<br/>ToolboxToolset<br/>• Market Data<br/>• Financial Stats<br/>• 79 endpoints"]
        PR_TB["dnb_public_register_agent<br/>ToolboxToolset<br/>• Entity Search<br/>• Publications<br/>• 5 endpoints"]
    end

    subgraph Azure_Specialists["☁️ Internal DNB Specialists 📋 PLANNED"]
        direction TB
        subgraph Azure_DB_Agents["Database-First Agents"]
            DataLoop_DB_Agent["dnb_dataloop_db_agent<br/>SQL Toolset (Azure IAM)<br/>• Report Status Queries<br/>• FI Communications Data"]
            ATM_DB_Agent["dnb_atm_db_agent<br/>PostgreSQL Toolset (Azure IAM)<br/>• Model Metadata Queries<br/>• Prediction History"]
            MEGA_DB_Agent["dnb_mega_db_agent<br/>SQL Toolset (Azure IAM)<br/>• Validation Rule Queries<br/>• Validation Results"]
        end
        subgraph Azure_API_Agents["API Fallback Agents"]
            DataLoop_API_Agent["dnb_dataloop_api_agent<br/>ADK OpenAPI Tool<br/>• REST Operations"]
            ATM_API_Agent["dnb_atm_api_agent<br/>ADK OpenAPI Tool<br/>• REST Operations"]
            MEGA_API_Agent["dnb_mega_api_agent<br/>ADK OpenAPI Tool<br/>• REST Operations"]
        end
        Azure_Note["Model: GitHub Copilot<br/>Deployment: DNB Azure<br/>Auth: Azure IAM + A2A"]
    end

    subgraph OpenAPI_Specialists["🆕 OpenAPI Specialists (Runtime Generation)"]
        direction LR
        Echo_OA["dnb_openapi_echo_agent<br/>OpenAPIToolset<br/>Runtime Generation"]
        Stats_OA["dnb_openapi_statistics_agent<br/>OpenAPIToolset<br/>Runtime Generation"]
        PR_OA["dnb_openapi_public_register_agent<br/>OpenAPIToolset<br/>Runtime Generation"]
    end

    subgraph Workflows["⚙️ Workflow Agents"]
        Sequential["data_pipeline<br/>SequentialAgent<br/>• Validate → Transform → Analyze"]
        Parallel["parallel_fetcher<br/>ParallelAgent<br/>• Fan-out/Fan-in Pattern"]
    end

    subgraph DataScience["🔬 Data Science Agents 📋 PLANNED"]
        direction LR
        BQ_Agent["bigquery_agent<br/>NL2SQL for BigQuery<br/>• CHASE-SQL / Baseline<br/>• Built-in BQ Tools"]
        AlloyDB_Agent["alloydb_agent<br/>NL2SQL for AlloyDB<br/>• MCP Toolbox<br/>• PostgreSQL Queries"]
        Analytics_Agent["analytics_agent<br/>NL2Py Analysis<br/>• Code Interpreter<br/>• Pandas/Plotting"]
        BQML_Agent["bqml_agent<br/>BigQuery ML<br/>• Model Training<br/>• RAG-based Reference"]
    end

    subgraph A2A_Integration["🔄 A2A Protocol Integration 📋 PLANNED"]
        A2A_Server["A2A JSON-RPC Server<br/>Agent Card Publishing<br/>Cross-Org Communication"]
        A2A_Client["A2A Client<br/>Remote Agent Access<br/>Task Management"]
    end

    RA --> DNB_Coord
    RA --> OpenAPI_Coord
    RA -.Future.-> Google_Coord
    RA -.Future.-> Data_Coord
    
    DNB_Coord --> Echo_TB
    DNB_Coord --> Stats_TB
    DNB_Coord --> PR_TB
    DNB_Coord -.Planned.-> DataLoop_DB_Agent
    DNB_Coord -.Planned.-> ATM_DB_Agent
    DNB_Coord -.Planned.-> MEGA_DB_Agent
    
    %% Database agents can fallback to API agents
    DataLoop_DB_Agent -.Fallback.-> DataLoop_API_Agent
    ATM_DB_Agent -.Fallback.-> ATM_API_Agent
    MEGA_DB_Agent -.Fallback.-> MEGA_API_Agent
    
    %% A2A Integration for Azure agents
    Azure_DB_Agents -.Expose via.-> A2A_Server
    A2A_Client -.Connect to.-> A2A_Server
    
    OpenAPI_Coord --> Echo_OA
    OpenAPI_Coord --> Stats_OA
    OpenAPI_Coord --> PR_OA
    
    Data_Coord -.-> Sequential
    Data_Coord -.-> Parallel
    Data_Coord -.-> BQ_Agent
    Data_Coord -.-> AlloyDB_Agent
    Data_Coord -.-> Analytics_Agent
    Data_Coord -.-> BQML_Agent

    classDef root fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef coordinator fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef specialist fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef azure_db fill:#bbdefb,stroke:#0d47a1,stroke-width:3px
    classDef azure_api fill:#c5cae9,stroke:#3f51b5,stroke-width:2px
    classDef openapi fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef workflow fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef datascience fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef a2a fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class RA root
    class DNB_Coord,OpenAPI_Coord,Google_Coord,Data_Coord coordinator
    class Echo_TB,Stats_TB,PR_TB specialist
    class DataLoop_DB_Agent,ATM_DB_Agent,MEGA_DB_Agent azure_db
    class DataLoop_API_Agent,ATM_API_Agent,MEGA_API_Agent,Azure_Note azure_api
    class Echo_OA,Stats_OA,PR_OA openapi
    class Sequential,Parallel workflow
    class BQ_Agent,AlloyDB_Agent,Analytics_Agent,BQML_Agent datascience
    class A2A_Server,A2A_Client a2a
```

**Agent Types:**
- **Root Agent**: Entry point ✅ **IMPLEMENTED**
- **Coordinators**: Domain routing ✅ **IMPLEMENTED** (DNB), 📋 **PLANNED** (Google, Data)
- **Specialists**: Public APIs ✅ **IMPLEMENTED** (Echo, Stats, PR)
- **Azure Database Agents**: Direct DB access via IAM 📋 **PLANNED**
- **Azure API Agents**: REST API fallback 📋 **PLANNED**
- **Workflows**: Orchestration patterns 📋 **PLANNED**
- **Data Science**: Analytics system 📋 **PLANNED**
- **A2A Protocol**: Cross-org communication 📋 **PLANNED**

**Azure Agent Requirements (DNB Infrastructure):**
- **Model**: GitHub Copilot (DNB policy, not Gemini)
- **Authentication**: Azure IAM + Managed Identities
- **Primary**: Direct database connections (SQL Server/PostgreSQL)
- **Secondary**: REST APIs as fallback
- **Protocol**: A2A JSON-RPC for agent cards + cross-org communication
- **Deployment**: Azure Container Apps

**Agent Communication:**
- Uses `transfer_to_agent()` for delegation
- State sharing via `output_key` parameter
- Coordinators aggregate specialist results

---

### OpenAPI Tool Integration Strategy

The Orkhon backend uses **three different approaches** for integrating with DNB services:

#### 1. **GenAI Toolbox (MCP Server)** - For Public DNB APIs ✅ **IMPLEMENTED**
- **Source**: Go-based MCP server from Google GenAI Toolbox project
- **Usage**: External public APIs (Echo, Statistics, Public Register)
- **Workflow**:
  1. OpenAPI spec → `openapi_toolbox.py` converter
  2. Generates YAML tool definitions
  3. Loaded by Toolbox MCP server at runtime
  4. Agents invoke via `ToolboxToolset`
- **Benefits**: 
  - Centralized tool management
  - Observability with OpenTelemetry
  - Runtime tool discovery
  - Works with any HTTP/REST API

#### 2. **Database Toolsets (SQL)** - For Internal Azure Services (PRIMARY) 📋 **PLANNED**
- **Source**: ADK SQL/PostgreSQL toolsets with Azure IAM
- **Usage**: Internal DNB databases (DataLoop DB, ATM DB, MEGA DB)
- **Workflow**:
  1. Azure IAM authentication with Managed Identity
  2. Direct SQL connections to databases
  3. Agents use SQL toolsets for queries
  4. Type-safe query generation
- **Benefits**:
  - Direct database access (faster than REST)
  - Full query capabilities (JOIN, aggregate, etc.)
  - IAM-based security
  - Connection pooling
- **Model Requirement**: GitHub Copilot for DNB infrastructure deployment

#### 3. **ADK Built-in OpenAPI Tool** - For Internal Azure APIs (FALLBACK) 📋 **PLANNED**
- **Source**: Agent Development Kit (google.adk) built-in OpenAPI toolset
- **Usage**: Internal DNB REST APIs (DataLoop API, ATM API, MEGA API) - used as fallback
- **Workflow**:
  1. OpenAPI spec provided directly to agent
  2. Agent generates tool definitions at runtime
  3. No external toolbox server required
  4. Direct HTTP requests from agent
- **Benefits**:
  - Lower latency (no MCP hop)
  - Simplified architecture
  - Runtime spec updates
  - Secure internal network access
**When to Use Which:**

| Approach | Use Case | Access Pattern | Status |
|----------|----------|----------------|---------|
| **GenAI Toolbox** | External public APIs | HTTP/REST | ✅ **IMPLEMENTED** |
| **Database Toolsets** | Internal Azure databases (PRIMARY) | SQL over IAM | 📋 **PLANNED** |
| **ADK OpenAPI Tool** | Internal Azure APIs (FALLBACK) | HTTP/REST | 📋 **PLANNED** |

**Azure Services Strategy:**
1. **First**: Connect to databases directly via Azure IAM auth
2. **Then**: Use REST APIs as fallback for specific operations
3. **Always**: Use GitHub Copilot as model for DNB infrastructure agents
4. **Required**: A2A protocol for cross-organization communication

---

## Tool Integration

### Tool Lifecycle

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Spec as OpenAPI Specs
    participant OpenAPIBox as OpenAPI-Box Converter
    participant YAML as Tool YAML Configs
    participant Docker as Docker Compose
    participant Toolbox as GenAI Toolbox
    participant Agent as ADK Agent
    participant API as DNB API

    Dev->>Spec: 1. Update OpenAPI spec
    Dev->>OpenAPIBox: 2. Run conversion
    OpenAPIBox->>Spec: 3. Parse spec
    OpenAPIBox->>YAML: 4. Generate tool definitions
    Note over YAML: 84+ tools defined<br/>• dnb-echo-* (3)<br/>• dnb-statistics-* (79)<br/>• dnb-public-register-* (5)
    
    Dev->>Docker: 5. Restart container
    Docker->>Toolbox: 6. Start MCP server
    Toolbox->>YAML: 7. Load configs
    Toolbox-->>Toolbox: 8. Register tools
    
    Agent->>Toolbox: 9. Discover tools (GET /api/toolset)
    Toolbox-->>Agent: 10. Return tool list + schemas
    
    Agent->>Toolbox: 11. Invoke tool (POST /api/tool/{name}/invoke)
    Toolbox->>API: 12. HTTP request + auth
    API-->>Toolbox: 13. Response
    Toolbox->>Toolbox: 14. Create trace span
    Toolbox-->>Agent: 15. Return result
```

**Tool Definition Structure:**

```yaml
# Example: dnb-echo-helloworld
tools:
  - name: dnb-echo-helloworld
    description: Get hello world message from DNB Echo API
    http:
      url: https://api.dnb.nl/echo-api/helloworld
      method: GET
      headers:
        Ocp-Apim-Subscription-Key: ${DNB_SUBSCRIPTION_KEY_DEV}
        Accept: application/json
```

---

### Toolbox Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        ADK_Agent["ADK Agent<br/>(ToolboxToolset)"]
        LangGraph["LangGraph Agent<br/>(ToolboxClient)"]
    end

    subgraph Toolbox_MCP["GenAI Toolbox MCP Server (Port 5000)"]
        direction TB
        API_Layer["REST API Layer<br/>• /api/toolset<br/>• /api/tools<br/>• /api/tool/{name}/invoke"]
        
        Registry["Tool Registry<br/>• Schema Validation<br/>• Tool Discovery<br/>• Toolset Grouping"]
        
        Executor["HTTP Executor<br/>• Request Building<br/>• Auth Injection<br/>• Response Parsing"]
        
        Telemetry["OpenTelemetry<br/>• Span Creation<br/>• Trace Context<br/>• OTLP Export"]
    end

    subgraph Config["Configuration Layer"]
        DevConfig["config/dev/<br/>• dnb-echo-tools.yaml<br/>• dnb-statistics-tools.yaml<br/>• dnb-public-register-tools.yaml"]
        ProdConfig["config/prod/<br/>• Production configs<br/>• Different endpoints"]
    end

    subgraph External_APIs["External APIs"]
        Echo_API["Echo API<br/>(3 endpoints)"]
        Stats_API["Statistics API<br/>(79 endpoints)"]
        PR_API["Public Register API<br/>(5 endpoints)"]
    end

    subgraph Observability["Observability"]
        Jaeger["Jaeger<br/>Port: 4318 (OTLP)<br/>Port: 16686 (UI)"]
    end

    %% Connections
    ADK_Agent --> API_Layer
    LangGraph --> API_Layer
    
    API_Layer --> Registry
    Registry --> Executor
    Executor --> Telemetry
    
    DevConfig -.Loaded at startup.-> Registry
    ProdConfig -.Loaded at startup.-> Registry
    
    Executor -.HTTPS + API Key.-> Echo_API
    Executor -.HTTPS + API Key.-> Stats_API
    Executor -.HTTPS + API Key.-> PR_API
    
    Telemetry -.OTLP/gRPC.-> Jaeger

    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef toolbox fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef config fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef api fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef obs fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class ADK_Agent,LangGraph client
    class API_Layer,Registry,Executor,Telemetry toolbox
    class DevConfig,ProdConfig config
    class Echo_API,Stats_API,PR_API api
    class Jaeger obs
```

**Toolbox Responsibilities:**
1. **Tool Management**: Register, validate, and discover tools
2. **Request Handling**: Build HTTP requests with authentication
3. **Observability**: Create distributed traces for debugging
4. **Schema Validation**: Ensure requests match tool definitions

---

## Data Science Agent Architecture

### Multi-Agent Data Analysis System (PLANNED)

```mermaid
graph TB
    subgraph User["👤 User Interface"]
        User_Input["Natural Language Query<br/>e.g., 'What are total sales by country?'"]
    end

    subgraph Root_Layer["🎯 Root Agent"]
        Data_Coord["data_coordinator<br/>Routes to appropriate sub-agent"]
    end

    subgraph Data_Sources["💾 Data Sources"]
        direction TB
        BQ_DS["BigQuery Datasets<br/>• dnb_statistics<br/>• flights_dataset<br/>• forecasting_sticker_sales"]
        AlloyDB_DS["AlloyDB Database<br/>• flights_dataset<br/>• PostgreSQL Tables"]
    end

    subgraph Sub_Agents["🔬 Specialized Sub-Agents"]
        direction TB
        
        subgraph BQ_Sub["BigQuery Sub-Agent"]
            BQ_Agent["bigquery_agent<br/>NL2SQL Translation"]
            BQ_Tools["Built-in BigQuery Tools<br/>• Query Execution<br/>• Schema Discovery"]
            BQ_CHASE["CHASE-SQL<br/>(Optional)<br/>Advanced NL2SQL"]
        end
        
        subgraph AlloyDB_Sub["AlloyDB Sub-Agent"]
            AlloyDB_Agent["alloydb_agent<br/>NL2SQL Translation"]
            MCP_Toolbox["MCP Toolbox for Databases<br/>• PostgreSQL Queries<br/>• Schema Introspection"]
        end
        
        subgraph Analytics_Sub["Analytics Sub-Agent"]
            Analytics_Agent["analytics_agent<br/>NL2Py Analysis"]
            Code_Interp["Code Interpreter Extension<br/>• Pandas Operations<br/>• Matplotlib/Seaborn<br/>• Data Visualization"]
        end
        
        subgraph BQML_Sub["BQML Sub-Agent"]
            BQML_Agent["bqml_agent<br/>ML Model Management"]
            BQML_RAG["RAG-based Reference Guide<br/>• BQML Documentation<br/>• Model Selection"]
        end
    end

    subgraph Cross_Dataset["🔗 Cross-Dataset Capabilities"]
        FK_Relations["Foreign Key Relations<br/>Dataset Configuration<br/>• cross_dataset_relations.json"]
        Join_Logic["Cross-Dataset Joins<br/>BigQuery ↔ AlloyDB"]
    end

    User_Input --> Data_Coord
    Data_Coord --> BQ_Agent
    Data_Coord --> AlloyDB_Agent
    Data_Coord --> Analytics_Agent
    Data_Coord --> BQML_Agent
    
    BQ_Agent --> BQ_Tools
    BQ_Agent -.Optional.-> BQ_CHASE
    BQ_Tools --> BQ_DS
    
    AlloyDB_Agent --> MCP_Toolbox
    MCP_Toolbox --> AlloyDB_DS
    
    Analytics_Agent --> Code_Interp
    Code_Interp -.Reads from.-> BQ_DS
    Code_Interp -.Reads from.-> AlloyDB_DS
    
    BQML_Agent --> BQML_RAG
    BQML_Agent --> BQ_DS
    
    FK_Relations --> BQ_Agent
    FK_Relations --> AlloyDB_Agent
    BQ_Agent -.Cross-Join.-> Join_Logic
    AlloyDB_Agent -.Cross-Join.-> Join_Logic

    classDef user fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef coordinator fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef agent fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef tool fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef datasource fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef config fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class User_Input user
    class Data_Coord coordinator
    class BQ_Agent,AlloyDB_Agent,Analytics_Agent,BQML_Agent agent
    class BQ_Tools,MCP_Toolbox,Code_Interp,BQML_RAG,BQ_CHASE tool
    class BQ_DS,AlloyDB_DS datasource
    class FK_Relations,Join_Logic config
```

**Key Features:**
- **Multi-Agent Architecture**: Specialized agents for different data analysis tasks
- **Database Interaction (NL2SQL)**: Translate natural language to SQL for BigQuery and AlloyDB
- **Data Science Analysis (NL2Py)**: Python-based analysis and visualization
- **Machine Learning (BQML)**: Train and evaluate ML models in BigQuery
- **Cross-Dataset Joins**: Query across BigQuery and AlloyDB using foreign key relationships

---

### Data Science Agent Tools & Technologies

```mermaid
mindmap
  root((Data Science<br/>Multi-Agent))
    Database Agents
      BigQuery Agent
        Built-in BQ Tools
        CHASE-SQL
        Schema Discovery
      AlloyDB Agent
        MCP Toolbox
        PostgreSQL Protocol
        Connection Pooling
    Analytics Agent
      Code Interpreter
        Pandas DataFrame
        NumPy Arrays
        Matplotlib Plots
        Seaborn Visualizations
      Python Execution
        Isolated Sandbox
        Base64 File I/O
    BQML Agent
      Model Training
        ARIMA_PLUS
        ARIMA_PLUS_XREG
        Forecasting Models
      RAG System
        BQML Reference Guide
        Vertex AI RAG Engine
        Model Selection Help
    Configuration
      Dataset Config
        JSON Format
        Multiple Sources
      Cross-Dataset Relations
        Foreign Keys
        Join Specifications
```

---

### Sample Dataset Configurations

#### Cymbal Airlines Flights Dataset

```mermaid
erDiagram
    BIGQUERY {
        string dataset "flights_dataset"
    }
    ALLOYDB {
        string database "flights_dataset"
    }
    
    FLIGHT_HISTORY ||--o{ TICKET_SALES : "flight_id"
    CYMBALAIR_POLICIES ||--o{ TICKET_SALES : "policy_id"
    
    FLIGHT_HISTORY {
        int flight_id PK
        date flight_date
        string origin
        string destination
        int duration_minutes
    }
    
    TICKET_SALES {
        int ticket_id PK
        int flight_id FK
        int policy_id FK
        decimal price
        date purchase_date
    }
    
    CYMBALAIR_POLICIES {
        int policy_id PK
        string policy_name
        string policy_description
        decimal discount_percentage
    }
    
    BIGQUERY ||--|| FLIGHT_HISTORY : "stores"
    BIGQUERY ||--|| CYMBALAIR_POLICIES : "stores"
    BIGQUERY ||--|| TICKET_SALES : "stores"
    ALLOYDB ||--|| FLIGHT_HISTORY : "stores (duplicate)"
```

**Cross-Dataset Configuration:**
```json
{
  "datasets": [
    {
      "type": "bigquery",
      "name": "flights_dataset",
      "description": "Flight history and ticket sales for Cymbal Airlines"
    },
    {
      "type": "alloydb",
      "name": "flights_dataset",
      "description": "Flight history in AlloyDB (demonstrates cross-DB joins)"
    }
  ],
  "cross_dataset_relations": {
    "foreign_keys": [
      {
        "child": {
          "type": "bigquery",
          "dataset": "flights_dataset",
          "table": "ticket_sales",
          "column": "flight_id"
        },
        "parent": {
          "type": "alloydb",
          "dataset": "flights_dataset",
          "table": "flight_history",
          "column": "flight_id"
        }
      }
    ]
  }
}
```

---

### Data Science Agent Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Root as root_agent
    participant DataCoord as data_coordinator
    participant BQAgent as bigquery_agent
    participant BQTool as Built-in BQ Tool
    participant BigQuery as BigQuery API
    participant Analytics as analytics_agent
    participant CodeInterp as Code Interpreter

    User->>Root: "What are total sales by country? Generate a plot."
    Root->>DataCoord: Route to data coordinator
    DataCoord->>DataCoord: Analyze intent: SQL query + visualization
    
    Note over DataCoord,BQAgent: Step 1: Fetch Data from BigQuery
    DataCoord->>BQAgent: Query for total sales by country
    BQAgent->>BQAgent: Generate SQL (NL2SQL)
    BQAgent->>BQTool: Execute query
    BQTool->>BigQuery: Run SQL query
    BigQuery-->>BQTool: Return results
    BQTool-->>BQAgent: Query results (DataFrame)
    BQAgent-->>DataCoord: Sales data by country
    
    Note over DataCoord,Analytics: Step 2: Generate Visualization
    DataCoord->>Analytics: Create bar plot of sales by country
    Analytics->>Analytics: Generate Python code (NL2Py)
    Analytics->>CodeInterp: Execute plotting code
    CodeInterp->>CodeInterp: Import matplotlib/pandas
    CodeInterp->>CodeInterp: Create bar chart
    CodeInterp->>CodeInterp: Encode as base64
    CodeInterp-->>Analytics: Plot image (base64)
    Analytics-->>DataCoord: Visualization ready
    
    DataCoord-->>Root: Aggregated results + plot
    Root-->>User: "Here are total sales by country [BAR CHART]"
```

---

### BigQuery Deployment Pipeline

```mermaid
flowchart LR
    subgraph Local["💻 Local Development"]
        ETL["ETL Extractors<br/>backend/etl/"]
        Bronze["Bronze Layer<br/>data/1-bronze/<br/>Parquet Files"]
    end

    subgraph Deploy["🚀 Deployment Scripts"]
        Deploy_Script["deploy_to_bigquery.py<br/>• Load Parquet to GCS<br/>• Create BQ Tables<br/>• Set Partitioning"]
        Service_Acct["GCP Service Account<br/>• bigquery.dataEditor<br/>• bigquery.jobUser"]
    end

    subgraph GCP["☁️ Google Cloud Platform"]
        GCS["Cloud Storage<br/>gs://dnb-data/bronze/<br/>Staging Area"]
        BQ_Dataset["BigQuery Dataset<br/>dnb_statistics<br/>• Partitioned Tables<br/>• Clustered Keys"]
    end

    subgraph Tables["📊 BigQuery Tables"]
        Ins_Corps["insurance_pensions__insurers__<br/>insurance_corps_balance_sheet_quarter"]
        Pension["insurance_pensions__pension_funds__<br/>pension_funds_balance_sheet"]
        Rates["financial_markets__<br/>exchange_rates"]
        More["+ 15 more tables"]
    end

    ETL --> Bronze
    Bronze --> Deploy_Script
    Deploy_Script -.Authenticate.-> Service_Acct
    Deploy_Script --> GCS
    GCS --> BQ_Dataset
    BQ_Dataset --> Ins_Corps
    BQ_Dataset --> Pension
    BQ_Dataset --> Rates
    BQ_Dataset --> More

    classDef local fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef deploy fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef cloud fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef tables fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    
    class ETL,Bronze local
    class Deploy_Script,Service_Acct deploy
    class GCS,BQ_Dataset cloud
    class Ins_Corps,Pension,Rates,More tables
```

**Deployment Process:**

1. **Local ETL**: Extract DNB data to Parquet (Bronze layer)
2. **Upload to GCS**: Stage Parquet files in Cloud Storage bucket
3. **Load to BigQuery**: Use `bq load` or Python BigQuery client
4. **Configure Tables**:
   - Partition by `period` column
   - Cluster by business keys (e.g., `category`, `subcategory`)
   - Set schema enforcement

**Table Naming Convention:**
```
{category}__{subcategory}__{endpoint_name}
```

Examples:
- `insurance_pensions__insurers__insurance_corps_balance_sheet_quarter`
- `financial_markets__interest_rates__market_interest_rates`
- `financial_markets__bond_yields__dutch_state_loans`

---

## ETL Pipeline

### ETL Architecture Overview

```mermaid
graph LR
    subgraph Sources["📡 Data Sources"]
        Echo["Echo API<br/>(Testing)"]
        Stats["Statistics API<br/>17+ Datasets"]
        PR["Public Register API<br/>6 Categories"]
    end

    subgraph Clients["🔌 Kiota Clients"]
        Echo_Client["DnbEchoClient<br/>(Type-safe)"]
        Stats_Client["DnbStatisticsClient<br/>(Type-safe)"]
        PR_Client["DnbPublicRegisterClient<br/>(Type-safe)"]
    end

    subgraph ETL_Pipelines["⚙️ ETL Pipelines"]
        direction TB
        Stats_ETL["Statistics ETL<br/>• 17+ Extractors<br/>• Smart Pagination<br/>• Metadata Tracking"]
        PR_ETL["Public Register ETL<br/>• 6 Extractors<br/>• Multi-register Support<br/>• Multi-language"]
    end

    subgraph Orchestration["🎛️ Orchestration"]
        Stats_Orch["Statistics Orchestrator<br/>• --all / --endpoints<br/>• --category<br/>• --dry-run"]
        PR_Orch["Public Register Orchestrator<br/>• --metadata / --organizations<br/>• --publications / --registrations<br/>• --register / --language"]
    end

    subgraph Storage["💾 Data Lake (Medallion)"]
        Bronze["🥉 Bronze Layer<br/>data/1-bronze/<br/>• Raw Parquet Files<br/>• Directly from API<br/>• Append-only"]
        Silver["🥈 Silver Layer<br/>data/2-silver/<br/>• Cleaned & Deduplicated<br/>• Type-safe Schemas<br/>(PLANNED)"]
        Gold["🥇 Gold Layer<br/>data/3-gold/<br/>• Business Aggregations<br/>• Analytics-ready<br/>(PLANNED)"]
    end

    %% Connections
    Stats --> Stats_Client
    PR --> PR_Client
    Echo --> Echo_Client
    
    Stats_Client --> Stats_ETL
    PR_Client --> PR_ETL
    
    Stats_ETL --> Stats_Orch
    PR_ETL --> PR_Orch
    
    Stats_Orch --> Bronze
    PR_Orch --> Bronze
    
    Bronze -.Transform.-> Silver
    Silver -.Aggregate.-> Gold

    classDef source fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef client fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef etl fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef orch fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef storage fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class Echo,Stats,PR source
    class Echo_Client,Stats_Client,PR_Client client
    class Stats_ETL,PR_ETL etl
    class Stats_Orch,PR_Orch orch
    class Bronze,Silver,Gold storage
```

**ETL Features:**
- **Type-Safe Clients**: Kiota-generated from OpenAPI specs
- **Smart Pagination**: Automatic handling of paginated responses
- **Metadata Tracking**: Extraction history and lineage
- **Incremental Updates**: Checkpoint-based resumption
- **Multi-format**: Parquet for analytics, JSON for exploration

---

### Statistics ETL Pipeline

```mermaid
graph TB
    subgraph Input["📥 Input"]
        API["DNB Statistics API<br/>v2024100101"]
    end

    subgraph Extractors["🔧 Extractors (17+)"]
        direction LR
        ExchangeRates["Exchange Rates<br/>(Day/Week/Month)"]
        InterestRates["Interest Rates<br/>(Market/Policy)"]
        Securities["Securities<br/>(Bond Yields)"]
        BankStats["Bank Statistics<br/>(Assets/Liabilities)"]
        Other["+ 10 more endpoints"]
    end

    subgraph BaseClass["🏗️ Base Classes"]
        PaginatedExtractor["PaginatedExtractor<br/>• Smart pagination<br/>• Rate limiting<br/>• Error handling"]
        Metadata["Metadata Tracker<br/>• Extraction history<br/>• Record counts<br/>• Timestamps"]
    end

    subgraph Orchestrator["🎛️ Orchestrator"]
        CLI["CLI Interface<br/>--all / --endpoints<br/>--category / --list"]
        Coordinator["Coordinator<br/>• Parallel execution<br/>• Error recovery<br/>• Progress logging"]
    end

    subgraph Output["📤 Output"]
        Parquet["Parquet Files<br/>data/1-bronze/market_data/<br/>data/1-bronze/financial_statistics/"]
        MetadataFile["extraction_metadata.json<br/>• Last run timestamp<br/>• Record counts<br/>• File paths"]
    end

    API --> Extractors
    Extractors --> PaginatedExtractor
    PaginatedExtractor --> Metadata
    
    CLI --> Coordinator
    Coordinator --> Extractors
    
    Extractors --> Parquet
    Metadata --> MetadataFile

    classDef input fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef extractor fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef base fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef orch fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class API input
    class ExchangeRates,InterestRates,Securities,BankStats,Other extractor
    class PaginatedExtractor,Metadata base
    class CLI,Coordinator orch
    class Parquet,MetadataFile output
```

**Key Extractors:**
- `ExchangeRatesExtractor` - EUR/USD, Gold prices
- `MarketInterestRatesExtractor` - EURIBOR, EONIA
- `BondYieldsExtractor` - Dutch government bonds
- `BankStatisticsExtractor` - Balance sheet items
- 13+ more specialized extractors

---

### Public Register ETL Pipeline

```mermaid
graph TB
    subgraph Input["📥 Input"]
        API["DNB Public Register API<br/>v1"]
    end

    subgraph Discovery["🔍 Discovery Phase"]
        Registers["RegistersExtractor<br/>• Discover all registers<br/>• WFTAF, WFT, etc."]
        Languages["LanguagesExtractor<br/>• Supported languages<br/>• NL, EN"]
    end

    subgraph Organizations["🏢 Organizations Phase"]
        RelationNums["RelationNumbersExtractor<br/>• Get org IDs per register<br/>• Paginated (max 1000/page)"]
        OrgDetails["OrganizationDetailsExtractor<br/>• Full org data<br/>• Batch: 25 IDs/request"]
    end

    subgraph Publications["📰 Publications Phase"]
        PubSearch["PublicationsSearchExtractor<br/>• Search across all publications<br/>• Filter by register/language"]
        PubDetails["PublicationDetailsExtractor<br/>• Get full publication data<br/>• Per register"]
    end

    subgraph Registrations["📝 Registrations Phase"]
        ActArticles["ActArticleNamesExtractor<br/>• Regulatory metadata<br/>• Per register + language"]
        RegisterArticles["RegisterArticlesExtractor<br/>• Act articles<br/>• Per register"]
    end

    subgraph Orchestrator["🎛️ Orchestrator"]
        CLI["CLI Interface<br/>--metadata / --organizations<br/>--publications / --registrations<br/>--register / --language"]
    end

    subgraph Output["📤 Output"]
        Bronze["Parquet Files<br/>• metadata/ (registers, languages)<br/>• organizations/ (relation_numbers, details)<br/>• publications/ (search, details)<br/>• registrations/ (act_articles)<br/>• register_articles/"]
    end

    API --> Discovery
    Discovery --> Organizations
    Discovery --> Publications
    Discovery --> Registrations
    
    Registers --> RelationNums
    RelationNums --> OrgDetails
    
    Registers --> PubSearch
    PubSearch --> PubDetails
    
    Registers --> ActArticles
    Registers --> RegisterArticles
    
    CLI --> Discovery
    CLI --> Organizations
    CLI --> Publications
    CLI --> Registrations
    
    Organizations --> Bronze
    Publications --> Bronze
    Registrations --> Bronze
    Discovery --> Bronze

    classDef input fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef discovery fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef org fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef pub fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef reg fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef orch fill:#ffccbc,stroke:#d84315,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class API input
    class Registers,Languages discovery
    class RelationNums,OrgDetails org
    class PubSearch,PubDetails pub
    class ActArticles,RegisterArticles reg
    class CLI orch
    class Bronze output
```

**Extraction Flow:**
1. **Discovery**: Find all registers and languages
2. **Organizations**: Get IDs → Fetch full details (batch of 25)
3. **Publications**: Search → Extract details per register
4. **Registrations**: Get regulatory metadata
5. **All write to Parquet**: Data lake ready for analytics

---

## Data Flow Patterns

### Agent Query Flow (End-to-End)

```mermaid
sequenceDiagram
    participant User
    participant ADK_UI as ADK Web UI
    participant Root as Root Agent
    participant Coord as DNB Coordinator
    participant Specialist as Statistics Agent
    participant Toolbox as GenAI Toolbox
    participant DNB as DNB Statistics API
    participant Jaeger as Jaeger Tracing

    User->>ADK_UI: 1. "Get latest EUR/USD exchange rate"
    ADK_UI->>Root: 2. WebSocket message
    Root->>Root: 3. Analyze intent (Gemini)
    Root->>Coord: 4. transfer_to_agent(dnb_coordinator)
    
    Coord->>Coord: 5. Determine specialist (Statistics)
    Coord->>Specialist: 6. transfer_to_agent(dnb_statistics_agent)
    
    Specialist->>Toolbox: 7. GET /api/toolset/dnb_statistics_tools
    Toolbox-->>Specialist: 8. Return 79 tools + schemas
    
    Specialist->>Specialist: 9. Gemini selects tool:<br/>dnb-statistics-exchange-rates-day
    
    Specialist->>Toolbox: 10. POST /api/tool/{name}/invoke<br/>{startDate, endDate}
    
    Toolbox->>Jaeger: 11. Create trace span
    Toolbox->>DNB: 12. HTTPS GET + API key
    DNB-->>Toolbox: 13. JSON response (exchange rates)
    Toolbox->>Jaeger: 14. Export span
    Toolbox-->>Specialist: 15. Return structured data
    
    Specialist->>Specialist: 16. Format results (Gemini)
    Specialist-->>Coord: 17. Return via output_key
    Coord-->>Root: 18. Aggregate results
    Root-->>ADK_UI: 19. Natural language response
    ADK_UI-->>User: 20. "EUR/USD: 1.08 as of Oct 23, 2025"
```

**Key Points:**
- **Reason-Act Loop**: Gemini analyzes → selects tools → interprets results
- **Transfer Pattern**: Root → Coordinator → Specialist (delegation chain)
- **Output Keys**: Agents share state via named outputs
- **Tracing**: Every tool invocation creates an OTLP span

---

### ETL Data Flow

```mermaid
flowchart TB
    Start([Developer runs ETL])
    
    subgraph Orchestrator["🎛️ Orchestrator"]
        CLI{Parse CLI Args}
        DryRun{Dry Run?}
        SelectEndpoints["Select Endpoints<br/>--all / --endpoints / --category"]
    end
    
    subgraph Extractor["🔧 Extractor"]
        Init["Initialize Extractor<br/>• Create Kiota client<br/>• Setup rate limiter"]
        Extract["Extract Data<br/>• Call API<br/>• Handle pagination<br/>• Parse responses"]
        Transform["Transform Records<br/>• Add ETL metadata<br/>• Flatten nested JSON<br/>• Type conversions"]
    end
    
    subgraph Storage["💾 Storage"]
        Validate["Validate Schema<br/>• Check required fields<br/>• Validate types"]
        WriteParquet["Write Parquet<br/>• Partition by category<br/>• Compress (snappy)<br/>• Add metadata"]
        UpdateMetadata["Update Metadata File<br/>• Extraction timestamp<br/>• Record count<br/>• File path"]
    end
    
    End([Complete])
    
    Start --> CLI
    CLI --> DryRun
    DryRun -->|Yes| ShowPlan["Show Extraction Plan"]
    ShowPlan --> End
    DryRun -->|No| SelectEndpoints
    SelectEndpoints --> Init
    
    Init --> Extract
    Extract --> Transform
    Transform --> Validate
    Validate --> WriteParquet
    WriteParquet --> UpdateMetadata
    UpdateMetadata --> End

    classDef orch fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef extract fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef storage fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef terminal fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    
    class CLI,DryRun,SelectEndpoints orch
    class Init,Extract,Transform extract
    class Validate,WriteParquet,UpdateMetadata storage
    class Start,End terminal
```

**ETL Features:**
- **Smart Pagination**: Automatically handles large result sets
- **Rate Limiting**: Respects API limits (configurable)
- **Error Recovery**: Checkpoint-based resumption on failure
- **Metadata Tracking**: Full lineage of extractions
- **Incremental Updates**: Skip already-extracted data

---

## Deployment Architecture

### Docker Compose Stack

```mermaid
graph TB
    subgraph Docker["🐳 Docker Compose (docker-compose.dev.yml)"]
        direction TB
        
        subgraph Network["orkhon-network (Bridge)"]
            Toolbox["genai-toolbox-mcp<br/>Port: 5000<br/>Image: genai-toolbox:dev<br/>Env: DEV"]
            
            Jaeger["jaeger<br/>Ports: 4318 (OTLP), 16686 (UI)<br/>Image: jaegertracing/all-in-one:latest<br/>Storage: In-memory"]
            
            Postgres["postgres<br/>Port: 5432<br/>Image: postgres:15<br/>Volume: postgres_data"]
        end
        
        subgraph Volumes["Volumes"]
            ToolConfig["./config → /app/config"]
            PostgresData["postgres_data"]
        end
    end

    subgraph Host["💻 Host Machine"]
        ADK_Web["ADK Web<br/>Port: 4200<br/>Angular Dev Server"]
        Python_Agents["Python Agents<br/>• LangGraph<br/>• ADK Agents<br/>Virtual env: .venv"]
        Browser["Web Browser<br/>• http://localhost:5000/ui<br/>• http://localhost:16686"]
    end

    %% Connections
    Toolbox --> Jaeger
    Toolbox --> Postgres
    ToolConfig -.Mount.-> Toolbox
    PostgresData -.Mount.-> Postgres
    
    ADK_Web -.HTTP.-> Python_Agents
    Python_Agents -.HTTP.-> Toolbox
    Browser -.HTTP.-> Toolbox
    Browser -.HTTP.-> Jaeger

    classDef docker fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef service fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef volume fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef host fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class Network docker
    class Toolbox,Jaeger,Postgres service
    class ToolConfig,PostgresData volume
    class ADK_Web,Python_Agents,Browser host
```

**Service Details:**

| Service | Purpose | Ports | Persistence |
|---------|---------|-------|-------------|
| **genai-toolbox-mcp** | MCP server for tools | 5000 | Config volume |
| **jaeger** | Distributed tracing | 4318 (OTLP), 16686 (UI) | In-memory (dev) |
| **postgres** | Tool metadata storage | 5432 | postgres_data volume |

**Environment Variables:**
```bash
# Required
DNB_SUBSCRIPTION_KEY_DEV=<your-api-key>
DNB_ENVIRONMENT=dev

# Optional
TOOLBOX_SERVER_URL=http://localhost:5000
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
```

---

### Development Workflow

```mermaid
flowchart LR
    subgraph Dev["👨‍💻 Development"]
        EditSpec["1. Edit OpenAPI Spec<br/>apis/dnb/specs/*.yaml"]
        RunConverter["2. Run OpenAPI-Box<br/>openapi_toolbox.py"]
    end

    subgraph Build["🔨 Build"]
        GenerateYAML["3. Generate Tool YAML<br/>toolbox/config/dev/*.yaml"]
        RestartDocker["4. Restart Docker<br/>docker-compose restart"]
    end

    subgraph Test["🧪 Testing"]
        TestUI["5. Test in Toolbox UI<br/>http://localhost:5000/ui"]
        TestAgent["6. Test with Agents<br/>run_dnb_openapi_agent.py<br/>or simple_dnb_agent.py"]
        ViewTraces["7. View Traces<br/>http://localhost:16686"]
    end

    subgraph Deploy["🚀 Deploy"]
        CommitChanges["8. Commit Changes<br/>Git commit"]
        PushToRepo["9. Push to Repo<br/>Git push"]
    end

    EditSpec --> RunConverter
    RunConverter --> GenerateYAML
    GenerateYAML --> RestartDocker
    RestartDocker --> TestUI
    TestUI --> TestAgent
    TestAgent --> ViewTraces
    ViewTraces --> CommitChanges
    CommitChanges --> PushToRepo

    classDef dev fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef build fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef test fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef deploy fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class EditSpec,RunConverter dev
    class GenerateYAML,RestartDocker build
    class TestUI,TestAgent,ViewTraces test
    class CommitChanges,PushToRepo deploy
```

**Quick Commands:**
```powershell
# Full workflow (VS Code Task)
Ctrl+Shift+P → "Convert & Restart: Convert APIs → Restart Server → Open UI"

# Manual steps
cd backend/open-api-box
python openapi_toolbox.py convert --all

cd ../toolbox
docker-compose -f docker-compose.dev.yml restart

# Test agent
cd ../adk
python simple_dnb_agent.py
```

---

## Deployment Topology

### Deployment Layers: Local vs Docker vs Cloud

```mermaid
graph TB
    subgraph Local_Dev["💻 LOCAL DEVELOPMENT"]
        direction TB
        
        subgraph Python_Local["Python Applications (Host)"]
            ADK_Web_Local["ADK Web Server<br/>Port: 8000<br/>Poetry/uv managed"]
            Root_Agent_Local["Root Agent<br/>gemini-2.0-flash<br/>.venv isolated"]
            ETL_Local["ETL Pipelines<br/>Poetry environment<br/>Scheduled via cron/tasks"]
        end
        
        subgraph Data_Local["File System"]
            Bronze_Local["Bronze Layer<br/>data/1-bronze/<br/>Parquet files"]
            Silver_Local["Silver Layer<br/>data/2-silver/<br/>Cleaned data"]
            Gold_Local["Gold Layer<br/>data/3-gold/<br/>Aggregated data"]
        end
        
        subgraph Docker_Local["🐳 Docker Containers"]
            Toolbox_Docker["genai-toolbox-mcp<br/>Port: 5000<br/>Go binary + YAML configs"]
            Jaeger_Docker["Jaeger All-in-One<br/>Ports: 4318, 16686<br/>OTLP + UI"]
            Postgres_Docker["PostgreSQL 17<br/>Port: 5432<br/>Session storage (future)"]
        end
    end

    subgraph Azure_Cloud["☁️ MICROSOFT AZURE (Internal DNB Services)"]
        direction TB
        
        subgraph Azure_Services["Internal Services"]
            DataLoop_Svc["DNB DataLoop<br/>Report Status API<br/>• Internal network<br/>• Financial institutions"]
            ATM_Svc["DNB ATM<br/>Models API<br/>• Third-party hosted<br/>• Secure access"]
            MEGA_Svc["DNB MEGA<br/>Validations API<br/>• Third-party hosted<br/>• Secure access"]
        end
        
        subgraph Azure_Network["Azure Network"]
            VNET["Virtual Network<br/>Private connectivity"]
            PrivateEndpoint["Private Endpoint<br/>Secure agent access"]
        end
    end

    subgraph GCP_Cloud["☁️ GOOGLE CLOUD PLATFORM (PLANNED)"]
        direction TB
        
        subgraph Cloud_Run["Cloud Run Services"]
            Toolbox_CR["MCP Toolbox<br/>Cloud Run Service<br/>• VPC Connector<br/>• Secret Manager<br/>• Auto-scaling"]
            ADK_Agent_CR["Data Science Agent<br/>Cloud Run Service<br/>• Agent Engine<br/>• Session Service<br/>• Cloud SQL Connector"]
        end
        
        subgraph Data_GCP["Data & Storage"]
            GCS["Cloud Storage<br/>gs://dnb-data/<br/>• Bronze exports<br/>• Staging area"]
            BQ["BigQuery<br/>dnb_statistics dataset<br/>• Partitioned tables<br/>• Clustered keys"]
            AlloyDB_GCP["AlloyDB<br/>PostgreSQL cluster<br/>• VPC peering<br/>• Public IP + Auth Proxy"]
            Cloud_SQL["Cloud SQL (PostgreSQL)<br/>Session storage<br/>• Private IP<br/>• Automated backups"]
        end
        
        subgraph AI_Platform["Vertex AI"]
            Gemini["Gemini API<br/>gemini-2.0-flash<br/>• NL2SQL<br/>• NL2Py"]
            Code_Interp["Code Interpreter<br/>Extension Service<br/>• Python sandbox<br/>• File I/O"]
            RAG_Engine["RAG Engine<br/>BQML Reference<br/>• Vector search<br/>• Document corpus"]
            Agent_Engine["Agent Engine<br/>Reasoning Engine<br/>• Multi-agent orchestration<br/>• Session management"]
        end
    end

    %% Local connections
    Root_Agent_Local -.HTTP.-> Toolbox_Docker
    Root_Agent_Local -.ADK OpenAPI Tool.-> PrivateEndpoint
    ADK_Web_Local -.WebSocket.-> Root_Agent_Local
    Toolbox_Docker -.OTLP.-> Jaeger_Docker
    ETL_Local --> Bronze_Local
    Bronze_Local --> Silver_Local
    Silver_Local --> Gold_Local
    
    %% Azure connections
    PrivateEndpoint --> VNET
    VNET --> DataLoop_Svc
    VNET --> ATM_Svc
    VNET --> MEGA_Svc
    
    %% GCP Cloud connections
    Toolbox_CR -.VPC Connector.-> AlloyDB_GCP
    ADK_Agent_CR --> Cloud_SQL
    ADK_Agent_CR --> Gemini
    ADK_Agent_CR --> Code_Interp
    ADK_Agent_CR --> RAG_Engine
    ADK_Agent_CR --> Agent_Engine
    ADK_Agent_CR -.Query.-> BQ
    ADK_Agent_CR -.Via MCP.-> Toolbox_CR
    ADK_Agent_CR -.Private Link.-> PrivateEndpoint
    
    %% Data flow: Local to Cloud
    Bronze_Local -.Upload Script.-> GCS
    GCS -.bq load.-> BQ
    
    classDef local_python fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef local_data fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef docker fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef azure_service fill:#bbdefb,stroke:#0d47a1,stroke-width:3px
    classDef azure_network fill:#90caf9,stroke:#1565c0,stroke-width:2px
    classDef cloud_run fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef gcp_data fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef vertex fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class ADK_Web_Local,Root_Agent_Local,ETL_Local local_python
    class Bronze_Local,Silver_Local,Gold_Local local_data
    class Toolbox_Docker,Jaeger_Docker,Postgres_Docker docker
    class DataLoop_Svc,ATM_Svc,MEGA_Svc azure_service
    class VNET,PrivateEndpoint azure_network
    class Toolbox_CR,ADK_Agent_CR cloud_run
    class GCS,BQ,AlloyDB_GCP,Cloud_SQL gcp_data
    class Gemini,Code_Interp,RAG_Engine,Agent_Engine vertex
```

---

### Deployment Comparison Matrix

| Component | Local Development | Docker (Local) | Azure (Internal) | Cloud Run (GCP) |
|-----------|-------------------|----------------|------------------|-----------------|
| **ADK Web Server** | Host (Poetry/uv)<br/>Port 8000 | N/A | N/A | Cloud Run Service<br/>Auto-scaling |
| **Root Agent** | Host (.venv)<br/>Gemini API via internet | N/A | N/A | Agent Engine<br/>Managed service |
| **Data Science Agents** | N/A | N/A | N/A | Agent Engine<br/>Multi-agent system |
| **MCP Toolbox** | N/A | Docker container<br/>Port 5000 | N/A | Cloud Run Service<br/>VPC + Secrets |
| **DNB Internal Services** | ADK OpenAPI Tool<br/>Private network | N/A | **Azure-hosted<br/>DataLoop/ATM/MEGA<br/>Private endpoints** | Via Private Link |
| **Jaeger** | N/A | Docker container<br/>In-memory storage | N/A | Cloud Trace<br/>Managed tracing |
| **PostgreSQL** | N/A | Docker container<br/>Local volume | N/A | Cloud SQL<br/>Automated backups |
| **AlloyDB** | N/A | N/A | N/A | AlloyDB cluster<br/>VPC + Auth Proxy |
| **BigQuery** | N/A | N/A | N/A | Managed dataset<br/>Partitioned tables |
| **Code Interpreter** | N/A | N/A | N/A | Vertex AI Extension<br/>Python sandbox |
| **ETL Scripts** | Host (Poetry)<br/>Cron/VS Code tasks | N/A | N/A | Cloud Scheduler<br/>+ Cloud Functions |
| **Bronze Data** | Local filesystem<br/>data/1-bronze/ | N/A | N/A | Cloud Storage<br/>gs://dnb-data/ |

---

### Cloud Run Deployment Architecture (PLANNED)

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        User["User Browser"]
        DNB_APIs["DNB APIs<br/>api.dnb.nl"]
    end

    subgraph GCP_Project["☁️ Google Cloud Project"]
        direction TB
        
        subgraph Cloud_Run_Services["Cloud Run (Auto-scaling)"]
            CR_Toolbox["MCP Toolbox Service<br/>• Private IP + Load Balancer<br/>• IAM Authentication<br/>• Min instances: 0, Max: 10"]
            CR_Agent["Data Science Agent Service<br/>• Public endpoint<br/>• Session management<br/>• Min instances: 1, Max: 20"]
        end
        
        subgraph VPC["VPC Network"]
            VPC_Connector["Serverless VPC Connector<br/>us-central1"]
            Subnet["Default Subnet<br/>10.128.0.0/20"]
        end
        
        subgraph Databases["Managed Databases"]
            AlloyDB_Cluster["AlloyDB Cluster<br/>• Primary instance (8 CPU)<br/>• Public IP enabled<br/>• SSL: ALLOW_UNENCRYPTED"]
            Cloud_SQL_Instance["Cloud SQL (PostgreSQL 17)<br/>• db-g1-small<br/>• Private IP only<br/>• Auto backups"]
        end
        
        subgraph Storage["Data Storage"]
            GCS_Bucket["Cloud Storage Bucket<br/>gs://dnb-data/<br/>• Parquet staging<br/>• Lifecycle policies"]
            BQ_Dataset["BigQuery Dataset<br/>dnb_statistics<br/>• US-multi region<br/>• Partitioned tables"]
        end
        
        subgraph AI_Services["Vertex AI"]
            Gemini_API["Gemini 2.0 Flash<br/>• NL2SQL generation<br/>• Agent reasoning"]
            Code_Interp_Ext["Code Interpreter Extension<br/>• projects/.../extensions/..."]
            RAG_Corpus["RAG Engine Corpus<br/>BQML reference docs"]
            Agent_Engine_RE["Agent Engine<br/>Reasoning Engine resource"]
        end
        
        subgraph Security["Security & Secrets"]
            Secret_Manager["Secret Manager<br/>• ALLOYDB_POSTGRES_PASSWORD<br/>• DNB_SUBSCRIPTION_KEY_PROD<br/>• tools.yaml config"]
            IAM["IAM Roles<br/>• Service Accounts<br/>• Workload Identity"]
        end
    end

    %% User connections
    User -.HTTPS.-> CR_Agent
    
    %% Agent to services
    CR_Agent --> Cloud_SQL_Instance
    CR_Agent --> Gemini_API
    CR_Agent --> Code_Interp_Ext
    CR_Agent --> RAG_Corpus
    CR_Agent --> Agent_Engine_RE
    CR_Agent -.Internal.-> CR_Toolbox
    CR_Agent --> BQ_Dataset
    
    %% Toolbox to databases
    CR_Toolbox --> VPC_Connector
    VPC_Connector --> Subnet
    Subnet --> AlloyDB_Cluster
    CR_Toolbox -.HTTPS.-> DNB_APIs
    CR_Toolbox --> Secret_Manager
    
    %% Data pipeline
    GCS_Bucket -.bq load.-> BQ_Dataset
    
    %% Security
    IAM -.Manages.-> CR_Toolbox
    IAM -.Manages.-> CR_Agent
    Secret_Manager -.Secrets.-> CR_Toolbox
    Secret_Manager -.Secrets.-> CR_Agent

    classDef internet fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef cloudrun fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef vpc fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef database fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef ai fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef security fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class User,DNB_APIs internet
    class CR_Toolbox,CR_Agent cloudrun
    class VPC_Connector,Subnet vpc
    class AlloyDB_Cluster,Cloud_SQL_Instance database
    class GCS_Bucket,BQ_Dataset storage
    class Gemini_API,Code_Interp_Ext,RAG_Corpus,Agent_Engine_RE ai
    class Secret_Manager,IAM security
```

**Cloud Run Service Configuration:**

```yaml
# MCP Toolbox Service
service: toolbox
image: us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest
args:
  - --tools-file=/app/tools.yaml
  - --address=0.0.0.0
  - --port=8080
secrets:
  - /app/tools.yaml=tools:latest
  - ALLOYDB_POSTGRES_PASSWORD=ALLOYDB_POSTGRES_PASSWORD:latest
network:
  vpc: default
  subnet: default
service_account: toolbox-identity@PROJECT_ID.iam.gserviceaccount.com
```

```yaml
# Data Science Agent Service
service: data-science-agent
port: 8080
memory: 2G
cloudsql_instances:
  - PROJECT_ID:us-central1:ds-agent-session-service
env_vars:
  SERVE_WEB_INTERFACE: "True"
  SESSION_SERVICE_URI: "postgresql+pg8000://postgres:PASSWORD@postgres/?unix_sock=/cloudsql/PROJECT_ID:us-central1:ds-agent-session-service/.s.PGSQL.5432"
  GOOGLE_CLOUD_PROJECT: "PROJECT_ID"
allow_unauthenticated: true
```

---

### Deployment Workflow Comparison

```mermaid
flowchart LR
    subgraph Local_Deploy["💻 Local Development Workflow"]
        direction TB
        UpdateSpec_L["1. Update OpenAPI Spec<br/>backend/apis/dnb/specs/"]
        Convert_L["2. Convert to Toolbox<br/>openapi_toolbox.py"]
        Restart_L["3. Restart Docker<br/>docker-compose restart"]
        Test_L["4. Test Locally<br/>localhost:5000"]
    end

    subgraph Cloud_Deploy["☁️ Cloud Run Deployment"]
        direction TB
        Build_C["1. Build Container<br/>docker build -t ..."]
        Push_C["2. Push to Artifact Registry<br/>docker push ..."]
        Deploy_C["3. Deploy to Cloud Run<br/>gcloud run deploy"]
        Migrate_C["4. Update Secrets<br/>gcloud secrets create"]
        Test_C["5. Test Cloud Endpoint<br/>https://toolbox-...run.app"]
    end

    UpdateSpec_L --> Convert_L
    Convert_L --> Restart_L
    Restart_L --> Test_L
    
    Build_C --> Push_C
    Push_C --> Deploy_C
    Deploy_C --> Migrate_C
    Migrate_C --> Test_C

    classDef local fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef cloud fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class UpdateSpec_L,Convert_L,Restart_L,Test_L local
    class Build_C,Push_C,Deploy_C,Migrate_C,Test_C cloud
```

---

## Technology Stack

### Core Technologies

```mermaid
mindmap
  root((Orkhon Backend))
    Agent Framework
      Google ADK
      LangGraph
      LangChain
    LLM
      Gemini 2.5/2.0
      Vertex AI
    Tool Orchestration
      GenAI Toolbox
      MCP Protocol
      OpenTelemetry
    API Integration
      OpenAPI 3.0
      Kiota Client Generator
      HTTP/REST
    Data Engineering
      Parquet
      Pandas
      PyArrow
    Observability
      Jaeger
      OTLP
      Distributed Tracing
    Development
      Python 3.12+
      Poetry
      Docker Compose
    Testing
      Pytest
      AsyncIO
      Type Hints
```

**Language & Runtime:**
- Python 3.12+ (type hints, async/await)
- Poetry for dependency management
- Virtual environment isolation

**Agent & LLM:**
- Google ADK (Agent Development Kit)
- LangGraph (agent workflow orchestration)
- Gemini 2.5-flash / 2.0-flash
- Vertex AI platform integration

**Tool & API:**
- GenAI Toolbox (Go-based MCP server)
- OpenAPI 3.0 specifications
- Kiota (type-safe client generator)
- HTTP/REST with API key authentication

**Data & Storage:**
- Parquet (columnar format)
- Pandas (data manipulation)
- PyArrow (Parquet I/O)
- Medallion architecture (Bronze/Silver/Gold)

**Observability:**
- Jaeger (distributed tracing)
- OpenTelemetry (OTLP protocol)
- Span-based tracing

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL (metadata storage)
- Volume mounts for configs

---

## Summary

### Key Architectural Principles

1. **Modularity**: Clear separation of concerns (agents, tools, ETL)
2. **Type Safety**: Kiota-generated clients, OpenAPI schemas
3. **Observability**: Full tracing from agent → tool → API
4. **Extensibility**: Plugin-based tool discovery, new extractors
5. **Developer Experience**: VS Code tasks, scripts, hot-reload

### Component Count

**Current (Implemented):**
- **Agents**: 10+ ✅ (root, 2 coordinators, 3 public API specialists, workflows, OpenAPI variants)
- **Tools**: 84+ ✅ (echo: 3, statistics: 79, public-register: 5)
- **ETL Extractors**: 23+ ✅ (statistics: 17, public-register: 6)
- **API Clients**: 3 Kiota clients ✅ (echo, statistics, public-register)
- **Services**: 3 running locally ✅ (toolbox, jaeger, postgres)
- **Data Layers**: 3 ✅ (bronze, silver, gold - medallion architecture)

**Planned (Azure + GCP):**
- **Agents**: +10 📋 (6 Azure DB/API agents, 4 data science agents)
- **Tools**: +6 📋 (3 Azure DB toolsets + 3 Azure API tools)
- **API Clients**: +3 ADK OpenAPI tools 📋 (DataLoop, ATM, MEGA APIs)
- **Database Connections**: +3 Azure IAM auth 📋 (DataLoop DB, ATM DB, MEGA DB)
- **Services (Azure)**: +3 databases + 3 APIs 📋
- **Services (GCP)**: +4 📋 (AlloyDB, Cloud SQL, BigQuery, Vertex AI)
- **Cloud Platforms**: +2 📋 (Microsoft Azure, Google Cloud)
- **A2A Endpoints**: +1 📋 (JSON-RPC server for agent cards)

**Total System (When Complete):**
- **Agents**: 20+ (10 implemented + 10 planned)
- **Tools**: 90+ (84 implemented + 6 planned)
- **Data Sources**: 9+ (3 public APIs + 3 Azure DBs + 3 Azure APIs)
- **Model Options**: 2 (Gemini for local/external, Copilot for DNB infrastructure)

### Integration Points

### Integration Points

| Component | Protocol | Port | Purpose | Status | Environment |
|-----------|----------|------|---------|--------|-------------|
| ADK Web UI | HTTP/WebSocket | 4200 | Agent interaction | ✅ IMPLEMENTED | Local Host |
| ADK Agents → Toolbox | HTTP REST | 5000 | Tool invocation | ✅ IMPLEMENTED | Local Host → Docker |
| Toolbox → DNB Public APIs | HTTPS REST | 443 | External API calls | ✅ IMPLEMENTED | Docker → Internet |
| Toolbox | OTLP/gRPC | 4318 | Trace export | ✅ IMPLEMENTED | Docker → Jaeger |
| Jaeger UI | HTTP | 16686 | Trace visualization | ✅ IMPLEMENTED | Browser → Docker |
| PostgreSQL (Local) | PostgreSQL | 5432 | Metadata storage | ✅ IMPLEMENTED | Docker |
| **Azure IAM** | **Token Auth** | **443** | **Identity verification** | 📋 **PLANNED** | **DNB → Azure** |
| **DataLoop DB** | **SQL Server** | **1433** | **Report status queries** | 📋 **PLANNED** | **DNB → Azure (PRIMARY)** |
| **ATM DB** | **PostgreSQL** | **5432** | **Model metadata queries** | 📋 **PLANNED** | **DNB → Azure (PRIMARY)** |
| **MEGA DB** | **SQL Server** | **1433** | **Validation queries** | 📋 **PLANNED** | **DNB → Azure (PRIMARY)** |
| **DNB DataLoop API** | **HTTPS/REST** | **443** | **Report status ops** | 📋 **PLANNED** | **DNB → Azure (FALLBACK)** |
| **DNB ATM API** | **HTTPS/REST** | **443** | **Model access** | 📋 **PLANNED** | **DNB → Azure (FALLBACK)** |
| **DNB MEGA API** | **HTTPS/REST** | **443** | **Validation services** | 📋 **PLANNED** | **DNB → Azure (FALLBACK)** |
| **A2A Protocol** | **JSON-RPC** | **8000** | **Agent cards + tasks** | 📋 **PLANNED** | **DNB → External** |
| BigQuery | gRPC/REST | 443 | Data warehouse | 📋 PLANNED | GCP |
| AlloyDB | PostgreSQL | 5432 | OLTP database | 📋 PLANNED | GCP |
| Cloud Run | HTTPS | 443 | Agent services | 📋 PLANNED | GCP |
| Vertex AI | gRPC/REST | 443 | AI/ML platform | 📋 PLANNED | GCP |

**Key Distinctions:**
- **PRIMARY**: Database access via Azure IAM (direct SQL connections)
- **FALLBACK**: API access via HTTPS/REST (when database unavailable)
- **A2A**: Required for DNB infrastructure deployment (agent-to-agent communication)
- **Model**: Gemini (local/external) vs Copilot (DNB infrastructure)

---

## Implementation Status & Next Steps

### ✅ Implemented & Working
- **Multi-agent system**: root_agent, dnb_coordinator, specialized agents
- **GenAI Toolbox**: MCP server with 84+ DNB public API tools
- **ETL pipelines**: Bronze layer extraction (Statistics + Public Register)
- **Docker Compose**: Local development stack (Toolbox, Jaeger, Postgres)
- **OpenTelemetry**: Full tracing and observability
- **Type-safe clients**: Kiota-generated clients for all public APIs
- **OpenAPI tooling**: Converter for Toolbox YAML generation

### 📋 Planned (Priority Order)

#### 1. **Azure Database Integration** (HIGHEST PRIORITY)
- [ ] Configure Azure IAM authentication with Managed Identities
- [ ] Implement database agents (DataLoop DB, ATM DB, MEGA DB)
- [ ] Create SQL toolsets with Azure IAM auth
- [ ] Set up connection pooling and retry logic
- [ ] Document database schemas and access patterns
- [ ] Configure GitHub Copilot as model for DNB infrastructure agents
- [ ] Implement API fallback agents for each database

#### 2. **A2A Protocol Implementation**
- [ ] Create agent cards (.well-known/agent.json) for all agents
- [ ] Set up JSON-RPC server endpoints
- [ ] Implement task management and streaming
- [ ] Configure authentication schemes for cross-org communication
- [ ] Test A2A client for remote agent access

#### 3. **Data Science Agents**
- [ ] Implement `data_coordinator` with NL2SQL/NL2Py routing
- [ ] Create `bigquery_agent` with CHASE-SQL and built-in BQ tools
- [ ] Develop `analytics_agent` with Code Interpreter extension
- [ ] Build `bqml_agent` with RAG-based BQML reference
- [ ] Set up `alloydb_agent` with MCP Toolbox for Databases

#### 4. **GCP Cloud Deployment**
- [ ] Deploy GenAI Toolbox to Cloud Run with VPC connector
- [ ] Set up AlloyDB cluster with Auth Proxy
- [ ] Create Cloud SQL instance for session storage
- [ ] Configure Vertex AI Code Interpreter extension
- [ ] Build RAG corpus for BQML documentation
- [ ] Implement Bronze → GCS upload scripts
- [ ] Create BigQuery dataset with partitioned tables

#### 5. **Advanced Features**
- [ ] Cross-dataset join capabilities (BigQuery ↔ AlloyDB)
- [ ] Dataset configuration files for flexible data source routing
- [ ] BQML model training workflows (ARIMA, forecasting)
- [ ] Performance optimization for large-scale analytics
- [ ] Multi-cloud observability (Azure + GCP traces in Jaeger)

### 🔄 In Progress (None currently)

---
   - Implement `data_coordinator` with NL2SQL/NL2Py routing
   - Create `bigquery_agent` with CHASE-SQL and built-in BQ tools
   - Develop `analytics_agent` with Code Interpreter extension
   - Build `bqml_agent` with RAG-based BQML reference guide
   - Set up `alloydb_agent` with MCP Toolbox for Databases

2. **Cloud Deployment**:
   - Deploy MCP Toolbox to Cloud Run with VPC connector
   - Set up AlloyDB cluster with Auth Proxy
   - Create Cloud SQL instance for session storage
   - Configure Vertex AI Code Interpreter extension
   - Build RAG corpus for BQML documentation

3. **Data Pipeline**:
   - Implement Bronze → GCS upload scripts
   - Create BigQuery dataset with partitioned tables
   - Develop Silver layer transformation logic
   - Build Gold layer aggregation views
   - Set up Cloud Scheduler for automated ETL

4. **Advanced Features**:
   - Cross-dataset join capabilities (BigQuery ↔ AlloyDB)
   - Dataset configuration files for flexible data source routing
   - BQML model training workflows (ARIMA, forecasting)
   - Performance optimization for large-scale analytics

---

*Generated: October 2025*  
*Version: 2.0.0*  
*Updated: Enhanced with Data Science Agent architecture and deployment topology*
