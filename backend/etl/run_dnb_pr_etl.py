#!/usr/bin/env python
"""
Quick start script for DNB Public Register ETL

Usage:
    python backend/etl/run_dnb_pr_etl.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from etl.dnb_public_register.orchestrator import main

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("DNB_SUBSCRIPTION_KEY_DEV"):
        print("❌ ERROR: DNB_SUBSCRIPTION_KEY_DEV environment variable not set")
        print("\nPlease set your API key:")
        print("  $env:DNB_SUBSCRIPTION_KEY_DEV = 'your-key-here'")
        print("\nGet your key from: https://api.portal.dnb.nl/")
        sys.exit(1)
    
    # Run ETL
    asyncio.run(main())
