#!/usr/bin/env python3
"""
OpenAPI to GenAI Toolbox Converter

A generic, reusable converter that transforms OpenAPI 3.0 specifications into 
GenAI Toolbox HTTP tool YAML format.

Features:
- Path-based tool naming (converts endpoint paths to tool names)
- Optional configurable tool prefixes for organizational branding
- Automatic parameter extraction and type mapping
- Request body template generation
- Environment-specific configuration (dev/prod)
- Validation against GenAI Toolbox requirements

Usage:
    python openapi_to_toolbox.py convert --api echo
    python openapi_to_toolbox.py convert --all
    python openapi_to_toolbox.py validate --api echo
    python openapi_to_toolbox.py diff --api echo
    python openapi_to_toolbox.py list

Configuration:
    Add APIs to the APIS dictionary with optional tool_prefix:
    
    APIS = {
        "my-api": {
            "spec": "openapi-spec.yaml",
            "description": "My API",
            "prefix": "10",
            "tool_prefix": "myorg"  # Optional: adds organizational prefix
        }
    }

See CONFIGURATION_GUIDE.md for detailed configuration options.
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml
import json
from dataclasses import dataclass
from enum import Enum
import re


# Base paths
SCRIPT_DIR = Path(__file__).parent
DNB_DIR = SCRIPT_DIR.parent / "apis" / "dnb"
SPECS_DIR = DNB_DIR / "specs"
GENERATED_DIR = DNB_DIR / "generated"
TOOLBOX_DIR = DNB_DIR.parent.parent / "toolbox" / "config"
TOOLBOX_DEV_DIR = TOOLBOX_DIR / "dev"
TOOLBOX_PROD_DIR = TOOLBOX_DIR / "prod"

# Ensure directories exist
GENERATED_DIR.mkdir(exist_ok=True)
TOOLBOX_DEV_DIR.mkdir(exist_ok=True)
TOOLBOX_PROD_DIR.mkdir(exist_ok=True)


# Type mapping from OpenAPI to GenAI Toolbox
OPENAPI_TO_TOOLBOX_TYPE_MAP = {
    'integer': 'integer',
    'number': 'number',
    'string': 'string',
    'boolean': 'boolean',
    'array': 'string',  # GenAI Toolbox doesn't support array type in parameters, use string
    'object': 'object',
}


def map_openapi_type(openapi_type: str) -> str:
    """Map OpenAPI type to GenAI Toolbox type"""
    return OPENAPI_TO_TOOLBOX_TYPE_MAP.get(openapi_type, 'string')


class AuthType(Enum):
    """Supported authentication types"""
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    OAUTH2 = "oauth2"


@dataclass
class ToolParameter:
    """Represents a tool parameter"""
    name: str
    param_type: str  # query, path, header, body
    data_type: str
    required: bool
    description: str = ""
    default: Optional[Any] = None


@dataclass
class ToolDefinition:
    """Represents a GenAI Toolbox tool"""
    id: str
    source_id: str
    method: str
    path: str
    description: str
    parameters: List[ToolParameter]
    request_body_template: Optional[str] = None
    
    def _convert_path_to_go_template(self, path: str) -> str:
        """Convert OpenAPI {param} syntax to Go template {{.param}} syntax"""
        return re.sub(r'\{([^}]+)\}', r'{{.\1}}', path)
    
    def to_toolbox_format(self) -> Dict[str, Any]:
        """Convert to GenAI Toolbox YAML format (dictionary format)"""
        tool = {
            "kind": "http",
            "source": self.source_id,
            "method": self.method,
            "path": self._convert_path_to_go_template(self.path),  # Convert path parameters
            "description": self.description
        }
        
        # Map parameters to GenAI Toolbox format
        # Toolbox uses specific field names: queryParams, pathParams, headers, body
        if self.parameters:
            # Group by parameter type
            query_params = [p for p in self.parameters if p.param_type == "query"]
            path_params = [p for p in self.parameters if p.param_type == "path"]
            header_params = [p for p in self.parameters if p.param_type == "header"]
            body_params = [p for p in self.parameters if p.param_type == "body"]
            
            # Add query parameters
            if query_params:
                tool["queryParams"] = [
                    {
                        "name": p.name,
                        "type": p.data_type,
                        "description": p.description or "",  # Always include description
                        "required": p.required,
                        **({"default": p.default} if p.default is not None else {})
                    }
                    for p in query_params
                ]
            
            # Add path parameters
            if path_params:
                tool["pathParams"] = [
                    {
                        "name": p.name,
                        "type": p.data_type,
                        "description": p.description or "",  # Always include description
                        "required": p.required
                    }
                    for p in path_params
                ]
            
            # Add header parameters
            if header_params:
                tool["headers"] = [
                    {
                        "name": p.name,
                        "type": p.data_type,
                        "description": p.description or "",  # Always include description
                        "required": p.required
                    }
                    for p in header_params
                ]
            
            # Add body parameters
            if body_params:
                tool["bodyParams"] = [
                    {
                        "name": p.name,
                        "type": p.data_type,
                        "description": p.description or "",
                        "required": p.required
                    }
                    for p in body_params
                ]
        
        # Add request body template if present
        if self.request_body_template:
            tool["requestBody"] = self.request_body_template
        
        return tool


@dataclass
class SourceDefinition:
    """Represents a GenAI Toolbox HTTP source"""
    id: str
    type: str
    base_url: str
    headers: Dict[str, str]
    timeout: int = 30
    
    def to_toolbox_format(self) -> Dict[str, Any]:
        """Convert to GenAI Toolbox YAML format (dictionary format)"""
        return {
            "kind": "http",  # Changed from "type" to "kind"
            "baseUrl": self.base_url,  # Changed from "base_url" to "baseUrl"
            "headers": self.headers,
            "timeout": f"{self.timeout}s"  # Add 's' suffix for timeout
        }


class OpenAPIParser:
    """Parse OpenAPI 3.0 specifications"""
    
    def __init__(self, spec_path: Path):
        self.spec_path = spec_path
        self.spec = self._load_spec()
    
    def _load_spec(self) -> Dict:
        """Load and parse OpenAPI specification"""
        with open(self.spec_path, 'r', encoding='utf-8') as f:
            if self.spec_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif self.spec_path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {self.spec_path.suffix}")
    
    def get_title(self) -> str:
        """Get API title"""
        return self.spec.get('info', {}).get('title', 'Unknown API')
    
    def get_version(self) -> str:
        """Get API version"""
        return self.spec.get('info', {}).get('version', '1.0.0')
    
    def get_description(self) -> str:
        """Get API description"""
        return self.spec.get('info', {}).get('description', '')
    
    def get_base_url(self) -> str:
        """Extract base URL from servers"""
        servers = self.spec.get('servers', [])
        if servers:
            return servers[0].get('url', '')
        return ''
    
    def get_security_config(self) -> Tuple[AuthType, Dict[str, str]]:
        """Extract authentication configuration"""
        security = self.spec.get('security', [])
        if not security:
            return AuthType.API_KEY, {}
        
        # Get first security requirement
        security_req = security[0]
        scheme_name = list(security_req.keys())[0]
        
        # Get security scheme definition
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        scheme = security_schemes.get(scheme_name, {})
        
        scheme_type = scheme.get('type', 'apiKey')
        
        if scheme_type == 'apiKey':
            header_name = scheme.get('name', 'X-API-Key')
            # Use environment variable reference
            return AuthType.API_KEY, {header_name: "${DNB_SUBSCRIPTION_KEY}"}
        elif scheme_type == 'http':
            auth_scheme = scheme.get('scheme', 'bearer')
            if auth_scheme == 'bearer':
                return AuthType.BEARER, {"Authorization": "Bearer ${DNB_TOKEN}"}
            elif auth_scheme == 'basic':
                return AuthType.BASIC, {"Authorization": "Basic ${DNB_CREDENTIALS}"}
        
        return AuthType.API_KEY, {}
    
    def generate_request_body_template(self, schema: Dict) -> Tuple[Optional[str], List[ToolParameter]]:
        """
        Generate Go template for request body from OpenAPI schema
        
        Returns:
            (template_string, list_of_body_params)
        """
        if not schema:
            return None, []
        
        schema_type = schema.get('type', 'object')
        
        # Handle object type (most common for JSON APIs)
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            if not properties:
                return None, []
            
            body_params = []
            template_props = []
            
            for prop_name, prop_schema in properties.items():
                prop_type = prop_schema.get('type', 'string')
                mapped_type = map_openapi_type(prop_type)
                
                # Get description, use property name as fallback if empty
                prop_desc = prop_schema.get('description', '').strip()
                if not prop_desc:
                    prop_desc = f"Property: {prop_name}"
                
                body_params.append(ToolParameter(
                    name=prop_name,
                    param_type='body',
                    data_type=mapped_type,
                    required=prop_name in required,
                    description=prop_desc
                ))
                
                # Generate template line based on type
                # Non-string types don't need quotes in JSON
                if prop_type in ['integer', 'number', 'boolean', 'array', 'object']:
                    template_props.append(f'    "{prop_name}": {{{{.{prop_name}}}}}')
                else:
                    # Strings need quotes
                    template_props.append(f'    "{prop_name}": "{{{{.{prop_name}}}}}"')
            
            # Build JSON template
            template = "{\n" + ",\n".join(template_props) + "\n  }"
            return template, body_params
        
        elif schema_type == 'array':
            # Handle array request bodies
            return "{{json .body}}", [ToolParameter(
                name='body',
                param_type='body',
                data_type='array',
                required=True,
                description='Array request body'
            )]
        
        else:
            # Handle primitive types (string, integer, etc.)
            return "{{.body}}", [ToolParameter(
                name='body',
                param_type='body',
                data_type=schema_type,
                required=True,
                description='Request body'
            )]
    
    def extract_parameters(self, operation: Dict) -> Tuple[List[ToolParameter], Optional[str]]:
        """Extract parameters from an operation
        
        Returns:
            (parameters_list, request_body_template)
        """
        parameters = []
        request_body_template = None
        
        # Path and query parameters
        for param in operation.get('parameters', []):
            param_in = param.get('in', 'query')
            param_schema = param.get('schema', {})
            
            # Get description, use parameter name as fallback if empty
            param_desc = param.get('description', '').strip()
            if not param_desc:
                param_desc = f"Parameter: {param.get('name', 'unknown')}"
            
            parameters.append(ToolParameter(
                name=param.get('name', ''),
                param_type=param_in,
                data_type=map_openapi_type(param_schema.get('type', 'string')),
                required=param.get('required', False),
                description=param_desc,
                default=param_schema.get('default')
            ))
        
        # Request body - generate template and parameters
        if 'requestBody' in operation:
            request_body = operation['requestBody']
            content = request_body.get('content', {})
            
            # Get first content type (usually application/json)
            if content:
                content_type = list(content.keys())[0]
                schema = content[content_type].get('schema', {})
                
                # Generate template and body parameters
                request_body_template, body_params = self.generate_request_body_template(schema)
                parameters.extend(body_params)
        
        return parameters, request_body_template
    
    def get_operations(self) -> List[Tuple[str, str, Dict]]:
        """Extract all operations (path, method, operation)"""
        operations = []
        
        for path, path_item in self.spec.get('paths', {}).items():
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method in path_item:
                    operations.append((path, method, path_item[method]))
        
        return operations
    
    def extract_path_params_from_path(self, path: str) -> List[str]:
        """Extract parameter names from path template like /users/{userId}"""
        return re.findall(r'\{([^}]+)\}', path)


class GenAIToolboxGenerator:
    """Generate GenAI Toolbox YAML configuration"""
    
    def __init__(self, api_id: str, parser: OpenAPIParser, tool_prefix: Optional[str] = None):
        """
        Initialize the generator
        
        Args:
            api_id: API identifier (e.g., 'echo', 'statistics')
            parser: OpenAPI parser instance
            tool_prefix: Optional prefix for tool names (e.g., 'dnb' -> 'dnb_echo_helloworld')
                        If None, only uses api_id (e.g., 'echo_helloworld')
        """
        self.api_id = api_id
        self.parser = parser
        self.tool_prefix = tool_prefix
    
    def generate_source_id(self) -> str:
        """Generate source ID using underscores (GenAI Toolbox convention)"""
        return f"{self.api_id.replace('-', '_')}_api"
    
    def generate_tool_id(self, operation: Dict, method: str, path: str) -> str:
        """Generate tool ID from operation path
        
        Strategy:
        - Use the URL path directly as the tool name
        - Replace hyphens with underscores
        - Remove path parameters (e.g., {registerCode})
        - Optionally prefix with {tool_prefix}_{api_name}_ (configurable)
        
        Following GenAI Toolbox naming conventions:
        - Tool names should be valid Python identifiers
        - Must start with letter or underscore
        - Can contain a-z, A-Z, 0-9, underscores, dots
        
        Examples (with tool_prefix='dnb'):
        - /summary-balance-sheet-of-insurance-corporations-by-type-quarter
          → dnb_statistics_summary_balance_sheet_of_insurance_corporations_by_type_quarter
        - /api/publicregister/{registerCode}/Organizations
          → dnb_public_register_api_publicregister_organizations
        
        Examples (without tool_prefix):
        - /summary-balance-sheet-of-insurance-corporations-by-type-quarter
          → statistics_summary_balance_sheet_of_insurance_corporations_by_type_quarter
        - /api/publicregister/{registerCode}/Organizations
          → public_register_api_publicregister_organizations
        """
        # Extract clean path name:
        # 1. Remove leading/trailing slashes
        # 2. Remove path parameters like {registerCode}
        # 3. Replace remaining slashes with underscores
        # 4. Replace hyphens with underscores
        clean_path = path.strip('/')
        
        # Remove path parameters and their slashes
        # E.g., "/api/publicregister/{registerCode}/Organizations" → "api/publicregister/Organizations"
        clean_path = re.sub(r'/\{[^}]+\}', '', clean_path)
        
        # Replace slashes with underscores
        clean_path = clean_path.replace('/', '_')
        
        # Replace hyphens with underscores
        clean_path = clean_path.replace('-', '_')
        
        # Build tool ID with optional prefix
        # Convert api_id (like "public-register") to underscore format
        api_prefix = self.api_id.replace('-', '_')
        
        # Apply tool_prefix if configured
        if self.tool_prefix:
            tool_id = f"{self.tool_prefix}_{api_prefix}_{clean_path}".lower()
        else:
            tool_id = f"{api_prefix}_{clean_path}".lower()
        
        # Ensure valid identifier (remove any remaining invalid characters)
        tool_id = re.sub(r'[^a-z0-9_.]', '_', tool_id)
        
        # Remove multiple consecutive underscores
        tool_id = re.sub(r'_+', '_', tool_id)
        
        # Truncate to 128 characters if needed (reasonable limit for tool names)
        # This allows most full path names while preventing excessively long identifiers
        if len(tool_id) > 128:
            tool_id = tool_id[:128]
        
        return tool_id
    
    def generate_source(self) -> SourceDefinition:
        """Generate HTTP source definition"""
        base_url = self.parser.get_base_url()
        auth_type, headers = self.parser.get_security_config()
        
        return SourceDefinition(
            id=self.generate_source_id(),
            type="http",
            base_url=base_url,
            headers=headers,
            timeout=30
        )
    
    def generate_tools(self) -> List[ToolDefinition]:
        """Generate tool definitions for all operations"""
        tools = []
        source_id = self.generate_source_id()
        
        for path, method, operation in self.parser.get_operations():
            tool_id = self.generate_tool_id(operation, method, path)
            description = operation.get('summary', operation.get('description', ''))
            parameters, request_body_template = self.parser.extract_parameters(operation)
            
            tools.append(ToolDefinition(
                id=tool_id,
                source_id=source_id,
                method=method.upper(),
                path=path,
                description=description,
                parameters=parameters,
                request_body_template=request_body_template
            ))
        
        return tools
    
    def generate_toolset(self, tools: List[ToolDefinition]) -> Dict[str, List[str]]:
        """Generate toolset definition for this API"""
        # Use underscores for toolset names (GenAI Toolbox convention)
        api_name = self.api_id.replace('-', '_')
        
        # Apply tool_prefix if configured
        if self.tool_prefix:
            toolset_name = f"{self.tool_prefix}_{api_name}_tools"
        else:
            toolset_name = f"{api_name}_tools"
        
        tool_ids = [tool.id for tool in tools]
        return {toolset_name: tool_ids}
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate complete GenAI Toolbox configuration in dictionary format"""
        source = self.generate_source()
        tools = self.generate_tools()
        
        # Convert to dictionary format (not list)
        sources_dict = {source.id: source.to_toolbox_format()}
        tools_dict = {tool.id: tool.to_toolbox_format() for tool in tools}
        toolsets_dict = self.generate_toolset(tools)
        
        return {
            "sources": sources_dict,
            "tools": tools_dict,
            "toolsets": toolsets_dict
        }


