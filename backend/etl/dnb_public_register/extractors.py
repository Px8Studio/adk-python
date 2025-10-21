"""
Endpoint-specific extractors for DNB Public Register API

Each extractor handles one major endpoint category:
- Metadata (registers, languages)
- Organizations (relation numbers and full details)
- Publications (search and direct access)
- Registrations (act article names)
- Register Articles
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, AsyncIterator

# Add backend/clients to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir / "clients"))

from public_register_client import DnbPublicRegisterClient
from kiota_abstractions.base_request_configuration import RequestConfiguration
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
        registers = await self.call_api_with_retry(
            lambda: client.api.publicregister.registers.get()
        )
        
        if not registers:
            logger.warning("No registers found")
            return
        
        logger.info(f"Found {len(registers)} registers")
        
        for register in registers:
            yield {
                "register_code": register.code,
                "register_name": register.name,
                "register_type": str(register.type) if register.type else None,
                "last_publish_date": str(register.last_publish_date) if register.last_publish_date else None,
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
        languages = await self.call_api_with_retry(
            lambda: client.api.publicregister.supported_languages.get()
        )
        
        if not languages:
            logger.warning("No languages found")
            return
        
        logger.info(f"Found {len(languages)} languages")
        
        for language in languages:
            yield {
                "language_code": language.code,
            }


# ==========================================
# Organizations Extractors
# ==========================================

class OrganizationRelationNumbersExtractor(PaginatedExtractor):
    """
    Extract organization relation numbers (latest) for a specific register.
    
    Endpoint: GET /api/publicregister/{registerCode}/Organizations
    Returns: List of relation numbers only (lightweight)
    """
    
    def __init__(self, register_code: str):
        super().__init__()
        self.register_code = register_code
    
    def get_category(self) -> str:
        return "organizations"
    
    def get_output_filename(self) -> str:
        return f"relation_numbers_{self.register_code.lower()}"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract relation numbers for this register using paginated endpoint."""
        url = (
            f"{config.DNB_BASE_URL}/api/publicregister/"
            f"{self.register_code}/Organizations"
        )
        
        logger.info(
            f"🔢 Extracting relation numbers: register={self.register_code}"
        )
        
        # This endpoint returns OrganizationRelationNumbersView with pagination
        async for record in self.extract_paginated(
            url=url,
            record_key="relationNumbers",
        ):
            yield {
                "register_code": self.register_code,
                "relation_number": record.get("relationNumber"),
            }


