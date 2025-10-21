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
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from . import config
from .extractors import (
    AllPublicationsExtractor,
    OrganizationDetailsExtractor,
    OrganizationRelationNumbersExtractor,
    PublicationDetailsExtractor,
    PublicationsSearchExtractor,
    RegisterArticlesExtractor,
    RegistersExtractor,
    RegistrationActArticleNamesExtractor,
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
    exclude_relation_numbers: Optional[set[str]] = None,
) -> dict[str, Any]:
    """
    Extract organizations for specified registers and languages.
    
    Two-step process:
    1. Get relation numbers (lightweight)
    2. Get full organization details (heavy - with names, addresses, etc.)
    
    Args:
        register_codes: List of register codes (or None for all)
        language_codes: List of language codes (or None for default)
        exclude_relation_numbers: Set of relation numbers to skip (deduplication)
    
    Returns:
        Extraction statistics
    """
    logger.info("\n" + "=" * 70)
    logger.info("🏢 ORGANIZATIONS EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    if exclude_relation_numbers:
        logger.info(
            f"🔍 Deduplication: Skipping {len(exclude_relation_numbers)} "
            "relation numbers already extracted from Publications"
        )
    
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
    
    # Step 1: Extract relation numbers for each register
    for register_code in register_codes:
        logger.info(f"\n🔢 Step 1: Getting relation numbers for {register_code}")
        
        relation_numbers_extractor = OrganizationRelationNumbersExtractor(
            register_code=register_code
        )
        
        try:
            # Collect all relation numbers
            relation_numbers = []
            async for record in relation_numbers_extractor.extract():
                if rel_num := record.get("relation_number"):
                    relation_numbers.append(rel_num)
            
            await relation_numbers_extractor.close()
            
            logger.info(
                f"   Found {len(relation_numbers)} organizations in {register_code}"
            )
            
            # Apply deduplication if needed
            if exclude_relation_numbers:
                original_count = len(relation_numbers)
                relation_numbers = [
                    rn for rn in relation_numbers
                    if rn not in exclude_relation_numbers
                ]
                skipped = original_count - len(relation_numbers)
                if skipped > 0:
                    logger.info(
                        f"   Skipped {skipped} already-extracted organizations "
                        f"({len(relation_numbers)} remaining)"
                    )
            
            # Skip if no organizations need extraction
            if not relation_numbers:
                logger.info(
                    f"   All organizations from {register_code} already extracted"
                )
                continue
            
            # Step 2: Get full details for these organizations (per language)
            for language_code in language_codes:
                key = f"details_{register_code}_{language_code}"
                logger.info(
                    f"\n🏢 Step 2: Getting full details for {register_code} "
                    f"({language_code})"
                )
                
                details_extractor = OrganizationDetailsExtractor(
                    register_code=register_code,
                    relation_numbers=relation_numbers,
                    language_code=language_code,
                )
                
                try:
                    stats[key] = await details_extractor.run()
                except Exception as exc:
                    logger.error(f"Failed to extract {key}: {exc}")
                    stats[key] = {"error": str(exc)}
        
        except Exception as exc:
            logger.error(
                f"Failed to get relation numbers for {register_code}: {exc}"
            )
            stats[f"relation_numbers_{register_code}"] = {"error": str(exc)}
    
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
    """
    Extract registration act article names for specified registers.
    
    This gets the distinct list of act article names used in registrations.
    """
    logger.info("\n" + "=" * 70)
    logger.info("📝 REGISTRATIONS (ACT ARTICLE NAMES) EXTRACTION")
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
            key = f"act_article_names_{register_code}_{language_code}"
            logger.info(f"\n🔍 Processing: {key}")
            
            extractor = RegistrationActArticleNamesExtractor(
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
    
    Optimized workflow:
    1. Metadata (registers, languages)
    2. Publications + Organizations in parallel (with deduplication)
    3. Registrations
    4. Register Articles
    
    Returns:
        Combined statistics from all extractions
    """
    logger.info("\n" + "=" * 70)
    logger.info("🚀 FULL DNB PUBLIC REGISTER EXTRACTION")
    logger.info("=" * 70 + "\n")
    
    overall_start = datetime.now()
    all_stats = {}
    
    # 1. Metadata (needed for discovering registers)
    logger.info("\n[1/4] Extracting metadata...")
    all_stats["metadata"] = await extract_metadata()
    
    # 2. Publications + Organizations in parallel with deduplication
    logger.info("\n[2/4] Extracting publications and organizations (parallel)...")
    logger.info("=" * 70)
    logger.info("🔄 Running Publications and Organizations extraction in parallel")
    logger.info("   Publications will extract all data from search endpoint")
    logger.info("   Organizations will fill gaps not found in Publications")
    logger.info("=" * 70 + "\n")
    
    # Track relation numbers from publications for deduplication
    seen_relation_numbers = set()
    
    # Create a custom publications extractor that tracks relation numbers
    async def extract_publications_with_tracking():
        """Extract publications and track relation numbers."""
        stats = await extract_publications(extract_all=True)
        
        # Read the output file to extract relation numbers
        output_file = (
            config.BRONZE_DIR / "publications" / 
            f"all_publications_{config.DEFAULT_LANGUAGE.lower()}.parquet"
        )
        
        if output_file.exists():
            logger.info(f"\n📊 Reading publications output to track relation numbers...")
            try:
                df = pd.read_parquet(output_file)
                if "relation_number" in df.columns:
                    relation_numbers = df["relation_number"].dropna().unique()
                    seen_relation_numbers.update(relation_numbers)
                    logger.info(
                        f"   Tracked {len(seen_relation_numbers)} unique relation numbers "
                        "from Publications"
                    )
            except Exception as exc:
                logger.warning(f"Failed to read relation numbers from Parquet: {exc}")
        
        return stats
    
    # Run Publications and Organizations in parallel
    parallel_start = datetime.now()
    
    publications_stats, organizations_stats = await asyncio.gather(
        extract_publications_with_tracking(),
        extract_organizations(exclude_relation_numbers=None),  # Will update after pubs
        return_exceptions=True,
    )
    
    parallel_elapsed = (datetime.now() - parallel_start).total_seconds()
    
    # Handle results
    if isinstance(publications_stats, Exception):
        logger.error(f"❌ Publications extraction failed: {publications_stats}")
        all_stats["publications"] = {"error": str(publications_stats)}
    else:
        all_stats["publications"] = publications_stats
    
    if isinstance(organizations_stats, Exception):
        logger.error(f"❌ Organizations extraction failed: {organizations_stats}")
        all_stats["organizations"] = {"error": str(organizations_stats)}
    else:
        all_stats["organizations"] = organizations_stats
    
    logger.info(
        f"\n✅ Parallel extraction completed in {parallel_elapsed:.2f}s "
        f"({parallel_elapsed/60:.1f}m)"
    )
    
    # Now run organizations again with deduplication (gap-filling)
    if len(seen_relation_numbers) > 0:
        logger.info(
            f"\n🔄 Running gap-filling Organizations extraction "
            f"(excluding {len(seen_relation_numbers)} already-seen orgs)..."
        )
        gap_fill_stats = await extract_organizations(
            exclude_relation_numbers=seen_relation_numbers
        )
        all_stats["organizations_gap_fill"] = gap_fill_stats
    
    # 3. Registrations
    logger.info("\n[3/4] Extracting registrations...")
    all_stats["registrations"] = await extract_registrations()
    
    # 4. Register Articles
    logger.info("\n[4/4] Extracting register articles...")
    all_stats["register_articles"] = await extract_register_articles()
    
    # Summary
    overall_elapsed = (datetime.now() - overall_start).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ FULL EXTRACTION COMPLETE")
    logger.info(f"   Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.1f}m)")
    logger.info(f"   Relation numbers from Publications: {len(seen_relation_numbers)}")
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
