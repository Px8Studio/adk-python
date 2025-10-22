"""
DNB Statistics ETL Orchestrator

Coordinates extraction of all DNB Statistics data.

Usage:
    # Extract everything (all endpoints)
    python -m backend.etl.dnb_statistics.orchestrator --all

    # Extract specific endpoints
    python -m backend.etl.dnb_statistics.orchestrator --endpoints exchange_rates_day market_interest_rates_day

    # Extract by category
    python -m backend.etl.dnb_statistics.orchestrator --category market_data

    # List available endpoints
    python -m backend.etl.dnb_statistics.orchestrator --list

Environment:
    DNB_SUBSCRIPTION_KEY_DEV: Required API key
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from . import config
from .extractors import EXTRACTOR_REGISTRY, get_extractor, list_available_endpoints
from .metadata import ExtractionMetadata

# Configure console to handle UTF-8 on Windows
def setup_console_encoding():
  """Configure console to handle UTF-8 on Windows."""
  if sys.platform == 'win32':
    try:
      sys.stdout.reconfigure(encoding='utf-8')
      sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
      import codecs
      sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
      sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

setup_console_encoding()

# Add emoji helper
def safe_emoji(emoji: str) -> str:
  """Return emoji or ASCII fallback for Windows console."""
  emoji_map = {
    '✅': '[SUCCESS]',
    '❌': '[FAILED]',
  }
  if sys.platform == 'win32':
    return emoji_map.get(emoji, emoji)
  return emoji

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            config.LOG_DIR / "etl_dnb_statistics.log"
        ),
    ],
)
logger = logging.getLogger(__name__)


# ==========================================
# Extraction Workflows
# ==========================================

async def extract_endpoint(endpoint_name: str, metadata: ExtractionMetadata) -> dict[str, Any]:
    """
    Extract data from a single endpoint.
    
    Args:
        endpoint_name: Name of the endpoint to extract
        metadata: Metadata manager for tracking extraction history
    
    Returns:
        Extraction statistics
    """
    logger.info(f"\n{'=' * 70}")
    logger.info(f"[EXTRACTING] {endpoint_name}")
    logger.info(f"{'=' * 70}\n")
    
    try:
        extractor = get_extractor(endpoint_name)
        stats = await extractor.run()
        
        # Update metadata with extraction results
        metadata.update_extraction(
            endpoint_name=endpoint_name,
            stats=stats,
            category=extractor.get_category(),
            filename=extractor.get_output_filename(),
            subcategory=extractor.get_subcategory(),
        )
        
        return stats
    
    except Exception as exc:
        logger.error(f"[FAILED] {endpoint_name}: {exc}", exc_info=True)
        
        # Record failure in metadata
        failure_stats = {
            "error": str(exc),
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "total_records": 0,
            "total_pages": 0,
            "failed_pages": 1,
        }
        
        metadata.update_extraction(
            endpoint_name=endpoint_name,
            stats=failure_stats,
            category="unknown",
            filename=endpoint_name,
        )
        
        return failure_stats


async def extract_by_category(category: str) -> dict[str, Any]:
    """
    Extract all endpoints in a specific category.
    
    Args:
        category: Category name (e.g., 'market_data', 'macroeconomic')
    
    Returns:
        Combined statistics from all extractions
    """
    logger.info(f"\n{'=' * 70}")
    logger.info(f"📁 CATEGORY EXTRACTION: {category}")
    logger.info(f"{'=' * 70}\n")
    
    # Initialize metadata tracker
    metadata = ExtractionMetadata()
    
    # Find all endpoints in this category
    endpoints = []
    for endpoint_name in EXTRACTOR_REGISTRY.keys():
        extractor = get_extractor(endpoint_name)
        if extractor.get_category() == category:
            endpoints.append(endpoint_name)
    
    if not endpoints:
        logger.warning(f"No endpoints found for category: {category}")
        return {}
    
    logger.info(f"Found {len(endpoints)} endpoints in category '{category}':")
    for ep in endpoints:
        logger.info(f"  • {ep}")
    logger.info("")
    
    # Extract each endpoint
    all_stats = {}
    for endpoint_name in endpoints:
        stats = await extract_endpoint(endpoint_name, metadata)
        all_stats[endpoint_name] = stats
    
    return all_stats


async def extract_all() -> dict[str, Any]:
    """
    Extract data from all available endpoints.
    
    Returns:
        Combined statistics from all extractions
    """
    logger.info("\n" + "=" * 70)
    logger.info("FULL DNB STATISTICS EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    # Initialize metadata tracker
    metadata = ExtractionMetadata()
    
    endpoints = list_available_endpoints()
    
    logger.info(f"Total endpoints to extract: {len(endpoints)}")
    logger.info("Endpoints:")
    for ep in endpoints:
        logger.info(f"  • {ep}")
    logger.info("")
    
    overall_start = datetime.now()
    all_stats = {}
    
    for i, endpoint_name in enumerate(endpoints, 1):
        logger.info(f"\n[{i}/{len(endpoints)}] Processing: {endpoint_name}")
        
        try:
            stats = await extract_endpoint(endpoint_name, metadata)
            all_stats[endpoint_name] = stats
        except Exception as exc:
            logger.error(f"Failed to process {endpoint_name}: {exc}")
            all_stats[endpoint_name] = {"error": str(exc)}
            continue
    
    # Summary
    overall_elapsed = (datetime.now() - overall_start).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info(f"{safe_emoji('✅')} FULL EXTRACTION COMPLETE")
    logger.info(f"   Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.1f}m)")
    logger.info(f"   Output directory: {config.BRONZE_DIR}")
    
    # Count successes and failures
    successes = sum(1 for s in all_stats.values() if "error" not in s)
    failures = sum(1 for s in all_stats.values() if "error" in s)
    
    logger.info(f"   Successes: {successes}/{len(endpoints)}")
    if failures > 0:
        logger.warning(f"   Failures: {failures}/{len(endpoints)}")
        logger.warning("   Failed endpoints:")
        for ep, stats in all_stats.items():
            if "error" in stats:
                logger.warning(f"     • {ep}: {stats['error']}")
    
    logger.info("=" * 70 + "\n")
    
    # Show metadata summary
    logger.info("\n" + metadata.generate_summary_report())
    
    # Warn about incomplete datasets
    incomplete = metadata.get_incomplete_endpoints()
    if incomplete:
        logger.warning(f"\n{safe_emoji('⚠️')} WARNING: {len(incomplete)} endpoint(s) may have incomplete data:")
        for item in incomplete:
            logger.warning(f"  • {item['endpoint']}: {item['total_records']:,} records")
            for note in item.get('notes', []):
                logger.warning(f"    - {note}")
    
    return all_stats
    
    return all_stats


async def list_endpoints_info() -> None:
    """List all available endpoints with their categories."""
    logger.info("\n" + "=" * 70)
    logger.info("📋 AVAILABLE DNB STATISTICS ENDPOINTS")
    logger.info("=" * 70 + "\n")
    
    # Group by category
    by_category: dict[str, list[str]] = {}
    
    for endpoint_name in list_available_endpoints():
        extractor = get_extractor(endpoint_name)
        category = extractor.get_category()
        
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(endpoint_name)
    
    # Print organized by category
    for category in sorted(by_category.keys()):
        logger.info(f"📁 {category.upper()}")
        for endpoint in sorted(by_category[category]):
            logger.info(f"   • {endpoint}")
        logger.info("")
    
    logger.info(f"Total: {len(list_available_endpoints())} endpoints")
    logger.info("=" * 70 + "\n")


# ==========================================
# CLI
# ==========================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DNB Statistics ETL Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Extraction scope
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all",
        action="store_true",
        help="Extract all available endpoints",
    )
    group.add_argument(
        "--endpoints",
        nargs="+",
        metavar="ENDPOINT",
        help="Extract specific endpoints (space-separated)",
    )
    group.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Extract all endpoints in a category",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="List all available endpoints and exit",
    )
    
    # Options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be extracted without actually doing it",
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    # Show configuration
    logger.info("=" * 70)
    logger.info("DNB STATISTICS ETL ORCHESTRATOR")
    logger.info("=" * 70)
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info(f"Output directory: {config.BRONZE_DIR}")
    logger.info(f"Rate limit: {config.RATE_LIMIT_CALLS} calls/{config.RATE_LIMIT_PERIOD}s")
    logger.info("=" * 70 + "\n")
    
    # List endpoints if requested
    if args.list:
        await list_endpoints_info()
        return
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No data will be extracted\n")
        if args.all:
            logger.info("Would extract all endpoints:")
            for ep in list_available_endpoints():
                logger.info(f"  • {ep}")
        elif args.endpoints:
            logger.info(f"Would extract endpoints: {', '.join(args.endpoints)}")
        elif args.category:
            logger.info(f"Would extract all endpoints in category: {args.category}")
        return
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Execute requested extraction
    try:
        if args.all:
            await extract_all()
        
        elif args.endpoints:
            logger.info(f"Extracting {len(args.endpoints)} endpoint(s)...\n")
            for endpoint_name in args.endpoints:
                if endpoint_name not in EXTRACTOR_REGISTRY:
                    logger.error(
                        f"{safe_emoji('❌')} Unknown endpoint: {endpoint_name}\n"
                        f"   Available: {', '.join(list_available_endpoints())}"
                    )
                    continue
                await extract_endpoint(endpoint_name)
        
        elif args.category:
            await extract_by_category(args.category)
        
        else:
            logger.error("No extraction scope specified. Use --all, --endpoints, --category, or --list")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning(f"\n{safe_emoji('⚠️')} Extraction interrupted by user")
        sys.exit(130)
    
    except Exception as exc:
        logger.error(f"\n{safe_emoji('❌')} Extraction failed: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
