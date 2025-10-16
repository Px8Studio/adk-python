# OpenAPI to Tool Converter Options

## Executive Summary

We currently manually configure DNB API tools in GenAI Toolbox using HTTP tool definitions. This document evaluates open-source tools that can automate the conversion from OpenAPI specs to various tool formats, including MCP servers and tool configurations.

## Current State

- **Manual Configuration**: We define each endpoint in `tools.dev.yaml` and `tools.prod.yaml`
- **OpenAPI Spec**: We have `openapi3-echo-api.yaml` for documentation
- **GenAI Toolbox**: Does NOT support direct OpenAPI ingestion - requires manual HTTP tool configuration

## Recommended Solutions

### 🏆 Option 1: cnoe-io/openapi-mcp-codegen (Python) - **RECOMMENDED**

**Repository**: https://github.com/cnoe-io/openapi-mcp-codegen

**Why This is Best for Us**:
- ✅ Generates **complete MCP servers** from OpenAPI specs
- ✅ Python-based (matches our backend stack)
- ✅ Generates **LangGraph agents** automatically (--generate-agent flag)
- ✅ Includes **evaluation and testing** (--generate-eval)
- ✅ Built-in **LLM-powered documentation generation**
- ✅ Supports OAuth2, API keys, Bearer tokens
- ✅ Active development (CNOE project)
- ✅ Complete project scaffolding with pyproject.toml, .env, README

**Installation**:
```bash
pip install --upgrade pip
# or use uvx (no install needed)
uvx --from git+https://github.com/cnoe-io/openapi-mcp-codegen.git openapi_mcp_codegen
```

**Usage for DNB Echo API**:
```bash
# Generate MCP server + LangGraph agent + eval
uvx --from git+https://github.com/cnoe-io/openapi-mcp-codegen.git openapi_mcp_codegen \
  --spec-file backend/apis/dnb/specs/openapi3-echo-api.yaml \
  --output-dir backend/apis/dnb/generated/mcp_server \
  --generate-agent \
  --generate-eval
```

**Output Structure**:
```
backend/apis/dnb/generated/mcp_server/
├── mcp_dnb_echo/
│   ├── api/
│   │   └── client.py         # HTTP client with auth
│   ├── models/
│   │   └── base.py
│   ├── tools/
│   │   └── helloworld.py     # Generated tool for /helloworld endpoint
│   └── server.py             # MCP server entry point
├── agent/
│   └── agent.py              # LangGraph agent with MCP integration
├── pyproject.toml
├── README.md
└── .env.example
```

**Advantages**:
- **Zero manual coding** - fully automated generation
- **Production-ready** - includes proper error handling, logging
- **Integration ready** - works directly with our existing LangGraph agents
- **Type-safe** - Pydantic models generated from schemas
- **Extensible** - can customize templates if needed

---

### Option 2: harsha-iiiv/openapi-mcp-generator (TypeScript/Node.js)

**Repository**: https://github.com/harsha-iiiv/openapi-mcp-generator

**Why Consider This**:
- ✅ NPM package - easy to install
- ✅ Multiple transport modes (stdio, SSE, StreamableHTTP)
- ✅ **Programmatic API** - can use in build scripts
- ✅ Filtering with `x-mcp` extension
- ✅ Built-in test clients

**Installation**:
```bash
npm install -g openapi-mcp-generator
```

**Usage**:
```bash
openapi-mcp-generator \
  --input backend/apis/dnb/specs/openapi3-echo-api.yaml \
  --output backend/apis/dnb/generated/mcp_server_ts \
  --server-name dnb-echo-api \
  --base-url https://api.dnb.nl/echo-api \
  --transport stdio
```

