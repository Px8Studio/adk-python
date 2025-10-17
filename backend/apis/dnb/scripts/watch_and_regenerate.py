#!/usr/bin/env python3
"""
Watch OpenAPI Specs and Auto-Regenerate MCP Servers
Monitors OpenAPI specification files for changes and automatically regenerates MCP servers
"""

import time
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import subprocess
import argparse

SCRIPT_DIR = Path(__file__).parent
SPECS_DIR = SCRIPT_DIR.parent / "specs"

# API configurations
WATCHED_SPECS = {
    "echo": {
        "file": "openapi3-echo-api.yaml",
        "command": ["python", str(SCRIPT_DIR / "generate_mcp_from_openapi.py"), "echo"]
    },
    "statistics": {
        "file": "openapi3_statisticsdatav2024100101.yaml",
        "command": ["python", str(SCRIPT_DIR / "generate_mcp_from_openapi.py"), "statistics"]
    },
    "public-register": {
        "file": "openapi3_publicdatav1.yaml",
        "command": ["python", str(SCRIPT_DIR / "generate_mcp_from_openapi.py"), "public-register"]
    }
}


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file"""
    if not file_path.exists():
        return ""
    
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def watch_specs(apis: list = None, interval: int = 5, run_once: bool = False):
    """Watch OpenAPI specs for changes"""
    
    # Track file hashes
    file_hashes = {}
    
    # Filter APIs to watch
    watch_list = {
        name: config for name, config in WATCHED_SPECS.items()
        if not apis or name in apis
    }
    
    if not watch_list:
        print("❌ No APIs to watch")
        return 1
    
    print(f"{'='*70}")
    print("👀 WATCHING OPENAPI SPECIFICATIONS")
    print(f"{'='*70}")
    print(f"📁 Directory: {SPECS_DIR}")
    print(f"⏱️  Check interval: {interval} seconds")
    print(f"\nWatching {len(watch_list)} API(s):")
    
    for name, config in watch_list.items():
        spec_file = SPECS_DIR / config["file"]
        print(f"  - {name}: {spec_file.name}")
        
        # Initialize hash
        file_hashes[name] = get_file_hash(spec_file)
    
    print(f"\n{'='*70}")
    print("Press Ctrl+C to stop watching")
    print(f"{'='*70}\n")
    
    if run_once:
        print("🔄 Running initial generation for all APIs...")
        for name in watch_list:
            regenerate_api(name, watch_list[name])
        return 0
    
    try:
        while True:
            for name, config in watch_list.items():
                spec_file = SPECS_DIR / config["file"]
                
                if not spec_file.exists():
                    continue
                
                current_hash = get_file_hash(spec_file)
                
                if current_hash != file_hashes[name]:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[{timestamp}] 📝 Change detected: {spec_file.name}")
                    
                    # Regenerate
                    if regenerate_api(name, config):
                        file_hashes[name] = current_hash
                        print(f"[{timestamp}] ✅ Regeneration complete: {name}")
                    else:
                        print(f"[{timestamp}] ❌ Regeneration failed: {name}")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopped watching")
        return 0


def regenerate_api(name: str, config: dict) -> bool:
    """Regenerate MCP server for API"""
    try:
        print(f"🔄 Regenerating MCP server: {name}...")
        
        result = subprocess.run(
            config["command"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error regenerating {name}:")
        print(e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Watch OpenAPI specs and auto-regenerate MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch all APIs
  python watch_and_regenerate.py
  
  # Watch specific API
  python watch_and_regenerate.py --api echo
  
  # Custom check interval
  python watch_and_regenerate.py --interval 10
  
  # Generate once and exit
  python watch_and_regenerate.py --once
        """
    )
    
    parser.add_argument(
        "--api",
        choices=list(WATCHED_SPECS.keys()),
        action="append",
        dest="apis",
        help="API to watch (can specify multiple times)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Check interval in seconds (default: 5)"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Generate once and exit (don't watch)"
    )
    
    args = parser.parse_args()
    
    return watch_specs(
        apis=args.apis,
        interval=args.interval,
        run_once=args.once
    )


if __name__ == "__main__":
    sys.exit(main())
