"""
Base classes and utilities for DNB Public Register ETL

Provides shared functionality for API interaction, rate limiting,
error handling, and data persistence.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Optional

import httpx
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_abstractions.authentication import AnonymousAuthenticationProvider

from . import config

# Configure logger
logger = logging.getLogger(__name__)


# ==========================================
# Rate Limiter
# ==========================================

class RateLimiter:
  """
  Token bucket rate limiter for API calls.
  
  Ensures we stay under DNB's 30 calls/minute limit with safety buffer.
  """
  
  def __init__(
      self,
      calls_per_period: int = config.RATE_LIMIT_CALLS,
      period_seconds: float = config.RATE_LIMIT_PERIOD,
      buffer_factor: float = config.RATE_LIMIT_BUFFER,
  ):
    # Apply safety buffer (e.g., 30 calls → 25 calls)
    self.max_calls = int(calls_per_period / buffer_factor)
    self.period = period_seconds
    self.tokens = self.max_calls
    self.last_refill = time.monotonic()
    self.lock = asyncio.Lock()
  
  async def acquire(self) -> None:
    """Wait until a token is available, then consume it."""
    async with self.lock:
      await self._refill()
      
      while self.tokens <= 0:
        # Wait until next refill
        elapsed = time.monotonic() - self.last_refill
        wait_time = self.period - elapsed
        if wait_time > 0:
          logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s...")
          await asyncio.sleep(wait_time)
        await self._refill()
      
      self.tokens -= 1
  
  async def _refill(self) -> None:
    """Refill tokens based on elapsed time."""
    now = time.monotonic()
    elapsed = now - self.last_refill
    
    if elapsed >= self.period:
      self.tokens = self.max_calls
      self.last_refill = now
      logger.debug(f"Rate limit refilled: {self.tokens} tokens")


# ==========================================
# Base Extractor
# ==========================================

class BaseExtractor(ABC):
  """
  Abstract base class for DNB Public Register endpoint extractors.
  
  Provides:
  - Kiota HTTP client with rate limiting
  - Retry logic with exponential backoff
  - Pagination support
  - Progress tracking
  - Data persistence to Parquet
  """
  
  def __init__(self):
    self.rate_limiter = RateLimiter()
    self.http_client = httpx.AsyncClient(
        timeout=config.REQUEST_TIMEOUT,
        headers={
            "Ocp-Apim-Subscription-Key": config.DNB_API_KEY,
            "Accept": "application/json",
        },
    )
    
    # Initialize Kiota request adapter
    auth_provider = AnonymousAuthenticationProvider()
    self.request_adapter: RequestAdapter = HttpxRequestAdapter(
        authentication_provider=auth_provider,
        http_client=self.http_client,
    )
    self.request_adapter.base_url = config.DNB_BASE_URL
    
    # Stats tracking
    self.stats = {
        "start_time": None,
        "end_time": None,
        "total_records": 0,
        "total_pages": 0,
        "failed_pages": 0,
        "api_calls": 0,
    }
  
  @abstractmethod
  async def extract(self) -> AsyncIterator[dict[str, Any]]:
    """
    Extract data from the endpoint.
    
    Yields:
        Individual records as dictionaries
    """
    pass
  
  @abstractmethod
  def get_output_filename(self) -> str:
    """
    Generate output filename for this extraction.
    
    Returns:
        Filename without extension
    """
    pass
  
  @abstractmethod
  def get_category(self) -> str:
    """
    Get data category for this extractor.
    
    Returns:
        Category name (e.g., 'metadata', 'entities')
    """
    pass
  
  async def fetch_with_retry(
      self,
      url: str,
      params: Optional[dict[str, Any]] = None,
      retry_count: int = 0,
  ) -> Optional[dict[str, Any]]:
    """
    Fetch from API with retry logic and rate limiting.
    
    Args:
        url: Full API URL
        params: Query parameters
        retry_count: Current retry attempt
    
    Returns:
        Response JSON or None if all retries failed
    """
    await self.rate_limiter.acquire()
    self.stats["api_calls"] += 1
    
    try:
      response = await self.http_client.get(url, params=params or {})
      response.raise_for_status()
      return response.json()
    
    except httpx.HTTPStatusError as exc:
      if exc.response.status_code == 429:  # Rate limit
        wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
        logger.warning(
            f"Rate limited (429), waiting {wait_time:.1f}s... "
            f"(retry {retry_count + 1}/{config.MAX_RETRIES})"
        )
        await asyncio.sleep(wait_time)
        
        if retry_count < config.MAX_RETRIES:
          return await self.fetch_with_retry(url, params, retry_count + 1)
      
      elif exc.response.status_code >= 500:  # Server error
        if retry_count < config.MAX_RETRIES:
          wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
          logger.warning(
              f"Server error {exc.response.status_code}, "
              f"retrying in {wait_time:.1f}s..."
          )
          await asyncio.sleep(wait_time)
          return await self.fetch_with_retry(url, params, retry_count + 1)
      
      logger.error(f"HTTP {exc.response.status_code}: {exc.response.text}")
      self.stats["failed_pages"] += 1
      return None
    
    except Exception as exc:
      logger.error(f"Request failed: {exc}")
      
      if retry_count < config.MAX_RETRIES:
        wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
        await asyncio.sleep(wait_time)
        return await self.fetch_with_retry(url, params, retry_count + 1)
      
      self.stats["failed_pages"] += 1
      return None
  
  async def call_api_with_retry(
      self,
      api_call_func,
      retry_count: int = 0,
  ):
    """
    Execute Kiota API call with rate limiting and retry logic.
    
    Args:
        api_call_func: Async function that makes the API call
        retry_count: Current retry attempt
    
    Returns:
        API response or raises exception if all retries failed
    """
    await self.rate_limiter.acquire()
    self.stats["api_calls"] += 1
    
    try:
      return await api_call_func()
    
    except Exception as exc:
      # Check if it's a rate limit error (429)
      if hasattr(exc, 'response_status_code') and exc.response_status_code == 429:
        wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
        logger.warning(
            f"⏳ Rate limited (429), waiting {wait_time:.1f}s... "
            f"(retry {retry_count + 1}/{config.MAX_RETRIES})"
        )
        await asyncio.sleep(wait_time)
        
        if retry_count < config.MAX_RETRIES:
          return await self.call_api_with_retry(api_call_func, retry_count + 1)
        else:
          logger.error(f"❌ Max retries exceeded for rate limit")
          raise
      
      # Check if it's a server error (500+)
      elif hasattr(exc, 'response_status_code') and exc.response_status_code >= 500:
        if retry_count < config.MAX_RETRIES:
          wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
          logger.warning(
              f"Server error {exc.response_status_code}, "
              f"retrying in {wait_time:.1f}s..."
          )
          await asyncio.sleep(wait_time)
          return await self.call_api_with_retry(api_call_func, retry_count + 1)
        else:
          logger.error(f"❌ Max retries exceeded for server error")
          raise
      
      # For other errors, retry a few times
      elif retry_count < config.MAX_RETRIES:
        wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
        logger.warning(
            f"API call failed: {exc}, retrying in {wait_time:.1f}s..."
        )
        await asyncio.sleep(wait_time)
        return await self.call_api_with_retry(api_call_func, retry_count + 1)
      
      # All retries exhausted
      logger.error(f"❌ API call failed after {retry_count + 1} attempts: {exc}")
      raise
  
  def add_etl_metadata(self, record: dict[str, Any]) -> dict[str, Any]:
    """
    Add ETL metadata fields to a record.
    
    Args:
        record: Original data record
    
    Returns:
        Record with added metadata fields
    """
    record["_etl_extracted_at"] = datetime.utcnow().isoformat()
    record["_etl_extractor"] = self.__class__.__name__
    return record
  
  async def save_to_parquet(
      self,
      records: list[dict[str, Any]],
      stage: str = "bronze",
  ) -> Path:
    """
    Save records to Parquet file.
    
    Args:
        records: List of records to save
        stage: Data stage ('fetch', 'bronze', 'silver', 'gold')
    
    Returns:
        Path to saved file
    """
    if not records:
      logger.warning("No records to save")
      return None
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Generate output path
    output_path = config.get_output_path(
        stage=stage,
        category=self.get_category(),
        filename=self.get_output_filename(),
    )
    
    # Write to Parquet
    logger.info(f"💾 Writing {len(records):,} records to {output_path.name}")
    
    table = pa.Table.from_pandas(df)
    pq.write_table(
        table,
        output_path,
        compression=config.PARQUET_COMPRESSION,
        row_group_size=config.PARQUET_ROW_GROUP_SIZE,
    )
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"✅ Saved {file_size_mb:.2f} MB to {output_path}")
    
    return output_path
  
  async def run(self, save_to_disk: bool = True) -> dict[str, Any]:
    """
    Execute the full extraction pipeline.
    
    Args:
        save_to_disk: Whether to save results to Parquet
    
    Returns:
        Extraction statistics
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Starting: {self.__class__.__name__}")
    logger.info(f"{'='*60}\n")
    
    self.stats["start_time"] = datetime.now()
    records = []
    
    try:
      async for record in self.extract():
        records.append(self.add_etl_metadata(record))
        self.stats["total_records"] += 1
      
      if save_to_disk and records:
        await self.save_to_parquet(records, stage="bronze")
      
      self.stats["end_time"] = datetime.now()
      elapsed = (
          self.stats["end_time"] - self.stats["start_time"]
      ).total_seconds()
      
      logger.info(f"\n{'='*60}")
      logger.info(f"✅ Completed: {self.__class__.__name__}")
      logger.info(f"   Records: {self.stats['total_records']:,}")
      logger.info(f"   API calls: {self.stats['api_calls']}")
      logger.info(f"   Failed: {self.stats['failed_pages']}")
      logger.info(f"   Duration: {elapsed:.2f}s")
      logger.info(f"{'='*60}\n")
      
      return self.stats
    
    except Exception as exc:
      logger.error(f"❌ Extraction failed: {exc}", exc_info=True)
      raise
    
    finally:
      await self.close()
  
  async def close(self):
    """Clean up resources."""
    await self.http_client.aclose()


