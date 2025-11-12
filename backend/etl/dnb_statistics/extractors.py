"""
Endpoint-specific extractors for DNB Statistics API

Each extractor handles one specific endpoint from the Statistics API.
The Kiota-generated client provides type-safe access to all endpoints.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator, ClassVar

from .base import PaginatedExtractor
from . import config

logger = logging.getLogger(__name__)


class CategoryExtractor(PaginatedExtractor):
    """Base extractor that exposes category and optional subcategory."""

    CATEGORY: ClassVar[str] = "other"
    SUBCATEGORY: ClassVar[str | None] = None

    def get_category(self) -> str:
        return self.CATEGORY

    def get_subcategory(self) -> str | None:
        return self.SUBCATEGORY


class MarketDataExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "market_data"


class MacroeconomicExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "macroeconomic"


class FinancialStatementsExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "financial_statements"


class InsurancePensionsExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "insurance_pensions"


class InvestmentsExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "investments"


class LoansMortgagesExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "loans_mortgages"


class PaymentsExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "payments"


class OtherExtractor(CategoryExtractor):
    CATEGORY: ClassVar[str] = "other"


# ==========================================
# Market Data Extractors
# ==========================================

class ExchangeRatesDayExtractor(MarketDataExtractor):
    """Extract daily exchange rates of the euro and gold price."""

    SUBCATEGORY: ClassVar[str | None] = "exchange_rates"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_day"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_day"
        ):
            yield record


class ExchangeRatesMonthExtractor(MarketDataExtractor):
    """Extract monthly exchange rates of the euro and gold price."""

    SUBCATEGORY: ClassVar[str | None] = "exchange_rates"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_month"
        ):
            yield record


class ExchangeRatesQuarterExtractor(MarketDataExtractor):
    """Extract quarterly exchange rates of the euro and gold price."""

    SUBCATEGORY: ClassVar[str | None] = "exchange_rates"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_quarter"
        ):
            yield record


class MarketInterestRatesDayExtractor(MarketDataExtractor):
    """Extract daily market interest rates."""

    SUBCATEGORY: ClassVar[str | None] = "interest_rates"
    
    def get_output_filename(self) -> str:
        return "market_interest_rates_day"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "market_interest_rates_day"
        ):
            yield record


class MarketInterestRatesMonthExtractor(MarketDataExtractor):
    """Extract monthly market interest rates."""

    SUBCATEGORY: ClassVar[str | None] = "interest_rates"
    
    def get_output_filename(self) -> str:
        return "market_interest_rates_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "market_interest_rates_month"
        ):
            yield record


class ECBInterestRatesExtractor(MarketDataExtractor):
    """Extract European Central Bank interest rates."""

    SUBCATEGORY: ClassVar[str | None] = "interest_rates"
    
    def get_output_filename(self) -> str:
        return "ecb_interest_rates"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "european_central_bank_interest_rates"
        ):
            yield record


class ExchangeRatesYearAverageExtractor(MarketDataExtractor):
    """Extract yearly average exchange rates of the euro and gold price."""

    SUBCATEGORY: ClassVar[str | None] = "exchange_rates"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_year_average"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_year_average"
        ):
            yield record


class ExchangeRatesYearEndExtractor(MarketDataExtractor):
    """Extract year-end exchange rates of the euro and gold price."""

    SUBCATEGORY: ClassVar[str | None] = "exchange_rates"
    
    def get_output_filename(self) -> str:
        return "exchange_rates_year_end"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "exchange_rates_of_the_euro_and_gold_price_year_end_of_period"
        ):
            yield record


# ==========================================
# Macroeconomic Extractors
# ==========================================

class BalanceOfPaymentsQuarterExtractor(MacroeconomicExtractor):
    """Extract quarterly balance of payments data."""

    SUBCATEGORY: ClassVar[str | None] = "balance_of_payments"
    
    def get_output_filename(self) -> str:
        return "balance_of_payments_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_of_payments_quarter"
        ):
            yield record


class BalanceOfPaymentsYearExtractor(MacroeconomicExtractor):
    """Extract yearly balance of payments data."""

    SUBCATEGORY: ClassVar[str | None] = "balance_of_payments"
    
    def get_output_filename(self) -> str:
        return "balance_of_payments_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_of_payments_year"
        ):
            yield record


class MacroeconomicScoreboardQuarterExtractor(MacroeconomicExtractor):
    """Extract quarterly macroeconomic scoreboard data."""

    SUBCATEGORY: ClassVar[str | None] = "macroeconomic_scoreboard"
    
    def get_output_filename(self) -> str:
        return "macroeconomic_scoreboard_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "macroeconomic_scoreboard_quarter"
        ):
            yield record


class MacroeconomicScoreboardYearExtractor(MacroeconomicExtractor):
    """Extract yearly macroeconomic scoreboard data."""

    SUBCATEGORY: ClassVar[str | None] = "macroeconomic_scoreboard"
    
    def get_output_filename(self) -> str:
        return "macroeconomic_scoreboard_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "macroeconomic_scoreboard_year"
        ):
            yield record


class NetExternalAssetsQuarterExtractor(MacroeconomicExtractor):
    """Extract quarterly net external assets data."""

    SUBCATEGORY: ClassVar[str | None] = "net_external_assets"
    
    def get_output_filename(self) -> str:
        return "net_external_assets_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "net_external_assets_quarter"
        ):
            yield record


class NetExternalAssetsYearExtractor(MacroeconomicExtractor):
    """Extract yearly net external assets data."""

    SUBCATEGORY: ClassVar[str | None] = "net_external_assets"
    
    def get_output_filename(self) -> str:
        return "net_external_assets_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "net_external_assets_year"
        ):
            yield record


class GeographicalFDIIncomeExtractor(MacroeconomicExtractor):
    """Extract geographical distribution of inward and outward FDI income."""

    SUBCATEGORY: ClassVar[str | None] = "fdi_income"
    
    def get_output_filename(self) -> str:
        return "geographical_fdi_income"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "geographical_distribution_of_inward_and_outward_fdi_income"
        ):
            yield record


class KeyIndicatorsMonetaryStatsMonthExtractor(MacroeconomicExtractor):
    """Extract monthly key indicators of monetary statistics."""

    SUBCATEGORY: ClassVar[str | None] = "monetary_indicators"
    
    def get_output_filename(self) -> str:
        return "key_indicators_monetary_stats_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "key_indicators_monetary_statistics_month"
        ):
            yield record


# ==========================================
# Financial Statements Extractors
# ==========================================

class DNBBalanceSheetMonthExtractor(FinancialStatementsExtractor):
    """Extract monthly balance sheet of De Nederlandsche Bank."""

    SUBCATEGORY: ClassVar[str | None] = "dnb"
    
    def get_output_filename(self) -> str:
        return "dnb_balance_sheet_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted"
        ):
            yield record


class MFIBalanceSheetMonthExtractor(FinancialStatementsExtractor):
    """Extract monthly balance sheet of Dutch MFIs (not including DNB)."""

    SUBCATEGORY: ClassVar[str | None] = "mfis_banks"
    
    def get_output_filename(self) -> str:
        return "mfi_balance_sheet_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_sheet_of_dutch_based_mfis_not_including_dnb_month"
        ):
            yield record


class FinancialDataIndividualBanksHalfYearExtractor(FinancialStatementsExtractor):
    """Extract half-yearly financial data of individual banks."""

    SUBCATEGORY: ClassVar[str | None] = "mfis_banks"
    
    def get_output_filename(self) -> str:
        return "financial_data_individual_banks_half_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "financial_data_of_individual_banks_half_year"
        ):
            yield record


class MFIHouseholdInterestRatesMonthExtractor(FinancialStatementsExtractor):
    """Extract monthly MFI household deposits and loans interest rates."""

    SUBCATEGORY: ClassVar[str | None] = "mfis_banks"
    
    def get_output_filename(self) -> str:
        return "mfi_household_interest_rates_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "mfi_household_deposits_and_loans_interest_rates_month"
        ):
            yield record


class OtherFinancialIntermediariesBalanceSheetGeographyExtractor(FinancialStatementsExtractor):
    """Extract quarterly balance sheet of other financial intermediaries by geography."""

    SUBCATEGORY: ClassVar[str | None] = "other_financial_intermediaries"
    
    def get_output_filename(self) -> str:
        return "other_fi_balance_sheet_geography_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "balance_sheet_of_other_financial_intermediaries_by_geography_quarter"
        ):
            yield record


class OtherFinancialIntermediariesBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of other financial intermediaries."""

    SUBCATEGORY: ClassVar[str | None] = "other_financial_intermediaries"
    
    def get_output_filename(self) -> str:
        return "other_fi_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "other_financial_intermediaries_balance_sheet"
        ):
            yield record


class FinanceCompaniesBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of finance companies."""

    SUBCATEGORY: ClassVar[str | None] = "other_financial_intermediaries"
    
    def get_output_filename(self) -> str:
        return "finance_companies_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "finance_companies_balance_sheet"
        ):
            yield record


class SpecialisedFinancialInstitutionsBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of specialised financial institutions."""

    SUBCATEGORY: ClassVar[str | None] = "other_financial_intermediaries"
    
    def get_output_filename(self) -> str:
        return "specialised_fi_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "specialised_financial_institutions_balance_sheet"
        ):
            yield record


class SecuritiesDerivativesTradersBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of securities and derivatives traders."""

    SUBCATEGORY: ClassVar[str | None] = "other_financial_intermediaries"
    
    def get_output_filename(self) -> str:
        return "securities_derivatives_traders_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "securities_and_derivatives_traders_balance_sheet"
        ):
            yield record


class SecuritisationVehiclesBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of securitisation vehicles."""

    SUBCATEGORY: ClassVar[str | None] = "other_financial_intermediaries"
    
    def get_output_filename(self) -> str:
        return "securitisation_vehicles_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "securitisation_vehicles_balance_sheet"
        ):
            yield record


class FinancialAuxiliariesBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of financial auxiliaries."""

    SUBCATEGORY: ClassVar[str | None] = "financial_auxiliaries"
    
    def get_output_filename(self) -> str:
        return "financial_auxiliaries_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "financial_auxiliaries_balance_sheet"
        ):
            yield record


class FinancialAuxiliariesBalanceSheetGeographyExtractor(FinancialStatementsExtractor):
    """Extract quarterly balance sheet of financial auxiliaries by geography."""

    SUBCATEGORY: ClassVar[str | None] = "financial_auxiliaries"
    
    def get_output_filename(self) -> str:
        return "financial_auxiliaries_balance_sheet_geography_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "financial_auxiliaries_balance_sheet_by_geography_quarter"
        ):
            yield record


class HeadOfficesFinancialAuxiliariesBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of head offices of financial auxiliaries."""

    SUBCATEGORY: ClassVar[str | None] = "financial_auxiliaries"
    
    def get_output_filename(self) -> str:
        return "head_offices_financial_auxiliaries_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "head_offices_of_financial_auxiliaries_balance_sheet"
        ):
            yield record


