# Orkhon Backend Architecture - Current Implementation

> **Current State Documentation**  
> This document reflects the **actual implemented system** as of October 2025

---

## 📖 Table of Contents

- [System Overview](#system-overview)
- [Implemented Components](#implemented-components)
- [Agent Architecture](#agent-architecture)
- [Tool Integration](#tool-integration)
- [ETL Pipeline](#etl-pipeline)
- [Deployment Architecture](#deployment-architecture)

---

## System Overview

### Current High-Level Architecture ✅

```mermaid
graph TB
    subgraph Frontend["🖥️ Frontend Layer ✅"]
        ADK_Web["ADK Web Server<br/>Port: 8000<br/>Python + FastAPI"]
        Browser["Web Browser<br/>Agent Interaction"]
    end

    subgraph Agents["🤖 Agent Layer ✅"]
        Root["Root Agent<br/>gemini-2.5-flash<br/>Main Coordinator"]
        DNB_Coord["DNB Coordinator<br/>Routes to API Specialists"]
        
        subgraph API_Agents["API Specialists ✅"]
            Echo["Echo Agent<br/>3 tools"]
            Stats["Statistics Agent<br/>79 tools"]
            PR["Public Register Agent<br/>5 tools"]
        end
    end

    subgraph Tools["🔧 Tool Layer ✅"]
        Toolbox["GenAI Toolbox<br/>MCP Server<br/>Port: 5000<br/>87 DNB Tools"]
        ToolConfigs["YAML Tool Configs<br/>backend/toolbox/config/dev/"]
    end

    subgraph Docker["🐳 Docker Services ✅"]
        Jaeger["Jaeger Tracing<br/>Port: 16686<br/>OTLP Collector"]
        Postgres["PostgreSQL<br/>Port: 5432<br/>Local Storage"]
    end

    subgraph External["🌐 External APIs ✅"]
        DNB_Echo["DNB Echo API<br/>api.dnb.nl/echo-api"]
        DNB_Stats["DNB Statistics API<br/>api.dnb.nl/statistics"]
        DNB_PR["DNB Public Register API<br/>api.dnb.nl/publicregister"]
    end

    subgraph Build["🛠️ Build Tools ✅"]
        OpenAPIBox["openapi-mcp-codegen<br/>OpenAPI → Toolbox Converter"]
        Specs["OpenAPI 3.0 Specs<br/>backend/apis/dnb/specs/"]
    end

    subgraph ETL["📊 ETL Pipeline ✅"]
        Stats_ETL["Statistics ETL<br/>17 Extractors"]
        PR_ETL["Public Register ETL<br/>6 Extractors"]
        Bronze["Bronze Layer<br/>Parquet Files<br/>data/1-bronze/"]
    end

    %% Current Connections
    Browser --> ADK_Web
    ADK_Web --> Root
    Root --> DNB_Coord
    DNB_Coord --> API_Agents
    API_Agents --> Toolbox
    Toolbox --> ToolConfigs
    Toolbox --> DNB_Echo
    Toolbox --> DNB_Stats
    Toolbox --> DNB_PR
    Toolbox --> Jaeger
    Toolbox --> Postgres
    
    Specs --> OpenAPIBox
    OpenAPIBox --> ToolConfigs
    
    Stats_ETL --> DNB_Stats
    PR_ETL --> DNB_PR
    Stats_ETL --> Bronze
    PR_ETL --> Bronze

    classDef implemented fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef tool fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef docker fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef external fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    
    class Browser,ADK_Web,Root,DNB_Coord,Echo,Stats,PR,Stats_ETL,PR_ETL,Bronze implemented
    class Toolbox,ToolConfigs,OpenAPIBox,Specs tool
    class Jaeger,Postgres docker
    class DNB_Echo,DNB_Stats,DNB_PR external
```

**Current Stack:**
- ✅ **Model**: Google Gemini 2.5-flash (via Vertex AI or API key)
- ✅ **Framework**: Google ADK (Agent Development Kit)
- ✅ **Tools**: GenAI Toolbox (Go-based MCP server)
- ✅ **Observability**: Jaeger + OpenTelemetry
- ✅ **Data**: Local Parquet files (Bronze layer)
- ✅ **Deployment**: Local development (Docker Compose + Python venv)

---

## Implemented Components

### Current Agent Hierarchy ✅

```mermaid
graph TB
    subgraph System_Root["🌐 System Root"]
        Root["root_agent<br/>system coordinator<br/>entry point"]
    end

    subgraph Domain_Coordinators["🎯 Domain Coordinators"]
        DNB_Coord["dnb_coordinator<br/>DNB API domain"]
        Data_Coord["data_science_coordinator<br/>Analytics domain"]
    end

    subgraph DNB_Specialists["🔧 DNB Specialists<br/>(Leaf Agents with Tools)"]
        Echo["dnb_echo_agent<br/>ToolboxToolset<br/>3 tools"]
        Stats["dnb_statistics_agent<br/>ToolboxToolset<br/>79 tools"]
        PR["dnb_public_register_agent<br/>ToolboxToolset<br/>5 tools"]
    end

    subgraph Data_Specialists["📊 Data Specialists<br/>(Leaf Agents with Tools)"]
        BQ["bigquery_agent<br/>BigQuery Tools<br/>NL2SQL"]
        Analytics["analytics_agent<br/>Code Interpreter<br/>NL2Py + Viz"]
    end

    Root -->|"transfer_to_agent()"| DNB_Coord
    Root -->|"transfer_to_agent()"| Data_Coord
    
    DNB_Coord -->|"transfer_to_agent()"| Echo
    DNB_Coord -->|"transfer_to_agent()"| Stats
    DNB_Coord -->|"transfer_to_agent()"| PR
    
    Data_Coord -->|"transfer_to_agent()"| BQ
    Data_Coord -->|"transfer_to_agent()"| Analytics

    classDef system fill:#e1f5fe,stroke:#01579b,stroke-width:4px
    classDef coordinator fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    classDef specialist fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    
    class Root system
    class DNB_Coord,Data_Coord coordinator
    class Echo,Stats,PR,BQ,Analytics specialist
```

**Agent Hierarchy Explained:**
