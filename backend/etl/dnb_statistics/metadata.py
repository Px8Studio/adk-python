"""
Metadata tracking for DNB Statistics ETL

Tracks extraction history, completeness status, and data freshness
to support incremental updates and data quality monitoring.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from . import config

logger = logging.getLogger(__name__)


class ExtractionMetadata:
    """
    Manages extraction metadata for DNB Statistics endpoints.
    
    Tracks:
    - Last successful extraction timestamp
    - Record counts and completeness status
    - Pagination details
    - Error history
    - Data freshness indicators
    """
    
    def __init__(self, metadata_path: Optional[Path] = None):
        """
        Initialize metadata manager.
        
        Args:
            metadata_path: Path to metadata JSON file (defaults to bronze dir)
        """
        self.metadata_path = metadata_path or (
            config.BRONZE_DIR / "_extraction_metadata.json"
        )
        self.data: dict[str, Any] = self._load()
    
    def _load(self) -> dict[str, Any]:
        """Load metadata from disk."""
        if not self.metadata_path.exists():
            logger.info("No existing metadata found - initializing new metadata")
            return {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "endpoints": {},
            }
        
        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded metadata for {len(data.get('endpoints', {}))} endpoints")
                return data
        except Exception as exc:
            logger.error(f"Failed to load metadata: {exc}", exc_info=True)
            return {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "endpoints": {},
            }
    
    def save(self) -> None:
        """Save metadata to disk."""
        try:
            self.data["last_updated"] = datetime.utcnow().isoformat()
            
            # Ensure directory exists
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with pretty formatting
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved metadata to {self.metadata_path}")
        
        except Exception as exc:
            logger.error(f"Failed to save metadata: {exc}", exc_info=True)
    
    def update_extraction(
        self,
        endpoint_name: str,
        stats: dict[str, Any],
        category: str,
        filename: str,
    ) -> None:
        """
        Update metadata for a completed extraction.
        
        Args:
            endpoint_name: Name of the endpoint
            stats: Extraction statistics from the extractor
            category: Data category
            filename: Output filename
        """
        # Ensure endpoints dict exists
        if "endpoints" not in self.data:
            self.data["endpoints"] = {}
        
        # Get or create endpoint metadata
        if endpoint_name not in self.data["endpoints"]:
            self.data["endpoints"][endpoint_name] = {
                "category": category,
                "filename": filename,
                "extraction_history": [],
            }
        
        endpoint_meta = self.data["endpoints"][endpoint_name]
        
        # Determine completeness status
        total_records = stats.get("total_records", 0)
        total_pages = stats.get("total_pages", 0)
        
        # Heuristic: If we got exactly 2000 records in a single page,
        # it might be truncated (API default limit)
        is_complete = True
        completeness_notes = []
        
        if total_records == 2000 and total_pages == 1:
            is_complete = False
            completeness_notes.append(
                "Dataset has exactly 2000 records - may be truncated at API limit"
            )
        
        # Check for failed pages
        failed_pages = stats.get("failed_pages", 0)
        if failed_pages > 0:
            is_complete = False
            completeness_notes.append(f"{failed_pages} page(s) failed to fetch")
        
        # Build extraction record
        extraction_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "start_time": stats.get("start_time").isoformat() if stats.get("start_time") else None,
            "end_time": stats.get("end_time").isoformat() if stats.get("end_time") else None,
            "duration_seconds": (
                (stats.get("end_time") - stats.get("start_time")).total_seconds()
                if stats.get("end_time") and stats.get("start_time")
                else None
            ),
            "total_records": total_records,
            "total_pages": total_pages,
            "failed_pages": failed_pages,
            "is_complete": is_complete,
            "completeness_notes": completeness_notes,
            "status": "success" if "error" not in stats else "error",
            "error": stats.get("error"),
        }
        
        # Add to history (keep last 10 extractions)
        endpoint_meta["extraction_history"].append(extraction_record)
        endpoint_meta["extraction_history"] = endpoint_meta["extraction_history"][-10:]
        
        # Update summary fields
        endpoint_meta["last_extraction"] = extraction_record["timestamp"]
        endpoint_meta["last_successful_extraction"] = (
            extraction_record["timestamp"] if extraction_record["status"] == "success" else
            endpoint_meta.get("last_successful_extraction")
        )
        endpoint_meta["total_records"] = total_records
        endpoint_meta["is_complete"] = is_complete
        endpoint_meta["category"] = category
        endpoint_meta["filename"] = filename
        
        # Save immediately
        self.save()
    
    def get_endpoint_metadata(self, endpoint_name: str) -> Optional[dict[str, Any]]:
        """Get metadata for a specific endpoint."""
        return self.data.get("endpoints", {}).get(endpoint_name)
    
    def get_incomplete_endpoints(self) -> list[dict[str, Any]]:
        """
        Get list of endpoints that may have incomplete data.
        
        Returns:
            List of endpoint metadata dicts that are flagged as incomplete
        """
        incomplete = []
        
        for endpoint_name, meta in self.data.get("endpoints", {}).items():
            if not meta.get("is_complete", True):
                incomplete.append({
                    "endpoint": endpoint_name,
                    "category": meta.get("category"),
                    "total_records": meta.get("total_records", 0),
                    "last_extraction": meta.get("last_extraction"),
                    "notes": (
                        meta.get("extraction_history", [])[-1]
                        .get("completeness_notes", [])
                        if meta.get("extraction_history")
                        else []
                    ),
                })
        
        return incomplete
    
    def get_stale_endpoints(
        self,
        max_age_hours: float = 24.0,
    ) -> list[dict[str, Any]]:
        """
        Get endpoints that haven't been updated recently.
        
        Args:
            max_age_hours: Maximum age in hours before considering stale
        
        Returns:
            List of stale endpoint metadata
        """
        from datetime import timedelta
        
        stale = []
        now = datetime.utcnow()
        max_age = timedelta(hours=max_age_hours)
        
        for endpoint_name, meta in self.data.get("endpoints", {}).items():
            last_extraction = meta.get("last_successful_extraction")
            
            if not last_extraction:
                # Never extracted
                stale.append({
                    "endpoint": endpoint_name,
                    "category": meta.get("category"),
                    "last_extraction": None,
                    "age_hours": None,
                    "status": "never_extracted",
                })
                continue
            
            # Parse timestamp
            try:
                last_time = datetime.fromisoformat(last_extraction.replace("Z", "+00:00"))
                age = now - last_time.replace(tzinfo=None)
                
                if age > max_age:
                    stale.append({
                        "endpoint": endpoint_name,
                        "category": meta.get("category"),
                        "last_extraction": last_extraction,
                        "age_hours": age.total_seconds() / 3600,
                        "status": "stale",
                    })
            
            except Exception as exc:
                logger.warning(f"Failed to parse timestamp for {endpoint_name}: {exc}")
        
        return stale
    
    def generate_summary_report(self) -> str:
        """
        Generate a human-readable summary report of extraction metadata.
        
        Returns:
            Formatted report string
        """
        endpoints = self.data.get("endpoints", {})
        
        total_endpoints = len(endpoints)
        complete_endpoints = sum(
            1 for meta in endpoints.values()
            if meta.get("is_complete", True)
        )
        incomplete_endpoints = total_endpoints - complete_endpoints
        
        total_records = sum(
            meta.get("total_records", 0)
            for meta in endpoints.values()
        )
        
        # Build report
        lines = [
            "=" * 70,
            "DNB STATISTICS EXTRACTION METADATA SUMMARY",
            "=" * 70,
            f"Total Endpoints: {total_endpoints}",
            f"Complete: {complete_endpoints}",
            f"Potentially Incomplete: {incomplete_endpoints}",
            f"Total Records Extracted: {total_records:,}",
            "",
        ]
        
        # Show incomplete endpoints
        if incomplete_endpoints > 0:
            lines.append("⚠️  POTENTIALLY INCOMPLETE DATASETS:")
            lines.append("")
            
            for endpoint_name, meta in endpoints.items():
                if not meta.get("is_complete", True):
                    lines.append(f"  • {endpoint_name}")
                    lines.append(f"    Records: {meta.get('total_records', 0):,}")
                    lines.append(f"    Category: {meta.get('category', 'unknown')}")
                    
                    # Get notes from latest extraction
                    history = meta.get("extraction_history", [])
                    if history:
                        notes = history[-1].get("completeness_notes", [])
                        for note in notes:
                            lines.append(f"    ⚠ {note}")
                    
                    lines.append("")
        
        # Show extraction timeline
        lines.append("📅 RECENT EXTRACTION ACTIVITY:")
        lines.append("")
        
        # Get endpoints sorted by last extraction
        sorted_endpoints = sorted(
            endpoints.items(),
            key=lambda x: x[1].get("last_extraction", ""),
            reverse=True,
        )
        
        for endpoint_name, meta in sorted_endpoints[:10]:  # Show last 10
            last_extraction = meta.get("last_extraction", "Never")
            total_records = meta.get("total_records", 0)
            status = "✅" if meta.get("is_complete", True) else "⚠️"
            
            lines.append(
                f"  {status} {endpoint_name:<40} {total_records:>8,} records  "
                f"{last_extraction}"
            )
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def should_extract_incremental(
        self,
        endpoint_name: str,
        max_age_hours: float = 24.0,
    ) -> tuple[bool, Optional[datetime]]:
        """
        Determine if an endpoint should use incremental extraction.
        
        Args:
            endpoint_name: Name of the endpoint
            max_age_hours: Maximum age before full refresh
        
        Returns:
            Tuple of (should_use_incremental, last_extraction_time)
        """
        meta = self.get_endpoint_metadata(endpoint_name)
        
        if not meta:
            # Never extracted - do full extraction
            return (False, None)
        
        last_extraction = meta.get("last_successful_extraction")
        if not last_extraction:
            return (False, None)
        
        try:
            last_time = datetime.fromisoformat(last_extraction.replace("Z", "+00:00"))
            last_time = last_time.replace(tzinfo=None)
            
            from datetime import timedelta
            age = datetime.utcnow() - last_time
            max_age = timedelta(hours=max_age_hours)
            
            # Use incremental if data is recent and complete
            if age < max_age and meta.get("is_complete", False):
                return (True, last_time)
            else:
                return (False, last_time)
        
        except Exception as exc:
            logger.warning(f"Failed to parse timestamp: {exc}")
            return (False, None)