class ConfigValidator:
    """Validate generated configuration against manual configuration"""
    
    def __init__(self, generated_config: Dict, manual_config: Dict):
        self.generated = generated_config
        self.manual = manual_config
    
    def validate_sources(self) -> List[str]:
        """Validate source configurations"""
        issues = []
        
        gen_sources = {s['id']: s for s in self.generated.get('sources', [])}
        man_sources = {s['id']: s for s in self.manual.get('sources', [])}
        
        # Check for missing sources
        gen_ids = set(gen_sources.keys())
        man_ids = set(man_sources.keys())
        
        missing = man_ids - gen_ids
        if missing:
            issues.append(f"Missing sources in generated config: {missing}")
        
        extra = gen_ids - man_ids
        if extra:
            issues.append(f"Extra sources in generated config: {extra}")
        
        # Check source configurations
        for source_id in gen_ids & man_ids:
            gen_source = gen_sources[source_id]
            man_source = man_sources[source_id]
            
            if gen_source['config']['base_url'] != man_source['config']['base_url']:
                issues.append(
                    f"Source {source_id}: base_url mismatch\n"
                    f"  Generated: {gen_source['config']['base_url']}\n"
                    f"  Manual: {man_source['config']['base_url']}"
                )
        
        return issues
    
    def validate_tools(self) -> List[str]:
        """Validate tool configurations"""
        issues = []
        
        gen_tools = {t['id']: t for t in self.generated.get('tools', [])}
        man_tools = {t['id']: t for t in self.manual.get('tools', [])}
        
        # Check for missing tools
        gen_ids = set(gen_tools.keys())
        man_ids = set(man_tools.keys())
        
        missing = man_ids - gen_ids
        if missing:
            issues.append(f"Missing tools in generated config: {missing}")
        
        extra = gen_ids - man_ids
        if extra:
            issues.append(f"Extra tools in generated config: {extra}")
        
        # Check tool configurations
        for tool_id in gen_ids & man_ids:
            gen_tool = gen_tools[tool_id]
            man_tool = man_tools[tool_id]
            
            # Check method
            if gen_tool['method'] != man_tool['method']:
                issues.append(
                    f"Tool {tool_id}: method mismatch\n"
                    f"  Generated: {gen_tool['method']}\n"
                    f"  Manual: {man_tool['method']}"
                )
            
            # Check path
            if gen_tool['path'] != man_tool['path']:
                issues.append(
                    f"Tool {tool_id}: path mismatch\n"
                    f"  Generated: {gen_tool['path']}\n"
                    f"  Manual: {man_tool['path']}"
                )
        
        return issues
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Run all validations"""
        issues = []
        issues.extend(self.validate_sources())
        issues.extend(self.validate_tools())
        
        return len(issues) == 0, issues


class ConfigComparator:
    """Compare and generate diffs between configurations"""
    
    def __init__(self, generated_config: Dict, manual_config: Dict):
        self.generated = generated_config
        self.manual = manual_config
    
    def _normalize_sources(self, config: Dict) -> Dict[str, Dict]:
        """Normalize sources to dict format"""
        sources = config.get('sources', {})
        
        # If it's already a dict (manual format)
        if isinstance(sources, dict):
            return sources
        
        # If it's a list (generated format), convert to dict
        if isinstance(sources, list):
            return {s['id']: s for s in sources}
        
        return {}
    
    def _normalize_tools(self, config: Dict) -> Dict[str, Dict]:
        """Normalize tools to dict format"""
        tools = config.get('tools', {})
        
        # If it's already a dict (manual format)
        if isinstance(tools, dict):
            return tools
        
        # If it's a list (generated format), convert to dict
        if isinstance(tools, list):
            return {t['id']: t for t in tools}
        
        return {}
    
    def generate_diff_report(self) -> str:
        """Generate human-readable diff report"""
        lines = []
        lines.append("=" * 80)
        lines.append("Configuration Comparison Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Normalize configs
        gen_sources = self._normalize_sources(self.generated)
        man_sources = self._normalize_sources(self.manual)
        
        # Sources diff
        lines.append("SOURCES:")
        lines.append("-" * 80)
        
        all_source_ids = set(gen_sources.keys()) | set(man_sources.keys())
        
        if not all_source_ids:
            lines.append("  (No sources found)")
        
        for source_id in sorted(all_source_ids):
            gen = gen_sources.get(source_id)
            man = man_sources.get(source_id)
            
            if gen and man:
                lines.append(f"\n  {source_id}:")
                lines.append(f"    Status: ✓ Present in both")
                
                # Extract base URL (handle both formats)
                gen_url = gen.get('config', {}).get('base_url') or gen.get('baseUrl', '')
                man_url = man.get('config', {}).get('base_url') or man.get('baseUrl', '')
                
                if gen_url == man_url:
                    lines.append(f"    Base URL: ✓ {gen_url}")
                else:
                    lines.append(f"    Base URL: ✗ MISMATCH")
                    lines.append(f"      Generated: {gen_url}")
                    lines.append(f"      Manual:    {man_url}")
                
                # Extract headers (handle both formats)
                gen_headers = gen.get('config', {}).get('headers') or gen.get('headers', {})
                man_headers = man.get('config', {}).get('headers') or man.get('headers', {})
                
                if gen_headers == man_headers:
                    lines.append(f"    Headers: ✓ Match")
                else:
                    lines.append(f"    Headers: ✗ MISMATCH")
                    lines.append(f"      Generated: {gen_headers}")
                    lines.append(f"      Manual:    {man_headers}")
            
            elif gen:
                lines.append(f"\n  {source_id}:")
                lines.append(f"    Status: ⚠ Only in GENERATED config")
            else:
                lines.append(f"\n  {source_id}:")
                lines.append(f"    Status: ⚠ Only in MANUAL config")
        
        lines.append("")
        lines.append("=" * 80)
        
        # Normalize tools
        gen_tools = self._normalize_tools(self.generated)
        man_tools = self._normalize_tools(self.manual)
        
        # Tools diff
        lines.append("TOOLS:")
        lines.append("-" * 80)
        
        all_tool_ids = set(gen_tools.keys()) | set(man_tools.keys())
        
        if not all_tool_ids:
            lines.append("  (No tools found)")
        
        for tool_id in sorted(all_tool_ids):
            gen = gen_tools.get(tool_id)
            man = man_tools.get(tool_id)
            
            if gen and man:
                lines.append(f"\n  {tool_id}:")
                lines.append(f"    Status: ✓ Present in both")
                
                # Compare method
                gen_method = gen.get('method', '')
                man_method = man.get('method', '')
                
                if gen_method == man_method:
                    lines.append(f"    Method: ✓ {gen_method}")
                else:
                    lines.append(f"    Method: ✗ MISMATCH")
                    lines.append(f"      Generated: {gen_method}")
                    lines.append(f"      Manual:    {man_method}")
                
                # Compare path
                gen_path = gen.get('path', '')
                man_path = man.get('path', '')
                
                if gen_path == man_path:
                    lines.append(f"    Path: ✓ {gen_path}")
                else:
                    lines.append(f"    Path: ✗ MISMATCH")
                    lines.append(f"      Generated: {gen_path}")
                    lines.append(f"      Manual:    {man_path}")
            
            elif gen:
                lines.append(f"\n  {tool_id}:")
                lines.append(f"    Status: ⚠ Only in GENERATED config")
                lines.append(f"    Method: {gen.get('method', 'N/A')}")
                lines.append(f"    Path: {gen.get('path', 'N/A')}")
            else:
                lines.append(f"\n  {tool_id}:")
                lines.append(f"    Status: ⚠ Only in MANUAL config")
                lines.append(f"    Method: {man.get('method', 'N/A')}")
                lines.append(f"    Path: {man.get('path', 'N/A')}")
        
        lines.append("")
        lines.append("=" * 80)
        
        # Summary
        total_sources = len(all_source_ids)
        matching_sources = len([sid for sid in all_source_ids 
                               if sid in gen_sources and sid in man_sources])
        total_tools = len(all_tool_ids)
        matching_tools = len([tid for tid in all_tool_ids 
                             if tid in gen_tools and tid in man_tools])
        
        lines.append("SUMMARY:")
        lines.append(f"  Sources: {matching_sources}/{total_sources} match")
        lines.append(f"  Tools: {matching_tools}/{total_tools} match")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# API configurations with file prefixes for ordering
APIS = {
    "echo": {
        "spec": "openapi3-echo-api.yaml",
        "description": "DNB Echo API - Test endpoint for API connectivity",
        "prefix": "10",
        "tool_prefix": "dnb"  # Optional: prefix for tool names (e.g., dnb_echo_helloworld)
    },
    "statistics": {
        "spec": "openapi3_statisticsdatav2024100101.yaml",
        "description": "DNB Statistics API - Dutch banking statistics data",
        "prefix": "20",
        "tool_prefix": "dnb"  # Optional: prefix for tool names
    },
    "public-register": {
        "spec": "openapi3_publicdatav1.yaml",
        "description": "DNB Public Register API - Licensed financial institutions",
        "prefix": "30",
        "tool_prefix": "dnb"  # Optional: prefix for tool names
    }
}


def validate_generated_config(config: Dict[str, Any]) -> List[str]:
    """Validate generated config against GenAI Toolbox requirements
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check sources
    sources = config.get('sources', {})
    if not sources:
        errors.append("Configuration has no sources defined")
    
    for source_id, source in sources.items():
        if 'kind' not in source:
            errors.append(f"Source '{source_id}': missing required field 'kind'")
        elif source['kind'] != 'http':
            errors.append(f"Source '{source_id}': only 'http' kind is supported, got '{source['kind']}'")
        
        if 'baseUrl' not in source:
            errors.append(f"Source '{source_id}': missing required field 'baseUrl'")
        
        if 'timeout' in source and not source['timeout'].endswith('s'):
            errors.append(f"Source '{source_id}': timeout must end with 's' (e.g., '30s'), got '{source['timeout']}'")
    
    # Check tools
    tools = config.get('tools', {})
    if not tools:
        errors.append("Configuration has no tools defined")
    
    tool_ids_set = set(tools.keys())
    
    for tool_id, tool in tools.items():
        # Check required fields
        required_fields = ['kind', 'source', 'method', 'path', 'description']
        for field in required_fields:
            if field not in tool:
                errors.append(f"Tool '{tool_id}': missing required field '{field}'")
        
        # Validate kind
        if tool.get('kind') != 'http':
            errors.append(f"Tool '{tool_id}': only 'http' kind is supported, got '{tool.get('kind')}'")
        
        # Validate method
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if tool.get('method') not in valid_methods:
            errors.append(f"Tool '{tool_id}': invalid HTTP method '{tool.get('method')}'")
        
        # Check path parameters consistency
        path = tool.get('path', '')
        if '{{.' in path:
            # Path has Go template variables, must have pathParams
            if not tool.get('pathParams'):
                errors.append(f"Tool '{tool_id}': path contains template variables but no pathParams defined")
            else:
                # Verify all path params are defined
                path_vars = set(re.findall(r'\{\{\.([^}]+)\}\}', path))
                defined_params = set(p['name'] for p in tool.get('pathParams', []))
                missing = path_vars - defined_params
                if missing:
                    errors.append(f"Tool '{tool_id}': path variables {missing} not defined in pathParams")
        
        # Check source reference
        if tool.get('source') not in sources:
            errors.append(f"Tool '{tool_id}': references non-existent source '{tool.get('source')}'")
        
        # Validate parameter structures
        for param_type in ['queryParams', 'pathParams', 'bodyParams', 'headerParams']:
            params = tool.get(param_type, [])
            if params and not isinstance(params, list):
                errors.append(f"Tool '{tool_id}': {param_type} must be a list")
            
            for param in params:
                if 'name' not in param:
                    errors.append(f"Tool '{tool_id}': {param_type} parameter missing 'name'")
                if 'type' not in param:
                    errors.append(f"Tool '{tool_id}': {param_type} parameter '{param.get('name', '?')}' missing 'type'")
    
    # Check toolsets
    toolsets = config.get('toolsets', {})
    if toolsets:
        for toolset_id, tool_list in toolsets.items():
            if not isinstance(tool_list, list):
                errors.append(f"Toolset '{toolset_id}': must be a list of tool IDs")
            else:
                # Verify all tools exist
                for tool_ref in tool_list:
                    if tool_ref not in tool_ids_set:
                        errors.append(f"Toolset '{toolset_id}': references non-existent tool '{tool_ref}'")
    
    return errors


