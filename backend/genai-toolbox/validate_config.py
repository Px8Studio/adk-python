#!/usr/bin/env python3
"""
Validate GenAI Toolbox Configuration Files
Checks for ID conflicts across multiple YAML files
"""

import yaml
from pathlib import Path
from typing import Dict, Set, List, Tuple

CONFIG_DIR = Path(__file__).parent / "config"


def load_yaml_files(directory: Path) -> Dict[str, dict]:
    """Load all YAML files from directory"""
    configs = {}
    
    for yaml_file in sorted(directory.glob("*.yaml")):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config:  # Skip empty files
                    configs[yaml_file.name] = config
        except Exception as e:
            print(f"⚠️  Error loading {yaml_file.name}: {e}")
    
    return configs


def extract_ids(config: dict, key: str) -> List[str]:
    """Extract IDs from sources or tools, handling both list and dict formats"""
    items = config.get(key, [])
    
    # Handle dict format (old style)
    if isinstance(items, dict):
        return list(items.keys())
    
    # Handle list format (new style)
    if isinstance(items, list):
        return [item.get('id', '') for item in items if item.get('id')]
    
    return []


def check_conflicts(configs: Dict[str, dict]) -> Tuple[bool, List[str]]:
    """Check for duplicate IDs across all configs"""
    all_sources: Dict[str, List[str]] = {}  # id -> [files]
    all_tools: Dict[str, List[str]] = {}
    all_toolsets: Dict[str, List[str]] = {}
    issues = []
    
    # Collect all IDs
    for filename, config in configs.items():
        # Sources
        for source_id in extract_ids(config, 'sources'):
            if source_id not in all_sources:
                all_sources[source_id] = []
            all_sources[source_id].append(filename)
        
        # Tools
        for tool_id in extract_ids(config, 'tools'):
            if tool_id not in all_tools:
                all_tools[tool_id] = []
            all_tools[tool_id].append(filename)
        
        # Toolsets
        for toolset_id in extract_ids(config, 'toolsets'):
            if toolset_id not in all_toolsets:
                all_toolsets[toolset_id] = []
            all_toolsets[toolset_id].append(filename)
    
    # Check for duplicates
    for source_id, files in all_sources.items():
        if len(files) > 1:
            issues.append(f"❌ DUPLICATE SOURCE: '{source_id}' in {', '.join(files)}")
    
    for tool_id, files in all_tools.items():
        if len(files) > 1:
            issues.append(f"❌ DUPLICATE TOOL: '{tool_id}' in {', '.join(files)}")
    
    for toolset_id, files in all_toolsets.items():
        if len(files) > 1:
            issues.append(f"❌ DUPLICATE TOOLSET: '{toolset_id}' in {', '.join(files)}")
    
    return len(issues) == 0, issues


def print_summary(configs: Dict[str, dict]):
    """Print summary of all configs"""
    print("\n" + "="*80)
    print("CONFIGURATION SUMMARY")
    print("="*80)
    
    total_sources = 0
    total_tools = 0
    total_toolsets = 0
    
    for filename, config in sorted(configs.items()):
        sources = extract_ids(config, 'sources')
        tools = extract_ids(config, 'tools')
        toolsets = extract_ids(config, 'toolsets')
        
        if sources or tools or toolsets:
            print(f"\n📄 {filename}")
            if sources:
                print(f"   Sources ({len(sources)}):")
                for sid in sources:
                    print(f"     - {sid}")
                total_sources += len(sources)
            
            if tools:
                print(f"   Tools ({len(tools)}):")
                for tid in tools[:5]:  # Show first 5
                    print(f"     - {tid}")
                if len(tools) > 5:
                    print(f"     ... and {len(tools) - 5} more")
                total_tools += len(tools)
            
            if toolsets:
                print(f"   Toolsets ({len(toolsets)}):")
                for tsid in toolsets:
                    print(f"     - {tsid}")
                total_toolsets += len(toolsets)
    
    print("\n" + "="*80)
    print(f"TOTALS: {total_sources} sources, {total_tools} tools, {total_toolsets} toolsets")
    print("="*80)


def main():
    print("🔍 Validating GenAI Toolbox Configuration Files")
    print(f"📂 Directory: {CONFIG_DIR}")
    
    # Load all configs
    configs = load_yaml_files(CONFIG_DIR)
    print(f"\n✅ Loaded {len(configs)} YAML files")
    
    # Check for conflicts
    print("\n🔍 Checking for ID conflicts...")
    valid, issues = check_conflicts(configs)
    
    if issues:
        print("\n⚠️  CONFLICTS FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print("\n❌ Validation FAILED - fix conflicts before deployment!")
        return False
    else:
        print("✅ No conflicts found!")
    
    # Print summary
    print_summary(configs)
    
    print("\n✅ Validation PASSED - configuration is ready!")
    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
