"""
Endpoint-specific extractors for DNB Public Register API

Each extractor handles one major endpoint category:
- Metadata (registers, languages)
- Organizations
- Publications
- Registrations
- Register Articles
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, AsyncIterator

# Add backend/clients to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir / "clients"))

from dnb_public_register.dnb_public_register_client import (
    DnbPublicRegisterClient,
)
from . import config
from .base import BaseExtractor, PaginatedExtractor

logger = logging.getLogger(__name__)


# ==========================================
# Metadata Extractors
# ==========================================

class RegistersExtractor(BaseExtractor):
    """Extract all available registers (metadata)."""
    
    def get_category(self) -> str:
        return "metadata"
    
    def get_output_filename(self) -> str:
        return "registers"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract all registers."""
        client = DnbPublicRegisterClient(self.request_adapter)
        
        logger.info("📋 Fetching all registers...")
        registers = await client.api.publicregister.registers.get()
        
        if not registers:
            logger.warning("No registers found")
            return
        
        logger.info(f"Found {len(registers)} registers")
        
        for register in registers:
            yield {
                "register_code": register.register_code,
                "register_name": register.register_name,
                "register_type": register.register_type,
            }


class SupportedLanguagesExtractor(BaseExtractor):
    """Extract all supported languages (metadata)."""
    
    def get_category(self) -> str:
        return "metadata"
    
    def get_output_filename(self) -> str:
        return "supported_languages"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract all supported languages."""
        client = DnbPublicRegisterClient(self.request_adapter)
        
        logger.info("🌐 Fetching supported languages...")
        languages = await client.api.publicregister.supported_languages.get()
        
        if not languages:
            logger.warning("No languages found")
            return
        
        logger.info(f"Found {len(languages)} languages")
        
        for language in languages:
            yield {
                "language_code": language.language_code,
                "language_name": language.language_name,
            }


# ==========================================
# Organizations Extractor
# ==========================================

class OrganizationsExtractor(PaginatedExtractor):
    """
    Extract organizations for all registers and languages.
    
    Creates separate files per register+language combination.
    """
    
    def __init__(
        self,
        register_code: str,
        language_code: str = config.DEFAULT_LANGUAGE,
    ):
        super().__init__()
        self.register_code = register_code
        self.language_code = language_code
    
    def get_category(self) -> str:
        return "entities"
    
    def get_output_filename(self) -> str:
        return (
            f"organizations_"
            f"{self.register_code.lower()}_"
            f"{self.language_code.lower()}"
        )
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract all organizations for this register."""
        url = (
            f"{config.DNB_BASE_URL}/api/publicregister/"
            f"{self.language_code}/Organizations"
        )
        
        logger.info(
            f"🏢 Extracting organizations: "
            f"register={self.register_code}, lang={self.language_code}"
        )
        
        # Organizations endpoint returns relation numbers
        async for record in self.extract_paginated(
            url=url,
            record_key="relationNumbers",  # DNB API uses this key
        ):
            yield {
                "register_code": self.register_code,
                "language_code": self.language_code,
                "relation_number": record.get("relationNumber"),
            }


# ==========================================
# Publications Extractors
# ==========================================

