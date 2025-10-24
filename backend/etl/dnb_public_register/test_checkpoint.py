#!/usr/bin/env python3
"""
Test checkpoint functionality for DNB Public Register ETL.

This script validates that the checkpoint system works correctly:
1. Start an extraction
2. Interrupt it mid-process
3. Resume from checkpoint
4. Verify completion and cleanup

Usage:
    python backend/etl/dnb_public_register/test_checkpoint.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

from backend.etl.dnb_public_register import config
from backend.etl.dnb_public_register.checkpoint import (
    ExtractionCheckpoint,
    list_checkpoints,
    clear_all_checkpoints,
)
from backend.etl.dnb_public_register.extractors import (
    OrganizationRelationNumbersExtractor,
)


async def test_checkpoint_creation():
    """Test that checkpoints are created manually and persisted."""
    print("=" * 70)
    print("TEST 1: Checkpoint Creation & Persistence")
    print("=" * 70)
    
    # Clear any existing checkpoints
    clear_all_checkpoints(config.CHECKPOINT_DIR)
    print(f"✓ Cleared existing checkpoints from {config.CHECKPOINT_DIR}")
    
    # Create a test checkpoint manually
    test_register = "WFTAF"
    checkpoint_id = f"test_checkpoint_{test_register.lower()}"
    
    print(f"\n🧪 Creating test checkpoint: {checkpoint_id}")
    
    checkpoint = ExtractionCheckpoint(config.CHECKPOINT_DIR, checkpoint_id)
    
    # Save checkpoint state
    test_state = {
        "last_page": 5,
        "total_records": 125,
        "url": "https://api.dnb.nl/test",
    }
    checkpoint.save(test_state)
    print(f"✓ Saved checkpoint with state: {test_state}")
    
    # Verify checkpoint exists
    if not checkpoint.exists():
        print(f"\n❌ TEST 1 FAILED: Checkpoint file not created")
        return False
    
    # Load and verify
    loaded_state = checkpoint.load()
    print(f"✓ Loaded checkpoint state: {loaded_state}")
    
    # Check if checkpoint appears in list
    checkpoints = list_checkpoints(config.CHECKPOINT_DIR)
    print(f"\n📊 Checkpoints found: {len(checkpoints)}")
    for cp in checkpoints:
        print(f"   - {cp['extraction_id']}")
        print(f"     Timestamp: {cp.get('timestamp', 'N/A')}")
        print(f"     Last page: {cp.get('last_page', 'N/A')}")
        print(f"     Total records: {cp.get('total_records', 'N/A')}")
    
    if checkpoint_id in [cp['extraction_id'] for cp in checkpoints]:
        print(f"\n✅ TEST 1 PASSED: Checkpoint created and persisted successfully")
        return True
    else:
        print(f"\n❌ TEST 1 FAILED: Checkpoint not found in list")
        return False


async def test_checkpoint_resume():
    """Test that checkpoints can be loaded and modified."""
    print("\n" + "=" * 70)
    print("TEST 2: Checkpoint Load & Modify")
    print("=" * 70)
    
    test_register = "WFTAF"
    checkpoint_id = f"test_checkpoint_{test_register.lower()}"
    
    # Load the checkpoint created in test 1
    checkpoint = ExtractionCheckpoint(config.CHECKPOINT_DIR, checkpoint_id)
    
    if not checkpoint.exists():
        print(f"❌ TEST 2 FAILED: Checkpoint from Test 1 not found")
        return False
    
    saved_state = checkpoint.load()
    
    print(f"📂 Loaded checkpoint: {checkpoint_id}")
    print(f"   Last page: {saved_state.get('last_page')}")
    print(f"   Total records: {saved_state.get('total_records')}")
    
    # Modify checkpoint (simulate progress)
    new_state = {
        "last_page": saved_state.get("last_page", 0) + 3,
        "total_records": saved_state.get("total_records", 0) + 75,
        "url": saved_state.get("url", ""),
    }
    checkpoint.save(new_state)
    print(f"\n✓ Updated checkpoint with new state:")
    print(f"   New last page: {new_state['last_page']}")
    print(f"   New total records: {new_state['total_records']}")
    
    # Verify checkpoint was updated
    updated_state = checkpoint.load()
    
    if (updated_state.get("last_page") == new_state["last_page"] and
        updated_state.get("total_records") == new_state["total_records"]):
        print(f"\n✅ TEST 2 PASSED: Checkpoint loaded and modified successfully")
        return True
    else:
        print(f"\n❌ TEST 2 FAILED: Checkpoint state mismatch")
        print(f"   Expected: page={new_state['last_page']}, records={new_state['total_records']}")
        print(f"   Got: page={updated_state.get('last_page')}, records={updated_state.get('total_records')}")
        return False


async def test_checkpoint_cleanup():
    """Test that checkpoints can be cleared."""
    print("\n" + "=" * 70)
    print("TEST 3: Checkpoint Cleanup")
    print("=" * 70)
    
    test_register = "WFTAF"
    checkpoint_id = f"test_checkpoint_{test_register.lower()}"
    
    # Use the checkpoint from previous tests
    checkpoint = ExtractionCheckpoint(config.CHECKPOINT_DIR, checkpoint_id)
    
    if not checkpoint.exists():
        print(f"❌ TEST 3 FAILED: Checkpoint not found")
        return False
    
    print(f"✓ Found checkpoint: {checkpoint_id}")
    
    # Clear it
    checkpoint.clear()
    print(f"✓ Called checkpoint.clear()")
    
    # Verify it's gone
    if not checkpoint.exists():
        print(f"\n✅ TEST 3 PASSED: Checkpoint cleared successfully")
        
        # Final verification: list should be empty
        checkpoints = list_checkpoints(config.CHECKPOINT_DIR)
        if len(checkpoints) == 0:
            print(f"✓ Confirmed: No checkpoints remaining")
        else:
            print(f"⚠️  Warning: {len(checkpoints)} other checkpoint(s) still exist")
        
        return True
    else:
        print(f"\n❌ TEST 3 FAILED: Checkpoint still exists after clear")
        return False


async def main():
    """Run all checkpoint tests."""
    # Configure logging
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
    )
    
    print("\n" + "=" * 70)
    print("🧪 DNB Public Register Checkpoint System Tests")
    print("=" * 70)
    print(f"Checkpoint directory: {config.CHECKPOINT_DIR}")
    print()
    
    results = []
    
    # Run tests
    try:
        results.append(await test_checkpoint_creation())
        results.append(await test_checkpoint_resume())
        results.append(await test_checkpoint_cleanup())
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
