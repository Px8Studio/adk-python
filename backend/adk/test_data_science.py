#!/usr/bin/env python3
"""Quick test for data science agent setup."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        from google.adk.agents.llm_agent import LlmAgent
        from google.adk.runners import Runner
        print("✅ ADK core imports OK")
    except ImportError as e:
        print(f"❌ ADK import failed: {e}")
        return False
    
    try:
        from backend.adk.agents.data_science.agent import root_agent
        print("✅ Data science agent import OK")
    except ImportError as e:
        print(f"❌ Agent import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_env():
    """Test environment variables."""
    print("\nChecking environment variables...")
    
    # Check both naming conventions (ADK samples use different patterns)
    required_vars = [
        ("GOOGLE_CLOUD_PROJECT", "woven-art-475517-n4"),
        ("BQ_PROJECT_ID", "woven-art-475517-n4"),  
        ("BQ_DATASET_ID", "dnb_statistics")
    ]
    
    all_good = True
    for var, expected_prefix in required_vars:
        value = os.getenv(var)
        if value:
            # Check if it has the expected value (not the placeholder)
            if "your-" in value:
                print(f"⚠️  {var}: Set but still has placeholder value: {value}")
                all_good = False
            else:
                print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    return all_good


def main():
    """Run all tests."""
    print("="*50)
    print("Data Science Agent Setup Test")
    print("="*50)
    
    # Load env from PROJECT ROOT - ADK standard pattern
    from dotenv import load_dotenv
    
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✅ Loaded .env from PROJECT ROOT: {env_path}")
        print("   (This is the ADK-recommended pattern)")
    else:
        print(f"⚠️  No .env file found at PROJECT ROOT: {env_path}")
        print("   ADK pattern: Single .env at project root")
        print("   NOT in subdirectories like agents/data_science/")
    
    print()
    
    # Run tests
    imports_ok = test_imports()
    env_ok = test_env()
    
    print("\n" + "="*50)
    if imports_ok and env_ok:
        print("✅ All tests passed! Agent is ready to use.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    print("="*50)


if __name__ == "__main__":
    main()