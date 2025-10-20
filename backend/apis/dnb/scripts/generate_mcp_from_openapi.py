#!/usr/bin/env python3
"""
Generate MCP Server from OpenAPI Specification
Uses cnoe-io/openapi-mcp-codegen to automatically generate MCP servers from DNB API specs
"""

import subprocess
import sys
from pathlib import Path
import argparse
import shutil
import os
from typing import Optional

# Base paths
SCRIPT_DIR = Path(__file__).parent
SPECS_DIR = SCRIPT_DIR.parent / "specs"
GENERATED_DIR = SCRIPT_DIR.parent / "generated"
CLIENTS_DIR = SCRIPT_DIR.parent / "generated_clients"


def get_uv_command():
    """Get the uv/uvx command, checking virtual environment first"""
    # Check if running in virtual environment
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        # Try venv Scripts directory (Windows)
        venv_uv = Path(venv) / "Scripts" / "uv.exe"
        if venv_uv.exists():
            return str(venv_uv)
        # Try venv bin directory (Unix)
        venv_uv = Path(venv) / "bin" / "uv"
        if venv_uv.exists():
            return str(venv_uv)
    
    # Check if running from a venv even if VIRTUAL_ENV not set
    python_exe = Path(sys.executable)
    if "venv" in python_exe.parts or ".venv" in python_exe.parts:
        scripts_dir = python_exe.parent
        venv_uv = scripts_dir / "uv.exe"
        if venv_uv.exists():
            return str(venv_uv)
        venv_uv = scripts_dir / "uv"
        if venv_uv.exists():
            return str(venv_uv)
    
    # Fall back to system uv
    return "uv"

# API Configurations
APIS = {
    "echo": {
        "spec": "openapi3-echo-api.yaml",
        "output": "dnb_echo_mcp",
        "description": "DNB Echo API - Test endpoint for API connectivity"
    },
    "statistics": {
        "spec": "openapi3_statisticsdatav2024100101.yaml",
        "output": "dnb_statistics_mcp",
        "description": "DNB Statistics API - Dutch banking statistics data"
    },
    "public-register": {
        "spec": "openapi3_publicdatav1.yaml",
        "output": "dnb_public_register_mcp",
        "description": "DNB Public Register API - Licensed financial institutions"
    }
}


