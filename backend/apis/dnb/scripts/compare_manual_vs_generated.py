#!/usr/bin/env python3
"""
Compare Manual Configuration vs Generated MCP Server
Validates that the generated MCP server matches our manual GenAI Toolbox configuration
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
import sys

# Paths
SCRIPT_DIR = Path(__file__).parent
MANUAL_CONFIG_DIR = SCRIPT_DIR.parent.parent.parent / "toolbox" / "config"
GENERATED_DIR = SCRIPT_DIR.parent / "generated"
SPECS_DIR = SCRIPT_DIR.parent / "specs"


class ConfigComparator:
    def __init__(self, api_name: str):
        self.api_name = api_name
        self.manual_config = None
        self.generated_config = None
        self.openapi_spec = None
        self.issues = []
        self.successes = []
    
    def load_manual_config(self, env: str = "dev"):
        """Load manual GenAI Toolbox configuration"""
        config_file = MANUAL_CONFIG_DIR / f"tools.{env}.yaml"
        
        if not config_file.exists():
            self.issues.append(f"Manual config not found: {config_file}")
            return False
        
        with open(config_file) as f:
            self.manual_config = yaml.safe_load(f)
        
        print(f"✅ Loaded manual config: {config_file}")
        return True
    
    def load_generated_config(self):
        """Load generated MCP server configuration"""
        # Find generated server directory
        generated_dir = GENERATED_DIR / f"dnb_{self.api_name}_mcp"
        
        if not generated_dir.exists():
            self.issues.append(f"Generated MCP server not found: {generated_dir}")
            self.issues.append("Run: python generate_mcp_from_openapi.py " + self.api_name)
            return False
        
        # Load pyproject.toml to understand structure
        pyproject = generated_dir / "pyproject.toml"
        if pyproject.exists():
            print(f"✅ Found generated MCP server: {generated_dir}")
        
        # Load tools from generated Python files
        tools_dir = generated_dir / f"mcp_{self.api_name}" / "tools"
        if tools_dir.exists():
            self.generated_config = {
                "tools": self._scan_generated_tools(tools_dir)
            }
        
        return True
    
    def _scan_generated_tools(self, tools_dir: Path) -> Dict[str, Any]:
        """Scan generated tools directory"""
        tools = {}
        
        for py_file in tools_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            # Parse Python file to extract tool info
            with open(py_file) as f:
                content = f.read()
            
            # Extract async function definitions
            import re
            functions = re.findall(r'async def (\w+)\(', content)
            
            for func_name in functions:
                tools[func_name] = {
                    "file": py_file.name,
                    "function": func_name
                }
        
        print(f"✅ Found {len(tools)} generated tools")
        return tools
    
    def load_openapi_spec(self):
        """Load OpenAPI specification for reference"""
        spec_mapping = {
            "echo": "openapi3-echo-api.yaml",
            "statistics": "openapi3_statisticsdatav2024100101.yaml",
            "public-register": "openapi3_publicdatav1.yaml"
        }
        
        spec_file = SPECS_DIR / spec_mapping.get(self.api_name, "")
        
        if not spec_file.exists():
            self.issues.append(f"OpenAPI spec not found: {spec_file}")
            return False
        
        with open(spec_file) as f:
            self.openapi_spec = yaml.safe_load(f)
        
        print(f"✅ Loaded OpenAPI spec: {spec_file}")
        return True
    
    def compare_endpoints(self):
        """Compare endpoints between manual and generated configs"""
        print(f"\n{'='*70}")
        print("🔍 COMPARING ENDPOINTS")
        print(f"{'='*70}")
        
        if not self.manual_config or not self.generated_config:
            self.issues.append("Cannot compare - missing configuration")
            return
        
        # Extract manual tools
        manual_tools = self.manual_config.get("tools", {})
        generated_tools = self.generated_config.get("tools", {})
        
        print(f"\nManual tools: {len(manual_tools)}")
        print(f"Generated tools: {len(generated_tools)}")
        
        # Compare each manual tool
        for tool_name, tool_config in manual_tools.items():
            if self.api_name not in tool_name:
                continue  # Skip tools from other APIs
            
            print(f"\n📌 Checking: {tool_name}")
            
            # Find matching generated tool
            matching = self._find_matching_tool(tool_name, tool_config, generated_tools)
            
            if matching:
                self.successes.append(f"✅ {tool_name}: Matched with {matching}")
                print(f"   ✅ Found match: {matching}")
            else:
                self.issues.append(f"❌ {tool_name}: No matching generated tool")
                print(f"   ❌ No match found")
    
    def _find_matching_tool(self, manual_name: str, manual_config: Dict, generated_tools: Dict) -> str:
        """Find matching tool in generated config"""
        # Extract path and method from manual config
        manual_path = manual_config.get("path", "")
        manual_method = manual_config.get("method", "").lower()
        
        # Look for similar tool in generated
        for gen_name, gen_config in generated_tools.items():
            # Simple name matching
            if manual_name.replace("-", "_") in gen_name.lower():
                return gen_name
            
            # Match by path/method in OpenAPI spec
            if self.openapi_spec:
                for path, methods in self.openapi_spec.get("paths", {}).items():
                    if path == manual_path:
                        for method, operation in methods.items():
                            if method.lower() == manual_method:
                                op_id = operation.get("operationId", "").replace("-", "_").lower()
                                if op_id == gen_name.lower():
                                    return gen_name
        
        return None
    
    def compare_authentication(self):
        """Compare authentication configuration"""
        print(f"\n{'='*70}")
        print("🔐 COMPARING AUTHENTICATION")
        print(f"{'='*70}")
        
        if not self.manual_config:
            return
        
        # Check manual source auth
        sources = self.manual_config.get("sources", {})
        for source_name, source_config in sources.items():
            if self.api_name not in source_name:
                continue
            
            headers = source_config.get("headers", {})
            auth_headers = [h for h in headers.keys() if "auth" in h.lower() or "key" in h.lower()]
            
            if auth_headers:
                print(f"\n📌 Manual auth headers in '{source_name}':")
                for header in auth_headers:
                    print(f"   - {header}")
                self.successes.append(f"✅ Authentication configured in manual config")
            else:
                self.issues.append(f"⚠️  No auth headers found in manual config")
        
        # Check OpenAPI spec security
        if self.openapi_spec:
            security_schemes = self.openapi_spec.get("components", {}).get("securitySchemes", {})
            if security_schemes:
                print(f"\n📌 OpenAPI security schemes:")
                for scheme_name, scheme_config in security_schemes.items():
                    print(f"   - {scheme_name}: {scheme_config.get('type')}")
                self.successes.append(f"✅ Security schemes defined in OpenAPI spec")
            else:
                self.issues.append(f"⚠️  No security schemes in OpenAPI spec")
    
    def generate_report(self):
        """Generate comparison report"""
        print(f"\n{'='*70}")
        print("📊 COMPARISON REPORT")
        print(f"{'='*70}")
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes:
            print(f"   {success}")
        
        print(f"\n❌ Issues: {len(self.issues)}")
        for issue in self.issues:
            print(f"   {issue}")
        
        print(f"\n{'='*70}")
        if not self.issues:
            print("🎉 VALIDATION PASSED - Generated config matches manual config!")
            return 0
        else:
            print("⚠️  VALIDATION INCOMPLETE - Some differences found")
            return 1


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Compare manual configuration vs generated MCP server"
    )
    
    parser.add_argument(
        "api",
        choices=["echo", "statistics", "public-register"],
        help="API to compare"
    )
    
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Environment to compare (default: dev)"
    )
    
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print(f"🔍 COMPARING: {args.api.upper()} API")
    print(f"   Environment: {args.env}")
    print(f"{'='*70}")
    
    comparator = ConfigComparator(args.api)
    
    # Load configurations
    comparator.load_manual_config(args.env)
    comparator.load_openapi_spec()
    comparator.load_generated_config()
    
    # Run comparisons
    comparator.compare_endpoints()
    comparator.compare_authentication()
    
    # Generate report
    return comparator.generate_report()


if __name__ == "__main__":
    sys.exit(main())