# ==========================================
# Paginated Extractor
# ==========================================

class PaginatedExtractor(BaseExtractor):
  """
  Base extractor for paginated endpoints.
  
  Automatically handles pagination with configurable page size.
  """
  
  async def fetch_page(
      self,
      url: str,
      page: int,
      page_size: int = config.DEFAULT_PAGE_SIZE,
      extra_params: Optional[dict[str, Any]] = None,
  ) -> Optional[dict[str, Any]]:
    """
    Fetch a single page.
    
    Args:
        url: API endpoint URL
        page: Page number (1-indexed)
        page_size: Records per page
        extra_params: Additional query parameters
    
    Returns:
        Page response or None if failed
    """
    params = {
        "page": page,
        "pageSize": page_size,
    }
    if extra_params:
      params.update(extra_params)
    
    logger.debug(f"Fetching page {page} (pageSize={page_size})...")
    return await self.fetch_with_retry(url, params)
  
  async def extract_paginated(
      self,
      url: str,
      page_size: int = config.DEFAULT_PAGE_SIZE,
      extra_params: Optional[dict[str, Any]] = None,
      record_key: str = "records",
  ) -> AsyncIterator[dict[str, Any]]:
    """
    Extract all records from a paginated endpoint.
    
    Handles pagination by continuing to fetch pages until an empty response is received,
    since the DNB API doesn't always provide reliable total count metadata.
    
    Args:
        url: API endpoint URL
        page_size: Records per page
        extra_params: Additional query parameters
        record_key: JSON key containing records (default: 'records')
    
    Yields:
        Individual records
    """
    page = config.DEFAULT_START_PAGE
    
    while True:
      response = await self.fetch_page(url, page, page_size, extra_params)
      
      if not response:
        logger.warning(f"⚠️ Failed to fetch page {page}, stopping pagination")
        break
      
      # Extract records (API structure varies)
      records = response.get(record_key, [])
      if not records:
        # Try alternative structures
        if isinstance(response, list):
          records = response
        else:
          logger.info(f"✅ No more records at page {page} - pagination complete")
          break
      
      record_count = len(records)
      
      for record in records:
        yield record
      
      # Check pagination metadata if available
      pagination = response.get("pagination", {})
      total_pages = pagination.get("totalPages")
      
      if total_pages:
        self.stats["total_pages"] = total_pages
        logger.info(
            f"📄 Page {page}/{total_pages}: "
            f"{record_count} records ({self.stats['total_records'] + record_count} total)"
        )
        
        # Stop if we've reached the last page
        if page >= total_pages:
          logger.info(f"✅ Reached last page {page}/{total_pages}")
          break
      else:
        # No pagination metadata - rely on empty response detection
        logger.info(
            f"📄 Page {page}: {record_count} records "
            f"({self.stats['total_records'] + record_count} total)"
        )
        
        # If we got fewer records than page size, likely the last page
        if record_count < page_size:
          logger.info(
              f"✅ Last page (partial): {record_count} records "
              f"(less than pageSize={page_size})"
          )
          break
      
      page += 1
