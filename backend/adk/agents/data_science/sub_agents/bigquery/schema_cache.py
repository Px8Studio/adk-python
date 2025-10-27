# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Schema caching for BigQuery datasets to reduce startup time.

Cache Invalidation Strategies:
------------------------------

1. Time-based (TTL):
   - Default: 24 hours
   - Configure: SCHEMA_CACHE_TTL_HOURS environment variable
   - Use case: Automatic expiration for development/testing

2. Manual force refresh:
   - Set FORCE_SCHEMA_REFRESH=true to bypass cache
   - Use case: After known schema changes (migrations, new columns)

3. Version-based:
   - Set SCHEMA_VERSION environment variable (e.g., "v2.1")
   - Cache is invalidated when version changes
   - Use case: Deployments with schema migrations

4. Manual clear:
   - Run: python -m backend.adk.agents.data_science.sub_agents.bigquery.clear_cache
   - Use case: Troubleshooting stale cache issues

Best Practices:
---------------
- Development: Use short TTL (1-6 hours) or FORCE_SCHEMA_REFRESH=true
- Production: Use longer TTL (24 hours) with SCHEMA_VERSION for deployments
- CI/CD: Clear cache or bump SCHEMA_VERSION after schema migrations
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

# In-memory cache
_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}

# Cache expiration time (24 hours by default)
CACHE_TTL_HOURS = int(os.getenv("SCHEMA_CACHE_TTL_HOURS", "24"))

# Cache directory
CACHE_DIR = Path(os.getenv("SCHEMA_CACHE_DIR", "./.cache/bigquery_schemas"))


def _get_cache_file_path(cache_key: str) -> Path:
  """Get the file path for a cache key.
  
  Args:
    cache_key: Unique identifier for the cached schema
    
  Returns:
    Path to cache file
  """
  # Create cache directory if it doesn't exist
  CACHE_DIR.mkdir(parents=True, exist_ok=True)
  
  # Sanitize cache key for filename
  safe_key = cache_key.replace("/", "_").replace(":", "_")
  return CACHE_DIR / f"{safe_key}.json"


def _is_cache_valid(cache_data: dict[str, Any]) -> bool:
  """Check if cached data is still valid based on TTL and schema version.
  
  Args:
    cache_data: Cached schema data with metadata
    
  Returns:
    True if cache is still valid, False otherwise
  """
  if "cached_at" not in cache_data:
    return False
  
  # Check TTL expiration
  cached_at = datetime.fromisoformat(cache_data["cached_at"])
  expiry = cached_at + timedelta(hours=CACHE_TTL_HOURS)
  
  if datetime.now() >= expiry:
    _logger.info("Cache expired (TTL)")
    return False
  
  # Check if environment variable forces cache refresh
  if os.getenv("FORCE_SCHEMA_REFRESH", "").lower() == "true":
    _logger.info("FORCE_SCHEMA_REFRESH enabled - invalidating cache")
    return False
  
  # Check schema version (if provided)
  expected_version = os.getenv("SCHEMA_VERSION")
  if expected_version:
    cached_version = cache_data.get("schema_version")
    if cached_version != expected_version:
      _logger.info(
          "Schema version mismatch: cached=%s, expected=%s",
          cached_version,
          expected_version,
      )
      return False
  
  return True


def get_cached_schema(cache_key: str) -> dict[str, Any] | None:
  """Retrieve schema from cache if available and valid.
  
  Args:
    cache_key: Unique identifier for the schema (e.g., "project_id:dataset_id")
    
  Returns:
    Cached schema dict or None if not found/expired
  """
  # Check in-memory cache first
  if cache_key in _SCHEMA_CACHE:
    cache_data = _SCHEMA_CACHE[cache_key]
    if _is_cache_valid(cache_data):
      _logger.info("Schema cache hit (memory): %s", cache_key)
      return cache_data["schema"]
    else:
      # Remove expired entry
      del _SCHEMA_CACHE[cache_key]
      _logger.info("Expired cache entry removed from memory: %s", cache_key)
  
  # Check disk cache
  cache_file = _get_cache_file_path(cache_key)
  if cache_file.exists():
    try:
      with open(cache_file, "r", encoding="utf-8") as f:
        cache_data = json.load(f)
      
      if _is_cache_valid(cache_data):
        _logger.info("Schema cache hit (disk): %s", cache_key)
        # Populate in-memory cache
        _SCHEMA_CACHE[cache_key] = cache_data
        return cache_data["schema"]
      else:
        # Remove expired file
        cache_file.unlink()
        _logger.info("Expired cache file removed: %s", cache_key)
    except Exception as e:
      _logger.warning("Failed to load cache from disk: %s - %s", cache_key, e)
  
  _logger.info("Schema cache miss: %s", cache_key)
  return None


def set_cached_schema(cache_key: str, schema: dict[str, Any]) -> None:
  """Store schema in both memory and disk cache.
  
  Args:
    cache_key: Unique identifier for the schema
    schema: Schema data to cache
  """
  cache_data = {
      "schema": schema,
      "cached_at": datetime.now().isoformat(),
      "schema_version": os.getenv("SCHEMA_VERSION", "unversioned"),
      "environment": os.getenv("ENVIRONMENT", "unknown"),
  }
  
  # Store in memory
  _SCHEMA_CACHE[cache_key] = cache_data
  _logger.info("Schema cached in memory: %s", cache_key)
  
  # Store on disk
  try:
    cache_file = _get_cache_file_path(cache_key)
    with open(cache_file, "w", encoding="utf-8") as f:
      json.dump(cache_data, f, indent=2)
    _logger.info("Schema cached on disk: %s", cache_key)
  except Exception as e:
    _logger.warning("Failed to cache schema on disk: %s - %s", cache_key, e)


def clear_cache(cache_key: str | None = None) -> None:
  """Clear schema cache.
  
  Args:
    cache_key: Specific key to clear, or None to clear all
  """
  if cache_key:
    # Clear specific cache entry
    if cache_key in _SCHEMA_CACHE:
      del _SCHEMA_CACHE[cache_key]
    
    cache_file = _get_cache_file_path(cache_key)
    if cache_file.exists():
      cache_file.unlink()
    
    _logger.info("Cleared cache for: %s", cache_key)
  else:
    # Clear all cache
    _SCHEMA_CACHE.clear()
    
    if CACHE_DIR.exists():
      for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()
    
    _logger.info("Cleared all schema cache")


def get_cache_stats() -> dict[str, Any]:
  """Get statistics about the current cache.
  
  Returns:
    Dictionary with cache statistics
  """
  disk_files = list(CACHE_DIR.glob("*.json")) if CACHE_DIR.exists() else []
  
  # Get cache metadata
  cache_entries = []
  for cache_key, cache_data in _SCHEMA_CACHE.items():
    cache_entries.append({
        "key": cache_key,
        "cached_at": cache_data.get("cached_at"),
        "schema_version": cache_data.get("schema_version"),
        "environment": cache_data.get("environment"),
    })
  
  return {
      "memory_entries": len(_SCHEMA_CACHE),
      "disk_files": len(disk_files),
      "cache_dir": str(CACHE_DIR),
      "ttl_hours": CACHE_TTL_HOURS,
      "force_refresh": os.getenv("FORCE_SCHEMA_REFRESH", "false"),
      "schema_version": os.getenv("SCHEMA_VERSION", "unversioned"),
      "entries": cache_entries,
  }