class OrganizationDetailsExtractor(BaseExtractor):
    """
    Extract full organization details using Kiota client.
    
    Endpoint: GET /api/publicregister/{languageCode}/{registerCode}/Organizations
    Returns: Complete organization data (names, addresses, registrations, etc.)
    
    This is the MOST IMPORTANT extractor - it gets all the rich data.
    """
    
    def __init__(
        self,
        register_code: str,
        relation_numbers: list[str],
        language_code: str = config.DEFAULT_LANGUAGE,
    ):
        super().__init__()
        self.register_code = register_code
        self.relation_numbers = relation_numbers
        self.language_code = language_code
    
    def get_category(self) -> str:
        return "organizations"
    
    def get_output_filename(self) -> str:
        return (
            f"organization_details_"
            f"{self.register_code.lower()}_"
            f"{self.language_code.lower()}"
        )
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract full organization details."""
        client = DnbPublicRegisterClient(self.request_adapter)
        
        logger.info(
            f"🏢 Extracting organization details: "
            f"register={self.register_code}, "
            f"lang={self.language_code}, "
            f"count={len(self.relation_numbers)}"
        )
        
        # API allows max 25 relation numbers per request
        batch_size = 25
        
        for i in range(0, len(self.relation_numbers), batch_size):
            batch = self.relation_numbers[i:i + batch_size]
            
            logger.info(
                f"  📦 Batch {i//batch_size + 1}: "
                f"Fetching {len(batch)} organizations..."
            )
            
            # Build request configuration with query parameters
            request_config = RequestConfiguration()
            request_config.query_parameters = (
                client.api
                .publicregister
                .by_language_code_id(self.language_code)
                .by_register_code(self.register_code)
                .organizations
                .OrganizationsRequestBuilderGetQueryParameters(
                    relation_numbers=batch
                )
            )
            
            # Use Kiota client with rate limiting and retry
            result = await self.call_api_with_retry(
                lambda: (
                    client.api
                    .publicregister
                    .by_language_code_id(self.language_code)
                    .by_register_code(self.register_code)
                    .organizations
                    .get(request_config)
                )
            )
            
            if not result or not result.organizations:
                logger.warning(f"No organizations returned for batch {i//batch_size + 1}")
                continue
            
            # Process each organization
            for org in result.organizations:
                yield self._flatten_organization(org)
    
    def _flatten_organization(self, org: Any) -> dict[str, Any]:
        """Flatten organization object for Parquet storage."""
        # Extract basic fields
        flattened = {
            "register_code": self.register_code,
            "language_code": self.language_code,
            "relation_number": org.relation_number,
            "chamber_of_commerce": org.chamber_of_commerce,
            "branch_number": org.branch_number,
            "legal_duration": org.legal_duration,
            "statutory_place": org.statutory_place,
            "statutory_country": org.statutory_country,
            "rsin_code": org.rsin_code,
            "lei_code": org.lei_code,
            "is_in_liquidation": org.is_in_liquidation,
            "date_of_liquidation": str(org.date_of_liquidation) if org.date_of_liquidation else None,
            "is_main": org.is_main,
        }
        
        # Store complex nested data as JSON strings for Parquet
        if org.official_names:
            flattened["official_names_json"] = json.dumps(
                [self._serialize_name(n) for n in org.official_names]
            )
        
        if org.statutory_names:
            flattened["statutory_names_json"] = json.dumps(
                [self._serialize_name(n) for n in org.statutory_names]
            )
        
        if org.trade_names:
            flattened["trade_names_json"] = json.dumps(
                [self._serialize_name(n) for n in org.trade_names]
            )
        
        if org.contact_channels:
            flattened["contact_channels_json"] = json.dumps(
                [self._serialize_contact(c) for c in org.contact_channels]
            )
        
        if org.registrations:
            flattened["registrations_json"] = json.dumps(
                [self._serialize_registration(r) for r in org.registrations]
            )
        
        if org.classifications:
            flattened["classifications_json"] = json.dumps(
                [c.name for c in org.classifications if c.name]
            )
        
        return flattened
    
    def _serialize_name(self, name_obj: Any) -> dict[str, Any]:
        """Serialize name object."""
        return {
            "name": name_obj.name,
            "validity_period_start_date": str(name_obj.validity_period_start_date) if name_obj.validity_period_start_date else None,
            "validity_period_end_date": str(name_obj.validity_period_end_date) if name_obj.validity_period_end_date else None,
        }
    
    def _serialize_contact(self, contact_obj: Any) -> dict[str, Any]:
        """Serialize contact channel object."""
        return {
            "contact_channel_type": contact_obj.contact_channel_type,
            "street": contact_obj.street,
            "house_number": contact_obj.house_number,
            "house_number_addition": contact_obj.house_number_addition,
            "postal_code": contact_obj.postal_code,
            "city": contact_obj.city,
            "country_iso_code": contact_obj.country_iso_code,
            "email_address": contact_obj.email_address,
            "url": contact_obj.url,
            "phone_number": contact_obj.phone_number,
        }
    
    def _serialize_registration(self, reg_obj: Any) -> dict[str, Any]:
        """Serialize registration object."""
        return {
            "id": str(reg_obj.id) if reg_obj.id else None,
            "act_article_name": reg_obj.act_article_name,
            "act_article_code": reg_obj.act_article_code,
            "validity_period_start_date": str(reg_obj.validity_period_start_date) if reg_obj.validity_period_start_date else None,
            "validity_period_end_date": str(reg_obj.validity_period_end_date) if reg_obj.validity_period_end_date else None,
            "registration_type": reg_obj.registration_type,
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


class PublicationDetailsExtractor(PaginatedExtractor):
    """
    Extract latest publication details directly (not via search).
    
    Endpoint: GET /api/publicregister/{languageCode}/Publications/{registerCode}
    Returns: Full publication with all organizations (paginated)
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
        return "publications"
    
    def get_output_filename(self) -> str:
        return (
            f"publication_direct_"
            f"{self.register_code.lower()}_"
            f"{self.language_code.lower()}"
        )
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract publication directly using Kiota client."""
        client = DnbPublicRegisterClient(self.request_adapter)
        
        logger.info(
            f"📰 Extracting publication (direct): "
            f"register={self.register_code}, lang={self.language_code}"
        )
        
        # Use Kiota client for paginated access
        page = 1
        has_more = True
        
        while has_more:
            query_params = type(
                'QueryParams',
                (),
                {'page': page, 'page_size': config.DEFAULT_PAGE_SIZE}
            )()
            
            request_config = RequestConfiguration(
                query_parameters=query_params
            )
            
            result = await self.call_api_with_retry(
                lambda: (
                    client.api
                    .publicregister
                    .by_language_code_id(self.language_code)
                    .publications
                    .by_register_code(self.register_code)
                    .get(request_config)
                )
            )
            
            if not result or not result.organizations:
                logger.info("No more organizations in publication")
                break
            
            logger.info(
                f"  Page {page}: {len(result.organizations)} organizations"
            )
            
            for org in result.organizations:
                yield {
                    "register_code": self.register_code,
                    "language_code": self.language_code,
                    "publish_date": str(result.publish_date) if result.publish_date else None,
                    "relation_number": org.relation_number,
                    "organization_json": json.dumps(
                        self._serialize_org_summary(org)
                    ),
                }
            
            # Check if more pages exist
            has_more = (
                result._metadata
                and result._metadata.has_more_pages
            )
            page += 1
    
    def _serialize_org_summary(self, org: Any) -> dict[str, Any]:
        """Serialize organization summary from publication."""
        return {
            "relation_number": org.relation_number,
            "chamber_of_commerce": org.chamber_of_commerce,
            "is_main": org.is_main,
        }


# ==========================================
# Registrations Extractors
# ==========================================

class RegistrationActArticleNamesExtractor(BaseExtractor):
    """
    Extract distinct act article names for registrations (latest).
    
    Endpoint: GET /api/publicregister/{languageCode}/{registerCode}/Registrations/ActArticleNames
    Returns: List of unique act article names used in registrations
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
            f"act_article_names_"
            f"{self.register_code.lower()}_"
            f"{self.language_code.lower()}"
        )
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        """Extract act article names using Kiota client."""
        client = DnbPublicRegisterClient(self.request_adapter)
        
        logger.info(
            f"📝 Extracting act article names: "
            f"register={self.register_code}, lang={self.language_code}"
        )
        
        result = await self.call_api_with_retry(
            lambda: (
                client.api
                .publicregister
                .by_language_code_id(self.language_code)
                .by_register_code(self.register_code)
                .registrations
                .act_article_names
                .get()
            )
        )
        
        if not result:
            logger.warning("No act article names found")
            return
        
        logger.info(f"Found {len(result)} act article names")
        
        for article in result:
            yield {
                "register_code": self.register_code,
                "language_code": self.language_code,
                "act_article_name": article.act_article_name,
            }


# ==========================================
# Register Articles Extractor
# ==========================================

class RegisterArticlesExtractor(BaseExtractor):
    """
    Extract register articles (regulatory framework metadata).
    
    Endpoint: GET /api/publicregister/{languageCode}/{registerCode}/RegisterArticles
    Returns: List of all act articles configured for this register
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
        """Extract all register articles using Kiota client."""
        client = DnbPublicRegisterClient(self.request_adapter)
        
        logger.info(
            f"⚖️  Extracting register articles: "
            f"register={self.register_code}, lang={self.language_code}"
        )
        
        result = await self.call_api_with_retry(
            lambda: (
                client.api
                .publicregister
                .by_language_code_id(self.language_code)
                .by_register_code(self.register_code)
                .register_articles
                .get()
            )
        )
        
        if not result:
            logger.warning("No register articles found")
            return
        
        logger.info(f"Found {len(result)} register articles")
        
        for article in result:
            yield {
                "register_code": self.register_code,
                "language_code": self.language_code,
                "act_article_code": article.act_article_code,
                "act_article_name": article.act_article_name,
            }
