"""
Endpoint-specific extractors for DNB Statistics API

Each extractor handles one specific endpoint from the Statistics API.
The Kiota-generated client provides type-safe access to all endpoints.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .base import PaginatedExtractor
from . import config

logger = logging.getLogger(__name__)


# ==========================================
# Market Data Extractors
# ==========================================

class ExchangeRatesDayExtractor(PaginatedExtractor):
    """Extract daily exchange rates of the euro and gold price."""
    
    def get_category(self) -> str:
        return "market_data"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_day"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_day"
        ):
            yield record


class ExchangeRatesMonthExtractor(PaginatedExtractor):
    """Extract monthly exchange rates of the euro and gold price."""
    
    def get_category(self) -> str:
        return "market_data"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_month"
        ):
            yield record


class ExchangeRatesQuarterExtractor(PaginatedExtractor):
    """Extract quarterly exchange rates of the euro and gold price."""
    
    def get_category(self) -> str:
        return "market_data"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_quarter"
        ):
            yield record


class MarketInterestRatesDayExtractor(PaginatedExtractor):
    """Extract daily market interest rates."""
    
    def get_category(self) -> str:
        return "market_data"
    
    def get_output_filename(self) -> str:
        return "market_interest_rates_day"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "market_interest_rates_day"
        ):
            yield record


class MarketInterestRatesMonthExtractor(PaginatedExtractor):
    """Extract monthly market interest rates."""
    
    def get_category(self) -> str:
        return "market_data"
    
    def get_output_filename(self) -> str:
        return "market_interest_rates_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "market_interest_rates_month"
        ):
            yield record


class ECBInterestRatesExtractor(PaginatedExtractor):
    """Extract European Central Bank interest rates."""
    
    def get_category(self) -> str:
        return "market_data"
    
    def get_output_filename(self) -> str:
        return "ecb_interest_rates"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "european_central_bank_interest_rates"
        ):
            yield record


# ==========================================
# Macroeconomic Extractors
# ==========================================

class BalanceOfPaymentsQuarterExtractor(PaginatedExtractor):
    """Extract quarterly balance of payments data."""
    
    def get_category(self) -> str:
        return "macroeconomic"
    
    def get_output_filename(self) -> str:
        return "balance_of_payments_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_of_payments_quarter"
        ):
            yield record


class BalanceOfPaymentsYearExtractor(PaginatedExtractor):
    """Extract yearly balance of payments data."""
    
    def get_category(self) -> str:
        return "macroeconomic"
    
    def get_output_filename(self) -> str:
        return "balance_of_payments_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_of_payments_year"
        ):
            yield record


class MacroeconomicScoreboardQuarterExtractor(PaginatedExtractor):
    """Extract quarterly macroeconomic scoreboard data."""
    
    def get_category(self) -> str:
        return "macroeconomic"
    
    def get_output_filename(self) -> str:
        return "macroeconomic_scoreboard_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "macroeconomic_scoreboard_quarter"
        ):
            yield record


# ==========================================
# Financial Statements Extractors
# ==========================================

class DNBBalanceSheetMonthExtractor(PaginatedExtractor):
    """Extract monthly balance sheet of De Nederlandsche Bank."""
    
    def get_category(self) -> str:
        return "financial_statements"
    
    def get_output_filename(self) -> str:
        return "dnb_balance_sheet_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted"
        ):
            yield record


class MFIBalanceSheetMonthExtractor(PaginatedExtractor):
    """Extract monthly balance sheet of Dutch MFIs (not including DNB)."""
    
    def get_category(self) -> str:
        return "financial_statements"
    
    def get_output_filename(self) -> str:
        return "mfi_balance_sheet_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_sheet_of_dutch_based_mfis_not_including_dnb_month"
        ):
            yield record


# ==========================================
# Insurance & Pensions Extractors
# ==========================================

class PensionFundsBalanceSheetExtractor(PaginatedExtractor):
    """Extract pension funds balance sheet data."""
    
    def get_category(self) -> str:
        return "insurance_pensions"
    
    def get_output_filename(self) -> str:
        return "pension_funds_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "pension_funds_balance_sheet"
        ):
            yield record


class InsuranceCorpsBalanceSheetQuarterExtractor(PaginatedExtractor):
    """Extract quarterly insurance corporations balance sheet data."""
    
    def get_category(self) -> str:
        return "insurance_pensions"
    
    def get_output_filename(self) -> str:
        return "insurance_corps_balance_sheet_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "insurance_corporations_balance_sheet_quarter"
        ):
            yield record


# ==========================================
# Investments & Securities Extractors
# ==========================================

class DutchHouseholdSavingsMonthExtractor(PaginatedExtractor):
    """Extract monthly Dutch household savings data."""
    
    def get_category(self) -> str:
        return "investments"
    
    def get_output_filename(self) -> str:
        return "dutch_household_savings_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_household_savings_month"
        ):
            yield record


class DutchSecuritiesHoldingsByHolderExtractor(PaginatedExtractor):
    """Extract Dutch securities holdings by sector of the holder."""
    
    def get_category(self) -> str:
        return "investments"
    
    def get_output_filename(self) -> str:
        return "dutch_securities_holdings_by_holder"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security"
        ):
            yield record


# ==========================================
# Payments Extractors
# ==========================================

class PaymentTransactionsHalfYearExtractor(PaginatedExtractor):
    """Extract half-yearly payment transactions data."""
    
    def get_category(self) -> str:
        return "payments"
    
    def get_output_filename(self) -> str:
        return "payment_transactions_half_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "number_and_value_of_payment_transactions_half_year"
        ):
            yield record


class RetailPaymentTransactionsExtractor(PaginatedExtractor):
    """Extract retail payment transactions data."""
    
    def get_category(self) -> str:
        return "payments"
    
    def get_output_filename(self) -> str:
        return "retail_payment_transactions"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "number_and_value_of_retail_payment_transactions"
        ):
            yield record


# ==========================================
# Extractor Registry
# ==========================================

# Map endpoint names to extractor classes for easy lookup
EXTRACTOR_REGISTRY: dict[str, type[PaginatedExtractor]] = {
    # Market Data
    "exchange_rates_day": ExchangeRatesDayExtractor,
    "exchange_rates_month": ExchangeRatesMonthExtractor,
    "exchange_rates_quarter": ExchangeRatesQuarterExtractor,
    "market_interest_rates_day": MarketInterestRatesDayExtractor,
    "market_interest_rates_month": MarketInterestRatesMonthExtractor,
    "ecb_interest_rates": ECBInterestRatesExtractor,
    
    # Macroeconomic
    "balance_of_payments_quarter": BalanceOfPaymentsQuarterExtractor,
    "balance_of_payments_year": BalanceOfPaymentsYearExtractor,
    "macroeconomic_scoreboard_quarter": MacroeconomicScoreboardQuarterExtractor,
    
    # Financial Statements
    "dnb_balance_sheet_month": DNBBalanceSheetMonthExtractor,
    "mfi_balance_sheet_month": MFIBalanceSheetMonthExtractor,
    
    # Insurance & Pensions
    "pension_funds_balance_sheet": PensionFundsBalanceSheetExtractor,
    "insurance_corps_balance_sheet_quarter": InsuranceCorpsBalanceSheetQuarterExtractor,
    
    # Investments & Securities
    "dutch_household_savings_month": DutchHouseholdSavingsMonthExtractor,
    "dutch_securities_holdings_by_holder": DutchSecuritiesHoldingsByHolderExtractor,
    
    # Payments
    "payment_transactions_half_year": PaymentTransactionsHalfYearExtractor,
    "retail_payment_transactions": RetailPaymentTransactionsExtractor,
}


def get_extractor(endpoint_name: str) -> PaginatedExtractor:
    """
    Get an extractor instance for a specific endpoint.
    
    Args:
        endpoint_name: Name of the endpoint (from registry keys)
    
    Returns:
        Extractor instance
    
    Raises:
        ValueError: If endpoint name is not in registry
    """
    extractor_class = EXTRACTOR_REGISTRY.get(endpoint_name)
    if not extractor_class:
        raise ValueError(
            f"Unknown endpoint: {endpoint_name}. "
            f"Available: {', '.join(EXTRACTOR_REGISTRY.keys())}"
        )
    return extractor_class()


def list_available_endpoints() -> list[str]:
    """Get list of all available endpoint names."""
    return sorted(EXTRACTOR_REGISTRY.keys())
