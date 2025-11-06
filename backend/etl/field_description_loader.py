"""
Field Description Loader

Loads and merges field descriptions from YAML files for BigQuery schema enrichment.

Usage:
    from backend.etl.field_description_loader import load_all_field_descriptions
    
    descriptions = load_all_field_descriptions()
    # descriptions = {"_etl_timestamp": "ETL extraction timestamp in ISO 8601 format (UTC)", ...}
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_field_descriptions_from_file(yaml_path: Path) -> dict[str, str]:
  """
  Load field descriptions from a YAML file.
  
  Args:
      yaml_path: Path to YAML file containing field descriptions
      
  Returns:
      Dictionary mapping field_name -> description
  """
  if not yaml_path.exists():
    logger.warning(f"Field descriptions file not found: {yaml_path}")
    return {}
  
  try:
    with open(yaml_path, "r", encoding="utf-8") as f:
      data = yaml.safe_load(f) or {}
    
    # Flatten nested structure (standard_fields, time_fields, etc.)
    descriptions = {}
    for category_data in data.values():
      if not isinstance(category_data, dict):
        continue
      
      for field_name, field_info in category_data.items():
        if isinstance(field_info, dict) and "description" in field_info:
          descriptions[field_name] = field_info["description"]
        elif isinstance(field_info, str):
          descriptions[field_name] = field_info
    
    logger.info(
      f"Loaded {len(descriptions)} field descriptions from {yaml_path.name}"
    )
    return descriptions
    
  except Exception as exc:
    logger.warning(
      f"Failed to load field descriptions from {yaml_path}: {exc}"
    )
    return {}


def load_all_field_descriptions(
  datasource_id: str | None = None,
) -> dict[str, str]:
  """
  Load all field descriptions with priority: datasource-specific > common.
  
  Args:
      datasource_id: Optional datasource identifier for loading specific descriptions
      
  Returns:
      Merged dictionary mapping field_name -> description
  """
  descriptions = {}
  
  # Step 1: Load common descriptions
  common_path = Path(__file__).parent / "field_descriptions.yaml"
  common_descriptions = load_field_descriptions_from_file(common_path)
  descriptions.update(common_descriptions)
  
  # Step 2: Load datasource-specific descriptions (if provided)
  if datasource_id:
    datasource_path = (
      Path(__file__).parent / f"{datasource_id}" / "field_descriptions.yaml"
    )
    
    if datasource_path.exists():
      specific_descriptions = load_field_descriptions_from_file(datasource_path)
      # Datasource-specific descriptions override common ones
      descriptions.update(specific_descriptions)
      logger.info(
        f"Merged {len(specific_descriptions)} datasource-specific descriptions"
      )
  
  return descriptions


def get_description_for_field(
  field_name: str,
  descriptions: dict[str, str] | None = None,
) -> str | None:
  """
  Get description for a specific field name.
  
  Args:
      field_name: Field name to look up
      descriptions: Optional pre-loaded descriptions dict
      
  Returns:
      Field description or None if not found
  """
  if descriptions is None:
    descriptions = load_all_field_descriptions()
  
  return descriptions.get(field_name)