def write_config_with_env_var(config: Dict[str, Any], output_file: Path, env_var: str) -> None:
    """Write config to file, replacing DNB_SUBSCRIPTION_KEY with environment-specific variable"""
    # Convert config to YAML string
    yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Replace generic variable with environment-specific one
    yaml_content = yaml_content.replace('${DNB_SUBSCRIPTION_KEY}', f'${{{env_var}}}')
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)


def convert_api(api_name: str, output_file: Optional[Path] = None, 
                write_to_toolbox: bool = True) -> bool:
    """Convert OpenAPI spec to GenAI Toolbox format
    
    Args:
        api_name: Name of the API to convert
        output_file: Optional custom output file (overrides write_to_toolbox)
        write_to_toolbox: If True, writes to config/dev and config/prod folders
    """
    if api_name not in APIS:
        print(f"❌ Unknown API: {api_name}")
        print(f"   Available: {', '.join(APIS.keys())}")
        return False
    
    config = APIS[api_name]
    spec_file = SPECS_DIR / config["spec"]
    
    if not spec_file.exists():
        print(f"❌ OpenAPI spec not found: {spec_file}")
        return False
    
    print(f"\n{'='*80}")
    print(f"Converting: {api_name.upper()}")
    print(f"{'='*80}")
    print(f"📄 Spec: {spec_file.name}")
    print(f"📝 Description: {config['description']}")
    
    # Get optional tool prefix from configuration
    tool_prefix = config.get('tool_prefix')
    if tool_prefix:
        print(f"🏷️  Tool Prefix: {tool_prefix}_")
    
    try:
        # Parse OpenAPI spec
        parser = OpenAPIParser(spec_file)
        print(f"✅ Parsed OpenAPI spec: {parser.get_title()} v{parser.get_version()}")
        
        # Generate GenAI Toolbox config with optional tool prefix
        generator = GenAIToolboxGenerator(api_name, parser, tool_prefix=tool_prefix)
        toolbox_config = generator.generate_config()
        
        print(f"✅ Generated {len(toolbox_config['sources'])} source(s)")
        print(f"✅ Generated {len(toolbox_config['tools'])} tool(s)")
        print(f"✅ Generated {len(toolbox_config.get('toolsets', {}))} toolset(s)")
        
        # Print toolset info
        for toolset_name, tool_list in toolbox_config.get('toolsets', {}).items():
            print(f"   📦 {toolset_name}: {len(tool_list)} tools")
        
        # Validate configuration
        validation_errors = validate_generated_config(toolbox_config)
        if validation_errors:
            print(f"\n⚠️  Configuration validation found {len(validation_errors)} issue(s):")
            for i, error in enumerate(validation_errors, 1):
                print(f"  {i}. {error}")
            print("\n❌ Validation failed. Configuration may not work correctly.")
            # Don't fail completely, just warn
        else:
            print(f"✅ Configuration validation passed")
        
        # Determine output strategy
        if output_file is not None:
            # Custom output file
            write_config_with_env_var(toolbox_config, output_file, 'DNB_SUBSCRIPTION_KEY')
            print(f"\n✅ Configuration saved to: {output_file}")
        elif write_to_toolbox:
            # Write to both dev and prod folders with proper naming and env vars
            prefix = config["prefix"]
            base_filename = f"{prefix}-dnb-{api_name}.generated.yaml"
            
            # Write to dev folder with DEV env var
            dev_file = TOOLBOX_DEV_DIR / base_filename
            write_config_with_env_var(toolbox_config, dev_file, 'DNB_SUBSCRIPTION_KEY_DEV')
            print(f"\n✅ Dev config saved to: {dev_file}")
            
            # Write to prod folder with PROD env var
            prod_file = TOOLBOX_PROD_DIR / base_filename
            write_config_with_env_var(toolbox_config, prod_file, 'DNB_SUBSCRIPTION_KEY_PROD')
            print(f"✅ Prod config saved to: {prod_file}")
            
            # Also write to generated folder for reference (generic var)
            generated_file = GENERATED_DIR / f"tools.{api_name}.generated.yaml"
            with open(generated_file, 'w', encoding='utf-8') as f:
                yaml.dump(toolbox_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"✅ Reference copy saved to: {generated_file}")
        else:
            # Legacy: write to generated folder only
            generated_file = GENERATED_DIR / f"tools.{api_name}.generated.yaml"
            with open(generated_file, 'w', encoding='utf-8') as f:
                yaml.dump(toolbox_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"\n✅ Configuration saved to: {generated_file}")
        
        print(f"{'='*80}\n")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_api(api_name: str) -> bool:
    """Validate generated config against manual config"""
    if api_name not in APIS:
        print(f"❌ Unknown API: {api_name}")
        return False
    
    generated_file = DNB_DIR / f"tools.{api_name}.generated.yaml"
    manual_file = TOOLBOX_DIR / "tools.dev.yaml"
    
    if not generated_file.exists():
        print(f"❌ Generated config not found: {generated_file}")
        print(f"   Run: python {Path(__file__).name} convert --api {api_name}")
        return False
    
    if not manual_file.exists():
        print(f"⚠️  Manual config not found: {manual_file}")
        print(f"   Skipping validation")
        return True
    
    print(f"\n{'='*80}")
    print(f"Validating: {api_name.upper()}")
    print(f"{'='*80}")
    
    try:
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_config = yaml.safe_load(f)
        
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_config = yaml.safe_load(f)
        
        validator = ConfigValidator(generated_config, manual_config)
        is_valid, issues = validator.validate()
        
        if is_valid:
            print(f"✅ Validation passed! Configuration matches manual config.")
        else:
            print(f"⚠️  Validation found {len(issues)} issue(s):")
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. {issue}")
        
        print(f"{'='*80}\n")
        return is_valid
    
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False


