"""
Base extractor classes for DNB Statistics ETL

Provides reusable infrastructure for paginated API extraction
and Parquet file writing.
"""

from __future__ import annotations

import asyncio
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


class IncompletePageSizeZeroError(RuntimeError):
    """Raised when a pageSize=0 response reports additional pages."""


class BaseExtractor(ABC):
    """
    Base class for all DNB Statistics data extractors.
    
    Provides:
    - HTTP client setup with authentication
    - Rate limiting
    - Output path management
    - Parquet writing
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
            "metadata": {},
            "used_fallback": False,
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

    def _resolve_metadata(self, response: Any) -> Any:
        """Locate the metadata payload on the API response object."""
        if response is None:
            return None

        # Kiota models expose the metadata dataclass via `_metadata`.
        meta_obj = getattr(response, "_metadata", None)
        if meta_obj is not None:
            return meta_obj

        # Fallback to a public attribute just in case future versions rename it.
        meta_obj = getattr(response, "metadata", None)
        if meta_obj is not None:
            return meta_obj

        # Some generators tuck metadata inside `additional_data`.
        additional = getattr(response, "additional_data", None)
        if isinstance(additional, dict):
            return additional.get("_metadata") or additional.get("metadata")

        return None

    def _capture_metadata(self, source: str, metadata_obj: Any) -> dict[str, Any]:
        """Record response metadata details for diagnostics."""
        info: dict[str, Any] = {}

        if metadata_obj is None:
            info = {}
        elif isinstance(metadata_obj, dict):
            # Support raw dict payloads (e.g. additional_data)
            info = {
                "page": metadata_obj.get("page"),
                "page_size": (
                    metadata_obj.get("page_size")
                    or metadata_obj.get("pageSize")
                ),
                "has_more_pages": (
                    metadata_obj.get("has_more_pages")
                    or metadata_obj.get("hasMorePages")
                ),
                "total_count": (
                    metadata_obj.get("total_count")
                    or metadata_obj.get("totalCount")
                ),
            }
        else:
            info = {
                "page": getattr(metadata_obj, "page", None),
                "page_size": getattr(metadata_obj, "page_size", None),
                "has_more_pages": getattr(metadata_obj, "has_more_pages", None),
                "total_count": getattr(metadata_obj, "total_count", None),
            }

        self.stats.setdefault("metadata", {})[source] = info
        return info
    
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
            
            # Prepare output path
            bronze_path = config.get_output_path(
                "bronze",
                self.get_category(),
                self.get_output_filename(),
            )
            
            # Clear existing file (fresh extraction)
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
                    await self._write_parquet(batch, bronze_path, append=True)
                    
                    logger.info(
                        f"  ✓ Processed {self.stats['total_records']:,} records"
                    )
                    batch.clear()
            
            # Write remaining records
            if batch:
                await self._write_parquet(batch, bronze_path, append=True)
            
            self.stats["end_time"] = datetime.now()
            elapsed = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            
            logger.info(
                f"{safe_emoji('✅')} Extraction complete: {self.stats['total_records']:,} records "
                f"in {elapsed:.2f}s"
            )
            logger.info(f"  Parquet: {bronze_path}")
            
            return self.stats
        
        except Exception as exc:
            logger.error(f"{safe_emoji('❌')} Extraction failed: {exc}", exc_info=True)
            raise
        
        finally:
            await self.close()


class PaginatedExtractor(BaseExtractor):
    """
    Extractor for DNB Statistics endpoints using Kiota client.
    
    The Statistics API supports pageSize=0 to fetch ALL records in a single request,
    which is much more efficient than pagination. This is the default behavior.
    
    Handles:
    - Single-request extraction with pageSize=0 (default)
    - Fallback to pagination if needed
    - Rate limiting and progress tracking
    """
    
    async def extract_from_endpoint(
        self,
        endpoint_path: str,
        query_params: Optional[dict[str, Any]] = None,
        from_date: Optional[str] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extract data from a DNB Statistics endpoint.
        
        Uses pageSize=0 to fetch all records in a single request (Statistics API feature).
        Automatically switches to pagination if we hit the 2000 record limit.
        
        Args:
            endpoint_path: Kiota client endpoint path
            query_params: Additional query parameters
            from_date: Optional date filter for incremental updates (ISO format: YYYY-MM-DD)
        """
        # Import from the wrapper module that handles the hyphenated directory
        from backend.clients.statistics_client import DnbStatisticsClient
        
        await self._init_client()
        
        client = DnbStatisticsClient(self.request_adapter)
        
        # Get the endpoint request builder
        endpoint_builder = getattr(client, endpoint_path)
        if endpoint_builder is None:
            raise ValueError(f"Unknown endpoint: {endpoint_path}")
        
        # Strategy 1: Try to fetch ALL records at once with pageSize=0
        if from_date:
            logger.info(
                f"{safe_emoji('📊')} Fetching records from {from_date} onwards "
                "(incremental update)..."
            )
        else:
            logger.info(
                f"{safe_emoji('📊')} Fetching ALL records with pageSize=0 "
                "(Statistics API feature)..."
            )
        
        await self._rate_limit()
        
        # Configure request with pageSize=0 to get all records
        config_obj = RequestConfiguration()
        config_obj.headers = HeadersCollection()
        config_obj.headers.try_add("Ocp-Apim-Subscription-Key", config.DNB_API_KEY)
        config_obj.headers.try_add("Accept", "application/json")
        config_obj.query_parameters = {}
        config_obj.query_parameters["page"] = 1
        config_obj.query_parameters["pageSize"] = config.DEFAULT_PAGE_SIZE  # 0 = all records
        
        # Add date filter if provided (for incremental updates)
        if from_date:
            config_obj.query_parameters["fromDate"] = from_date
        
        # Add any additional query params
        if query_params:
            config_obj.query_parameters.update(query_params)
        
        try:
            response = await endpoint_builder.get(config_obj)
            
            if not response:
                logger.warning("No data returned from endpoint")
                return
            
            # Check if we got records
            if hasattr(response, "records") and response.records:
                record_count = len(response.records)

                metadata_obj = self._resolve_metadata(response)
                metadata_info = self._capture_metadata(
                    "page_size_zero",
                    metadata_obj,
                )

                has_more_pages = metadata_info.get("has_more_pages")
                total_count = metadata_info.get("total_count")
                page_size = metadata_info.get("page_size")

                if metadata_info:
                    logger.debug(
                        "Metadata (pageSize=0 attempt): page=%s, page_size=%s, total_count=%s, has_more_pages=%s",
                        metadata_info.get("page"),
                        page_size,
                        total_count,
                        has_more_pages,
                    )

                if has_more_pages:
                    raise IncompletePageSizeZeroError(
                        "pageSize=0 response reports additional pages; refusing to proceed with partial dataset"
                    )
                
                # Success - got all records with pageSize=0
                # Note: The API with pageSize=0 returns ALL records in one shot.
                # We trust the API response regardless of count.
                logger.info(
                    f"{safe_emoji('✅')} Successfully fetched {record_count:,} records "
                    "in a single request!"
                )
                
                # Yield all records
                for record in response.records:
                    yield self._serialize_record(record)
                
                self.stats["total_pages"] = 1
                self.stats["is_complete"] = True
                return
            else:
                logger.warning("No records in response")
                return
                
        except Exception as exc:
            logger.warning(
                f"{safe_emoji('⚠️')} pageSize=0 failed: {exc}. "
                f"Falling back to pagination with pageSize={config.FALLBACK_PAGE_SIZE}..."
            )
            self.stats["used_fallback"] = True
            
            # Strategy 2: Fall back to traditional pagination
            async for record in self._paginated_extraction(endpoint_builder, query_params):
                yield record
    
    async def _paginated_extraction(
        self,
        endpoint_builder,
        query_params: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Fallback pagination strategy if pageSize=0 doesn't work.
        
        This method implements traditional page-by-page fetching.
        """
        logger.info(f"{safe_emoji('📊')} Using fallback pagination strategy...")
        
        await self._rate_limit()
        
        # Configure request with fallback page size (not 0, but actual limit)
        config_obj = RequestConfiguration()
        config_obj.headers = HeadersCollection()
        config_obj.headers.try_add("Ocp-Apim-Subscription-Key", config.DNB_API_KEY)
        config_obj.headers.try_add("Accept", "application/json")
        config_obj.query_parameters = {}
        config_obj.query_parameters["page"] = 1
        config_obj.query_parameters["pageSize"] = config.FALLBACK_PAGE_SIZE  # Use 2000, not 0
        
        first_response = await endpoint_builder.get(config_obj)
        
        if not first_response:
            logger.warning("No data returned from endpoint")
            return
        
        # Extract metadata
        metadata_obj = self._resolve_metadata(first_response)
        fallback_metadata = self._capture_metadata(
            "fallback_page_1",
            metadata_obj,
        )
        if fallback_metadata:
            logger.debug(
                "Metadata (fallback page 1): page=%s, page_size=%s, total_count=%s, has_more_pages=%s",
                fallback_metadata.get("page"),
                fallback_metadata.get("page_size"),
                fallback_metadata.get("total_count"),
                fallback_metadata.get("has_more_pages"),
            )

        total_count = fallback_metadata.get("total_count", 0)
        
        # Check if first page has records
        first_page_records = []
        if hasattr(first_response, "records") and first_response.records:
            first_page_records = first_response.records
        
        if not first_page_records:
            logger.warning("No records in first page")
            return
        
        # Since API doesn't provide total_count, we'll paginate until we get an empty page
        if total_count == 0:
            logger.warning(
                f"{safe_emoji('⚠️')} Total count unavailable from API - "
                "will fetch all pages until empty"
            )
            
            # Yield records from first page
            for record in first_page_records:
                yield self._serialize_record(record)
            
            # Continue fetching pages until we get no records
            page_num = 2
            while True:
                logger.info(f"Fetching page {page_num}...")
                
                await self._rate_limit()
                
                try:
                    config_obj = RequestConfiguration()
                    config_obj.headers = HeadersCollection()
                    config_obj.headers.try_add("Ocp-Apim-Subscription-Key", config.DNB_API_KEY)
                    config_obj.headers.try_add("Accept", "application/json")
                    config_obj.query_parameters = {}
                    config_obj.query_parameters["page"] = page_num
                    config_obj.query_parameters["pageSize"] = config.FALLBACK_PAGE_SIZE  # Use 2000 for pagination
                    
                    response = await endpoint_builder.get(config_obj)
                    
                    if not response or not hasattr(response, "records") or not response.records:
                        logger.info(
                            f"{safe_emoji('✅')} Reached end of data at page {page_num - 1}"
                        )
                        break
                    
                    record_count = len(response.records)
                    for record in response.records:
                        yield self._serialize_record(record)
                    
                    logger.info(f"  Page {page_num}: {record_count} records")
                    
                    # If we got fewer records than page size, we're probably at the end
                    if record_count < config.FALLBACK_PAGE_SIZE:
                        logger.info(
                            f"{safe_emoji('✅')} Last page (partial): {record_count} records"
                        )
                        break
                    
                    page_num += 1
                    self.stats["total_pages"] = page_num
                
                except Exception as exc:
                    logger.error(f"Failed to fetch page {page_num}: {exc}")
                    self.stats["failed_pages"] += 1
                    break
            
            return
        
        # If we have total_count, use traditional pagination
        total_pages = (total_count // config.FALLBACK_PAGE_SIZE) + (
            1 if total_count % config.FALLBACK_PAGE_SIZE else 0
        )
        
        logger.info(
            f"Total: {total_count:,} records across {total_pages} pages "
            f"(pageSize={config.FALLBACK_PAGE_SIZE})"
        )
        
        self.stats["total_pages"] = total_pages
        
        # Yield records from first page
        for record in first_page_records:
            yield self._serialize_record(record)
        
        # Fetch remaining pages
        if total_pages > 1:
            for page_num in range(2, total_pages + 1):
                logger.info(f"Fetching page {page_num}/{total_pages}...")
                
                await self._rate_limit()
                
                try:
                    config_obj = RequestConfiguration()
                    config_obj.headers = HeadersCollection()
                    config_obj.headers.try_add("Ocp-Apim-Subscription-Key", config.DNB_API_KEY)
                    config_obj.headers.try_add("Accept", "application/json")
                    config_obj.query_parameters = {}
                    config_obj.query_parameters["page"] = page_num
                    config_obj.query_parameters["pageSize"] = config.FALLBACK_PAGE_SIZE  # Use 2000 for pagination
                    
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
                logger.info(f"  ✓ Progress: {progress:.1f}% ({page_num}/{total_pages} pages)")
    
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
