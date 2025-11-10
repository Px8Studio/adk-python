# Orkhon Backend Architecture - DNB IT Implementation (Planned)

> Future State: Planned deployment within DNB IT using Azure AI Foundry and Copilot  
> Document Suite:
> - Full Architecture (this document)
> - Quick Reference
> - Visual Summary
> - Executive Presentation

## Table of Contents

- [Vision Overview](#vision-overview)
- [DNB IT Stack](#dnb-it-stack)
- [Microsoft AI Foundry Deep Dive](#microsoft-ai-foundry-deep-dive)
- [Multi-Agent Orchestration Architecture](#multi-agent-orchestration-architecture)
- [Framework Migration Strategy](#framework-migration-strategy)
- [Azure AI Foundry Integration](#azure-ai-foundry-integration)
- [Internal Service Integration](#internal-service-integration)
- [Security & Compliance Architecture](#security--compliance-architecture)
- [A2A Protocol Implementation](#a2a-protocol-implementation)
- [Data Science Platform](#data-science-platform)
- [Deployment Architecture](#deployment-architecture)
- [Technical Decision Matrix](#technical-decision-matrix)
- [Comparison: Current vs Future](#comparison-current-vs-future)
- [Migration Path](#migration-path)
- [Summary](#summary)

## Vision Overview

### Future DNB IT Architecture

```mermaid
graph TB
    subgraph DNB_Frontend["DNB Frontend"]
        Copilot_UI["Microsoft 365 Copilot<br/>Chat Interface<br/>Teams Integration"]
        Portal["Azure Portal<br/>AI Foundry Studio"]
    end

    subgraph Azure_AI_Foundry["Azure AI Foundry"]
        direction TB
        
        subgraph Model_Catalog["Model Catalog"]
            Copilot_Model["GitHub Copilot<br/>GPT-4 Based<br/>DNB Standard Model"]
            OpenAI["Azure OpenAI<br/>GPT-4 Turbo<br/>Fallback Option"]
        end
        
        subgraph Prompt_Flow["Prompt Flow"]
            Agent_Orchestrator["Agent Orchestrator<br/>Low-Code Design"]
            Flow_Templates["DNB Flow Templates<br/>Pre-built Workflows"]
        end
        
        subgraph Content_Safety["Content Safety"]
            Safety_Filter["Azure AI Content Safety<br/>Compliance Checks"]
        end
    end

    subgraph DNB_Agents["DNB Agent System"]
        direction TB
        Root_DNB["Root Agent<br/>GitHub Copilot<br/>Azure Deployment<br/>System Coordinator"]
        
        subgraph Coordinators["Domain Coordinators"]
            Internal_Coord["Internal Services Coordinator<br/>DataLoop + ATM + MEGA"]
            External_Coord["External API Coordinator<br/>DNB Public APIs"]
            Data_Coord["Data Science Coordinator<br/>Analytics + Reporting"]
        end
        
        subgraph Internal_Agents["Internal Service Specialists"]
            DataLoop_Agent["DataLoop Specialist<br/>Azure SQL Tools<br/>IAM Auth"]
            ATM_Agent["ATM Specialist<br/>PostgreSQL Tools<br/>IAM Auth"]
            MEGA_Agent["MEGA Specialist<br/>Azure SQL Tools<br/>IAM Auth"]
        end
        
        subgraph External_Agents["External API Specialists"]
            DNB_Echo["Echo Specialist<br/>Connectivity Tests"]
            DNB_Stats["Statistics Specialist<br/>Economic Data"]
            DNB_PR["Public Register Specialist<br/>Regulatory Data"]
        end
        
        subgraph Data_Agents["Data Science Specialists"]
            Fabric_Agent["Fabric Specialist<br/>Lakehouse Queries"]
            Analytics_Agent["Analytics Specialist<br/>Power BI Integration"]
        end
    end

    subgraph Azure_Services["Azure Core Services"]
        direction TB
        
        subgraph IAM["Identity & Access"]
            Entra_ID["Azure Entra ID<br/>Role-Based Access"]
            Managed_ID["Managed Identities<br/>Service Principals"]
        end
        
        subgraph Databases["Internal Databases"]
            DataLoop_DB["DataLoop Database<br/>Azure SQL Server<br/>Report Status Data"]
            ATM_DB["ATM Database<br/>Azure PostgreSQL<br/>Model Metadata"]
            MEGA_DB["MEGA Database<br/>Azure SQL Server<br/>Validation Rules"]
        end
        
        subgraph APIs["Internal APIs"]
            DataLoop_API["DataLoop REST API<br/>OpenAPI 3.0"]
            ATM_API["ATM REST API<br/>OpenAPI 3.0"]
            MEGA_API["MEGA REST API<br/>OpenAPI 3.0"]
        end
        
        subgraph Container_Platform["Container Platform"]
            ACA["Azure Container Apps<br/>Agent Deployment<br/>Auto-scaling"]
            ACR["Azure Container Registry<br/>Private Images"]
        end
        
        subgraph Observability["Observability"]
            AppInsights["Application Insights<br/>Tracing + Metrics"]
            LogAnalytics["Log Analytics<br/>Centralized Logs"]
        end
    end

    subgraph A2A_Protocol["A2A Protocol"]
        A2A_Server["A2A JSON-RPC Server<br/>Agent Card Publishing<br/>/.well-known/agent.json"]
        A2A_Registry["DNB Agent Registry<br/>Cross-Org Discovery"]
    end

    subgraph Data_Platform["Data Platform"]
        direction TB
        
        subgraph Microsoft_Fabric["Microsoft Fabric"]
            Fabric_Lakehouse["Fabric Lakehouse<br/>Bronze/Silver/Gold"]
            Fabric_Warehouse["Fabric Warehouse<br/>Analytics"]
            Fabric_ML["Fabric ML<br/>Model Training"]
        end
        
        subgraph PowerBI["Power BI"]
            Reports["Interactive Reports<br/>Executive Dashboards"]
        end
    end

    %% Connections
    Copilot_UI --> Azure_AI_Foundry
    Portal --> Azure_AI_Foundry
    
    Azure_AI_Foundry --> Copilot_Model
    Azure_AI_Foundry --> Agent_Orchestrator
    Azure_AI_Foundry --> Safety_Filter
    
    Agent_Orchestrator --> Root_DNB
    Root_DNB --> Coordinators
    Internal_Coord --> Internal_Agents
    
    Internal_Agents --> Entra_ID
    Entra_ID --> Managed_ID
    Managed_ID --> DataLoop_DB
    Managed_ID --> ATM_DB
    Managed_ID --> MEGA_DB
    
    DataLoop_DB -.Backed by.-> DataLoop_API
    ATM_DB -.Backed by.-> ATM_API
    MEGA_DB -.Backed by.-> MEGA_API
    
    Root_DNB --> ACA
    ACA --> ACR
    ACA --> AppInsights
    AppInsights --> LogAnalytics
    
    Internal_Agents --> A2A_Server
    A2A_Server --> A2A_Registry
    
    DataLoop_DB --> Fabric_Lakehouse
    Fabric_Lakehouse --> Fabric_Warehouse
    Fabric_Warehouse --> Reports

    classDef dnb_future fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    classDef azure_ai fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef azure_service fill:#bbdefb,stroke:#0d47a1,stroke-width:3px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef a2a fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class Copilot_UI,Portal,Root_DNB,Internal_Coord,External_Coord,Data_Coord dnb_future
    class Copilot_Model,OpenAI,Agent_Orchestrator,Flow_Templates,Safety_Filter azure_ai
    class Entra_ID,Managed_ID,DataLoop_DB,ATM_DB,MEGA_DB,ACA,ACR,AppInsights,LogAnalytics azure_service
    class Fabric_Lakehouse,Fabric_Warehouse,Fabric_ML,Reports data
    class A2A_Server,A2A_Registry a2a
```

## DNB IT Stack

### Required Microsoft Technologies

| Component | Microsoft Technology | Purpose |
|-----------|---------------------|---------|
| **Model** | GitHub Copilot / Azure OpenAI | DNB standard AI model |
| **Orchestration** | Azure AI Foundry Prompt Flow | Low-code agent design |
| **IDE** | Visual Studio Code + Copilot | Development environment |
| **Identity** | Azure Entra ID | Authentication & authorization |
| **Compute** | Azure Container Apps | Serverless container hosting |
| **Databases** | Azure SQL + PostgreSQL | Internal data sources |
| **Data Warehouse** | Azure Synapse Analytics (Dedicated SQL Pools) | XBRL Verrijkt (enriched) and other enterprise warehouses |
| **Observability** | Application Insights | Distributed tracing |
| **Data Platform** | Microsoft Fabric | Lakehouse + Warehouse |
| **Reporting** | Power BI | Executive dashboards |
| **Registry** | Azure Container Registry | Private container images |
| **Protocol** | Agent-to-Agent (A2A) | Cross-org communication |

## Microsoft AI Foundry Deep Dive

### Overview
Azure AI Foundry is the enterprise platform for model access, orchestration
(Prompt Flow), evaluation, and governed deployment.

### Drivers for Selection
- Compliance: EU residency, audit logging, integrated identity.
- Microsoft 365 (M365) Integration: Teams, Copilot Studio, SharePoint, Outlook.
- Low-Code Acceleration: Prompt Flow templates and connectors.
- Operational Foundations: Auto-scaling, high availability (HA), cost telemetry.

### Components

```mermaid
graph TB
    subgraph Foundry_Platform["Azure AI Foundry Platform"]
        direction TB
        
        subgraph Development["Development Environment"]
            AI_Studio["AI Foundry Studio<br/>Web-based IDE"]
            VS_Code["VS Code Extension<br/>Local Development"]
            Notebooks["Jupyter Notebooks<br/>Experimentation"]
        end
        
        subgraph Models["Model Management"]
            Model_Catalog["Model Catalog<br/>• Azure OpenAI (GPT-4, Copilot)<br/>• Open Source (Llama, Mistral)<br/>• Custom Fine-tuned"]
            Model_Registry["Model Registry<br/>Version Control<br/>A/B Testing"]
        end
        
        subgraph Orchestration["Orchestration Layer"]
            Prompt_Flow["Prompt Flow<br/>Visual Agent Designer"]
            Semantic_Kernel["Semantic Kernel<br/>Code-First Option"]
            LangChain["LangChain Integration<br/>Framework Bridge"]
        end
        
        subgraph Evaluation["Evaluation & Safety"]
            Eval_Suite["Evaluation Suite<br/>• Groundedness<br/>• Relevance<br/>• Coherence"]
            Safety_System["Content Safety<br/>• Jailbreak Detection<br/>• PII Filtering<br/>• Hate Speech"]
        end
        
        subgraph Deployment["Deployment Targets"]
            ACA_Deploy["Azure Container Apps<br/>Production Agents"]
            Functions_Deploy["Azure Functions<br/>Serverless Agents"]
            K8s_Deploy["Azure Kubernetes Service<br/>Complex Orchestration"]
        end
        
        subgraph Data_Integration["Data & Tools"]
            AI_Search["Azure AI Search<br/>Vector Database<br/>RAG Support"]
            Cosmos_DB["Cosmos DB<br/>Session State<br/>Memory Store"]
            Connectors["Built-in Connectors<br/>• Azure Services (300+)<br/>• REST APIs<br/>• Databases"]
        end
    end
    
    AI_Studio --> Prompt_Flow
    VS_Code --> Semantic_Kernel
    Notebooks --> Model_Catalog
    
    Prompt_Flow --> Model_Registry
    Semantic_Kernel --> Model_Registry
    
    Prompt_Flow --> Eval_Suite
    Prompt_Flow --> Safety_System
    
    Prompt_Flow --> ACA_Deploy
    Semantic_Kernel --> Functions_Deploy
    LangChain --> K8s_Deploy
    
    Prompt_Flow --> AI_Search
    Prompt_Flow --> Cosmos_DB
    Prompt_Flow --> Connectors

    classDef dev fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef models fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef orchestration fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef safety fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef deploy fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class AI_Studio,VS_Code,Notebooks dev
    class Model_Catalog,Model_Registry models
    class Prompt_Flow,Semantic_Kernel,LangChain orchestration
    class Eval_Suite,Safety_System safety
    class ACA_Deploy,Functions_Deploy,K8s_Deploy deploy
    class AI_Search,Cosmos_DB,Connectors data
```

### Prompt Flow vs Code-First Development

Azure AI Foundry supports **two development paradigms**:

#### **Option 1: Prompt Flow (Visual/Low-Code)** - Recommended for DNB

**Characteristics:**
- Drag-and-drop visual canvas for building agent workflows
- Pre-built nodes for LLM calls, tool invocations, conditional logic, loops
- Built-in debugging with step-through execution
- Automatic versioning and deployment to Azure
- Business analysts can contribute to agent development

**Best For:**
- Standard CRUD operations against internal databases
- API orchestration workflows (call API A → transform → call API B)
- Decision trees and approval workflows
- Report generation and data exports

**Example Use Cases at DNB:**
- "Get all pending reports for financial institution X"
- "Route supervisory questions to correct internal database"
- "Generate quarterly compliance summary from multiple sources"

#### **Option 2: Semantic Kernel (Code-First)** - For Complex Logic

**Characteristics:**
- .NET or Python SDK for programmatic agent development
- Full control over orchestration logic, error handling, retries
- Integration with existing codebases and libraries
- Requires software engineering skills
- Better for complex algorithms and custom business logic

**Best For:**
- Complex data transformations and calculations
- Custom authentication flows
- Integration with legacy systems
- Performance-critical scenarios

**Example Use Cases at DNB:**
- Advanced risk calculations with custom formulas
- Multi-step validation workflows with rollback logic
- Real-time fraud detection algorithms

### DNB Architectural Choice: Hybrid Approach

**Recommended Strategy:**

```mermaid
graph LR
    subgraph Layer1["Layer 1: Orchestration (Prompt Flow)"]
        Root["Root Agent<br/>Routing & Coordination"]
        Coordinators["Domain Coordinators<br/>Intent Classification"]
    end
    
    subgraph Layer2["Layer 2: Business Logic (Prompt Flow)"]
        Simple_Agents["Simple Specialists<br/>CRUD Operations<br/>API Calls<br/>Data Retrieval"]
    end
    
    subgraph Layer3["Layer 3: Complex Logic (Semantic Kernel)"]
        Complex_Agents["Complex Specialists<br/>Risk Calculations<br/>Validations<br/>Algorithms"]
    end
    
    subgraph Supporting["Supporting Services"]
        Custom_Tools["Custom Python/C# Tools<br/>Deployed as Azure Functions"]
    end
    
    Root --> Coordinators
    Coordinators --> Simple_Agents
    Coordinators --> Complex_Agents
    Complex_Agents --> Custom_Tools

    classDef pf fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef sk fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef tools fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    
    class Root,Coordinators,Simple_Agents pf
    class Complex_Agents sk
    class Custom_Tools tools
```

**Benefits of Hybrid Approach:**
- ✅ **80% of agents** use Prompt Flow (fast development, easy maintenance)
- ✅ **20% of agents** use Semantic Kernel (complex logic, performance-critical)
- ✅ **Custom tools** as Azure Functions (reusable across both approaches)
- ✅ **Business analysts** contribute to Prompt Flow agents
- ✅ **Developers** focus on complex Semantic Kernel agents

## Multi-Agent Orchestration Architecture

### DNB Multi-Agent System Overview

The DNB multi-agent system is designed as a **hierarchical orchestration pattern** with three distinct layers:

```mermaid
graph TB
    subgraph Layer1["Layer 1: System Root"]
        Root["Root Agent<br/><b>Role:</b> Entry Point & System Coordinator<br/><b>Model:</b> GitHub Copilot (GPT-4)<br/><b>Deployment:</b> Azure Container Apps"]
    end
    
    subgraph Layer2["Layer 2: Domain Coordinators"]
        Internal_Coord["Internal Services Coordinator<br/><b>Domain:</b> DataLoop + ATM + MEGA<br/><b>Auth:</b> Managed Identity + IAM"]
        External_Coord["External API Coordinator<br/><b>Domain:</b> DNB Public APIs<br/><b>Auth:</b> API Keys"]
        Data_Coord["Data Science Coordinator<br/><b>Domain:</b> Analytics + Reporting<br/><b>Tools:</b> Fabric + Power BI"]
    end
    
    subgraph Layer3_Internal["Layer 3A: Internal Service Specialists"]
        DataLoop["DataLoop Agent<br/><b>Database:</b> Azure SQL<br/><b>Purpose:</b> Report Status Queries"]
        ATM["ATM Agent<br/><b>Database:</b> PostgreSQL<br/><b>Purpose:</b> Model Metadata"]
        MEGA["MEGA Agent<br/><b>Database:</b> Azure SQL<br/><b>Purpose:</b> Validation Rules"]
    end
    
    subgraph Layer3_External["Layer 3B: External API Specialists"]
        Echo["Echo Agent<br/><b>API:</b> DNB Echo API<br/><b>Tools:</b> 3 endpoints"]
        Stats["Statistics Agent<br/><b>API:</b> DNB Statistics API<br/><b>Tools:</b> 79 endpoints"]
        PR["Public Register Agent<br/><b>API:</b> DNB Public Register API<br/><b>Tools:</b> 5 endpoints"]
    end
    
    subgraph Layer3_Data["Layer 3C: Data Science Specialists"]
        BigQuery["Fabric Lakehouse Agent<br/><b>Tool:</b> SQL Query Engine<br/><b>Purpose:</b> Historical Analytics"]
        Analytics["Analytics Agent<br/><b>Tool:</b> Python Code Interpreter<br/><b>Purpose:</b> Custom Calculations"]
        PowerBI["Power BI Agent<br/><b>Tool:</b> DAX Query Engine<br/><b>Purpose:</b> Dashboard Generation"]
    end
    
    Root -->|"Delegation"| Internal_Coord
    Root -->|"Delegation"| External_Coord
    Root -->|"Delegation"| Data_Coord
    
    Internal_Coord -->|"Task Assignment"| DataLoop
    Internal_Coord -->|"Task Assignment"| ATM
    Internal_Coord -->|"Task Assignment"| MEGA
    
    External_Coord -->|"Task Assignment"| Echo
    External_Coord -->|"Task Assignment"| Stats
    External_Coord -->|"Task Assignment"| PR
    
    Data_Coord -->|"Task Assignment"| BigQuery
    Data_Coord -->|"Task Assignment"| Analytics
    Data_Coord -->|"Task Assignment"| PowerBI

    classDef root fill:#ffcdd2,stroke:#c62828,stroke-width:4px
    classDef coordinator fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef specialist fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class Root root
    class Internal_Coord,External_Coord,Data_Coord coordinator
    class DataLoop,ATM,MEGA,Echo,Stats,PR,BigQuery,Analytics,PowerBI specialist
```

### Agent Communication Patterns

#### Pattern 1: Sequential Delegation (Most Common)

**Use Case**: User query requires data from a single domain

```mermaid
sequenceDiagram
    participant User
    participant Root as Root Agent
    participant Coord as Domain Coordinator
    participant Specialist as Specialist Agent
    participant Tool as Tool/Database

    User->>Root: "What's the status of report X?"
    Note over Root: Intent: Query DataLoop
    Root->>Coord: Delegate to Internal Services Coordinator
    Note over Coord: Domain: Internal databases
    Coord->>Specialist: Assign task to DataLoop Agent
    Specialist->>Tool: Execute SQL query (IAM auth)
    Tool-->>Specialist: Query results
    Specialist-->>Coord: Formatted response
    Coord-->>Root: Synthesized answer
    Root-->>User: Final response
```

**Key Characteristics:**
- ✅ Root agent identifies domain (internal vs external vs data science)
- ✅ Coordinator agent identifies specific specialist (DataLoop vs ATM vs MEGA)
- ✅ Specialist agent executes tool calls (SQL queries, API calls)
- ✅ Response flows back up the hierarchy
- ✅ Each layer adds context and formatting

#### Pattern 2: Parallel Fan-Out (Multi-Source Queries)

**Use Case**: User query requires data from multiple domains

```mermaid
sequenceDiagram
    participant User
    participant Root as Root Agent
    box Domain Coordinators
        participant Internal as Internal Coord
        participant External as External Coord
    end
    box Specialists
        participant DataLoop as DataLoop Agent
        participant Stats as Statistics Agent
    end

    User->>Root: "Compare report status with<br/>macroeconomic indicators"
    
    par Parallel Delegation
        Root->>Internal: Get report status
        Root->>External: Get economic data
    end
    
    par Parallel Execution
        Internal->>DataLoop: Query DataLoop DB
        External->>Stats: Call Statistics API
    end
    
    par Parallel Responses
        DataLoop-->>Internal: Report status
        Stats-->>External: Economic indicators
    end
    
    Internal-->>Root: Internal data
    External-->>Root: External data
    
    Note over Root: Synthesize & correlate results
    Root-->>User: Combined analysis
```

**Key Characteristics:**
- ✅ Root agent spawns multiple parallel tasks
- ✅ Each coordinator works independently
- ✅ Root agent waits for all responses (timeout: 60s)
- ✅ Root agent correlates and synthesizes final answer
- ✅ Handles partial failures gracefully

#### Pattern 3: A2A Cross-Organization (Future State)

**Use Case**: Agent-to-agent communication across DNB departments

```mermaid
sequenceDiagram
    participant User
    participant Root as DNB Root Agent
    participant Registry as DNB Agent Registry
    participant Remote as Remote Dept Agent<br/>(e.g., AFM, ECB)
    
    User->>Root: "Get pension fund data from AFM"
    Note over Root: Check if query requires<br/>cross-org collaboration
    
    Root->>Registry: Discover available agents<br/>GET /.well-known/agent-registry
    Registry-->>Root: Agent cards (AFM Pension Agent found)
    
    Root->>Remote: JSON-RPC task request<br/>POST /a2a/tasks
    Note over Remote: Execute query in AFM system
    Remote-->>Root: Task response (SSE streaming)
    
    Root-->>User: AFM pension fund data
```

**Key Characteristics:**
- ✅ Agents publish "agent cards" describing capabilities
- ✅ Central registry for agent discovery
- ✅ JSON-RPC 2.0 protocol for task management
- ✅ Server-Sent Events (SSE) for real-time updates
- ✅ OAuth 2.0 / Azure Entra ID for cross-org auth

### Agent State Management

**Challenge**: Maintaining conversation context across multiple agents in a hierarchy

**Solution**: Azure Cosmos DB as shared session store

```mermaid
graph LR
    subgraph Agents["Agent Layer"]
        Root[Root Agent]
        Coord1[Coordinator 1]
        Coord2[Coordinator 2]
        Spec1[Specialist 1]
        Spec2[Specialist 2]
    end
    
    subgraph State["State Management"]
        Cosmos[("Azure Cosmos DB<br/>Session Store")]
        
        subgraph Session["Session Document"]
            SessionID["session_id: uuid"]
            UserID["user_id: string"]
            Messages["messages: array"]
            Context["context: object"]
            Metadata["metadata: object"]
        end
    end
    
    Root -->|Read/Write| Cosmos
    Coord1 -->|Read/Write| Cosmos
    Coord2 -->|Read/Write| Cosmos
    Spec1 -->|Read| Cosmos
    Spec2 -->|Read| Cosmos
    
    Cosmos --> Session

    classDef agent fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef db fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef doc fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    
    class Root,Coord1,Coord2,Spec1,Spec2 agent
    class Cosmos db
    class SessionID,UserID,Messages,Context,Metadata doc
```

**Session Document Structure**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user@dnb.nl",
  "created_at": "2025-11-03T10:00:00Z",
  "updated_at": "2025-11-03T10:05:23Z",
  "messages": [
    {
      "role": "user",
      "content": "What's the status of report X?",
      "timestamp": "2025-11-03T10:00:00Z"
    },
    {
      "role": "root_agent",
      "content": "Delegating to Internal Services Coordinator",
      "timestamp": "2025-11-03T10:00:02Z"
    },
    {
      "role": "dataloop_agent",
      "content": "Query results: Report X status = APPROVED",
      "timestamp": "2025-11-03T10:00:05Z"
    }
  ],
  "context": {
    "current_agent": "root_agent",
    "delegation_chain": ["root_agent", "internal_coordinator", "dataloop_agent"],
    "active_domain": "internal_services"
  },
  "metadata": {
    "total_agents_invoked": 3,
    "total_tool_calls": 1,
    "total_tokens": 450
  }
}
```

**Key Benefits:**
- ✅ All agents share conversation history
- ✅ Coordinators understand previous delegation decisions
- ✅ Specialists see full user intent (not just coordinator instructions)
- ✅ Root agent tracks entire conversation flow for synthesis
- ✅ Cosmos DB provides global distribution and low latency

## Framework Migration Strategy

### From Google ADK to Azure AI Foundry

DNB's current prototype uses **Google ADK (Agent Development Kit)**, but production deployment must use **Azure AI Foundry**. This section explains the migration path.

### Architecture Mapping: ADK → Azure AI Foundry

```mermaid
graph LR
    subgraph ADK["Current: Google ADK"]
        ADK_Agent["Agent Class<br/>(Python)"]
        ADK_Runner["Runner<br/>(Orchestration)"]
        ADK_Tools["Tools<br/>(Python functions)"]
        ADK_Session["SessionService<br/>(In-memory)"]
        ADK_Model["Gemini 2.5-flash<br/>(Google AI)"]
    end
    
    subgraph Azure["Future: Azure AI Foundry"]
        AZ_PromptFlow["Prompt Flow<br/>(Visual Canvas)"]
        AZ_Orchestration["Agent Orchestration<br/>(Built-in)"]
        AZ_Connectors["Connectors<br/>(Pre-built + Custom)"]
        AZ_Cosmos["Cosmos DB<br/>(Managed State)"]
        AZ_Copilot["GitHub Copilot<br/>(Azure OpenAI)"]
    end
    
    ADK_Agent -.Migration.-> AZ_PromptFlow
    ADK_Runner -.Migration.-> AZ_Orchestration
    ADK_Tools -.Migration.-> AZ_Connectors
    ADK_Session -.Migration.-> AZ_Cosmos
    ADK_Model -.Migration.-> AZ_Copilot

    classDef adk fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef azure fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    
    class ADK_Agent,ADK_Runner,ADK_Tools,ADK_Session,ADK_Model adk
    class AZ_PromptFlow,AZ_Orchestration,AZ_Connectors,AZ_Cosmos,AZ_Copilot azure
```

### Component-by-Component Migration Guide

#### 1. **Agent Definitions** (ADK → Prompt Flow)

**Current ADK Code (Python):**
```python
from google.adk import Agent

dnb_statistics_agent = Agent(
    name="dnb_statistics_agent",
    model="gemini-2.5-flash",
    instruction="You are a specialist for DNB Statistics API.",
    tools=[toolbox_toolset.from_server("dnb_statistics_tools")]
)
```

**Future Prompt Flow (Visual Config):**
```yaml
# dnb_statistics_agent.yaml
agent:
  name: dnb_statistics_agent
  type: prompt_flow
  model:
    provider: azure_openai
    deployment: copilot-gpt4
    temperature: 0.2
  system_prompt: |
    You are a specialist for DNB Statistics API.
    Use the provided tools to query economic data.
  tools:
    - type: connector
      name: dnb_statistics_connector
      connection: dnb_statistics_api_connection
  deployment:
    target: azure_container_apps
    environment: dnb-production
```

**Migration Steps:**
1. Export ADK agent configuration as YAML
2. Import into Prompt Flow visual canvas
3. Configure model (Copilot instead of Gemini)
4. Map tools to Azure connectors
5. Test in AI Foundry Studio
6. Deploy to Container Apps

#### 2. **Tool Functions** (Python → Azure Functions)

**Current ADK Tool (Python):**
```python
@tool
def get_report_status(fi_id: str, report_type: str) -> dict:
    """Get current status of a regulatory report."""
    conn = get_db_connection()  # Local connection
    result = conn.execute(
        "SELECT status FROM reports WHERE fi_id = ? AND type = ?",
        (fi_id, report_type)
    )
    return {"status": result[0]}
```

**Future Azure Function (Python + Managed Identity):**
```python
import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get report status (Azure Function with Managed Identity)."""
    # Authenticate using Managed Identity (no keys needed)
    credential = ManagedIdentityCredential()
    
    # Connect to Azure SQL using IAM
    connection_string = get_connection_string(credential)
    conn = pymssql.connect(connection_string)
    
    # Execute query
    fi_id = req.params.get('fi_id')
    report_type = req.params.get('report_type')
    result = conn.execute(
        "SELECT status FROM reports WHERE fi_id = ? AND type = ?",
        (fi_id, report_type)
    )
    
    return func.HttpResponse(json.dumps({"status": result[0]}))
```

**Prompt Flow Integration:**
```yaml
# In Prompt Flow canvas
- node: get_report_status
  type: azure_function
  connection: dnb-function-app
  function_name: get_report_status
  inputs:
    fi_id: ${inputs.financial_institution_id}
    report_type: ${inputs.report_type}
  outputs:
    status: ${get_report_status.status}
```

#### 3. **Session Management** (In-Memory → Cosmos DB)

**Current ADK (In-Memory):**
```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = session_service.create_session(user_id="user@dnb.nl")
```

**Future Azure AI Foundry (Cosmos DB):**
```python
from azure.cosmos import CosmosClient
from azure.identity import ManagedIdentityCredential

# Authenticate with Managed Identity
credential = ManagedIdentityCredential()
client = CosmosClient(
    url="https://dnb-agents.documents.azure.com:443/",
    credential=credential
)

database = client.get_database_client("dnb_agents")
container = database.get_container_client("sessions")

# Create session
session_doc = {
    "session_id": str(uuid.uuid4()),
    "user_id": "user@dnb.nl",
    "messages": [],
    "created_at": datetime.utcnow().isoformat()
}
container.create_item(session_doc)
```

**Prompt Flow Auto-Configuration:**
- Prompt Flow automatically manages session state in Cosmos DB
- No manual code required for most scenarios
- Specify Cosmos DB connection in Prompt Flow settings

#### 4. **Multi-Agent Orchestration** (ADK Runner → Prompt Flow Router)

**Current ADK (Python Code):**
```python
from google.adk import Agent, Runner

root_agent = Agent(
    name="root_agent",
    sub_agents=[dnb_coordinator, data_science_coordinator]
)

runner = Runner()
response = runner.run(agent=root_agent, user_message="Get report status")
```

**Future Prompt Flow (Visual Routing):**
```mermaid
graph LR
    subgraph Prompt_Flow_Canvas["Prompt Flow Visual Canvas"]
        Input["User Input Node"]
        Intent["LLM Node<br/>Intent Classification"]
        Router["Router Node<br/>Condition Logic"]
        
        subgraph Tools["Tool Nodes"]
            DB_Tool["Database Query Tool<br/>Azure SQL + PostgreSQL"]
            API_Tool["REST API Tool<br/>Internal DNB APIs"]
            A2A_Tool["A2A Tool<br/>Remote Agent Call"]
        end
        
        Output["Output Node<br/>Formatted Response"]
    end

    Canvas --> Input
    Input --> LLM
    LLM --> Router
    Router --> Tools
    Tools --> Output

    classDef foundry fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef flow fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class Canvas,Nodes foundry
    class Input,LLM,Router,DB_Tool,API_Tool,A2A_Tool,Output flow
```

**Prompt Flow Configuration:**
```yaml
# root_agent_flow.yaml
nodes:
  - name: user_input
    type: input
    
  - name: intent_classifier
    type: llm
    model: copilot-gpt4
    prompt: |
      Classify user intent into: internal_query, api_query, analytics_query
      User query: ${user_input.message}
    output: ${intent}
    
  - name: router
    type: router
    conditions:
      - condition: ${intent} == "internal_query"
        next: call_internal_coordinator
      - condition: ${intent} == "api_query"
        next: call_external_coordinator
      - condition: ${intent} == "analytics_query"
        next: call_data_coordinator
    
  - name: call_internal_coordinator
    type: agent
    agent: internal_services_coordinator
    input: ${user_input.message}
    
  - name: merge_results
    type: python
    code: |
      # Combine results from all coordinators
      results = [r for r in [internal_result, external_result, data_result] if r]
      return {"combined": results}
```

## Security & Compliance Architecture

### DNB Security Requirements

As a financial regulatory authority, DNB has stringent security requirements that must be met:

#### 1. **Identity & Access Management (IAM)**

```mermaid
graph TB
    subgraph User_Layer["User Layer"]
        DNB_User["DNB Employee<br/>Azure Entra ID Account"]
        External_User["External Partner<br/>Guest Account"]
    end
    
    subgraph Authentication["Authentication Layer"]
        Entra_ID["Azure Entra ID<br/>Multi-Factor Auth (MFA)<br/>Conditional Access"]
        RBAC["Role-Based Access Control<br/>• Agent Admin<br/>• Agent User<br/>• Read-Only"]
    end
    
    subgraph Agent_Layer["Agent Layer"]
        Agent_Identity["Agent Managed Identity<br/>Service Principal<br/>No passwords/keys"]
    end
    
    subgraph Resource_Layer["Resource Layer"]
        SQL_IAM["Azure SQL<br/>IAM Authentication"]
        Postgres_IAM["PostgreSQL<br/>Azure AD Integration"]
        KeyVault["Azure Key Vault<br/>Secrets Management"]
    end
    
    DNB_User --> Entra_ID
    External_User --> Entra_ID
    Entra_ID --> RBAC
    RBAC --> Agent_Identity
    
    Agent_Identity --> SQL_IAM
    Agent_Identity --> Postgres_IAM
    Agent_Identity --> KeyVault

    classDef user fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef auth fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef agent fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef resource fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    
    class DNB_User,External_User user
    class Entra_ID,RBAC auth
    class Agent_Identity agent
    class SQL_IAM,Postgres_IAM,KeyVault resource
```

**Key Security Principles:**
- ✅ **Zero Trust**: Every request authenticated and authorized
- ✅ **Least Privilege**: Agents only access resources they need
- ✅ **No Secrets in Code**: All credentials in Key Vault or Managed Identity
- ✅ **Audit Trails**: All access logged to Log Analytics

#### 2. **Data Protection & Privacy**

```mermaid
graph TB
    subgraph Input["Data Input"]
        User_Query["User Query<br/>(May contain PII)"]
    end
    
    subgraph Safety_Layer["Content Safety Layer"]
        PII_Detection["PII Detection<br/>Azure AI Content Safety"]
        Jailbreak["Jailbreak Detection<br/>Prompt Injection Filter"]
        Hate_Speech["Hate Speech Filter<br/>Harmful Content"]
    end
    
    subgraph Processing["Processing Layer"]
        Agent_LLM["Agent + LLM<br/>Copilot Processing"]
        Encryption["Encryption at Rest<br/>TLS 1.3 in Transit"]
    end
    
    subgraph Storage["Storage Layer"]
        Cosmos_Encrypted["Cosmos DB<br/>Customer-Managed Keys (CMK)"]
        Logs_Masked["Log Analytics<br/>PII Masking"]
    end
    
    subgraph Output["Data Output"]
        Response["User Response<br/>(PII Redacted)"]
    end
    
    User_Query --> PII_Detection
    PII_Detection --> Jailbreak
    Jailbreak --> Hate_Speech
    Hate_Speech --> Agent_LLM
    Agent_LLM --> Encryption
    Encryption --> Cosmos_Encrypted
    Encryption --> Logs_Masked
    Encryption --> Response

    classDef input fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef safety fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef processing fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef storage fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef output fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class User_Query input
    class PII_Detection,Jailbreak,Hate_Speech safety
    class Agent_LLM,Encryption processing
    class Cosmos_Encrypted,Logs_Masked storage
    class Response output
```

**Data Protection Measures:**
- ✅ **PII Detection**: Automatic detection and masking of personal data
- ✅ **Encryption**: AES-256 at rest, TLS 1.3 in transit
- ✅ **Customer-Managed Keys**: DNB controls encryption keys
- ✅ **Data Residency**: All data stays in EU-West region
- ✅ **Retention Policies**: Automatic data deletion after 90 days

#### 3. **Audit & Compliance**

```mermaid
graph LR
    subgraph Events["Audit Events"]
        User_Action["User Actions<br/>• Login<br/>• Query<br/>• Export"]
        Agent_Action["Agent Actions<br/>• Tool Calls<br/>• DB Queries<br/>• API Calls"]
        System_Event["System Events<br/>• Deployments<br/>• Config Changes<br/>• Errors"]
    end
    
    subgraph Collection["Collection Layer"]
        AppInsights["Application Insights<br/>Real-time Telemetry"]
        LogAnalytics["Log Analytics<br/>Centralized Logs"]
    end
    
    subgraph Analysis["Analysis Layer"]
        Queries["KQL Queries<br/>Security Investigations"]
        Alerts["Azure Monitor Alerts<br/>Anomaly Detection"]
    end
    
    subgraph Reporting["Reporting Layer"]
        Dashboards["Azure Dashboards<br/>Real-time Metrics"]
        Compliance_Reports["Compliance Reports<br/>GDPR, NIS2, DORA"]
    end
    
    User_Action --> AppInsights
    Agent_Action --> AppInsights
    System_Event --> LogAnalytics
    
    AppInsights --> Queries
    LogAnalytics --> Queries
    Queries --> Alerts
    
    Queries --> Dashboards
    Queries --> Compliance_Reports

    classDef events fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef collection fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef analysis fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef reporting fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    
    class User_Action,Agent_Action,System_Event events
    class AppInsights,LogAnalytics collection
    class Queries,Alerts analysis
    class Dashboards,Compliance_Reports reporting
```

**Audit Capabilities:**
- ✅ **Complete Tracing**: Every request traced end-to-end
- ✅ **Immutable Logs**: Logs cannot be deleted or modified
- ✅ **Real-time Alerts**: Suspicious activity triggers alerts
- ✅ **Compliance Reports**: Automated GDPR/NIS2/DORA reporting

## Azure AI Foundry Integration

### Prompt Flow Agent Design

```mermaid
graph LR
    subgraph Foundry_Studio["Azure AI Foundry Studio"]
        Canvas["Visual Canvas<br/>Drag & Drop"]
        Nodes["Flow Nodes<br/>• LLM<br/>• Tool<br/>• Condition<br/>• Loop"]
    end

    subgraph Agent_Flow["DNB Agent Flow"]
        Input["User Input<br/>Natural Language"]
        LLM["Copilot Node<br/>Intent Recognition"]
        Router["Router Node<br/>Condition Logic"]
        
        subgraph Tools["Tool Nodes"]
            DB_Tool["Database Query Tool<br/>Azure SQL + PostgreSQL"]
            API_Tool["REST API Tool<br/>Internal DNB APIs"]
            A2A_Tool["A2A Tool<br/>Remote Agent Call"]
        end
        
        Output["Output Node<br/>Formatted Response"]
    end

    Canvas --> Input
    Input --> LLM
    LLM --> Router
    Router --> Tools
    Tools --> Output

    classDef foundry fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef flow fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class Canvas,Nodes foundry
    class Input,LLM,Router,DB_Tool,API_Tool,A2A_Tool,Output flow
```

## Internal Service Integration

**Key Requirements:**
- Azure Entra ID (formerly Azure Active Directory) for authentication
- Managed Identities for service-to-service auth
- Role-Based Access Control (RBAC) for database permissions
- Token refresh and caching
- Connection pooling for performance
...existing code...

## A2A Protocol Implementation
- JSON-RPC 2.0 (JavaScript Object Notation Remote Procedure Call) for task
  management; Server-Sent Events (SSE) for real-time updates.
...existing code...

## Data Science Platform
...existing code...

### Microsoft Fabric Integration
...existing code...

### Synapse Data Warehouses (Azure Synapse Analytics)
- XBRL Verrijkt (enriched) warehouse hosted on Azure Synapse Analytics
  Dedicated SQL pools; primary store for enriched XBRL filings.
- Access patterns:
  - Data Engineering Agent: Conversational T‑SQL and Spark for joins,
    compaction, and lineage-aware transformations.
  - Data Analytics Agent: Aggregations and slice‑and‑dice over curated schemas
    with citation and audit notes.
- Connectivity: Private endpoints, Managed Identity, Azure Entra ID RBAC.
- Coexistence with Microsoft Fabric: Fabric remains the enterprise data
  platform; Synapse serves existing warehouses and high-throughput SQL workloads.
...existing code...

## Deployment Architecture
...existing code...

## Technical Decision Matrix
...existing code...

#### 5. **Data Platform: Microsoft Fabric vs Databricks vs Synapse**
...existing code...

**Decision**: Microsoft Fabric (primary) + Azure Synapse Analytics (for existing
enterprise warehouses such as XBRL Verrijkt)

**Rationale**:
- Fabric is the enterprise standard for analytics and BI (business intelligence).
- Synapse supports existing dedicated SQL pools and high-throughput SQL needs.
- Agents converse with Synapse using governed T‑SQL/Spark while Fabric powers BI.
...existing code...

## Comparison: Current vs Future
...existing code...

## Migration Path
...existing code...

### From Current to Future
...existing code...
- Phase 3: Connect Azure Synapse Analytics (XBRL Verrijkt dedicated SQL pool)
  and configure Managed Identity + private endpoints.
...existing code...

## Summary
...existing code...
- Synapse integration: XBRL Verrijkt warehouse exposed to Data Engineering and
  Data Analytics agents through governed T‑SQL/Spark endpoints with RBAC and
  audit.
...existing code...