class PublicationsSearchExtractor(PaginatedExtractor):
    """
    Search publications with various criteria.
    
    Supports filtering by:
    - Register code (required)
    - Organization name (optional wildcard search)
    - Act article name (optional)
    """
    
    def __init__(
        self,
        register_code: str,
        language_code: str = config.DEFAULT_LANGUAGE,
        organization_name: str | None = None,
        act_article_name: str | None = None,
    ):
        super().__init__()
        self.register_code = register_code
        self.language_code = language_code
        self.organization_name = organization_name
        self.act_article_name = act_article_name
    
    def get_category(self) -> str:
        return "publications"
    
    def get_output_filename(self) -> str:
        parts = ["publications_search", self.register_code.lower()]
        
        if self.organization_name:
            # Sanitize for filename
            safe_name = self.organization_name.lower().replace(" ", "_")[:30]
            parts.append(safe_name)
        
        if self.act_article_name:
            safe_article = self.act_article_name.lower().replace(" ", "_")[:20]
            parts.append(safe_article)
        
        parts.append(self.language_code.lower())
        return "_".join(parts)
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Search publications with current criteria."""
        url = (
            f"{config.DNB_BASE_URL}/api/publicregister/"
            f"{self.language_code}/Publications/search"
        )
        
        # Build search parameters
        extra_params = {"RegisterCode": self.register_code}
        
        if self.organization_name:
            extra_params["OrganizationName"] = self.organization_name
        
        if self.act_article_name:
            extra_params["ActArticleName"] = self.act_article_name
        
        logger.info(
            f"📰 Searching publications: "
            f"register={self.register_code}, "
            f"org={self.organization_name or 'all'}, "
            f"article={self.act_article_name or 'all'}"
        )
        
        async for record in self.extract_paginated(
            url=url,
            extra_params=extra_params,
        ):
            # Flatten nested structures for Parquet
            yield {
                "register_code": self.register_code,
                "language_code": self.language_code,
                "relation_number": record.get("relationNumber"),
                "register_article_code": record.get("registerArticleCode"),
                "publication_date": record.get("publicationDate"),
                "valid_from_date": record.get("validFromDate"),
                "organization_name": record.get("organizationName"),
                "raw_json": str(record),  # Keep full record for reference
            }


class AllPublicationsExtractor(BaseExtractor):
    """
    Extract ALL publications across all registers.
    
    This is a convenience wrapper that:
    1. Discovers all registers
    2. Runs PublicationsSearchExtractor for each
    3. Combines results
    """
    
    def __init__(self, language_code: str = config.DEFAULT_LANGUAGE):
        super().__init__()
        self.language_code = language_code
    
    def get_category(self) -> str:
        return "publications"
    
    def get_output_filename(self) -> str:
        return f"all_publications_{self.language_code.lower()}"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract publications from all registers."""
        # First, get all register codes
        registers_extractor = RegistersExtractor()
        register_codes = []
        
        async for register in registers_extractor.extract():
            register_codes.append(register["register_code"])
        
        await registers_extractor.close()
        
        logger.info(f"Found {len(register_codes)} registers to process")
        
        # Extract publications for each register
        for register_code in register_codes:
            logger.info(f"\n🔍 Processing register: {register_code}")
            
            extractor = PublicationsSearchExtractor(
                register_code=register_code,
                language_code=self.language_code,
            )
            
            async for record in extractor.extract():
                yield record
            
            await extractor.close()


# ==========================================
# Registrations Extractor
# ==========================================

class RegistrationsExtractor(PaginatedExtractor):
    """
    Extract registrations for specific organizations.
    
    Requires register code and language code.
    """
    
    def __init__(
        self,
        register_code: str,
        language_code: str = config.DEFAULT_LANGUAGE,
    ):
        super().__init__()
        self.register_code = register_code
        self.language_code = language_code
    
    def get_category(self) -> str:
        return "registrations"
    
    def get_output_filename(self) -> str:
        return (
            f"registrations_"
            f"{self.register_code.lower()}_"
            f"{self.language_code.lower()}"
        )
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract all registrations for this register."""
        url = (
            f"{config.DNB_BASE_URL}/api/publicregister/"
            f"{self.language_code}/{self.register_code}/Registrations"
        )
        
        logger.info(
            f"📝 Extracting registrations: "
            f"register={self.register_code}, lang={self.language_code}"
        )
        
        async for record in self.extract_paginated(url=url):
            # Flatten for Parquet
            yield {
                "register_code": self.register_code,
                "language_code": self.language_code,
                "relation_number": record.get("relationNumber"),
                "registration_date": record.get("registrationDate"),
                "act_article_code": record.get("actArticleCode"),
                "act_article_name": record.get("actArticleName"),
                "status": record.get("status"),
                "raw_json": str(record),
            }


# ==========================================
# Register Articles Extractor
# ==========================================

class RegisterArticlesExtractor(PaginatedExtractor):
    """
    Extract register articles (regulatory framework metadata).
    """
    
    def __init__(
        self,
        register_code: str,
        language_code: str = config.DEFAULT_LANGUAGE,
    ):
        super().__init__()
        self.register_code = register_code
        self.language_code = language_code
    
    def get_category(self) -> str:
        return "regulatory"
    
    def get_output_filename(self) -> str:
        return (
            f"register_articles_"
            f"{self.register_code.lower()}_"
            f"{self.language_code.lower()}"
        )
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract all register articles."""
        url = (
            f"{config.DNB_BASE_URL}/api/publicregister/"
            f"{self.language_code}/{self.register_code}/RegisterArticles"
        )
        
        logger.info(
            f"⚖️  Extracting register articles: "
            f"register={self.register_code}, lang={self.language_code}"
        )
        
        async for record in self.extract_paginated(url=url):
            yield {
                "register_code": self.register_code,
                "language_code": self.language_code,
                "article_code": record.get("articleCode"),
                "article_name": record.get("articleName"),
                "article_description": record.get("articleDescription"),
                "raw_json": str(record),
            }
