from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.api_client_builder import enable_backing_store_for_serialization_writer_factory, register_default_deserializer, register_default_serializer
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import ParseNodeFactoryRegistry, SerializationWriterFactoryRegistry
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory
from kiota_serialization_form.form_serialization_writer_factory import FormSerializationWriterFactory
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from kiota_serialization_multipart.multipart_serialization_writer_factory import MultipartSerializationWriterFactory
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer_factory import TextSerializationWriterFactory
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .balance_of_payments_quarter.balance_of_payments_quarter_request_builder import BalanceOfPaymentsQuarterRequestBuilder
    from .balance_of_payments_year.balance_of_payments_year_request_builder import BalanceOfPaymentsYearRequestBuilder
    from .balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted.balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted_request_builder import BalanceSheetOfDeNederlandscheBankMonthNonBreakAdjustedRequestBuilder
    from .balance_sheet_of_dutch_based_mfis_not_including_dnb_month.balance_sheet_of_dutch_based_mfis_not_including_dnb_month_request_builder import BalanceSheetOfDutchBasedMfisNotIncludingDnbMonthRequestBuilder
    from .balance_sheet_of_other_financial_intermediaries_by_geography_quarter.balance_sheet_of_other_financial_intermediaries_by_geography_quarter_request_builder import BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRequestBuilder
    from .dutch_debt_securities_holdings_by_sector_of_the_holder.dutch_debt_securities_holdings_by_sector_of_the_holder_request_builder import DutchDebtSecuritiesHoldingsBySectorOfTheHolderRequestBuilder
    from .dutch_fund_unit_holdings_by_sector_of_the_holder.dutch_fund_unit_holdings_by_sector_of_the_holder_request_builder import DutchFundUnitHoldingsBySectorOfTheHolderRequestBuilder
    from .dutch_government_paper_holdings.dutch_government_paper_holdings_request_builder import DutchGovernmentPaperHoldingsRequestBuilder
    from .dutch_household_savings_month.dutch_household_savings_month_request_builder import DutchHouseholdSavingsMonthRequestBuilder
    from .dutch_listed_shares_holdings_by_sector_of_the_holder.dutch_listed_shares_holdings_by_sector_of_the_holder_request_builder import DutchListedSharesHoldingsBySectorOfTheHolderRequestBuilder
    from .dutch_securities_holdings_by_sector_of_the_holder_by_geography.dutch_securities_holdings_by_sector_of_the_holder_by_geography_request_builder import DutchSecuritiesHoldingsBySectorOfTheHolderByGeographyRequestBuilder
    from .dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security.dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security_request_builder import DutchSecuritiesHoldingsBySectorOfTheHolderByTypeOfSecurityRequestBuilder
    from .european_central_bank_interest_rates.european_central_bank_interest_rates_request_builder import EuropeanCentralBankInterestRatesRequestBuilder
    from .exchange_rates_of_the_euro_and_gold_price_day.exchange_rates_of_the_euro_and_gold_price_day_request_builder import ExchangeRatesOfTheEuroAndGoldPriceDayRequestBuilder
    from .exchange_rates_of_the_euro_and_gold_price_month.exchange_rates_of_the_euro_and_gold_price_month_request_builder import ExchangeRatesOfTheEuroAndGoldPriceMonthRequestBuilder
    from .exchange_rates_of_the_euro_and_gold_price_quarter.exchange_rates_of_the_euro_and_gold_price_quarter_request_builder import ExchangeRatesOfTheEuroAndGoldPriceQuarterRequestBuilder
    from .exchange_rates_of_the_euro_and_gold_price_year_average.exchange_rates_of_the_euro_and_gold_price_year_average_request_builder import ExchangeRatesOfTheEuroAndGoldPriceYearAverageRequestBuilder
    from .exchange_rates_of_the_euro_and_gold_price_year_end_of_period.exchange_rates_of_the_euro_and_gold_price_year_end_of_period_request_builder import ExchangeRatesOfTheEuroAndGoldPriceYearEndOfPeriodRequestBuilder
    from .finance_companies_balance_sheet.finance_companies_balance_sheet_request_builder import FinanceCompaniesBalanceSheetRequestBuilder
    from .financial_auxiliaries_balance_sheet.financial_auxiliaries_balance_sheet_request_builder import FinancialAuxiliariesBalanceSheetRequestBuilder
    from .financial_auxiliaries_balance_sheet_by_geography_quarter.financial_auxiliaries_balance_sheet_by_geography_quarter_request_builder import FinancialAuxiliariesBalanceSheetByGeographyQuarterRequestBuilder
    from .financial_data_of_individual_banks_half_year.financial_data_of_individual_banks_half_year_request_builder import FinancialDataOfIndividualBanksHalfYearRequestBuilder
    from .geographical_distribution_of_inward_and_outward_fdi_income.geographical_distribution_of_inward_and_outward_fdi_income_request_builder import GeographicalDistributionOfInwardAndOutwardFdiIncomeRequestBuilder
    from .head_offices_of_financial_auxiliaries_balance_sheet.head_offices_of_financial_auxiliaries_balance_sheet_request_builder import HeadOfficesOfFinancialAuxiliariesBalanceSheetRequestBuilder
    from .holding_of_bonds_by_type_of_sustainability_characteristic_by_sector.holding_of_bonds_by_type_of_sustainability_characteristic_by_sector_request_builder import HoldingOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder
    from .holding_of_green_bonds_with_external_assurance_by_sector.holding_of_green_bonds_with_external_assurance_by_sector_request_builder import HoldingOfGreenBondsWithExternalAssuranceBySectorRequestBuilder
    from .individual_pension_fund_data_quarter.individual_pension_fund_data_quarter_request_builder import IndividualPensionFundDataQuarterRequestBuilder
    from .infrastructure_domestic_payments_in_units_half_year.infrastructure_domestic_payments_in_units_half_year_request_builder import InfrastructureDomesticPaymentsInUnitsHalfYearRequestBuilder
    from .infrastructure_of_domestic_retail_payments_units.infrastructure_of_domestic_retail_payments_units_request_builder import InfrastructureOfDomesticRetailPaymentsUnitsRequestBuilder
    from .insurance_corporations_balance_sheet_quarter.insurance_corporations_balance_sheet_quarter_request_builder import InsuranceCorporationsBalanceSheetQuarterRequestBuilder
    from .insurance_corporation_assets_and_liabilities_by_domestic_countersector_quarter.insurance_corporation_assets_and_liabilities_by_domestic_countersector_quarter_request_builder import InsuranceCorporationAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder
    from .insurance_corporation_assets_and_liabilities_by_geography_quarter.insurance_corporation_assets_and_liabilities_by_geography_quarter_request_builder import InsuranceCorporationAssetsAndLiabilitiesByGeographyQuarterRequestBuilder
    from .insurers_cash_flow_statement_quarter.insurers_cash_flow_statement_quarter_request_builder import InsurersCashFlowStatementQuarterRequestBuilder
    from .investments_by_dutch_households_in_individual_aex_shares.investments_by_dutch_households_in_individual_aex_shares_request_builder import InvestmentsByDutchHouseholdsInIndividualAexSharesRequestBuilder
    from .investments_by_dutch_households_in_securities_by_instrument_category.investments_by_dutch_households_in_securities_by_instrument_category_request_builder import InvestmentsByDutchHouseholdsInSecuritiesByInstrumentCategoryRequestBuilder
    from .issuance_of_bonds_by_type_of_sustainability_characteristic_by_sector.issuance_of_bonds_by_type_of_sustainability_characteristic_by_sector_request_builder import IssuanceOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder
    from .issuance_of_green_bonds_with_external_assurance_by_sector.issuance_of_green_bonds_with_external_assurance_by_sector_request_builder import IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder
    from .key_indicators_monetary_statistics_month.key_indicators_monetary_statistics_month_request_builder import KeyIndicatorsMonetaryStatisticsMonthRequestBuilder
    from .loans_by_type_and_securitisation_type_quarter.loans_by_type_and_securitisation_type_quarter_request_builder import LoansByTypeAndSecuritisationTypeQuarterRequestBuilder
    from .macroeconomic_scoreboard_quarter.macroeconomic_scoreboard_quarter_request_builder import MacroeconomicScoreboardQuarterRequestBuilder
    from .macroeconomic_scoreboard_year.macroeconomic_scoreboard_year_request_builder import MacroeconomicScoreboardYearRequestBuilder
    from .market_interest_rates_day.market_interest_rates_day_request_builder import MarketInterestRatesDayRequestBuilder
    from .market_interest_rates_month.market_interest_rates_month_request_builder import MarketInterestRatesMonthRequestBuilder
    from .mfi_household_deposits_and_loans_interest_rates_month.mfi_household_deposits_and_loans_interest_rates_month_request_builder import MfiHouseholdDepositsAndLoansInterestRatesMonthRequestBuilder
    from .net_deposits_in_investment_funds_by_sector_of_the_holder_quarter.net_deposits_in_investment_funds_by_sector_of_the_holder_quarter_request_builder import NetDepositsInInvestmentFundsBySectorOfTheHolderQuarterRequestBuilder
    from .net_external_assets_quarter.net_external_assets_quarter_request_builder import NetExternalAssetsQuarterRequestBuilder
    from .net_external_assets_year.net_external_assets_year_request_builder import NetExternalAssetsYearRequestBuilder
    from .nominal_irts_for_pension_funds_zero_coupon.nominal_irts_for_pension_funds_zero_coupon_request_builder import NominalIrtsForPensionFundsZeroCouponRequestBuilder
    from .number_and_value_of_payment_transactions_half_year.number_and_value_of_payment_transactions_half_year_request_builder import NumberAndValueOfPaymentTransactionsHalfYearRequestBuilder
    from .number_and_value_of_retail_payment_transactions.number_and_value_of_retail_payment_transactions_request_builder import NumberAndValueOfRetailPaymentTransactionsRequestBuilder
    from .other_financial_auxiliaries_balance_sheet.other_financial_auxiliaries_balance_sheet_request_builder import OtherFinancialAuxiliariesBalanceSheetRequestBuilder
    from .other_financial_intermediaries_balance_sheet.other_financial_intermediaries_balance_sheet_request_builder import OtherFinancialIntermediariesBalanceSheetRequestBuilder
    from .pension_funds_assets_and_liabilities_by_domestic_countersector_quarter.pension_funds_assets_and_liabilities_by_domestic_countersector_quarter_request_builder import PensionFundsAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder
    from .pension_funds_assets_and_liabilities_by_geographical_area_quarter.pension_funds_assets_and_liabilities_by_geographical_area_quarter_request_builder import PensionFundsAssetsAndLiabilitiesByGeographicalAreaQuarterRequestBuilder
    from .pension_funds_balance_sheet.pension_funds_balance_sheet_request_builder import PensionFundsBalanceSheetRequestBuilder
    from .pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter.pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter_request_builder import PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder
    from .pension_funds_cash_flow_statement_quarter.pension_funds_cash_flow_statement_quarter_request_builder import PensionFundsCashFlowStatementQuarterRequestBuilder
    from .premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_quarter.premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_quarter_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiQuarterRequestBuilder
    from .premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_year.premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_year_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiYearRequestBuilder
    from .premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_quarter.premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_quarter_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiQuarterRequestBuilder
    from .premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_year.premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_year_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRequestBuilder
    from .residential_mortgages_provided_by_dutch_institutional_investors_to_dutch_households_quarter.residential_mortgages_provided_by_dutch_institutional_investors_to_dutch_households_quarter_request_builder import ResidentialMortgagesProvidedByDutchInstitutionalInvestorsToDutchHouseholdsQuarterRequestBuilder
    from .residential_mortgage_loans_provided_to_households_by_sector.residential_mortgage_loans_provided_to_households_by_sector_request_builder import ResidentialMortgageLoansProvidedToHouseholdsBySectorRequestBuilder
    from .securities_and_derivatives_traders_balance_sheet.securities_and_derivatives_traders_balance_sheet_request_builder import SecuritiesAndDerivativesTradersBalanceSheetRequestBuilder
    from .securitisation_vehicles_balance_sheet.securitisation_vehicles_balance_sheet_request_builder import SecuritisationVehiclesBalanceSheetRequestBuilder
    from .specialised_financial_institutions_balance_sheet.specialised_financial_institutions_balance_sheet_request_builder import SpecialisedFinancialInstitutionsBalanceSheetRequestBuilder
    from .statutory_interest_rate_half_year.statutory_interest_rate_half_year_request_builder import StatutoryInterestRateHalfYearRequestBuilder
    from .summary_balance_sheet_of_insurance_corporations_by_type_quarter.summary_balance_sheet_of_insurance_corporations_by_type_quarter_request_builder import SummaryBalanceSheetOfInsuranceCorporationsByTypeQuarterRequestBuilder
    from .summary_balance_sheet_of_pension_funds_by_type_quarter.summary_balance_sheet_of_pension_funds_by_type_quarter_request_builder import SummaryBalanceSheetOfPensionFundsByTypeQuarterRequestBuilder
    from .the25_largest_investments_by_dutch_households_in_individual_investment_funds.the25_largest_investments_by_dutch_households_in_individual_investment_funds_request_builder import The25LargestInvestmentsByDutchHouseholdsInIndividualInvestmentFundsRequestBuilder
    from .the25_largest_investments_in_individual_listed_shares.the25_largest_investments_in_individual_listed_shares_request_builder import The25LargestInvestmentsInIndividualListedSharesRequestBuilder