def diff_api(api_name: str) -> bool:
    """Generate diff report between generated and manual configs"""
    if api_name not in APIS:
        print(f"❌ Unknown API: {api_name}")
        return False
    
    generated_file = GENERATED_DIR / f"tools.{api_name}.generated.yaml"
    manual_file = TOOLBOX_DIR / "tools.dev.yaml"
    
    if not generated_file.exists():
        print(f"❌ Generated config not found: {generated_file}")
        print(f"   Run: python {Path(__file__).name} convert --api {api_name}")
        return False
    
    if not manual_file.exists():
        print(f"⚠️  Manual config not found: {manual_file}")
        return True
    
    try:
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_config = yaml.safe_load(f)
        
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_config = yaml.safe_load(f)
        
        comparator = ConfigComparator(generated_config, manual_config)
        report = comparator.generate_diff_report()
        
        print(report)
        
        # Save report
        report_file = GENERATED_DIR / f"tools.{api_name}.diff-report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Diff report saved to: {report_file}\n")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error generating diff: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="OpenAPI to GenAI Toolbox Converter Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert Echo API
  python openapi_to_toolbox_agent.py convert --api echo
  
  # Convert all APIs
  python openapi_to_toolbox_agent.py convert --all
  
  # Validate generated config
  python openapi_to_toolbox_agent.py validate --api echo
  
  # Generate diff report
  python openapi_to_toolbox_agent.py diff --api echo
  
  # List available APIs
  python openapi_to_toolbox_agent.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert OpenAPI spec to GenAI Toolbox format')
    convert_parser.add_argument('--api', choices=list(APIS.keys()), help='API to convert')
    convert_parser.add_argument('--all', action='store_true', help='Convert all APIs')
    convert_parser.add_argument('--output', type=Path, help='Output file path')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate generated config against manual config')
    validate_parser.add_argument('--api', choices=list(APIS.keys()), required=True, help='API to validate')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Generate diff report')
    diff_parser.add_argument('--api', choices=list(APIS.keys()), required=True, help='API to compare')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available APIs')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        if args.all:
            print("Converting all APIs...")
            success_count = 0
            for api_name in APIS.keys():
                if convert_api(api_name, args.output):
                    success_count += 1
            
            print(f"\n✅ Successfully converted {success_count}/{len(APIS)} APIs\n")
            sys.exit(0 if success_count == len(APIS) else 1)
        
        elif args.api:
            success = convert_api(args.api, args.output)
            sys.exit(0 if success else 1)
        
        else:
            print("❌ Please specify --api or --all")
            sys.exit(1)
    
    elif args.command == 'validate':
        success = validate_api(args.api)
        sys.exit(0 if success else 1)
    
    elif args.command == 'diff':
        success = diff_api(args.api)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        print("\nAvailable APIs:\n")
        for api_name, config in APIS.items():
            print(f"  {api_name}")
            print(f"    Spec: {config['spec']}")
            print(f"    Description: {config['description']}\n")
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