class OtherFinancialAuxiliariesBalanceSheetExtractor(FinancialStatementsExtractor):
    """Extract balance sheet of other financial auxiliaries."""

    SUBCATEGORY: ClassVar[str | None] = "financial_auxiliaries"
    
    def get_output_filename(self) -> str:
        return "other_financial_auxiliaries_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "other_financial_auxiliaries_balance_sheet"
        ):
            yield record


# ==========================================
# Insurance & Pensions Extractors
# ==========================================

class PensionFundsBalanceSheetExtractor(InsurancePensionsExtractor):
    """Extract pension funds balance sheet data."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "pension_funds_balance_sheet"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "pension_funds_balance_sheet"
        ):
            yield record


class InsuranceCorpsBalanceSheetQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly insurance corporations balance sheet data."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "insurance_corps_balance_sheet_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "insurance_corporations_balance_sheet_quarter"
        ):
            yield record


class InsuranceCorpsAssetsDomesticCountersectorExtractor(InsurancePensionsExtractor):
    """Extract quarterly insurance corporation assets by domestic countersector."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "insurance_corps_assets_domestic_countersector_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "insurance_corporation_assets_and_liabilities_by_domestic_countersector_quarter"
        ):
            yield record


class InsuranceCorpsAssetsGeographyExtractor(InsurancePensionsExtractor):
    """Extract quarterly insurance corporation assets by geography."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "insurance_corps_assets_geography_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "insurance_corporation_assets_and_liabilities_by_geography_quarter"
        ):
            yield record


class InsurersCashFlowQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly insurers cash flow statement."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "insurers_cash_flow_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "insurers_cash_flow_statement_quarter"
        ):
            yield record


class SummaryInsuranceCorpsByTypeQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly summary balance sheet of insurance corporations by type."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "summary_insurance_corps_by_type_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "summary_balance_sheet_of_insurance_corporations_by_type_quarter"
        ):
            yield record


class LifeInsurersPremiumsClaimsCostsQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly premiums, claims and costs by line of business of life insurers."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "life_insurers_premiums_claims_costs_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_quarter"
        ):
            yield record


class LifeInsurersPremiumsClaimsCostsYearExtractor(InsurancePensionsExtractor):
    """Extract yearly premiums, claims and costs by line of business of life insurers."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "life_insurers_premiums_claims_costs_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_year"
        ):
            yield record