def check_uvx():
    """Check if uvx is available"""
    uv_cmd = get_uv_command()
    
    # Check for 'uv' (uvx is part of uv package)
    try:
        result = subprocess.run(
            [uv_cmd, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ uv is available: {result.stdout.strip()}")
        print(f"   Using: {uv_cmd}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback: try uvx directly  
    try:
        result = subprocess.run(
            ["uvx", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ uvx is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv is not installed or not in PATH")
        print("\n⚠️  Note: uvx is provided by the 'uv' package")
        print("   DO NOT install 'uvx' separately - it's a dummy package!")
        print("\nTo install uv:")
        print("  pip install uv")
        print("  or visit: https://docs.astral.sh/uv/")
        return False


def _locate_mcp_package(output_dir: Path) -> Optional[Path]:
    """Return the generated MCP package directory (mcp_*)."""
    if not output_dir.exists():
        return None

    candidates = [path for path in output_dir.iterdir() if path.is_dir()]
    # Prefer directories starting with mcp_
    for candidate in candidates:
        if candidate.name.startswith("mcp_"):
            return candidate
    return candidates[0] if candidates else None


def _extract_http_client(output_dir: Path, api_name: str) -> bool:
    """Copy the generated http client, tools, and models into generated_clients/."""
    mcp_pkg = _locate_mcp_package(output_dir)
    if not mcp_pkg:
        print("⚠️  Unable to locate generated MCP package; skipping client extraction")
        return False

    # Prepare destination
    dest_root = CLIENTS_DIR / api_name
    if dest_root.exists():
        shutil.rmtree(dest_root)
    dest_root.mkdir(parents=True, exist_ok=True)

    api_client = mcp_pkg / "api" / "client.py"
    if not api_client.exists():
        print(f"⚠️  No client.py found in {api_client.parent}; skipping client extraction")
        return False

    shutil.copy2(api_client, dest_root / "client.py")

    for subdir in ["models", "tools"]:
        src_dir = mcp_pkg / subdir
        dest_dir = dest_root / subdir
        if src_dir.exists():
            shutil.copytree(src_dir, dest_dir)

    print(f"📦 HTTP client materials copied to: {dest_root}")
    return True


def generate_mcp_server(api_name: str, include_agent: bool = True, include_eval: bool = True, *, client_only: bool = False):
    """Generate MCP server for specified API"""
    
    if api_name not in APIS:
        print(f"❌ Unknown API: {api_name}")
        print(f"   Available APIs: {', '.join(APIS.keys())}")
        return False
    
    config = APIS[api_name]
    spec_file = SPECS_DIR / config["spec"]
    output_dir = GENERATED_DIR / config["output"]
    
    if not spec_file.exists():
        print(f"❌ OpenAPI spec not found: {spec_file}")
        return False
    
    print(f"\n{'='*70}")
    print(f"🚀 Generating MCP Server: {api_name.upper()}")
    print(f"{'='*70}")
    print(f"📄 Spec: {spec_file.name}")
    print(f"📁 Output: {output_dir}")
    print(f"📝 Description: {config['description']}")
    
    # Get uv command (handles virtual environment)
    uv_cmd = get_uv_command()
    
    # Prepare command - use 'uv tool run' instead of 'uvx'
    cmd = [
        uv_cmd, "tool", "run",
        "--from", "git+https://github.com/cnoe-io/openapi-mcp-codegen.git",
        "openapi_mcp_codegen",
        "--spec-file", str(spec_file),
        "--output-dir", str(output_dir),
    ]
    
    if include_agent and not client_only:
        cmd.append("--generate-agent")
        print("🤖 Agent: YES")

    if include_eval and not client_only:
        cmd.append("--generate-eval")
        print("🧪 Evaluation: YES")
    elif client_only:
        print("🤖 Agent: NO (client-only mode)")
        print("🧪 Evaluation: NO (client-only mode)")
    
    print(f"\n⏳ Running code generation...")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SCRIPT_DIR.parent,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"\n✅ Generation successful!")
        print(f"\n📦 Generated files in: {output_dir}")
        
        # Show structure
        if output_dir.exists():
            print(f"\n📂 Directory structure:")
            for item in sorted(output_dir.rglob("*")):
                if item.is_file():
                    rel_path = item.relative_to(output_dir)
                    print(f"   {rel_path}")

        if client_only:
            CLIENTS_DIR.mkdir(parents=True, exist_ok=True)
            _extract_http_client(output_dir, api_name)
        
        # Show README if exists
        readme = output_dir / "README.md"
        if readme.exists() and not client_only:
            print(f"\n📖 Next steps - see: {readme}")
            print("\nQuick start:")
            print(f"   cd {output_dir}")
            print("   poetry install")
            print("   poetry run mcp_{api_name.replace('-', '_')}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Generation failed!")
        print(f"\nError output:")
        print(e.stderr)
        return False


def clean_generated(api_name: str = None):
    """Clean generated files"""
    if api_name:
        if api_name not in APIS:
            print(f"❌ Unknown API: {api_name}")
            return False
        
        output_dir = GENERATED_DIR / APIS[api_name]["output"]
        if output_dir.exists():
            shutil.rmtree(output_dir)
            print(f"🧹 Cleaned: {output_dir}")
        else:
            print(f"ℹ️  Nothing to clean: {output_dir} doesn't exist")
    else:
        # Clean all
        if GENERATED_DIR.exists():
            shutil.rmtree(GENERATED_DIR)
            print(f"🧹 Cleaned all generated files: {GENERATED_DIR}")
        else:
            print(f"ℹ️  Nothing to clean: {GENERATED_DIR} doesn't exist")
    
    return True


def generate_all(include_agent: bool = True, include_eval: bool = True, *, client_only: bool = False):
    """Generate MCP servers for all APIs"""
    results = {}
    
    for api_name in APIS:
        success = generate_mcp_server(api_name, include_agent, include_eval, client_only=client_only)
        results[api_name] = success
    
    print(f"\n{'='*70}")
    print("📊 GENERATION SUMMARY")
    print(f"{'='*70}")
    
    for api_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {api_name}")
    
    all_success = all(results.values())
    if all_success:
        print(f"\n🎉 All API servers generated successfully!")
    else:
        print(f"\n⚠️  Some API servers failed to generate")
    
    return all_success


def main():
    parser = argparse.ArgumentParser(
        description="Generate MCP servers from OpenAPI specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate MCP server for Echo API
  python generate_mcp_from_openapi.py echo
  
  # Generate for all APIs
  python generate_mcp_from_openapi.py --all
  
  # Generate without agent/eval
  python generate_mcp_from_openapi.py echo --no-agent --no-eval
  
  # Clean generated files
  python generate_mcp_from_openapi.py --clean echo
  python generate_mcp_from_openapi.py --clean-all
        """
    )
    
    parser.add_argument(
        "api",
        nargs="?",
        choices=list(APIS.keys()),
        help="API to generate (echo, statistics, public-register)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate MCP servers for all APIs"
    )
    
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Don't generate LangGraph agent"
    )
    
    parser.add_argument(
        "--no-eval",
        action="store_true",
        help="Don't generate evaluation suite"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean generated files for specified API"
    )
    
    parser.add_argument(
        "--clean-all",
        action="store_true",
        help="Clean all generated files"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available APIs"
    )

    parser.add_argument(
        "--client-only",
        action="store_true",
        help="Generate only the HTTP client/modules and copy them into generated_clients/."
    )
    
    args = parser.parse_args()
    
    # Handle list
    if args.list:
        print("Available APIs:")
        for name, config in APIS.items():
            print(f"\n  {name}")
            print(f"    Spec: {config['spec']}")
            print(f"    Description: {config['description']}")
        return 0
    
    # Handle clean
    if args.clean_all:
        clean_generated()
        if CLIENTS_DIR.exists():
            shutil.rmtree(CLIENTS_DIR)
            print(f"🧹 Cleaned all generated HTTP clients: {CLIENTS_DIR}")
        return 0
    
    if args.clean:
        if not args.api:
            print("❌ Please specify an API to clean")
            return 1
        clean_generated(args.api)
        client_dir = CLIENTS_DIR / args.api
        if client_dir.exists():
            shutil.rmtree(client_dir)
            print(f"🧹 Cleaned HTTP client artifacts: {client_dir}")
        return 0
    
    # Check uvx
    if not check_uvx():
        return 1
    
    # Ensure generated directory exists
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Handle generation
    if args.all:
        success = generate_all(
            include_agent=not args.no_agent,
            include_eval=not args.no_eval,
            client_only=args.client_only
        )
        return 0 if success else 1
    
    if args.api:
        success = generate_mcp_server(
            args.api,
            include_agent=not args.no_agent,
            include_eval=not args.no_eval,
            client_only=args.client_only
        )
        return 0 if success else 1
    
    # No action specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