**Programmatic Usage** (Can integrate into build pipeline):
```javascript
import { getToolsFromOpenApi } from 'openapi-mcp-generator';

// Extract tool definitions
const tools = await getToolsFromOpenApi(
  'backend/apis/dnb/specs/openapi3-echo-api.yaml',
  {
    baseUrl: 'https://api.dnb.nl/echo-api',
    dereference: true
  }
);

// Generate GenAI Toolbox YAML from tools
tools.forEach(tool => {
  console.log(`  ${tool.operationId}:`);
  console.log(`    kind: http`);
  console.log(`    source: dnb-echo-api`);
  console.log(`    method: ${tool.method}`);
  console.log(`    path: ${tool.pathTemplate}`);
  console.log(`    description: ${tool.description}`);
});
```

**Advantages**:
- **Programmatic API** - can automate in CI/CD
- **Multiple transports** - flexible deployment options
- **TypeScript** - if we want to use Node.js agents

---

### Option 3: zxypro1/openapi-to-mcp-converter (TypeScript)

**Repository**: https://github.com/zxypro1/openapi-to-mcp-converter

**Why Consider This**:
- ✅ Lightweight and focused
- ✅ Runtime conversion (no code generation)
- ✅ Multiple transport support

**Usage**:
```typescript
import { OpenApiMCPSeverConverter } from 'openapi-mcp-converter';

const converter = new OpenApiMCPSeverConverter(openApiDoc, {
  timeout: 30000,
  security: { apiKey: process.env.DNB_SUBSCRIPTION_KEY_DEV }
});

const server = converter.getServer();
```

**Advantages**:
- **Runtime conversion** - no build step
- **Simple integration**
- **Good for dynamic APIs**

---

### Option 4: openapi2tools (Python - LangChain focused)

**PyPI**: https://pypi.org/project/openapi2tools/

**Why Consider This**:
- ✅ Direct LangChain/LangGraph integration
- ✅ Generates agent code directly
- ✅ Python-based

**Installation**:
```bash
pip install openapi2tools
```

**Usage**:
```bash
openapi2tools backend/apis/dnb/specs/openapi3-echo-api.yaml dnb_agent.py
```

**Advantages**:
- **Direct LangGraph integration**
- **Simpler than full MCP server**
- **Good for prototyping**

---

## Comparison Matrix

| Feature | cnoe-io | harsha-iiiv | zxypro1 | openapi2tools |
|---------|---------|-------------|---------|---------------|
| **Language** | Python ✅ | TypeScript | TypeScript | Python ✅ |
| **MCP Server** | ✅ Full | ✅ Full | ✅ Basic | ❌ |
| **LangGraph Agent** | ✅ Auto-gen | ⚠️ Manual | ⚠️ Manual | ✅ Auto-gen |
| **Evaluation/Testing** | ✅ | ❌ | ❌ | ❌ |
| **Programmatic API** | ❌ | ✅ | ✅ | ❌ |
| **Auth Support** | ✅ Full | ✅ Full | ✅ Basic | ⚠️ Limited |
| **Active Development** | ✅ | ✅ | ⚠️ Small | ⚠️ |
| **Documentation** | ✅ Excellent | ✅ Good | ⚠️ Basic | ⚠️ Basic |

---

## Recommended Implementation Strategy

### Phase 1: Proof of Concept (Week 1)
Use **cnoe-io/openapi-mcp-codegen** to generate MCP server from our Echo API

```bash
# 1. Generate from Echo API spec
cd c:\Users\rjjaf\_Projects\orkhon\backend\apis\dnb
mkdir -p generated

uvx --from git+https://github.com/cnoe-io/openapi-mcp-codegen.git openapi_mcp_codegen \
  --spec-file specs/openapi3-echo-api.yaml \
  --output-dir generated/dnb_echo_mcp \
  --generate-agent \
  --generate-eval

# 2. Review generated code
cd generated/dnb_echo_mcp
cat README.md

# 3. Test the generated MCP server
poetry install
poetry run mcp_dnb_echo
```

### Phase 2: Integration (Week 2)
1. Compare generated MCP server with our current manual configuration
2. Test with our existing agents
3. Validate authentication and error handling
4. Run generated evaluation suite