class NonLifeInsurersPremiumsClaimsCostsQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly premiums, claims and costs by line of business of non-life insurers."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "non_life_insurers_premiums_claims_costs_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_quarter"
        ):
            yield record


class NonLifeInsurersPremiumsClaimsCostsYearExtractor(InsurancePensionsExtractor):
    """Extract yearly premiums, claims and costs by line of business of non-life insurers."""

    SUBCATEGORY: ClassVar[str | None] = "insurers"
    
    def get_output_filename(self) -> str:
        return "non_life_insurers_premiums_claims_costs_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_year"
        ):
            yield record


class IndividualPensionFundDataQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly individual pension fund data."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "individual_pension_fund_data_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "individual_pension_fund_data_quarter"
        ):
            yield record


class PensionFundsAssetsDomesticCountersectorExtractor(InsurancePensionsExtractor):
    """Extract quarterly pension funds assets by domestic countersector."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "pension_funds_assets_domestic_countersector_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "pension_funds_assets_and_liabilities_by_domestic_countersector_quarter"
        ):
            yield record


class PensionFundsAssetsGeographyExtractor(InsurancePensionsExtractor):
    """Extract quarterly pension funds assets by geographical area."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "pension_funds_assets_geography_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "pension_funds_assets_and_liabilities_by_geographical_area_quarter"
        ):
            yield record


class PensionFundsBalanceSheetLookThroughExtractor(InsurancePensionsExtractor):
    """Extract quarterly pension funds balance sheet including look-through participation."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "pension_funds_balance_sheet_look_through_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter"
        ):
            yield record


class PensionFundsCashFlowQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly pension funds cash flow statement."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "pension_funds_cash_flow_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "pension_funds_cash_flow_statement_quarter"
        ):
            yield record


class SummaryPensionFundsByTypeQuarterExtractor(InsurancePensionsExtractor):
    """Extract quarterly summary balance sheet of pension funds by type."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "summary_pension_funds_by_type_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "summary_balance_sheet_of_pension_funds_by_type_quarter"
        ):
            yield record


class NominalIRTSPensionFundsZeroCouponExtractor(InsurancePensionsExtractor):
    """Extract nominal IRTS for pension funds zero coupon."""

    SUBCATEGORY: ClassVar[str | None] = "pension_funds"
    
    def get_output_filename(self) -> str:
        return "nominal_irts_pension_funds_zero_coupon"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "nominal_irts_for_pension_funds_zero_coupon"
        ):
            yield record


# ==========================================
# Investments & Securities Extractors
# ==========================================

class DutchHouseholdSavingsMonthExtractor(InvestmentsExtractor):
    """Extract monthly Dutch household savings data."""

    SUBCATEGORY: ClassVar[str | None] = "household_positions"
    
    def get_output_filename(self) -> str:
        return "dutch_household_savings_month"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_household_savings_month"
        ):
            yield record


