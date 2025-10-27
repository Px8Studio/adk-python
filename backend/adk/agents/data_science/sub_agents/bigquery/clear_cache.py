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

"""CLI utility to manage BigQuery schema cache."""

from __future__ import annotations

import sys

from .schema_cache import clear_cache, get_cache_stats


def main() -> None:
  """Clear BigQuery schema cache."""
  stats = get_cache_stats()
  
  print("=" * 70)
  print("BigQuery Schema Cache Status")
  print("=" * 70)
  print(f"  Memory entries:    {stats['memory_entries']}")
  print(f"  Disk files:        {stats['disk_files']}")
  print(f"  Cache directory:   {stats['cache_dir']}")
  print(f"  TTL:               {stats['ttl_hours']} hours")
  print(f"  Force refresh:     {stats['force_refresh']}")
  print(f"  Schema version:    {stats['schema_version']}")
  print()
  
  if stats['entries']:
    print("Cached Entries:")
    for entry in stats['entries']:
      print(f"  - {entry['key']}")
      print(f"    Cached at:       {entry['cached_at']}")
      print(f"    Schema version:  {entry['schema_version']}")
      print(f"    Environment:     {entry['environment']}")
      print()
  
  print("=" * 70)
  response = input("\nClear all cache? (y/n): ")
  if response.lower() == "y":
    clear_cache()
    print("✓ Cache cleared successfully")
    sys.exit(0)
  else:
    print("Cache clear cancelled")
    sys.exit(1)


if __name__ == "__main__":
  main()