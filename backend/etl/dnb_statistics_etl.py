"""
DNB Statistics API ETL Pipeline

Extracts all data from DNB Statistics API endpoints and loads into data warehouse.
Optimized for bulk extraction with parallel page fetching.

Usage:
    python backend/etl/dnb_statistics_etl.py

Environment Variables:
    DNB_SUBSCRIPTION_KEY_DEV: DNB API key
    WAREHOUSE_URL: Database connection string (optional, defaults to logging)
"""

import asyncio
import httpx
import logging
import os
import sys
from datetime import datetime
from typing import AsyncIterator, Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent.parent / 'logs' / 'etl_statistics.log')
    ]
)
logger = logging.getLogger(__name__)


# Configuration
DNB_BASE_URL = "https://api.dnb.nl/statistics/v2024100101"
DNB_API_KEY = os.getenv("DNB_SUBSCRIPTION_KEY_DEV")
PAGE_SIZE = 2000  # Maximum allowed by DNB API
MAX_PARALLEL_PAGES = 5  # Concurrent page fetches
REQUEST_TIMEOUT = 30.0  # seconds
MAX_RETRIES = 3


class DNBStatisticsExtractor:
    """
    Extracts data from DNB Statistics API with pagination and parallel fetching.
    
    Features:
    - Parallel page fetching for speed
    - Automatic retry with exponential backoff
    - Progress tracking
    - Graceful error handling
    """
    
    def __init__(self):
        if not DNB_API_KEY:
            raise ValueError("DNB_SUBSCRIPTION_KEY_DEV environment variable not set")
        
        self.client = httpx.AsyncClient(
            headers={
                "Ocp-Apim-Subscription-Key": DNB_API_KEY,
                "Accept": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        self.stats = {
            "total_records": 0,
            "total_pages": 0,
            "failed_pages": 0,
            "start_time": None
        }
    
    async def fetch_page(
        self,
        endpoint: str,
        page: int,
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single page with retry logic.
        
        Args:
            endpoint: API endpoint name (e.g., 'exchange-rates-day')
            page: Page number (1-indexed)
            retry_count: Current retry attempt
            
        Returns:
            Response dict or None if all retries failed
        """
        url = f"{DNB_BASE_URL}/{endpoint}"
        params = {"page": page, "pageSize": PAGE_SIZE}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.warning(f"Rate limited on page {page}, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                
                if retry_count < MAX_RETRIES:
                    return await self.fetch_page(endpoint, page, retry_count + 1)
            
            logger.error(f"HTTP {e.response.status_code} on page {page}: {e}")
            self.stats["failed_pages"] += 1
            return None
        
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            
            if retry_count < MAX_RETRIES:
                wait_time = 2 ** retry_count
                await asyncio.sleep(wait_time)
                return await self.fetch_page(endpoint, page, retry_count + 1)
            
            self.stats["failed_pages"] += 1
            return None
    
    async def extract_all_pages(
        self,
        endpoint: str,
        start_page: int = 1
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Extract all pages from an endpoint with parallel batching.
        
        Args:
            endpoint: API endpoint name
            start_page: Starting page number (for resuming)
            
        Yields:
            Individual records from all pages
        """
        self.stats["start_time"] = datetime.now()
        
        # Fetch first page to get metadata
        logger.info(f"📊 Fetching metadata for {endpoint}...")
        first_page = await self.fetch_page(endpoint, page=start_page)
        
        if not first_page:
            logger.error(f"Failed to fetch first page of {endpoint}")
            return
        
        metadata = first_page.get("_metadata", {})
        total_count = metadata.get("totalCount", 0)
        total_pages = (total_count // PAGE_SIZE) + (1 if total_count % PAGE_SIZE else 0)
        
        logger.info(
            f"📈 {endpoint}: {total_count:,} records across {total_pages} pages "
            f"(pageSize={PAGE_SIZE})"
        )
        
        self.stats["total_pages"] = total_pages
        
        # Yield records from first page
        for record in first_page.get("records", []):
            self.stats["total_records"] += 1
            yield record
        
        # Fetch remaining pages in parallel batches
        if total_pages > 1:
            for batch_start in range(start_page + 1, total_pages + 1, MAX_PARALLEL_PAGES):
                batch_end = min(batch_start + MAX_PARALLEL_PAGES, total_pages + 1)
                pages = range(batch_start, batch_end)
                
                logger.info(f"⏳ Fetching pages {batch_start}-{batch_end-1}...")
                
                # Fetch batch concurrently
                tasks = [self.fetch_page(endpoint, p) for p in pages]
                results = await asyncio.gather(*tasks)
                
                # Yield records from successful pages
                for page_num, result in zip(pages, results):
                    if result is None:
                        continue
                    
                    for record in result.get("records", []):
                        self.stats["total_records"] += 1
                        yield record
                
                # Progress update
                progress = (batch_end - 1) / total_pages * 100
                logger.info(f"✓ Progress: {progress:.1f}% ({batch_end-1}/{total_pages} pages)")
        
        # Final summary
        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        logger.info(
            f"✅ Extraction complete: {self.stats['total_records']:,} records "
            f"in {elapsed:.2f}s ({self.stats['failed_pages']} failed pages)"
        )
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class WarehouseLoader:
    """
    Loads records into data warehouse.
    
    TODO: Replace with your actual warehouse implementation
    (PostgreSQL, BigQuery, Snowflake, etc.)
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
        # TODO: Initialize database connection
        # self.engine = create_engine(connection_string)
    
    async def bulk_insert(self, table_name: str, records: List[Dict[str, Any]]):
        """
        Bulk insert records into warehouse.
        
        Args:
            table_name: Target table name
            records: List of records to insert
        """
        if not records:
            return
        
        logger.info(f"💾 Loading {len(records):,} records into {table_name}...")
        
        # TODO: Implement actual bulk insert
        # Example for PostgreSQL:
        # async with self.engine.begin() as conn:
        #     await conn.execute(
        #         insert(table).values(records)
        #         .on_conflict_do_update(...)  # Handle duplicates
        #     )
        
        # For now, just log
        logger.info(f"   (Logging only - implement warehouse connection)")
        
        # Optionally save to JSON for testing
        # import json
        # with open(f"output/{table_name}.jsonl", "a") as f:
        #     for record in records:
        #         f.write(json.dumps(record) + "\n")
    
    async def close(self):
        """Close warehouse connection."""
        # TODO: Close database connection
        pass


async def run_etl_for_endpoint(
    endpoint: str,
    table_name: str,
    batch_size: int = 10000
):
    """
    Run complete ETL pipeline for a single endpoint.
    
    Args:
        endpoint: DNB API endpoint name
        table_name: Target warehouse table name
        batch_size: Number of records per batch insert
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Starting ETL: {endpoint} → {table_name}")
    logger.info(f"{'='*60}\n")
    
    extractor = DNBStatisticsExtractor()
    loader = WarehouseLoader(os.getenv("WAREHOUSE_URL"))
    
    try:
        batch = []
        
        async for record in extractor.extract_all_pages(endpoint):
            # Add metadata for auditing
            record["_etl_timestamp"] = datetime.utcnow().isoformat()
            record["_etl_source"] = endpoint
            
            batch.append(record)
            
            # Bulk insert when batch is full
            if len(batch) >= batch_size:
                await loader.bulk_insert(table_name, batch)
                batch.clear()
        
        # Insert remaining records
        if batch:
            await loader.bulk_insert(table_name, batch)
        
        logger.info(f"✅ ETL completed for {endpoint}\n")
    
    except Exception as e:
        logger.error(f"❌ ETL failed for {endpoint}: {e}", exc_info=True)
        raise
    
    finally:
        await extractor.close()
        await loader.close()


async def main():
    """
    Run ETL pipeline for all DNB Statistics endpoints.
    """
    # Define endpoints to extract
    # See: https://api.dnb.nl/statistics/v2024100101/metadata for full list
    endpoints = [
        ("exchange-rates-day", "dnb_exchange_rates_day"),
        ("market-interest-rates-day", "dnb_market_interest_rates_day"),
        # Add more endpoints as needed
        # ("balance-of-payments-quarter", "dnb_balance_of_payments_quarter"),
        # ("credit-institutions-balance-sheet-month", "dnb_credit_institutions_balance_sheet_month"),
    ]
    
    logger.info("=" * 70)
    logger.info("DNB STATISTICS ETL PIPELINE")
    logger.info("=" * 70)
    logger.info(f"Starting at: {datetime.now().isoformat()}")
    logger.info(f"Endpoints to process: {len(endpoints)}")
    logger.info(f"Configuration:")
    logger.info(f"  - Page size: {PAGE_SIZE}")
    logger.info(f"  - Parallel pages: {MAX_PARALLEL_PAGES}")
    logger.info(f"  - Max retries: {MAX_RETRIES}")
    logger.info("=" * 70 + "\n")
    
    overall_start = datetime.now()
    
    for endpoint, table_name in endpoints:
        try:
            await run_etl_for_endpoint(endpoint, table_name)
        except Exception as e:
            logger.error(f"Failed to process {endpoint}: {e}")
            # Continue with next endpoint
            continue
    
    overall_elapsed = (datetime.now() - overall_start).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info(f"✅ PIPELINE COMPLETE")
    logger.info(f"   Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.1f}m)")
    logger.info(f"   Finished at: {datetime.now().isoformat()}")
    logger.info("=" * 70)


if __name__ == "__main__":
    # Ensure logs directory exists
    Path(__file__).parent.parent.parent.joinpath("logs").mkdir(exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  ETL interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {e}", exc_info=True)
        sys.exit(1)
