#!/usr/bin/env python3
"""
OpenAPI to GenAI Toolbox Converter Agent

Converts OpenAPI 3.0 specifications to GenAI Toolbox HTTP tool YAML format.
Provides validation against existing manual configurations and diff reporting.

Usage:
    python openapi_to_toolbox_agent.py convert --api echo
    python openapi_to_toolbox_agent.py convert --all
    python openapi_to_toolbox_agent.py validate --api echo
    python openapi_to_toolbox_agent.py diff --api echo
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml
import json
from dataclasses import dataclass, asdict
from enum import Enum


# Base paths
SCRIPT_DIR = Path(__file__).parent
DNB_DIR = SCRIPT_DIR.parent / "apis" / "dnb"
SPECS_DIR = DNB_DIR / "specs"
TOOLBOX_DIR = DNB_DIR.parent.parent / "toolbox" / "config"


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
    
    def to_toolbox_format(self) -> Dict[str, Any]:
        """Convert to GenAI Toolbox YAML format"""
        tool = {
            "id": self.id,
            "source_id": self.source_id,
            "method": self.method,
            "path": self.path,
            "description": self.description
        }
        
        # Group parameters by type
        if self.parameters:
            params_by_type = {}
            for param in self.parameters:
                if param.param_type not in params_by_type:
                    params_by_type[param.param_type] = []
                
                param_def = {
                    "name": param.name,
                    "type": param.data_type,
                    "required": param.required
                }
                if param.description:
                    param_def["description"] = param.description
                if param.default is not None:
                    param_def["default"] = param.default
                
                params_by_type[param.param_type].append(param_def)
            
            if params_by_type:
                tool["parameters"] = params_by_type
        
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
        """Convert to GenAI Toolbox YAML format"""
        return {
            "id": self.id,
            "type": self.type,
            "config": {
                "base_url": self.base_url,
                "headers": self.headers,
                "timeout": self.timeout
            }
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
    
    def extract_parameters(self, operation: Dict) -> List[ToolParameter]:
        """Extract parameters from an operation"""
        parameters = []
        
        # Path and query parameters
        for param in operation.get('parameters', []):
            param_in = param.get('in', 'query')
            param_schema = param.get('schema', {})
            
            parameters.append(ToolParameter(
                name=param.get('name', ''),
                param_type=param_in,
                data_type=param_schema.get('type', 'string'),
                required=param.get('required', False),
                description=param.get('description', ''),
                default=param_schema.get('default')
            ))
        
        # Request body
        if 'requestBody' in operation:
            request_body = operation['requestBody']
            content = request_body.get('content', {})
            
            # Get first content type (usually application/json)
            if content:
                content_type = list(content.keys())[0]
                schema = content[content_type].get('schema', {})
                
                parameters.append(ToolParameter(
                    name='body',
                    param_type='body',
                    data_type='object',
                    required=request_body.get('required', False),
                    description=request_body.get('description', 'Request body'),
                    default=None
                ))
        
        return parameters
    
    def get_operations(self) -> List[Tuple[str, str, Dict]]:
        """Extract all operations (path, method, operation)"""
        operations = []
        
        for path, path_item in self.spec.get('paths', {}).items():
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method in path_item:
                    operations.append((path, method, path_item[method]))
        
        return operations


class GenAIToolboxGenerator:
    """Generate GenAI Toolbox YAML configuration"""
    
    def __init__(self, api_id: str, parser: OpenAPIParser):
        self.api_id = api_id
        self.parser = parser
    
    def generate_source_id(self) -> str:
        """Generate source ID"""
        return f"{self.api_id}-api"
    
    def generate_tool_id(self, operation: Dict, method: str, path: str) -> str:
        """Generate tool ID from operation"""
        # Try operationId first
        if 'operationId' in operation:
            op_id = operation['operationId']
            # Clean up operationId
            return op_id.replace('_', '-').lower()
        
        # Fallback: use method + path
        # Remove leading slash and parameters
        clean_path = path.strip('/').replace('/', '-').replace('{', '').replace('}', '')
        return f"{self.api_id}-{method}-{clean_path}".lower()
    
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
            parameters = self.parser.extract_parameters(operation)
            
            tools.append(ToolDefinition(
                id=tool_id,
                source_id=source_id,
                method=method.upper(),
                path=path,
                description=description,
                parameters=parameters
            ))
        
        return tools
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate complete GenAI Toolbox configuration"""
        source = self.generate_source()
        tools = self.generate_tools()
        
        return {
            "sources": [source.to_toolbox_format()],
            "tools": [tool.to_toolbox_format() for tool in tools]
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


# API configurations
APIS = {
    "echo": {
        "spec": "openapi3-echo-api.yaml",
        "description": "DNB Echo API - Test endpoint for API connectivity"
    },
    "statistics": {
        "spec": "openapi3_statisticsdatav2024100101.yaml",
        "description": "DNB Statistics API - Dutch banking statistics data"
    },
    "public-register": {
        "spec": "openapi3_publicdatav1.yaml",
        "description": "DNB Public Register API - Licensed financial institutions"
    }
}


def convert_api(api_name: str, output_file: Optional[Path] = None) -> bool:
    """Convert OpenAPI spec to GenAI Toolbox format"""
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
    
    try:
        # Parse OpenAPI spec
        parser = OpenAPIParser(spec_file)
        print(f"✅ Parsed OpenAPI spec: {parser.get_title()} v{parser.get_version()}")
        
        # Generate GenAI Toolbox config
        generator = GenAIToolboxGenerator(api_name, parser)
        toolbox_config = generator.generate_config()
        
        print(f"✅ Generated {len(toolbox_config['sources'])} source(s)")
        print(f"✅ Generated {len(toolbox_config['tools'])} tool(s)")
        
        # Output file
        if output_file is None:
            output_file = DNB_DIR / f"tools.{api_name}.generated.yaml"
        
        # Write YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(toolbox_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"\n✅ Generated configuration saved to: {output_file}")
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
    
    generated_file = DNB_DIR / f"tools.{api_name}.generated.yaml"
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
        report_file = DNB_DIR / f"tools.{api_name}.diff-report.txt"
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
