"""
Configuration for DNB Public Register ETL Pipeline

Centralized settings for API access, output paths, and processing parameters.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# Load environment variables from .env file in project root
_project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(_project_root / ".env")

# ==========================================
# API Configuration
# ==========================================

DNB_BASE_URL: Final[str] = "https://api.dnb.nl/publicdata/v1"
DNB_API_KEY: str = os.getenv("DNB_SUBSCRIPTION_KEY_DEV", "")

if not DNB_API_KEY:
    raise ValueError(
        "DNB_SUBSCRIPTION_KEY_DEV environment variable must be set. "
        "Get your key from https://api.portal.dnb.nl/"
    )

# ==========================================
# Output Configuration
# ==========================================

# Root data directory
DATA_ROOT: Final[Path] = Path(__file__).parent.parent.parent / "data"

# 0-fetch: Raw API responses (landing zone)
FETCH_DIR: Final[Path] = DATA_ROOT / "0-fetch" / "dnb_public_register"

# 1-bronze: Cleaned and typed Parquet files
BRONZE_DIR: Final[Path] = DATA_ROOT / "1-bronze" / "dnb_public_register"

# 2-silver: Enriched and joined data
SILVER_DIR: Final[Path] = DATA_ROOT / "2-silver" / "dnb_public_register"

# 3-gold: Analytics-ready aggregations
GOLD_DIR: Final[Path] = DATA_ROOT / "3-gold" / "dnb_public_register"

# ==========================================
# Processing Configuration
# ==========================================

# Pagination settings
DEFAULT_PAGE_SIZE: Final[int] = 25  # DNB API max
DEFAULT_START_PAGE: Final[int] = 1

# Request settings
REQUEST_TIMEOUT: Final[float] = 30.0  # seconds
MAX_RETRIES: Final[int] = 3
RETRY_BACKOFF_FACTOR: Final[float] = 2.0  # Exponential backoff

# Rate limiting (DNB allows 30 calls/minute)
RATE_LIMIT_CALLS: Final[int] = 30
RATE_LIMIT_PERIOD: Final[float] = 60.0  # seconds
RATE_LIMIT_BUFFER: Final[float] = 1.2  # Safety margin (20% slower)

# Parallel processing
MAX_CONCURRENT_REQUESTS: Final[int] = 5  # Stay under rate limit

# ==========================================
# Language & Register Codes
# ==========================================

SUPPORTED_LANGUAGES: Final[list[str]] = ["NL", "EN"]
DEFAULT_LANGUAGE: Final[str] = "NL"

# Known register codes (will be discovered dynamically)
KNOWN_REGISTER_CODES: Final[list[str]] = [
  "WFTAF",  # Financial services under Wft
  "WFT",    # Various financial supervision categories
  # More codes discovered at runtime via /Registers endpoint
]

# ==========================================
# Parquet Configuration
# ==========================================

PARQUET_ENGINE: Final[str] = "pyarrow"
PARQUET_COMPRESSION: Final[str] = "snappy"  # Good balance of speed/size
PARQUET_ROW_GROUP_SIZE: Final[int] = 10000

# ==========================================
# Logging Configuration
# ==========================================

LOG_DIR: Final[Path] = Path(__file__).parent.parent.parent.parent / "logs"
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ==========================================
# Endpoint Configuration
# ==========================================

# Map endpoint names to their data categories
ENDPOINT_CATEGORIES: Final[dict[str, str]] = {
  "registers": "metadata",
  "supported_languages": "metadata",
  "organizations": "entities",
  "publications": "publications",
  "registrations": "registrations",
  "register_articles": "regulatory",
}

# ==========================================
# Helper Functions
# ==========================================

def ensure_directories() -> None:
    """Create all required directories if they don't exist."""
    directories = [
        FETCH_DIR,
        BRONZE_DIR,
        SILVER_DIR,
        GOLD_DIR,
        LOG_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_output_path(
    stage: str,  # 'fetch', 'bronze', 'silver', 'gold'
    category: str,  # 'metadata', 'entities', 'publications', etc.
    filename: str,
) -> Path:
    """
    Generate standardized output path for data files.
    
    Args:
        stage: Data processing stage
        category: Data category (from ENDPOINT_CATEGORIES)
        filename: File name (without extension)
    
    Returns:
        Full path to output file
    
    Example:
        >>> get_output_path('bronze', 'entities', 'organizations_wftaf_nl')
        Path('.../data/1-bronze/dnb_public_register/entities/organizations_wftaf_nl.parquet')
    """
    stage_dirs = {
        "fetch": FETCH_DIR,
        "bronze": BRONZE_DIR,
        "silver": SILVER_DIR,
        "gold": GOLD_DIR,
    }
    
    base_dir = stage_dirs.get(stage)
    if not base_dir:
        raise ValueError(f"Unknown stage: {stage}")
    
    category_dir = base_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # Always use .parquet extension
    extension = ".parquet"
    return category_dir / f"{filename}{extension}"


# Initialize directories on module import
ensure_directories()
