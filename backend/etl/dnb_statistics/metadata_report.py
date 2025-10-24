"""
Metadata Reporting Utility for DNB Statistics ETL

Provides command-line tool to query and analyze extraction metadata.

Usage:
    # Show summary report
    python -m backend.etl.dnb_statistics.metadata_report
    
    # Show incomplete datasets
    python -m backend.etl.dnb_statistics.metadata_report --incomplete
    
    # Show stale datasets (not updated in 24 hours)
    python -m backend.etl.dnb_statistics.metadata_report --stale
    
    # Show details for specific endpoint
    python -m backend.etl.dnb_statistics.metadata_report --endpoint exchange_rates_day
    
    # Export metadata to JSON
    python -m backend.etl.dnb_statistics.metadata_report --export metadata_export.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .metadata import ExtractionMetadata
from . import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Simple format for reports
)
logger = logging.getLogger(__name__)


def show_summary(metadata: ExtractionMetadata) -> None:
    """Display summary report."""
    print(metadata.generate_summary_report())


def show_incomplete(metadata: ExtractionMetadata) -> None:
    """Display incomplete datasets."""
    incomplete = metadata.get_incomplete_endpoints()
    
    if not incomplete:
        print("✅ All endpoints have complete data!")
        return
    
    print("=" * 70)
    print(f"⚠️  INCOMPLETE DATASETS ({len(incomplete)} found)")
    print("=" * 70)
    print()
    
    for item in incomplete:
        print(f"Endpoint: {item['endpoint']}")
        print(f"  Category: {item.get('category', 'unknown')}")
        print(f"  Records: {item['total_records']:,}")
        print(f"  Last Extraction: {item.get('last_extraction', 'Never')}")
        
        notes = item.get('notes', [])
        if notes:
            print("  Issues:")
            for note in notes:
                print(f"    • {note}")
        print()


def show_stale(metadata: ExtractionMetadata, max_age_hours: float = 24.0) -> None:
    """Display stale datasets."""
    stale = metadata.get_stale_endpoints(max_age_hours=max_age_hours)
    
    if not stale:
        print(f"✅ All endpoints updated within {max_age_hours} hours!")
        return
    
    print("=" * 70)
    print(f"📅 STALE DATASETS ({len(stale)} found - older than {max_age_hours}h)")
    print("=" * 70)
    print()
    
    for item in stale:
        print(f"Endpoint: {item['endpoint']}")
        print(f"  Category: {item.get('category', 'unknown')}")
        print(f"  Status: {item['status']}")
        
        if item.get('age_hours'):
            print(f"  Age: {item['age_hours']:.1f} hours ({item['age_hours']/24:.1f} days)")
        
        print(f"  Last Extraction: {item.get('last_extraction', 'Never')}")
        print()


def show_endpoint_details(metadata: ExtractionMetadata, endpoint_name: str) -> None:
    """Display detailed information for a specific endpoint."""
    endpoint_meta = metadata.get_endpoint_metadata(endpoint_name)
    
    if not endpoint_meta:
        print(f"❌ No metadata found for endpoint: {endpoint_name}")
        return
    
    print("=" * 70)
    print(f"📊 ENDPOINT DETAILS: {endpoint_name}")
    print("=" * 70)
    print()
    
    print(f"Category: {endpoint_meta.get('category', 'unknown')}")
    print(f"Filename: {endpoint_meta.get('filename', 'unknown')}")
    print(f"Total Records: {endpoint_meta.get('total_records', 0):,}")
    print(f"Complete: {'✅ Yes' if endpoint_meta.get('is_complete', True) else '⚠️ No'}")
    print(f"Last Extraction: {endpoint_meta.get('last_extraction', 'Never')}")
    print()
    
    # Show extraction history
    history = endpoint_meta.get('extraction_history', [])
    
    if history:
        print(f"📜 EXTRACTION HISTORY (last {len(history)} runs):")
        print()
        
        for i, run in enumerate(reversed(history), 1):
            timestamp = run.get('timestamp', 'Unknown')
            status = run.get('status', 'unknown')
            records = run.get('total_records', 0)
            duration = run.get('duration_seconds', 0)
            
            status_icon = "✅" if status == "success" else "❌"
            
            print(f"{i}. {status_icon} {timestamp}")
            print(f"   Records: {records:,}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Pages: {run.get('total_pages', 0)}")
            
            if run.get('failed_pages', 0) > 0:
                print(f"   Failed Pages: {run['failed_pages']}")
            
            if run.get('completeness_notes'):
                print("   Notes:")
                for note in run['completeness_notes']:
                    print(f"     • {note}")
            
            if run.get('error'):
                print(f"   Error: {run['error']}")
            
            print()


def export_metadata(metadata: ExtractionMetadata, output_path: Path) -> None:
    """Export metadata to JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata exported to: {output_path}")
        print(f"   Endpoints: {len(metadata.data.get('endpoints', {}))}")
        print(f"   Size: {output_path.stat().st_size:,} bytes")
    
    except Exception as exc:
        print(f"❌ Failed to export metadata: {exc}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DNB Statistics Metadata Report Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    group = parser.add_mutually_exclusive_group()
    
    group.add_argument(
        "--summary",
        action="store_true",
        help="Show summary report (default)",
    )
    
    group.add_argument(
        "--incomplete",
        action="store_true",
        help="Show incomplete datasets",
    )
    
    group.add_argument(
        "--stale",
        action="store_true",
        help="Show stale datasets (not updated recently)",
    )
    
    group.add_argument(
        "--endpoint",
        type=str,
        metavar="NAME",
        help="Show details for specific endpoint",
    )
    
    group.add_argument(
        "--export",
        type=Path,
        metavar="FILE",
        help="Export metadata to JSON file",
    )
    
    parser.add_argument(
        "--max-age",
        type=float,
        default=24.0,
        metavar="HOURS",
        help="Maximum age in hours for stale check (default: 24)",
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Load metadata
    try:
        metadata = ExtractionMetadata()
    except Exception as exc:
        print(f"❌ Failed to load metadata: {exc}")
        sys.exit(1)
    
    # Check if metadata exists
    if not metadata.data.get('endpoints'):
        print("⚠️  No extraction metadata found.")
        print("   Run an extraction first:")
        print("   python -m backend.etl.dnb_statistics.orchestrator --all")
        sys.exit(0)
    
    # Execute requested operation
    if args.incomplete:
        show_incomplete(metadata)
    
    elif args.stale:
        show_stale(metadata, max_age_hours=args.max_age)
    
    elif args.endpoint:
        show_endpoint_details(metadata, args.endpoint)
    
    elif args.export:
        export_metadata(metadata, args.export)
    
    else:
        # Default: show summary
        show_summary(metadata)


if __name__ == "__main__":
    main()