class DnbStatisticsClient(BaseRequestBuilder):
    """
    The main entry point of the SDK, exposes the configuration and the fluent API.
    """
    def __init__(self,request_adapter: RequestAdapter) -> None:
        """
        Instantiates a new DnbStatisticsClient and sets the default values.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        if request_adapter is None:
            raise TypeError("request_adapter cannot be null.")
        super().__init__(request_adapter, "{+baseurl}", None)
        register_default_serializer(JsonSerializationWriterFactory)
        register_default_serializer(TextSerializationWriterFactory)
        register_default_serializer(FormSerializationWriterFactory)
        register_default_serializer(MultipartSerializationWriterFactory)
        register_default_deserializer(JsonParseNodeFactory)
        register_default_deserializer(TextParseNodeFactory)
        register_default_deserializer(FormParseNodeFactory)
        if not self.request_adapter.base_url:
            self.request_adapter.base_url = "https://api.dnb.nl/statisticsdata/v2024100101"
        self.path_parameters["base_url"] = self.request_adapter.base_url
    
    @property
    def balance_of_payments_quarter(self) -> BalanceOfPaymentsQuarterRequestBuilder:
        """
        The balanceOfPaymentsQuarter property
        """
        from .balance_of_payments_quarter.balance_of_payments_quarter_request_builder import BalanceOfPaymentsQuarterRequestBuilder

        return BalanceOfPaymentsQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def balance_of_payments_year(self) -> BalanceOfPaymentsYearRequestBuilder:
        """
        The balanceOfPaymentsYear property
        """
        from .balance_of_payments_year.balance_of_payments_year_request_builder import BalanceOfPaymentsYearRequestBuilder

        return BalanceOfPaymentsYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted(self) -> BalanceSheetOfDeNederlandscheBankMonthNonBreakAdjustedRequestBuilder:
        """
        The balanceSheetOfDeNederlandscheBankMonthNonBreakAdjusted property
        """
        from .balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted.balance_sheet_of_de_nederlandsche_bank_month_non_break_adjusted_request_builder import BalanceSheetOfDeNederlandscheBankMonthNonBreakAdjustedRequestBuilder

        return BalanceSheetOfDeNederlandscheBankMonthNonBreakAdjustedRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def balance_sheet_of_dutch_based_mfis_not_including_dnb_month(self) -> BalanceSheetOfDutchBasedMfisNotIncludingDnbMonthRequestBuilder:
        """
        The balanceSheetOfDutchBasedMfisNotIncludingDnbMonth property
        """
        from .balance_sheet_of_dutch_based_mfis_not_including_dnb_month.balance_sheet_of_dutch_based_mfis_not_including_dnb_month_request_builder import BalanceSheetOfDutchBasedMfisNotIncludingDnbMonthRequestBuilder

        return BalanceSheetOfDutchBasedMfisNotIncludingDnbMonthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def balance_sheet_of_other_financial_intermediaries_by_geography_quarter(self) -> BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRequestBuilder:
        """
        The balanceSheetOfOtherFinancialIntermediariesByGeographyQuarter property
        """
        from .balance_sheet_of_other_financial_intermediaries_by_geography_quarter.balance_sheet_of_other_financial_intermediaries_by_geography_quarter_request_builder import BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRequestBuilder

        return BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_debt_securities_holdings_by_sector_of_the_holder(self) -> DutchDebtSecuritiesHoldingsBySectorOfTheHolderRequestBuilder:
        """
        The dutchDebtSecuritiesHoldingsBySectorOfTheHolder property
        """
        from .dutch_debt_securities_holdings_by_sector_of_the_holder.dutch_debt_securities_holdings_by_sector_of_the_holder_request_builder import DutchDebtSecuritiesHoldingsBySectorOfTheHolderRequestBuilder

        return DutchDebtSecuritiesHoldingsBySectorOfTheHolderRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_fund_unit_holdings_by_sector_of_the_holder(self) -> DutchFundUnitHoldingsBySectorOfTheHolderRequestBuilder:
        """
        The dutchFundUnitHoldingsBySectorOfTheHolder property
        """
        from .dutch_fund_unit_holdings_by_sector_of_the_holder.dutch_fund_unit_holdings_by_sector_of_the_holder_request_builder import DutchFundUnitHoldingsBySectorOfTheHolderRequestBuilder

        return DutchFundUnitHoldingsBySectorOfTheHolderRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_government_paper_holdings(self) -> DutchGovernmentPaperHoldingsRequestBuilder:
        """
        The dutchGovernmentPaperHoldings property
        """
        from .dutch_government_paper_holdings.dutch_government_paper_holdings_request_builder import DutchGovernmentPaperHoldingsRequestBuilder

        return DutchGovernmentPaperHoldingsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_household_savings_month(self) -> DutchHouseholdSavingsMonthRequestBuilder:
        """
        The dutchHouseholdSavingsMonth property
        """
        from .dutch_household_savings_month.dutch_household_savings_month_request_builder import DutchHouseholdSavingsMonthRequestBuilder

        return DutchHouseholdSavingsMonthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_listed_shares_holdings_by_sector_of_the_holder(self) -> DutchListedSharesHoldingsBySectorOfTheHolderRequestBuilder:
        """
        The dutchListedSharesHoldingsBySectorOfTheHolder property
        """
        from .dutch_listed_shares_holdings_by_sector_of_the_holder.dutch_listed_shares_holdings_by_sector_of_the_holder_request_builder import DutchListedSharesHoldingsBySectorOfTheHolderRequestBuilder

        return DutchListedSharesHoldingsBySectorOfTheHolderRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_securities_holdings_by_sector_of_the_holder_by_geography(self) -> DutchSecuritiesHoldingsBySectorOfTheHolderByGeographyRequestBuilder:
        """
        The dutchSecuritiesHoldingsBySectorOfTheHolderByGeography property
        """
        from .dutch_securities_holdings_by_sector_of_the_holder_by_geography.dutch_securities_holdings_by_sector_of_the_holder_by_geography_request_builder import DutchSecuritiesHoldingsBySectorOfTheHolderByGeographyRequestBuilder

        return DutchSecuritiesHoldingsBySectorOfTheHolderByGeographyRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security(self) -> DutchSecuritiesHoldingsBySectorOfTheHolderByTypeOfSecurityRequestBuilder:
        """
        The dutchSecuritiesHoldingsBySectorOfTheHolderByTypeOfSecurity property
        """
        from .dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security.dutch_securities_holdings_by_sector_of_the_holder_by_type_of_security_request_builder import DutchSecuritiesHoldingsBySectorOfTheHolderByTypeOfSecurityRequestBuilder

        return DutchSecuritiesHoldingsBySectorOfTheHolderByTypeOfSecurityRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def european_central_bank_interest_rates(self) -> EuropeanCentralBankInterestRatesRequestBuilder:
        """
        The europeanCentralBankInterestRates property
        """
        from .european_central_bank_interest_rates.european_central_bank_interest_rates_request_builder import EuropeanCentralBankInterestRatesRequestBuilder

        return EuropeanCentralBankInterestRatesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def exchange_rates_of_the_euro_and_gold_price_day(self) -> ExchangeRatesOfTheEuroAndGoldPriceDayRequestBuilder:
        """
        The exchangeRatesOfTheEuroAndGoldPriceDay property
        """
        from .exchange_rates_of_the_euro_and_gold_price_day.exchange_rates_of_the_euro_and_gold_price_day_request_builder import ExchangeRatesOfTheEuroAndGoldPriceDayRequestBuilder

        return ExchangeRatesOfTheEuroAndGoldPriceDayRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def exchange_rates_of_the_euro_and_gold_price_month(self) -> ExchangeRatesOfTheEuroAndGoldPriceMonthRequestBuilder:
        """
        The exchangeRatesOfTheEuroAndGoldPriceMonth property
        """
        from .exchange_rates_of_the_euro_and_gold_price_month.exchange_rates_of_the_euro_and_gold_price_month_request_builder import ExchangeRatesOfTheEuroAndGoldPriceMonthRequestBuilder

        return ExchangeRatesOfTheEuroAndGoldPriceMonthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def exchange_rates_of_the_euro_and_gold_price_quarter(self) -> ExchangeRatesOfTheEuroAndGoldPriceQuarterRequestBuilder:
        """
        The exchangeRatesOfTheEuroAndGoldPriceQuarter property
        """
        from .exchange_rates_of_the_euro_and_gold_price_quarter.exchange_rates_of_the_euro_and_gold_price_quarter_request_builder import ExchangeRatesOfTheEuroAndGoldPriceQuarterRequestBuilder

        return ExchangeRatesOfTheEuroAndGoldPriceQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def exchange_rates_of_the_euro_and_gold_price_year_average(self) -> ExchangeRatesOfTheEuroAndGoldPriceYearAverageRequestBuilder:
        """
        The exchangeRatesOfTheEuroAndGoldPriceYearAverage property
        """
        from .exchange_rates_of_the_euro_and_gold_price_year_average.exchange_rates_of_the_euro_and_gold_price_year_average_request_builder import ExchangeRatesOfTheEuroAndGoldPriceYearAverageRequestBuilder

        return ExchangeRatesOfTheEuroAndGoldPriceYearAverageRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def exchange_rates_of_the_euro_and_gold_price_year_end_of_period(self) -> ExchangeRatesOfTheEuroAndGoldPriceYearEndOfPeriodRequestBuilder:
        """
        The exchangeRatesOfTheEuroAndGoldPriceYearEndOfPeriod property
        """
        from .exchange_rates_of_the_euro_and_gold_price_year_end_of_period.exchange_rates_of_the_euro_and_gold_price_year_end_of_period_request_builder import ExchangeRatesOfTheEuroAndGoldPriceYearEndOfPeriodRequestBuilder

        return ExchangeRatesOfTheEuroAndGoldPriceYearEndOfPeriodRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def finance_companies_balance_sheet(self) -> FinanceCompaniesBalanceSheetRequestBuilder:
        """
        The financeCompaniesBalanceSheet property
        """
        from .finance_companies_balance_sheet.finance_companies_balance_sheet_request_builder import FinanceCompaniesBalanceSheetRequestBuilder

        return FinanceCompaniesBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def financial_auxiliaries_balance_sheet(self) -> FinancialAuxiliariesBalanceSheetRequestBuilder:
        """
        The financialAuxiliariesBalanceSheet property
        """
        from .financial_auxiliaries_balance_sheet.financial_auxiliaries_balance_sheet_request_builder import FinancialAuxiliariesBalanceSheetRequestBuilder

        return FinancialAuxiliariesBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def financial_auxiliaries_balance_sheet_by_geography_quarter(self) -> FinancialAuxiliariesBalanceSheetByGeographyQuarterRequestBuilder:
        """
        The financialAuxiliariesBalanceSheetByGeographyQuarter property
        """
        from .financial_auxiliaries_balance_sheet_by_geography_quarter.financial_auxiliaries_balance_sheet_by_geography_quarter_request_builder import FinancialAuxiliariesBalanceSheetByGeographyQuarterRequestBuilder

        return FinancialAuxiliariesBalanceSheetByGeographyQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def financial_data_of_individual_banks_half_year(self) -> FinancialDataOfIndividualBanksHalfYearRequestBuilder:
        """
        The financialDataOfIndividualBanksHalfYear property
        """
        from .financial_data_of_individual_banks_half_year.financial_data_of_individual_banks_half_year_request_builder import FinancialDataOfIndividualBanksHalfYearRequestBuilder

        return FinancialDataOfIndividualBanksHalfYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def geographical_distribution_of_inward_and_outward_fdi_income(self) -> GeographicalDistributionOfInwardAndOutwardFdiIncomeRequestBuilder:
        """
        The geographicalDistributionOfInwardAndOutwardFdiIncome property
        """
        from .geographical_distribution_of_inward_and_outward_fdi_income.geographical_distribution_of_inward_and_outward_fdi_income_request_builder import GeographicalDistributionOfInwardAndOutwardFdiIncomeRequestBuilder

        return GeographicalDistributionOfInwardAndOutwardFdiIncomeRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def head_offices_of_financial_auxiliaries_balance_sheet(self) -> HeadOfficesOfFinancialAuxiliariesBalanceSheetRequestBuilder:
        """
        The headOfficesOfFinancialAuxiliariesBalanceSheet property
        """
        from .head_offices_of_financial_auxiliaries_balance_sheet.head_offices_of_financial_auxiliaries_balance_sheet_request_builder import HeadOfficesOfFinancialAuxiliariesBalanceSheetRequestBuilder

        return HeadOfficesOfFinancialAuxiliariesBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def holding_of_bonds_by_type_of_sustainability_characteristic_by_sector(self) -> HoldingOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder:
        """
        The holdingOfBondsByTypeOfSustainabilityCharacteristicBySector property
        """
        from .holding_of_bonds_by_type_of_sustainability_characteristic_by_sector.holding_of_bonds_by_type_of_sustainability_characteristic_by_sector_request_builder import HoldingOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder

        return HoldingOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def holding_of_green_bonds_with_external_assurance_by_sector(self) -> HoldingOfGreenBondsWithExternalAssuranceBySectorRequestBuilder:
        """
        The holdingOfGreenBondsWithExternalAssuranceBySector property
        """
        from .holding_of_green_bonds_with_external_assurance_by_sector.holding_of_green_bonds_with_external_assurance_by_sector_request_builder import HoldingOfGreenBondsWithExternalAssuranceBySectorRequestBuilder

        return HoldingOfGreenBondsWithExternalAssuranceBySectorRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def individual_pension_fund_data_quarter(self) -> IndividualPensionFundDataQuarterRequestBuilder:
        """
        The individualPensionFundDataQuarter property
        """
        from .individual_pension_fund_data_quarter.individual_pension_fund_data_quarter_request_builder import IndividualPensionFundDataQuarterRequestBuilder

        return IndividualPensionFundDataQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def infrastructure_domestic_payments_in_units_half_year(self) -> InfrastructureDomesticPaymentsInUnitsHalfYearRequestBuilder:
        """
        The infrastructureDomesticPaymentsInUnitsHalfYear property
        """
        from .infrastructure_domestic_payments_in_units_half_year.infrastructure_domestic_payments_in_units_half_year_request_builder import InfrastructureDomesticPaymentsInUnitsHalfYearRequestBuilder

        return InfrastructureDomesticPaymentsInUnitsHalfYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def infrastructure_of_domestic_retail_payments_units(self) -> InfrastructureOfDomesticRetailPaymentsUnitsRequestBuilder:
        """
        The infrastructureOfDomesticRetailPaymentsUnits property
        """
        from .infrastructure_of_domestic_retail_payments_units.infrastructure_of_domestic_retail_payments_units_request_builder import InfrastructureOfDomesticRetailPaymentsUnitsRequestBuilder

        return InfrastructureOfDomesticRetailPaymentsUnitsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def insurance_corporation_assets_and_liabilities_by_domestic_countersector_quarter(self) -> InsuranceCorporationAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder:
        """
        The insuranceCorporationAssetsAndLiabilitiesByDomesticCountersectorQuarter property
        """
        from .insurance_corporation_assets_and_liabilities_by_domestic_countersector_quarter.insurance_corporation_assets_and_liabilities_by_domestic_countersector_quarter_request_builder import InsuranceCorporationAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder

        return InsuranceCorporationAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def insurance_corporation_assets_and_liabilities_by_geography_quarter(self) -> InsuranceCorporationAssetsAndLiabilitiesByGeographyQuarterRequestBuilder:
        """
        The insuranceCorporationAssetsAndLiabilitiesByGeographyQuarter property
        """
        from .insurance_corporation_assets_and_liabilities_by_geography_quarter.insurance_corporation_assets_and_liabilities_by_geography_quarter_request_builder import InsuranceCorporationAssetsAndLiabilitiesByGeographyQuarterRequestBuilder

        return InsuranceCorporationAssetsAndLiabilitiesByGeographyQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def insurance_corporations_balance_sheet_quarter(self) -> InsuranceCorporationsBalanceSheetQuarterRequestBuilder:
        """
        The insuranceCorporationsBalanceSheetQuarter property
        """
        from .insurance_corporations_balance_sheet_quarter.insurance_corporations_balance_sheet_quarter_request_builder import InsuranceCorporationsBalanceSheetQuarterRequestBuilder

        return InsuranceCorporationsBalanceSheetQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def insurers_cash_flow_statement_quarter(self) -> InsurersCashFlowStatementQuarterRequestBuilder:
        """
        The insurersCashFlowStatementQuarter property
        """
        from .insurers_cash_flow_statement_quarter.insurers_cash_flow_statement_quarter_request_builder import InsurersCashFlowStatementQuarterRequestBuilder

        return InsurersCashFlowStatementQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def investments_by_dutch_households_in_individual_aex_shares(self) -> InvestmentsByDutchHouseholdsInIndividualAexSharesRequestBuilder:
        """
        The investmentsByDutchHouseholdsInIndividualAexShares property
        """
        from .investments_by_dutch_households_in_individual_aex_shares.investments_by_dutch_households_in_individual_aex_shares_request_builder import InvestmentsByDutchHouseholdsInIndividualAexSharesRequestBuilder

        return InvestmentsByDutchHouseholdsInIndividualAexSharesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def investments_by_dutch_households_in_securities_by_instrument_category(self) -> InvestmentsByDutchHouseholdsInSecuritiesByInstrumentCategoryRequestBuilder:
        """
        The investmentsByDutchHouseholdsInSecuritiesByInstrumentCategory property
        """
        from .investments_by_dutch_households_in_securities_by_instrument_category.investments_by_dutch_households_in_securities_by_instrument_category_request_builder import InvestmentsByDutchHouseholdsInSecuritiesByInstrumentCategoryRequestBuilder

        return InvestmentsByDutchHouseholdsInSecuritiesByInstrumentCategoryRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def issuance_of_bonds_by_type_of_sustainability_characteristic_by_sector(self) -> IssuanceOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder:
        """
        The issuanceOfBondsByTypeOfSustainabilityCharacteristicBySector property
        """
        from .issuance_of_bonds_by_type_of_sustainability_characteristic_by_sector.issuance_of_bonds_by_type_of_sustainability_characteristic_by_sector_request_builder import IssuanceOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder

        return IssuanceOfBondsByTypeOfSustainabilityCharacteristicBySectorRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def issuance_of_green_bonds_with_external_assurance_by_sector(self) -> IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder:
        """
        The issuanceOfGreenBondsWithExternalAssuranceBySector property
        """
        from .issuance_of_green_bonds_with_external_assurance_by_sector.issuance_of_green_bonds_with_external_assurance_by_sector_request_builder import IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder

        return IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def key_indicators_monetary_statistics_month(self) -> KeyIndicatorsMonetaryStatisticsMonthRequestBuilder:
        """
        The keyIndicatorsMonetaryStatisticsMonth property
        """
        from .key_indicators_monetary_statistics_month.key_indicators_monetary_statistics_month_request_builder import KeyIndicatorsMonetaryStatisticsMonthRequestBuilder

        return KeyIndicatorsMonetaryStatisticsMonthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def loans_by_type_and_securitisation_type_quarter(self) -> LoansByTypeAndSecuritisationTypeQuarterRequestBuilder:
        """
        The loansByTypeAndSecuritisationTypeQuarter property
        """
        from .loans_by_type_and_securitisation_type_quarter.loans_by_type_and_securitisation_type_quarter_request_builder import LoansByTypeAndSecuritisationTypeQuarterRequestBuilder

        return LoansByTypeAndSecuritisationTypeQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def macroeconomic_scoreboard_quarter(self) -> MacroeconomicScoreboardQuarterRequestBuilder:
        """
        The macroeconomicScoreboardQuarter property
        """
        from .macroeconomic_scoreboard_quarter.macroeconomic_scoreboard_quarter_request_builder import MacroeconomicScoreboardQuarterRequestBuilder

        return MacroeconomicScoreboardQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def macroeconomic_scoreboard_year(self) -> MacroeconomicScoreboardYearRequestBuilder:
        """
        The macroeconomicScoreboardYear property
        """
        from .macroeconomic_scoreboard_year.macroeconomic_scoreboard_year_request_builder import MacroeconomicScoreboardYearRequestBuilder

        return MacroeconomicScoreboardYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def market_interest_rates_day(self) -> MarketInterestRatesDayRequestBuilder:
        """
        The marketInterestRatesDay property
        """
        from .market_interest_rates_day.market_interest_rates_day_request_builder import MarketInterestRatesDayRequestBuilder

        return MarketInterestRatesDayRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def market_interest_rates_month(self) -> MarketInterestRatesMonthRequestBuilder:
        """
        The marketInterestRatesMonth property
        """
        from .market_interest_rates_month.market_interest_rates_month_request_builder import MarketInterestRatesMonthRequestBuilder

        return MarketInterestRatesMonthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def mfi_household_deposits_and_loans_interest_rates_month(self) -> MfiHouseholdDepositsAndLoansInterestRatesMonthRequestBuilder:
        """
        The mfiHouseholdDepositsAndLoansInterestRatesMonth property
        """
        from .mfi_household_deposits_and_loans_interest_rates_month.mfi_household_deposits_and_loans_interest_rates_month_request_builder import MfiHouseholdDepositsAndLoansInterestRatesMonthRequestBuilder

        return MfiHouseholdDepositsAndLoansInterestRatesMonthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def net_deposits_in_investment_funds_by_sector_of_the_holder_quarter(self) -> NetDepositsInInvestmentFundsBySectorOfTheHolderQuarterRequestBuilder:
        """
        The netDepositsInInvestmentFundsBySectorOfTheHolderQuarter property
        """
        from .net_deposits_in_investment_funds_by_sector_of_the_holder_quarter.net_deposits_in_investment_funds_by_sector_of_the_holder_quarter_request_builder import NetDepositsInInvestmentFundsBySectorOfTheHolderQuarterRequestBuilder

        return NetDepositsInInvestmentFundsBySectorOfTheHolderQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def net_external_assets_quarter(self) -> NetExternalAssetsQuarterRequestBuilder:
        """
        The netExternalAssetsQuarter property
        """
        from .net_external_assets_quarter.net_external_assets_quarter_request_builder import NetExternalAssetsQuarterRequestBuilder

        return NetExternalAssetsQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def net_external_assets_year(self) -> NetExternalAssetsYearRequestBuilder:
        """
        The netExternalAssetsYear property
        """
        from .net_external_assets_year.net_external_assets_year_request_builder import NetExternalAssetsYearRequestBuilder

        return NetExternalAssetsYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def nominal_irts_for_pension_funds_zero_coupon(self) -> NominalIrtsForPensionFundsZeroCouponRequestBuilder:
        """
        The nominalIrtsForPensionFundsZeroCoupon property
        """
        from .nominal_irts_for_pension_funds_zero_coupon.nominal_irts_for_pension_funds_zero_coupon_request_builder import NominalIrtsForPensionFundsZeroCouponRequestBuilder

        return NominalIrtsForPensionFundsZeroCouponRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def number_and_value_of_payment_transactions_half_year(self) -> NumberAndValueOfPaymentTransactionsHalfYearRequestBuilder:
        """
        The numberAndValueOfPaymentTransactionsHalfYear property
        """
        from .number_and_value_of_payment_transactions_half_year.number_and_value_of_payment_transactions_half_year_request_builder import NumberAndValueOfPaymentTransactionsHalfYearRequestBuilder

        return NumberAndValueOfPaymentTransactionsHalfYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def number_and_value_of_retail_payment_transactions(self) -> NumberAndValueOfRetailPaymentTransactionsRequestBuilder:
        """
        The numberAndValueOfRetailPaymentTransactions property
        """
        from .number_and_value_of_retail_payment_transactions.number_and_value_of_retail_payment_transactions_request_builder import NumberAndValueOfRetailPaymentTransactionsRequestBuilder

        return NumberAndValueOfRetailPaymentTransactionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def other_financial_auxiliaries_balance_sheet(self) -> OtherFinancialAuxiliariesBalanceSheetRequestBuilder:
        """
        The otherFinancialAuxiliariesBalanceSheet property
        """
        from .other_financial_auxiliaries_balance_sheet.other_financial_auxiliaries_balance_sheet_request_builder import OtherFinancialAuxiliariesBalanceSheetRequestBuilder

        return OtherFinancialAuxiliariesBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def other_financial_intermediaries_balance_sheet(self) -> OtherFinancialIntermediariesBalanceSheetRequestBuilder:
        """
        The otherFinancialIntermediariesBalanceSheet property
        """
        from .other_financial_intermediaries_balance_sheet.other_financial_intermediaries_balance_sheet_request_builder import OtherFinancialIntermediariesBalanceSheetRequestBuilder

        return OtherFinancialIntermediariesBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def pension_funds_assets_and_liabilities_by_domestic_countersector_quarter(self) -> PensionFundsAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder:
        """
        The pensionFundsAssetsAndLiabilitiesByDomesticCountersectorQuarter property
        """
        from .pension_funds_assets_and_liabilities_by_domestic_countersector_quarter.pension_funds_assets_and_liabilities_by_domestic_countersector_quarter_request_builder import PensionFundsAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder

        return PensionFundsAssetsAndLiabilitiesByDomesticCountersectorQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def pension_funds_assets_and_liabilities_by_geographical_area_quarter(self) -> PensionFundsAssetsAndLiabilitiesByGeographicalAreaQuarterRequestBuilder:
        """
        The pensionFundsAssetsAndLiabilitiesByGeographicalAreaQuarter property
        """
        from .pension_funds_assets_and_liabilities_by_geographical_area_quarter.pension_funds_assets_and_liabilities_by_geographical_area_quarter_request_builder import PensionFundsAssetsAndLiabilitiesByGeographicalAreaQuarterRequestBuilder

        return PensionFundsAssetsAndLiabilitiesByGeographicalAreaQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def pension_funds_balance_sheet(self) -> PensionFundsBalanceSheetRequestBuilder:
        """
        The pensionFundsBalanceSheet property
        """
        from .pension_funds_balance_sheet.pension_funds_balance_sheet_request_builder import PensionFundsBalanceSheetRequestBuilder

        return PensionFundsBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter(self) -> PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder:
        """
        The pensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarter property
        """
        from .pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter.pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter_request_builder import PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder

        return PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def pension_funds_cash_flow_statement_quarter(self) -> PensionFundsCashFlowStatementQuarterRequestBuilder:
        """
        The pensionFundsCashFlowStatementQuarter property
        """
        from .pension_funds_cash_flow_statement_quarter.pension_funds_cash_flow_statement_quarter_request_builder import PensionFundsCashFlowStatementQuarterRequestBuilder

        return PensionFundsCashFlowStatementQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_quarter(self) -> PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiQuarterRequestBuilder:
        """
        The premiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiQuarter property
        """
        from .premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_quarter.premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_quarter_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiQuarterRequestBuilder

        return PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_year(self) -> PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiYearRequestBuilder:
        """
        The premiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiYear property
        """
        from .premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_year.premiums_claims_and_costs_by_line_of_business_of_life_insurers_solvency_ii_year_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiYearRequestBuilder

        return PremiumsClaimsAndCostsByLineOfBusinessOfLifeInsurersSolvencyIiYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_quarter(self) -> PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiQuarterRequestBuilder:
        """
        The premiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiQuarter property
        """
        from .premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_quarter.premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_quarter_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiQuarterRequestBuilder

        return PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_year(self) -> PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRequestBuilder:
        """
        The premiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYear property
        """
        from .premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_year.premiums_claims_and_costs_by_line_of_business_of_non_life_insurers_solvency_ii_year_request_builder import PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRequestBuilder

        return PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def residential_mortgage_loans_provided_to_households_by_sector(self) -> ResidentialMortgageLoansProvidedToHouseholdsBySectorRequestBuilder:
        """
        The residentialMortgageLoansProvidedToHouseholdsBySector property
        """
        from .residential_mortgage_loans_provided_to_households_by_sector.residential_mortgage_loans_provided_to_households_by_sector_request_builder import ResidentialMortgageLoansProvidedToHouseholdsBySectorRequestBuilder

        return ResidentialMortgageLoansProvidedToHouseholdsBySectorRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def residential_mortgages_provided_by_dutch_institutional_investors_to_dutch_households_quarter(self) -> ResidentialMortgagesProvidedByDutchInstitutionalInvestorsToDutchHouseholdsQuarterRequestBuilder:
        """
        The residentialMortgagesProvidedByDutchInstitutionalInvestorsToDutchHouseholdsQuarter property
        """
        from .residential_mortgages_provided_by_dutch_institutional_investors_to_dutch_households_quarter.residential_mortgages_provided_by_dutch_institutional_investors_to_dutch_households_quarter_request_builder import ResidentialMortgagesProvidedByDutchInstitutionalInvestorsToDutchHouseholdsQuarterRequestBuilder

        return ResidentialMortgagesProvidedByDutchInstitutionalInvestorsToDutchHouseholdsQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def securities_and_derivatives_traders_balance_sheet(self) -> SecuritiesAndDerivativesTradersBalanceSheetRequestBuilder:
        """
        The securitiesAndDerivativesTradersBalanceSheet property
        """
        from .securities_and_derivatives_traders_balance_sheet.securities_and_derivatives_traders_balance_sheet_request_builder import SecuritiesAndDerivativesTradersBalanceSheetRequestBuilder

        return SecuritiesAndDerivativesTradersBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def securitisation_vehicles_balance_sheet(self) -> SecuritisationVehiclesBalanceSheetRequestBuilder:
        """
        The securitisationVehiclesBalanceSheet property
        """
        from .securitisation_vehicles_balance_sheet.securitisation_vehicles_balance_sheet_request_builder import SecuritisationVehiclesBalanceSheetRequestBuilder

        return SecuritisationVehiclesBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def specialised_financial_institutions_balance_sheet(self) -> SpecialisedFinancialInstitutionsBalanceSheetRequestBuilder:
        """
        The specialisedFinancialInstitutionsBalanceSheet property
        """
        from .specialised_financial_institutions_balance_sheet.specialised_financial_institutions_balance_sheet_request_builder import SpecialisedFinancialInstitutionsBalanceSheetRequestBuilder

        return SpecialisedFinancialInstitutionsBalanceSheetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def statutory_interest_rate_half_year(self) -> StatutoryInterestRateHalfYearRequestBuilder:
        """
        The statutoryInterestRateHalfYear property
        """
        from .statutory_interest_rate_half_year.statutory_interest_rate_half_year_request_builder import StatutoryInterestRateHalfYearRequestBuilder

        return StatutoryInterestRateHalfYearRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def summary_balance_sheet_of_insurance_corporations_by_type_quarter(self) -> SummaryBalanceSheetOfInsuranceCorporationsByTypeQuarterRequestBuilder:
        """
        The summaryBalanceSheetOfInsuranceCorporationsByTypeQuarter property
        """
        from .summary_balance_sheet_of_insurance_corporations_by_type_quarter.summary_balance_sheet_of_insurance_corporations_by_type_quarter_request_builder import SummaryBalanceSheetOfInsuranceCorporationsByTypeQuarterRequestBuilder

        return SummaryBalanceSheetOfInsuranceCorporationsByTypeQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def summary_balance_sheet_of_pension_funds_by_type_quarter(self) -> SummaryBalanceSheetOfPensionFundsByTypeQuarterRequestBuilder:
        """
        The summaryBalanceSheetOfPensionFundsByTypeQuarter property
        """
        from .summary_balance_sheet_of_pension_funds_by_type_quarter.summary_balance_sheet_of_pension_funds_by_type_quarter_request_builder import SummaryBalanceSheetOfPensionFundsByTypeQuarterRequestBuilder

        return SummaryBalanceSheetOfPensionFundsByTypeQuarterRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def the25_largest_investments_by_dutch_households_in_individual_investment_funds(self) -> The25LargestInvestmentsByDutchHouseholdsInIndividualInvestmentFundsRequestBuilder:
        """
        The the25LargestInvestmentsByDutchHouseholdsInIndividualInvestmentFunds property
        """
        from .the25_largest_investments_by_dutch_households_in_individual_investment_funds.the25_largest_investments_by_dutch_households_in_individual_investment_funds_request_builder import The25LargestInvestmentsByDutchHouseholdsInIndividualInvestmentFundsRequestBuilder

        return The25LargestInvestmentsByDutchHouseholdsInIndividualInvestmentFundsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def the25_largest_investments_in_individual_listed_shares(self) -> The25LargestInvestmentsInIndividualListedSharesRequestBuilder:
        """
        The the25LargestInvestmentsInIndividualListedShares property
        """
        from .the25_largest_investments_in_individual_listed_shares.the25_largest_investments_in_individual_listed_shares_request_builder import The25LargestInvestmentsInIndividualListedSharesRequestBuilder

        return The25LargestInvestmentsInIndividualListedSharesRequestBuilder(self.request_adapter, self.path_parameters)
    