class DutchSecuritiesHoldingsByHolderExtractor(InvestmentsExtractor):
    """Extract Dutch securities holdings by sector of the holder."""

    SUBCATEGORY: ClassVar[str | None] = "holdings_by_sector"
    
    def get_output_filename(self) -> str:
        return "dutch_securities_holdings_by_holder"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security"
        ):
            yield record


class DutchDebtSecuritiesHoldingsByHolderExtractor(InvestmentsExtractor):
    """Extract Dutch debt securities holdings by sector of the holder."""

    SUBCATEGORY: ClassVar[str | None] = "holdings_by_sector"
    
    def get_output_filename(self) -> str:
        return "dutch_debt_securities_holdings_by_holder"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_debt_securities_holdings_by_sector_of_the_holder"
        ):
            yield record


class DutchFundUnitHoldingsByHolderExtractor(InvestmentsExtractor):
    """Extract Dutch fund unit holdings by sector of the holder."""

    SUBCATEGORY: ClassVar[str | None] = "holdings_by_sector"
    
    def get_output_filename(self) -> str:
        return "dutch_fund_unit_holdings_by_holder"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_fund_unit_holdings_by_sector_of_the_holder"
        ):
            yield record


class DutchGovernmentPaperHoldingsExtractor(InvestmentsExtractor):
    """Extract Dutch government paper holdings."""

    SUBCATEGORY: ClassVar[str | None] = "holdings_geography"
    
    def get_output_filename(self) -> str:
        return "dutch_government_paper_holdings"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_government_paper_holdings"
        ):
            yield record


class DutchListedSharesHoldingsByHolderExtractor(InvestmentsExtractor):
    """Extract Dutch listed shares holdings by sector of the holder."""

    SUBCATEGORY: ClassVar[str | None] = "holdings_by_sector"
    
    def get_output_filename(self) -> str:
        return "dutch_listed_shares_holdings_by_holder"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_listed_shares_holdings_by_sector_of_the_holder"
        ):
            yield record


class DutchSecuritiesHoldingsByGeographyExtractor(InvestmentsExtractor):
    """Extract Dutch securities holdings by sector of the holder by geography."""

    SUBCATEGORY: ClassVar[str | None] = "holdings_geography"
    
    def get_output_filename(self) -> str:
        return "dutch_securities_holdings_by_geography"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "dutch_securities_holdings_by_sector_of_the_holder_by_geography"
        ):
            yield record


class NetDepositsInvestmentFundsQuarterExtractor(InvestmentsExtractor):
    """Extract quarterly net deposits in investment funds by sector of the holder."""

    SUBCATEGORY: ClassVar[str | None] = "fund_flows"
    
    def get_output_filename(self) -> str:
        return "net_deposits_investment_funds_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "net_deposits_in_investment_funds_by_sector_of_the_holder_quarter"
        ):
            yield record


class InvestmentsByHouseholdsAEXSharesExtractor(InvestmentsExtractor):
    """Extract investments by Dutch households in individual AEX shares."""

    SUBCATEGORY: ClassVar[str | None] = "household_positions"
    
    def get_output_filename(self) -> str:
        return "investments_by_households_aex_shares"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "investments_by_dutch_households_in_individual_aex_shares"
        ):
            yield record


class InvestmentsByHouseholdsSecuritiesByCategoryExtractor(InvestmentsExtractor):
    """Extract investments by Dutch households in securities by instrument category."""

    SUBCATEGORY: ClassVar[str | None] = "household_positions"
    
    def get_output_filename(self) -> str:
        return "investments_by_households_securities_by_category"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "investments_by_dutch_households_in_securities_by_instrument_category"
        ):
            yield record


class Top25InvestmentsHouseholdsInvestmentFundsExtractor(InvestmentsExtractor):
    """Extract the 25 largest investments by Dutch households in individual investment funds."""

    SUBCATEGORY: ClassVar[str | None] = "household_positions"
    
    def get_output_filename(self) -> str:
        return "top25_investments_households_investment_funds"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "the25_largest_investments_by_dutch_households_in_individual_investment_funds"
        ):
            yield record