### Phase 3: Expand to Other APIs (Week 3-4)
1. Generate for Statistics API
2. Generate for Public Register API
3. Create build script to regenerate on spec changes
4. Document team workflow

### Phase 4: Automation (Week 5)
Create automation script:

```python
# scripts/generate_dnb_tools.py
import subprocess
import os

SPECS = [
    ("specs/openapi3-echo-api.yaml", "dnb_echo"),
    ("specs/openapi3_statisticsdatav2024100101.yaml", "dnb_statistics"),
    ("specs/openapi3_publicdatav1.yaml", "dnb_public_register"),
]

for spec_file, output_name in SPECS:
    print(f"Generating {output_name}...")
    subprocess.run([
        "uvx", "--from", "git+https://github.com/cnoe-io/openapi-mcp-codegen.git",
        "openapi_mcp_codegen",
        "--spec-file", spec_file,
        "--output-dir", f"generated/{output_name}",
        "--generate-agent",
        "--generate-eval"
    ])
```

---

## Alternative: Custom Script for GenAI Toolbox YAML

If we want to stay with GenAI Toolbox's HTTP tools but automate generation:

```python
# scripts/openapi_to_genai_toolbox.py
import yaml
import json
from pathlib import Path

def convert_openapi_to_toolbox(openapi_file, output_file):
    """Convert OpenAPI spec to GenAI Toolbox HTTP tool configuration"""
    
    with open(openapi_file) as f:
        if openapi_file.endswith('.yaml') or openapi_file.endswith('.yml'):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    
    base_url = spec['servers'][0]['url']
    
    # Extract source configuration
    source_name = spec['info']['title'].lower().replace(' ', '-')
    sources = {
        source_name: {
            'kind': 'http',
            'baseUrl': base_url,
            'headers': {
                'Accept': 'application/json',
                # Add auth headers from securitySchemes
            },
            'timeout': '30s'
        }
    }
    
    # Extract tools from paths
    tools = {}
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if method not in ['get', 'post', 'put', 'delete', 'patch']:
                continue
            
            operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
            
            tool_config = {
                'kind': 'http',
                'source': source_name,
                'method': method.upper(),
                'path': path,
                'description': operation.get('description') or operation.get('summary', '')
            }
            
            # Add parameters
            if 'parameters' in operation:
                query_params = [
                    p for p in operation['parameters'] 
                    if p.get('in') == 'query'
                ]
                if query_params:
                    tool_config['queryParams'] = [
                        {
                            'name': p['name'],
                            'type': p.get('schema', {}).get('type', 'string'),
                            'description': p.get('description', '')
                        }
                        for p in query_params
                    ]
            
            tools[operation_id] = tool_config
    
    # Write output
    config = {'sources': sources, 'tools': tools}
    with open(output_file, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)
    
    print(f"✅ Generated {len(tools)} tools from {openapi_file}")
    print(f"📝 Output: {output_file}")

# Usage
if __name__ == '__main__':
    convert_openapi_to_toolbox(
        'backend/apis/dnb/specs/openapi3-echo-api.yaml',
        'backend/toolbox/config/tools.dev.generated.yaml'
    )
```

---

## Conclusion

**Primary Recommendation**: Use **cnoe-io/openapi-mcp-codegen**

**Reasons**:
1. ✅ Python-based (matches our stack)
2. ✅ Generates complete MCP servers (future-proof for MCP adoption)
3. ✅ Auto-generates LangGraph agents (perfect for our use case)
4. ✅ Includes evaluation and testing
5. ✅ Active development and good documentation
6. ✅ Can scale to all three DNB APIs

**Next Steps**:
1. Run POC with Echo API (this week)
2. Compare output with manual configuration
3. If successful, expand to Statistics and Public Register APIs
4. Create automation script for regeneration
5. Update team documentation

**Fallback**: If MCP servers are overkill, use the custom Python script above to generate GenAI Toolbox YAML configs from OpenAPI specs.
