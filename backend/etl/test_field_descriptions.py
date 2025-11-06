"""
Test Field Description Loading

Quick test script to verify field descriptions are loading correctly.
"""

from backend.etl.field_description_loader import (
    load_all_field_descriptions,
    get_description_for_field,
)


def main():
    print("=" * 70)
    print("TESTING FIELD DESCRIPTION LOADER")
    print("=" * 70 + "\n")
    
    # Test 1: Load all descriptions
    print("Test 1: Load all common descriptions")
    descriptions = load_all_field_descriptions()
    print(f"  ✓ Loaded {len(descriptions)} descriptions\n")
    
    # Test 2: Check specific fields
    print("Test 2: Check specific field descriptions")
    test_fields = [
        "_etl_timestamp",
        "_etl_source",
        "period",
        "date",
        "currency",
        "register_code",
        "relation_number",
        "sector",
        "instrument",
        "official_name",
        "publication_date",
        "status",
    ]
    
    for field in test_fields:
        desc = descriptions.get(field)
        if desc:
            print(f"  ✓ {field:25s}: {desc[:60]}...")
        else:
            print(f"  ✗ {field:25s}: NOT FOUND")
    
    # Test 3: Test datasource-specific loading (will be empty for now)
    print("\nTest 3: Load datasource-specific descriptions")
    dnb_stats_descriptions = load_all_field_descriptions(
      datasource_id="dnb_statistics"
    )
    print(
      f"  ✓ Total descriptions (common + specific): "
      f"{len(dnb_stats_descriptions)}\n"
    )
    
    # Test 4: Show all categories
    print("Test 4: Show all available field categories")
    from pathlib import Path
    import yaml
    
    yaml_path = Path("backend/etl/field_descriptions.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    for category in data.keys():
        count = len(data[category])
        print(f"  • {category:30s}: {count:3d} fields")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