class Top25InvestmentsListedSharesExtractor(InvestmentsExtractor):
    """Extract the 25 largest investments in individual listed shares."""

    SUBCATEGORY: ClassVar[str | None] = "household_positions"
    
    def get_output_filename(self) -> str:
        return "top25_investments_listed_shares"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "the25_largest_investments_in_individual_listed_shares"
        ):
            yield record


class HoldingBondsSustainabilityBySectorExtractor(InvestmentsExtractor):
    """Extract holding of bonds by type of sustainability characteristic by sector."""

    SUBCATEGORY: ClassVar[str | None] = "sustainable_finance"
    
    def get_output_filename(self) -> str:
        return "holding_bonds_sustainability_by_sector"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "holding_of_bonds_by_type_of_sustainability_characteristic_by_sector"
        ):
            yield record


class HoldingGreenBondsWithAssuranceExtractor(InvestmentsExtractor):
    """Extract holding of green bonds with external assurance by sector."""

    SUBCATEGORY: ClassVar[str | None] = "sustainable_finance"
    
    def get_output_filename(self) -> str:
        return "holding_green_bonds_with_assurance"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "holding_of_green_bonds_with_external_assurance_by_sector"
        ):
            yield record


class IssuanceBondsSustainabilityBySectorExtractor(InvestmentsExtractor):
    """Extract issuance of bonds by type of sustainability characteristic by sector."""

    SUBCATEGORY: ClassVar[str | None] = "sustainable_finance"
    
    def get_output_filename(self) -> str:
        return "issuance_bonds_sustainability_by_sector"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "issuance_of_bonds_by_type_of_sustainability_characteristic_by_sector"
        ):
            yield record


class IssuanceGreenBondsWithAssuranceExtractor(InvestmentsExtractor):
    """Extract issuance of green bonds with external assurance by sector."""

    SUBCATEGORY: ClassVar[str | None] = "sustainable_finance"
    
    def get_output_filename(self) -> str:
        return "issuance_green_bonds_with_assurance"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "issuance_of_green_bonds_with_external_assurance_by_sector"
        ):
            yield record


# ==========================================
# Loans & Mortgages Extractors
# ==========================================

class LoansByTypeSecuritisationQuarterExtractor(LoansMortgagesExtractor):
    """Extract quarterly loans by type and securitisation type."""

    SUBCATEGORY: ClassVar[str | None] = "securitisation"
    
    def get_output_filename(self) -> str:
        return "loans_by_type_securitisation_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "loans_by_type_and_securitisation_type_quarter"
        ):
            yield record


class ResidentialMortgagesBySectorExtractor(LoansMortgagesExtractor):
    """Extract residential mortgage loans provided to households by sector."""

    SUBCATEGORY: ClassVar[str | None] = "mortgages"
    
    def get_output_filename(self) -> str:
        return "residential_mortgages_by_sector"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "residential_mortgage_loans_provided_to_households_by_sector"
        ):
            yield record


class ResidentialMortgagesInstitutionalInvestorsQuarterExtractor(LoansMortgagesExtractor):
    """Extract quarterly residential mortgages provided by Dutch institutional investors."""

    SUBCATEGORY: ClassVar[str | None] = "mortgages"
    
    def get_output_filename(self) -> str:
        return "residential_mortgages_institutional_investors_quarter"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "residential_mortgages_provided_by_dutch_institutional_investors_to_dutch_households_quarter"
        ):
            yield record


# ==========================================
# Payments Extractors
# ==========================================

class PaymentTransactionsHalfYearExtractor(PaymentsExtractor):
    """Extract half-yearly payment transactions data."""

    SUBCATEGORY: ClassVar[str | None] = "transactions"
    
    def get_output_filename(self) -> str:
        return "payment_transactions_half_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "number_and_value_of_payment_transactions_half_year"
        ):
            yield record


class RetailPaymentTransactionsExtractor(PaymentsExtractor):
    """Extract retail payment transactions data."""

    SUBCATEGORY: ClassVar[str | None] = "transactions"
    
    def get_output_filename(self) -> str:
        return "retail_payment_transactions"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "number_and_value_of_retail_payment_transactions"
        ):
            yield record


