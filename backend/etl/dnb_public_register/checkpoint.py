"""
Checkpoint management for resumable extractions.

Provides save/load functionality to enable long-running extractions to resume
from the last successful page in case of interruption.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ExtractionCheckpoint:
    """
    Save and load extraction progress for resume capability.
    
    Each checkpoint is stored as a JSON file containing:
    - register_code: The register being extracted
    - language_code: Language variant being extracted
    - last_page: Last successfully completed page number
    - total_records: Total records extracted so far
    - timestamp: When the checkpoint was saved
    
    Usage:
        checkpoint = ExtractionCheckpoint(
            checkpoint_dir=Path("./checkpoints"),
            extraction_id="WFTAF_NL"
        )
        
        # Load existing checkpoint
        state = checkpoint.load()
        if state:
            start_page = state["last_page"] + 1
        else:
            start_page = 1
        
        # Save progress after each page
        for page in range(start_page, max_pages):
            # ... extract page ...
            checkpoint.save({
                "last_page": page,
                "total_records": records_count,
            })
        
        # Clear on success
        checkpoint.clear()
    """
    
    def __init__(self, checkpoint_dir: Path, extraction_id: str):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
            extraction_id: Unique identifier for this extraction
                          (e.g., "WFTAF_NL", "organizations_WFMBESVE")
        """
        self.checkpoint_dir = checkpoint_dir
        self.extraction_id = extraction_id
        self.checkpoint_file = checkpoint_dir / f"{extraction_id}.json"
        
        # Ensure checkpoint directory exists
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, state: dict[str, Any]) -> None:
        """
        Save checkpoint state to disk.
        
        Args:
            state: Dictionary containing extraction state
                  Must include at minimum: last_page, total_records
        """
        # Add timestamp
        state["_timestamp"] = datetime.utcnow().isoformat()
        state["_extraction_id"] = self.extraction_id
        
        try:
            self.checkpoint_file.write_text(
                json.dumps(state, indent=2, ensure_ascii=False)
            )
            logger.debug(
                f"💾 Checkpoint saved: {self.extraction_id} "
                f"(page {state.get('last_page')}, "
                f"{state.get('total_records')} records)"
            )
        except Exception as exc:
            logger.error(f"Failed to save checkpoint: {exc}")
    
    def load(self) -> Optional[dict[str, Any]]:
        """
        Load checkpoint state from disk if it exists.
        
        Returns:
            Dictionary with checkpoint state, or None if no checkpoint exists
        """
        if not self.checkpoint_file.exists():
            return None
        
        try:
            state = json.loads(self.checkpoint_file.read_text())
            logger.info(
                f"📍 Checkpoint found: {self.extraction_id} "
                f"(saved at {state.get('_timestamp')})"
            )
            return state
        except Exception as exc:
            logger.error(f"Failed to load checkpoint: {exc}")
            return None
    
    def clear(self) -> None:
        """
        Remove checkpoint file after successful completion.
        
        Call this when the extraction completes successfully to clean up.
        """
        if self.checkpoint_file.exists():
            try:
                self.checkpoint_file.unlink()
                logger.info(f"🗑️  Checkpoint cleared: {self.extraction_id}")
            except Exception as exc:
                logger.warning(f"Failed to remove checkpoint: {exc}")
    
    def exists(self) -> bool:
        """
        Check if a checkpoint exists for this extraction.
        
        Returns:
            True if checkpoint file exists, False otherwise
        """
        return self.checkpoint_file.exists()
    
    def get_info(self) -> dict[str, Any]:
        """
        Get checkpoint information without loading full state.
        
        Returns:
            Dictionary with checkpoint metadata (file path, size, modified time)
        """
        if not self.exists():
            return {"exists": False}
        
        stat = self.checkpoint_file.stat()
        return {
            "exists": True,
            "path": str(self.checkpoint_file),
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }


def list_checkpoints(checkpoint_dir: Path) -> list[dict[str, Any]]:
    """
    List all checkpoints in a directory.
    
    Args:
        checkpoint_dir: Directory containing checkpoint files
    
    Returns:
        List of checkpoint info dictionaries
    """
    if not checkpoint_dir.exists():
        return []
    
    checkpoints = []
    for checkpoint_file in checkpoint_dir.glob("*.json"):
        try:
            state = json.loads(checkpoint_file.read_text())
            checkpoints.append({
                "extraction_id": state.get("_extraction_id", checkpoint_file.stem),
                "last_page": state.get("last_page"),
                "total_records": state.get("total_records"),
                "timestamp": state.get("_timestamp"),
                "file": str(checkpoint_file),
            })
        except Exception as exc:
            logger.warning(f"Failed to read checkpoint {checkpoint_file}: {exc}")
    
    return checkpoints


def clear_all_checkpoints(checkpoint_dir: Path) -> int:
    """
    Clear all checkpoint files in a directory.
    
    Useful for forcing a fresh extraction from scratch.
    
    Args:
        checkpoint_dir: Directory containing checkpoint files
    
    Returns:
        Number of checkpoints cleared
    """
    if not checkpoint_dir.exists():
        return 0
    
    count = 0
    for checkpoint_file in checkpoint_dir.glob("*.json"):
        try:
            checkpoint_file.unlink()
            count += 1
        except Exception as exc:
            logger.warning(f"Failed to remove {checkpoint_file}: {exc}")
    
    logger.info(f"🗑️  Cleared {count} checkpoint(s)")
    return count
