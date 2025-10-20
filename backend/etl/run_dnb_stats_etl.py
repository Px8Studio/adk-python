#!/usr/bin/env python
"""
Quick start script for DNB Statistics ETL

Usage:
    python backend/etl/run_dnb_stats_etl.py

    # Or with specific endpoints
    python backend/etl/run_dnb_stats_etl.py exchange_rates_day market_interest_rates_day

Environment:
    DNB_SUBSCRIPTION_KEY_DEV: Required API key
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from etl.dnb_statistics.orchestrator import (
    extract_all,
    extract_endpoint,
    list_endpoints_info,
)


async def main():
    # Check for API key
    if not os.getenv("DNB_SUBSCRIPTION_KEY_DEV"):
        print("❌ ERROR: DNB_SUBSCRIPTION_KEY_DEV environment variable not set")
        print("\nPlease set your API key:")
        print("  $env:DNB_SUBSCRIPTION_KEY_DEV = 'your-key-here'")
        print("\nGet your key from: https://api.portal.dnb.nl/")
        sys.exit(1)
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    if not args:
        # No arguments - extract everything
        print("🚀 Starting full DNB Statistics extraction...")
        print("   (To extract specific endpoints, pass them as arguments)")
        print()
        await extract_all()
    
    elif args[0] == "--list":
        # List available endpoints
        await list_endpoints_info()
    
    else:
        # Extract specific endpoints
        print(f"🚀 Extracting {len(args)} endpoint(s)...")
        print()
        
        for endpoint_name in args:
            try:
                await extract_endpoint(endpoint_name)
            except Exception as exc:
                print(f"❌ Failed to extract {endpoint_name}: {exc}")
                continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  ETL interrupted by user")
        sys.exit(130)
    except Exception as exc:
        print(f"❌ ETL pipeline failed: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