class InfrastructureDomesticPaymentsHalfYearExtractor(PaymentsExtractor):
    """Extract half-yearly infrastructure domestic payments in units."""

    SUBCATEGORY: ClassVar[str | None] = "infrastructure"
    
    def get_output_filename(self) -> str:
        return "infrastructure_domestic_payments_half_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "infrastructure_domestic_payments_in_units_half_year"
        ):
            yield record


class InfrastructureRetailPaymentsUnitsExtractor(PaymentsExtractor):
    """Extract infrastructure of domestic retail payments units."""

    SUBCATEGORY: ClassVar[str | None] = "infrastructure"
    
    def get_output_filename(self) -> str:
        return "infrastructure_retail_payments_units"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "infrastructure_of_domestic_retail_payments_units"
        ):
            yield record


# ==========================================
# Other Extractors
# ==========================================

class StatutoryInterestRateHalfYearExtractor(OtherExtractor):
    """Extract half-yearly statutory interest rate."""
    
    def get_output_filename(self) -> str:
        return "statutory_interest_rate_half_year"
    
    async def extract(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self.extract_from_endpoint(
            "statutory_interest_rate_half_year"
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
    "exchange_rates_year_average": ExchangeRatesYearAverageExtractor,
    "exchange_rates_year_end": ExchangeRatesYearEndExtractor,
    "market_interest_rates_day": MarketInterestRatesDayExtractor,
    "market_interest_rates_month": MarketInterestRatesMonthExtractor,
    "ecb_interest_rates": ECBInterestRatesExtractor,
    
    # Macroeconomic
    "balance_of_payments_quarter": BalanceOfPaymentsQuarterExtractor,
    "balance_of_payments_year": BalanceOfPaymentsYearExtractor,
    "macroeconomic_scoreboard_quarter": MacroeconomicScoreboardQuarterExtractor,
    "macroeconomic_scoreboard_year": MacroeconomicScoreboardYearExtractor,
    "net_external_assets_quarter": NetExternalAssetsQuarterExtractor,
    "net_external_assets_year": NetExternalAssetsYearExtractor,
    "geographical_fdi_income": GeographicalFDIIncomeExtractor,
    "key_indicators_monetary_stats_month": KeyIndicatorsMonetaryStatsMonthExtractor,
    
    # Financial Statements - MFIs & Banks
    "dnb_balance_sheet_month": DNBBalanceSheetMonthExtractor,
    "mfi_balance_sheet_month": MFIBalanceSheetMonthExtractor,
    "financial_data_individual_banks_half_year": FinancialDataIndividualBanksHalfYearExtractor,
    "mfi_household_interest_rates_month": MFIHouseholdInterestRatesMonthExtractor,
    
    # Financial Statements - Other Financial Institutions
    "other_fi_balance_sheet_geography_quarter": OtherFinancialIntermediariesBalanceSheetGeographyExtractor,
    "other_fi_balance_sheet": OtherFinancialIntermediariesBalanceSheetExtractor,
    "finance_companies_balance_sheet": FinanceCompaniesBalanceSheetExtractor,
    "specialised_fi_balance_sheet": SpecialisedFinancialInstitutionsBalanceSheetExtractor,
    "securities_derivatives_traders_balance_sheet": SecuritiesDerivativesTradersBalanceSheetExtractor,
    "securitisation_vehicles_balance_sheet": SecuritisationVehiclesBalanceSheetExtractor,
    "financial_auxiliaries_balance_sheet": FinancialAuxiliariesBalanceSheetExtractor,
    "financial_auxiliaries_balance_sheet_geography_quarter": FinancialAuxiliariesBalanceSheetGeographyExtractor,
    "head_offices_financial_auxiliaries_balance_sheet": HeadOfficesFinancialAuxiliariesBalanceSheetExtractor,
    "other_financial_auxiliaries_balance_sheet": OtherFinancialAuxiliariesBalanceSheetExtractor,
    
    # Insurance & Pensions
    "pension_funds_balance_sheet": PensionFundsBalanceSheetExtractor,
    "insurance_corps_balance_sheet_quarter": InsuranceCorpsBalanceSheetQuarterExtractor,
    "insurance_corps_assets_domestic_countersector_quarter": InsuranceCorpsAssetsDomesticCountersectorExtractor,
    "insurance_corps_assets_geography_quarter": InsuranceCorpsAssetsGeographyExtractor,
    "insurers_cash_flow_quarter": InsurersCashFlowQuarterExtractor,
    "summary_insurance_corps_by_type_quarter": SummaryInsuranceCorpsByTypeQuarterExtractor,
    "life_insurers_premiums_claims_costs_quarter": LifeInsurersPremiumsClaimsCostsQuarterExtractor,
    "life_insurers_premiums_claims_costs_year": LifeInsurersPremiumsClaimsCostsYearExtractor,
    "non_life_insurers_premiums_claims_costs_quarter": NonLifeInsurersPremiumsClaimsCostsQuarterExtractor,
    "non_life_insurers_premiums_claims_costs_year": NonLifeInsurersPremiumsClaimsCostsYearExtractor,
    "individual_pension_fund_data_quarter": IndividualPensionFundDataQuarterExtractor,
    "pension_funds_assets_domestic_countersector_quarter": PensionFundsAssetsDomesticCountersectorExtractor,
    "pension_funds_assets_geography_quarter": PensionFundsAssetsGeographyExtractor,
    "pension_funds_balance_sheet_look_through_quarter": PensionFundsBalanceSheetLookThroughExtractor,
    "pension_funds_cash_flow_quarter": PensionFundsCashFlowQuarterExtractor,
    "summary_pension_funds_by_type_quarter": SummaryPensionFundsByTypeQuarterExtractor,
    "nominal_irts_pension_funds_zero_coupon": NominalIRTSPensionFundsZeroCouponExtractor,
    
    # Investments & Securities
    "dutch_household_savings_month": DutchHouseholdSavingsMonthExtractor,
    "dutch_securities_holdings_by_holder": DutchSecuritiesHoldingsByHolderExtractor,
    "dutch_debt_securities_holdings_by_holder": DutchDebtSecuritiesHoldingsByHolderExtractor,
    "dutch_fund_unit_holdings_by_holder": DutchFundUnitHoldingsByHolderExtractor,
    "dutch_government_paper_holdings": DutchGovernmentPaperHoldingsExtractor,
    "dutch_listed_shares_holdings_by_holder": DutchListedSharesHoldingsByHolderExtractor,
    "dutch_securities_holdings_by_geography": DutchSecuritiesHoldingsByGeographyExtractor,
    "net_deposits_investment_funds_quarter": NetDepositsInvestmentFundsQuarterExtractor,
    "investments_by_households_aex_shares": InvestmentsByHouseholdsAEXSharesExtractor,
    "investments_by_households_securities_by_category": InvestmentsByHouseholdsSecuritiesByCategoryExtractor,
    "top25_investments_households_investment_funds": Top25InvestmentsHouseholdsInvestmentFundsExtractor,
    "top25_investments_listed_shares": Top25InvestmentsListedSharesExtractor,
    "holding_bonds_sustainability_by_sector": HoldingBondsSustainabilityBySectorExtractor,
    "holding_green_bonds_with_assurance": HoldingGreenBondsWithAssuranceExtractor,
    "issuance_bonds_sustainability_by_sector": IssuanceBondsSustainabilityBySectorExtractor,
    "issuance_green_bonds_with_assurance": IssuanceGreenBondsWithAssuranceExtractor,
    
    # Loans & Mortgages
    "loans_by_type_securitisation_quarter": LoansByTypeSecuritisationQuarterExtractor,
    "residential_mortgages_by_sector": ResidentialMortgagesBySectorExtractor,
    "residential_mortgages_institutional_investors_quarter": ResidentialMortgagesInstitutionalInvestorsQuarterExtractor,
    
    # Payments
    "payment_transactions_half_year": PaymentTransactionsHalfYearExtractor,
    "retail_payment_transactions": RetailPaymentTransactionsExtractor,
    "infrastructure_domestic_payments_half_year": InfrastructureDomesticPaymentsHalfYearExtractor,
    "infrastructure_retail_payments_units": InfrastructureRetailPaymentsUnitsExtractor,
    
    # Other
    "statutory_interest_rate_half_year": StatutoryInterestRateHalfYearExtractor,
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
