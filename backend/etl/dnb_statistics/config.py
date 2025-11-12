"""
Configuration for DNB Statistics ETL Pipeline

Centralized settings for API access, output paths, and processing parameters.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(_project_root / ".env")

# ==========================================
# API Configuration
# ==========================================

DNB_BASE_URL: Final[str] = "https://api.dnb.nl/statisticsdata/v2024100101"
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

# 1-bronze: Cleaned and typed Parquet files (primary output)
BRONZE_DIR: Final[Path] = DATA_ROOT / "1-bronze" / "dnb_statistics"

# 2-silver: Enriched and joined data (optional)
SILVER_DIR: Final[Path] = DATA_ROOT / "2-silver" / "dnb_statistics"

# 3-gold: Analytics-ready aggregations (optional)
GOLD_DIR: Final[Path] = DATA_ROOT / "3-gold" / "dnb_statistics"

# Legacy fetch directory (no longer used - kept for backwards compatibility)
FETCH_DIR: Final[Path] = DATA_ROOT / "0-fetch" / "dnb_statistics"

# ==========================================
# Processing Configuration
# ==========================================

# Pagination settings
# Statistics API supports pageSize=0 to fetch ALL records in a single request!
# This is much more efficient than paginating through thousands of pages.
# See: https://api.dnb.nl/statisticsdata/v2024100101 - pageSize parameter docs
DEFAULT_PAGE_SIZE: Final[int] = 0  # 0 = fetch all records at once (API feature)
FALLBACK_PAGE_SIZE: Final[int] = 2000  # Fallback if pageSize=0 fails
DEFAULT_START_PAGE: Final[int] = 1

# Request settings
REQUEST_TIMEOUT: Final[float] = 30.0  # seconds
MAX_RETRIES: Final[int] = 3
RETRY_BACKOFF_FACTOR: Final[float] = 2.0  # Exponential backoff

# Rate limiting (conservative to avoid 429 errors)
RATE_LIMIT_CALLS: Final[int] = 25  # Slightly under limit for safety
RATE_LIMIT_PERIOD: Final[float] = 60.0  # seconds
RATE_LIMIT_BUFFER: Final[float] = 1.2  # Safety margin (20% slower)

# Parallel processing
MAX_CONCURRENT_REQUESTS: Final[int] = 3  # Stay well under rate limit

# Batch processing for Parquet writes
BATCH_SIZE: Final[int] = 10000  # Records per batch write

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
# Endpoint Categories
# ==========================================

# Group endpoints by domain for organized storage
ENDPOINT_CATEGORIES: Final[dict[str, str]] = {
    # Exchange Rates & Interest Rates
    "exchange_rates": "market_data",
    "interest_rates": "market_data",
    
    # Balance Sheets
    "balance_sheets": "financial_statements",
    
    # Payments
    "payments": "payments",
    
    # Securities & Investments
    "securities": "investments",
    "investments": "investments",
    
    # Insurance & Pensions
    "insurance": "insurance_pensions",
    "pension": "insurance_pensions",
    
    # Macroeconomic
    "macroeconomic": "macroeconomic",
    "balance_of_payments": "macroeconomic",
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
    category: str,  # From ENDPOINT_CATEGORIES
    filename: str,
    *,
    subcategory: str | None = None,
) -> Path:
    """
    Generate standardized output path for data files.
    
    Args:
        stage: Data processing stage ('fetch', 'bronze', 'silver', 'gold')
        category: Data category
        filename: File name (without extension)

        subcategory: Optional nested directory under the category
    
    Returns:
        Full path to output file
    
    Example:
        >>> get_output_path('bronze', 'market_data', 'exchange_rates_day')
        Path('.../data/1-bronze/dnb_statistics/market_data/exchange_rates_day.parquet')
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

    target_dir = category_dir
    if subcategory:
        target_dir = category_dir / subcategory
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # Always use .parquet extension
    extension = ".parquet"
    return target_dir / f"{filename}{extension}"


def categorize_endpoint(endpoint_name: str) -> str:
    """
    Determine category for an endpoint based on its name.
    
    Args:
        endpoint_name: Name of the endpoint (snake_case)
    
    Returns:
        Category name for organizing files
    """
    name_lower = endpoint_name.lower()
    
    # Check each category's keywords
    for keyword, category in ENDPOINT_CATEGORIES.items():
        if keyword in name_lower:
            return category
    
    # Default category for uncategorized endpoints
    return "other"


# Initialize directories on module import
ensure_directories()
