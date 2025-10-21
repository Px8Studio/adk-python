"""
Base extractor classes for DNB Statistics ETL

Provides reusable infrastructure for paginated API extraction
and Parquet file writing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Optional, AsyncGenerator

import pandas as pd
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_abstractions.authentication import AnonymousAuthenticationProvider
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.headers_collection import HeadersCollection
import httpx

from . import config

logger = logging.getLogger(__name__)

def setup_console_encoding():
  """Configure console to handle UTF-8 on Windows."""
  if sys.platform == 'win32':
    try:
      sys.stdout.reconfigure(encoding='utf-8')
      sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
      # Python < 3.7
      import codecs
      sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
      sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Call at module level
setup_console_encoding()

# Replace emoji usage with ASCII fallbacks
EMOJI_MAP = {
  '🚀': '[START]',
  '📊': '[FETCH]',
  '✅': '[SUCCESS]',
  '❌': '[ERROR]',
  '⚠️': '[WARNING]',
}

def safe_emoji(emoji: str) -> str:
  """Return emoji or ASCII fallback for Windows console."""
  if sys.platform == 'win32':
    return EMOJI_MAP.get(emoji, emoji)
  return emoji


class BaseExtractor(ABC):
    """
    Base class for all DNB Statistics data extractors.
    
    Provides:
    - HTTP client setup with authentication
    - Rate limiting
    - Output path management
    - JSONL and Parquet writing
    - Error handling and retry logic
    """
    
    def __init__(self):
        self.request_adapter: RequestAdapter | None = None
        self.stats = {
            "total_records": 0,
            "total_pages": 0,
            "failed_pages": 0,
            "start_time": None,
            "end_time": None,
        }
        self._rate_limiter = asyncio.Semaphore(config.RATE_LIMIT_CALLS)
        self._last_request_time = 0.0
    
    @abstractmethod
    def get_category(self) -> str:
        """Return the data category for this extractor."""
        pass
    
    @abstractmethod
    def get_output_filename(self) -> str:
        """Return the base filename (without extension)."""
        pass
    
    @abstractmethod
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """
        Extract records from the API.
        
        Yields:
            Individual records as dictionaries
        """
        pass
    
    async def _init_client(self) -> None:
        """Initialize the HTTP client with authentication."""
        if self.request_adapter is not None:
            return
        
        # Debug: Verify API key is loaded
        if not config.DNB_API_KEY:
            logger.error(f"{safe_emoji('❌')} DNB_API_KEY is empty! Check your .env file.")
            raise ValueError("DNB_API_KEY not configured")
        
        logger.debug(f"Using DNB API key: {config.DNB_API_KEY[:8]}...{config.DNB_API_KEY[-4:]}")
        
        # Create HTTP client
        http_client = httpx.AsyncClient(
            timeout=config.REQUEST_TIMEOUT,
        )
        
        # Create Kiota request adapter with authentication provider
        auth_provider = AnonymousAuthenticationProvider()
        self.request_adapter = HttpxRequestAdapter(auth_provider)
        self.request_adapter._http_client = http_client
        
        # Set base URL - required for Kiota client
        self.request_adapter.base_url = config.DNB_BASE_URL
    
    async def _rate_limit(self) -> None:
        """Apply rate limiting to API calls."""
        async with self._rate_limiter:
            # Calculate minimum time between requests
            min_interval = config.RATE_LIMIT_PERIOD / config.RATE_LIMIT_CALLS
            min_interval *= config.RATE_LIMIT_BUFFER  # Add safety margin
            
            # Wait if needed
            now = asyncio.get_event_loop().time()
            time_since_last = now - self._last_request_time
            
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self._last_request_time = asyncio.get_event_loop().time()
    
    async def close(self):
        """Close the HTTP client connection."""
        if self.request_adapter and hasattr(self.request_adapter, '_http_client'):
            # Access the private _http_client attribute directly
            await self.request_adapter._http_client.aclose()
            self.request_adapter = None
    
    def _add_metadata(self, record: dict[str, Any]) -> dict[str, Any]:
        """Add ETL metadata to a record."""
        record["_etl_timestamp"] = datetime.utcnow().isoformat()
        record["_etl_source"] = self.get_output_filename()
        return record
    
    async def _write_jsonl(self, records: list[dict[str, Any]], path: Path) -> None:
        """Write records to JSONL file (append mode)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "a", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
    
    async def _write_parquet(
        self,
        records: list[dict[str, Any]],
        path: Path,
        append: bool = False,
    ) -> None:
        """Write records to Parquet file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if not records:
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Write Parquet
        if append and path.exists():
            # Append to existing file
            existing_df = pd.read_parquet(path, engine=config.PARQUET_ENGINE)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_parquet(
            path,
            engine=config.PARQUET_ENGINE,
            compression=config.PARQUET_COMPRESSION,
            index=False,
        )
    
    async def run(self) -> dict[str, Any]:
        """
        Run the complete extraction pipeline.
        
        Returns:
            Statistics about the extraction
        """
        self.stats["start_time"] = datetime.now()
        
        logger.info(f"{safe_emoji('🚀')} Starting extraction: {self.get_output_filename()}")
        
        try:
            await self._init_client()
            
            # Prepare output paths
            fetch_path = config.get_output_path(
                "fetch",
                self.get_category(),
                self.get_output_filename(),
            )
            bronze_path = config.get_output_path(
                "bronze",
                self.get_category(),
                self.get_output_filename(),
            )
            
            # Clear existing files (fresh extraction)
            if fetch_path.exists():
                fetch_path.unlink()
            if bronze_path.exists():
                bronze_path.unlink()
            
            # Collect records in batches
            batch: list[dict[str, Any]] = []
            
            async for record in self.extract():
                # Add metadata
                record = self._add_metadata(record)
                batch.append(record)
                self.stats["total_records"] += 1
                
                # Write batch when full
                if len(batch) >= config.BATCH_SIZE:
                    await self._write_jsonl(batch, fetch_path)
                    await self._write_parquet(batch, bronze_path, append=True)
                    
                    logger.info(
                        f"  ✓ Processed {self.stats['total_records']:,} records"
                    )
                    batch.clear()
            
            # Write remaining records
            if batch:
                await self._write_jsonl(batch, fetch_path)
                await self._write_parquet(batch, bronze_path, append=True)
            
            self.stats["end_time"] = datetime.now()
            elapsed = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            
            logger.info(
                f"{safe_emoji('✅')} Extraction complete: {self.stats['total_records']:,} records "
                f"in {elapsed:.2f}s"
            )
            logger.info(f"  JSONL: {fetch_path}")
            logger.info(f"  Parquet: {bronze_path}")
            
            return self.stats
        
        except Exception as exc:
            logger.error(f"{safe_emoji('❌')} Extraction failed: {exc}", exc_info=True)
            raise
        
        finally:
            await self.close()


class PaginatedExtractor(BaseExtractor):
    """
    Extractor for paginated DNB Statistics endpoints using Kiota client.
    
    Handles:
    - Automatic pagination with page/pageSize parameters
    - Parallel page fetching with rate limiting
    - Progress tracking
    """
    
    async def extract_from_endpoint(
        self,
        endpoint_path: str,
        query_params: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Generic method to extract data from a DNB Statistics endpoint."""
        # Import from the wrapper module that handles the hyphenated directory
        from backend.clients.statistics_client import DnbStatisticsClient
        
        await self._init_client()
        
        client = DnbStatisticsClient(self.request_adapter)
        
        # Get the endpoint request builder
        endpoint_builder = getattr(client, endpoint_path)
        if endpoint_builder is None:
            raise ValueError(f"Unknown endpoint: {endpoint_path}")
        
        # Fetch first page to get total count
        logger.info(f"{safe_emoji('📊')} Fetching first page...")
        
        await self._rate_limit()
        
        # Configure request with pagination and authentication header
        config_obj = RequestConfiguration()
        config_obj.headers = HeadersCollection()
        config_obj.headers.try_add("Ocp-Apim-Subscription-Key", config.DNB_API_KEY)
        config_obj.headers.try_add("Accept", "application/json")
        config_obj.query_parameters = {}
        config_obj.query_parameters["page"] = 1
        config_obj.query_parameters["pageSize"] = config.DEFAULT_PAGE_SIZE
        
        first_response = await endpoint_builder.get(config_obj)
        
        if not first_response:
            logger.warning("No data returned from endpoint")
            return
        
        # Extract metadata
        metadata = first_response.metadata if hasattr(first_response, "metadata") else None
        total_count = metadata.total_count if metadata and hasattr(metadata, "total_count") else 0
        
        if total_count == 0:
            logger.warning("Total count is 0, using records from first page only")
            # Yield records from first page
            if hasattr(first_response, "records") and first_response.records:
                for record in first_response.records:
                    yield self._serialize_record(record)
            return
        
        total_pages = (total_count // config.DEFAULT_PAGE_SIZE) + (
            1 if total_count % config.DEFAULT_PAGE_SIZE else 0
        )
        
        logger.info(
            f"📈 Total: {total_count:,} records across {total_pages} pages "
            f"(pageSize={config.DEFAULT_PAGE_SIZE})"
        )
        
        self.stats["total_pages"] = total_pages
        
        # Yield records from first page
        if hasattr(first_response, "records") and first_response.records:
            for record in first_response.records:
                yield self._serialize_record(record)
        
        # Fetch remaining pages
        if total_pages > 1:
            for page_num in range(2, total_pages + 1):
                logger.info(f"⏳ Fetching page {page_num}/{total_pages}...")
                
                await self._rate_limit()
                
                try:
                    config_obj = RequestConfiguration()
                    config_obj.headers = HeadersCollection()
                    config_obj.headers.try_add("Ocp-Apim-Subscription-Key", config.DNB_API_KEY)
                    config_obj.headers.try_add("Accept", "application/json")
                    config_obj.query_parameters = {}
                    config_obj.query_parameters["page"] = page_num
                    config_obj.query_parameters["pageSize"] = config.DEFAULT_PAGE_SIZE
                    
                    response = await endpoint_builder.get(config_obj)
                    
                    if response and hasattr(response, "records") and response.records:
                        for record in response.records:
                            yield self._serialize_record(record)
                
                except Exception as exc:
                    logger.error(f"Failed to fetch page {page_num}: {exc}")
                    self.stats["failed_pages"] += 1
                    continue
                
                # Progress update
                progress = page_num / total_pages * 100
                logger.info(f"✓ Progress: {progress:.1f}% ({page_num}/{total_pages} pages)")
    
    def _serialize_record(self, record: Any) -> dict[str, Any]:
        """
        Convert a Kiota model object to a plain dictionary.
        
        Args:
            record: Kiota model object
        
        Returns:
            Dictionary representation with all values JSON-serializable
        """
        def make_serializable(obj):
            """Convert object to JSON-serializable format."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return {k: make_serializable(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
            else:
                return obj
        
        if hasattr(record, "to_dict"):
            result = record.to_dict()
            result = make_serializable(result)
        elif hasattr(record, "__dict__"):
            # Convert object attributes to dict
            result = {}
            for key, value in record.__dict__.items():
                if not key.startswith("_"):
                    result[key] = make_serializable(value)
        else:
            # Already a dict or primitive
            result = make_serializable(record)
        
        # Remove Kiota-specific metadata fields that cause Parquet issues
        if isinstance(result, dict):
            result.pop("additional_data", None)
            result.pop("backing_store", None)
        
        return result
