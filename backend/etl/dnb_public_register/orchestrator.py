"""
DNB Public Register ETL Orchestrator

Coordinates extraction of all DNB Public Register data.

Usage:
    # Extract everything (recommended for first run)
    python -m backend.etl.dnb_public_register.orchestrator --all

    # Extract specific categories
    python -m backend.etl.dnb_public_register.orchestrator --metadata
    python -m backend.etl.dnb_public_register.orchestrator --organizations
    python -m backend.etl.dnb_public_register.orchestrator --publications

    # Extract for specific register
    python -m backend.etl.dnb_public_register.orchestrator --register WFTAF

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
from typing import Any, Optional

from . import config
from .extractors import (
    AllPublicationsExtractor,
    OrganizationsExtractor,
    PublicationsSearchExtractor,
    RegisterArticlesExtractor,
    RegistersExtractor,
    RegistrationsExtractor,
    SupportedLanguagesExtractor,
)

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            config.LOG_DIR / "etl_dnb_public_register.log"
        ),
    ],
)
logger = logging.getLogger(__name__)


# ==========================================
# Extraction Workflows
# ==========================================

async def extract_metadata() -> dict[str, Any]:
    """Extract metadata (registers and languages)."""
    logger.info("\n" + "=" * 70)
    logger.info("🔍 METADATA EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    stats = {}
    
    # Registers
    logger.info("📋 Extracting registers...")
    registers_extractor = RegistersExtractor()
    stats["registers"] = await registers_extractor.run()
    
    # Languages
    logger.info("\n🌐 Extracting supported languages...")
    languages_extractor = SupportedLanguagesExtractor()
    stats["languages"] = await languages_extractor.run()
    
    return stats


async def extract_organizations(
    register_codes: Optional[list[str]] = None,
    language_codes: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Extract organizations for specified registers and languages.
    
    Args:
        register_codes: List of register codes (or None for all)
        language_codes: List of language codes (or None for default)
    
    Returns:
        Extraction statistics
    """
    logger.info("\n" + "=" * 70)
    logger.info("🏢 ORGANIZATIONS EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    # Get register codes if not specified
    if not register_codes:
        logger.info("📋 Discovering register codes...")
        registers_extractor = RegistersExtractor()
        register_codes = []
        
        async for register in registers_extractor.extract():
            register_codes.append(register["register_code"])
        
        await registers_extractor.close()
        logger.info(f"Found {len(register_codes)} registers")
    
    # Use default language if not specified
    if not language_codes:
        language_codes = [config.DEFAULT_LANGUAGE]
    
    stats = {}
    
    # Extract for each register x language combination
    for register_code in register_codes:
        for language_code in language_codes:
            key = f"{register_code}_{language_code}"
            logger.info(f"\n🔍 Processing: {key}")
            
            extractor = OrganizationsExtractor(
                register_code=register_code,
                language_code=language_code,
            )
            
            try:
                stats[key] = await extractor.run()
            except Exception as exc:
                logger.error(f"Failed to extract {key}: {exc}")
                stats[key] = {"error": str(exc)}
    
    return stats


async def extract_publications(
    register_codes: Optional[list[str]] = None,
    language_codes: Optional[list[str]] = None,
    extract_all: bool = False,
) -> dict[str, Any]:
    """
    Extract publications for specified registers and languages.
    
    Args:
        register_codes: List of register codes (or None for all)
        language_codes: List of language codes (or None for default)
        extract_all: If True, use AllPublicationsExtractor
    
    Returns:
        Extraction statistics
    """
    logger.info("\n" + "=" * 70)
    logger.info("📰 PUBLICATIONS EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    stats = {}
    
    # Option 1: Extract all publications at once (faster, single file)
    if extract_all:
        logger.info("🚀 Using AllPublicationsExtractor (single file)")
        extractor = AllPublicationsExtractor(
            language_code=config.DEFAULT_LANGUAGE
        )
        stats["all_publications"] = await extractor.run()
        return stats
    
    # Option 2: Extract per register (separate files)
    if not register_codes:
        logger.info("📋 Discovering register codes...")
        registers_extractor = RegistersExtractor()
        register_codes = []
        
        async for register in registers_extractor.extract():
            register_codes.append(register["register_code"])
        
        await registers_extractor.close()
    
    if not language_codes:
        language_codes = [config.DEFAULT_LANGUAGE]
    
    for register_code in register_codes:
        for language_code in language_codes:
            key = f"publications_{register_code}_{language_code}"
            logger.info(f"\n🔍 Processing: {key}")
            
            extractor = PublicationsSearchExtractor(
                register_code=register_code,
                language_code=language_code,
            )
            
            try:
                stats[key] = await extractor.run()
            except Exception as exc:
                logger.error(f"Failed to extract {key}: {exc}")
                stats[key] = {"error": str(exc)}
    
    return stats


async def extract_registrations(
    register_codes: Optional[list[str]] = None,
    language_codes: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Extract registrations for specified registers."""
    logger.info("\n" + "=" * 70)
    logger.info("📝 REGISTRATIONS EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    if not register_codes:
        logger.info("📋 Discovering register codes...")
        registers_extractor = RegistersExtractor()
        register_codes = []
        
        async for register in registers_extractor.extract():
            register_codes.append(register["register_code"])
        
        await registers_extractor.close()
    
    if not language_codes:
        language_codes = [config.DEFAULT_LANGUAGE]
    
    stats = {}
    
    for register_code in register_codes:
        for language_code in language_codes:
            key = f"registrations_{register_code}_{language_code}"
            logger.info(f"\n🔍 Processing: {key}")
            
            extractor = RegistrationsExtractor(
                register_code=register_code,
                language_code=language_code,
            )
            
            try:
                stats[key] = await extractor.run()
            except Exception as exc:
                logger.error(f"Failed to extract {key}: {exc}")
                stats[key] = {"error": str(exc)}
    
    return stats


async def extract_register_articles(
    register_codes: Optional[list[str]] = None,
    language_codes: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Extract register articles (regulatory metadata)."""
    logger.info("\n" + "=" * 70)
    logger.info("⚖️  REGISTER ARTICLES EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    if not register_codes:
        logger.info("📋 Discovering register codes...")
        registers_extractor = RegistersExtractor()
        register_codes = []
        
        async for register in registers_extractor.extract():
            register_codes.append(register["register_code"])
        
        await registers_extractor.close()
    
    if not language_codes:
        language_codes = [config.DEFAULT_LANGUAGE]
    
    stats = {}
    
    for register_code in register_codes:
        for language_code in language_codes:
            key = f"articles_{register_code}_{language_code}"
            logger.info(f"\n🔍 Processing: {key}")
            
            extractor = RegisterArticlesExtractor(
                register_code=register_code,
                language_code=language_code,
            )
            
            try:
                stats[key] = await extractor.run()
            except Exception as exc:
                logger.error(f"Failed to extract {key}: {exc}")
                stats[key] = {"error": str(exc)}
    
    return stats


async def extract_all() -> dict[str, Any]:
    """
    Extract all data from DNB Public Register API.
    
    Order:
    1. Metadata (registers, languages)
    2. Publications (comprehensive search)
    3. Organizations
    4. Registrations
    5. Register Articles
    
    Returns:
        Combined statistics from all extractions
    """
    logger.info("\n" + "=" * 70)
    logger.info("🚀 FULL DNB PUBLIC REGISTER EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    overall_start = datetime.now()
    all_stats = {}
    
    # 1. Metadata (needed for discovering registers)
    logger.info("\n[1/5] Extracting metadata...")
    all_stats["metadata"] = await extract_metadata()
    
    # 2. Publications (most comprehensive dataset)
    logger.info("\n[2/5] Extracting publications...")
    all_stats["publications"] = await extract_publications(extract_all=True)
    
    # 3. Organizations
    logger.info("\n[3/5] Extracting organizations...")
    all_stats["organizations"] = await extract_organizations()
    
    # 4. Registrations
    logger.info("\n[4/5] Extracting registrations...")
    all_stats["registrations"] = await extract_registrations()
    
    # 5. Register Articles
    logger.info("\n[5/5] Extracting register articles...")
    all_stats["register_articles"] = await extract_register_articles()
    
    # Summary
    overall_elapsed = (datetime.now() - overall_start).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ FULL EXTRACTION COMPLETE")
    logger.info(f"   Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.1f}m)")
    logger.info(f"   Output directory: {config.BRONZE_DIR}")
    logger.info("=" * 70 + "\n")
    
    return all_stats


# ==========================================
# CLI
# ==========================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DNB Public Register ETL Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Extraction scope
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all",
        action="store_true",
        help="Extract all data (recommended for first run)",
    )
    group.add_argument(
        "--metadata",
        action="store_true",
        help="Extract only metadata (registers, languages)",
    )
    group.add_argument(
        "--organizations",
        action="store_true",
        help="Extract organizations",
    )
    group.add_argument(
        "--publications",
        action="store_true",
        help="Extract publications",
    )
    group.add_argument(
        "--registrations",
        action="store_true",
        help="Extract registrations",
    )
    group.add_argument(
        "--articles",
        action="store_true",
        help="Extract register articles",
    )
    
    # Filters
    parser.add_argument(
        "--register",
        type=str,
        action="append",
        dest="registers",
        help="Specific register code(s) to extract (can specify multiple)",
    )
    parser.add_argument(
        "--language",
        type=str,
        action="append",
        dest="languages",
        help="Language code(s) to use (default: NL)",
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
    logger.info("DNB PUBLIC REGISTER ETL ORCHESTRATOR")
    logger.info("=" * 70)
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info(f"Output: {config.BRONZE_DIR}")
    logger.info(f"Rate limit: {config.RATE_LIMIT_CALLS} calls/{config.RATE_LIMIT_PERIOD}s")
    logger.info("=" * 70 + "\n")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No data will be extracted\n")
        return
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Execute requested extraction
    try:
        if args.all:
            await extract_all()
        elif args.metadata:
            await extract_metadata()
        elif args.organizations:
            await extract_organizations(args.registers, args.languages)
        elif args.publications:
            await extract_publications(args.registers, args.languages)
        elif args.registrations:
            await extract_registrations(args.registers, args.languages)
        elif args.articles:
            await extract_register_articles(args.registers, args.languages)
        else:
            logger.error("No extraction scope specified. Use --all or a specific flag.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Extraction interrupted by user")
        sys.exit(130)
    
    except Exception as exc:
        logger.error(f"\n❌ Extraction failed: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
