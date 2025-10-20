from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from .pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter_get_response import PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterGetResponse

class PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /pension-funds-balance-sheet-including-look-through-participation-in-dutch-investment-funds-quarter
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/pension-funds-balance-sheet-including-look-through-participation-in-dutch-investment-funds-quarter{?page*,pageSize*,sort*,sortDirection*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilderGetQueryParameters]] = None) -> Optional[PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterGetResponse]:
        """
        <p><p class="MsoNormal"><span lang="EN-GB">The table shows the balance sheet of pension&#10;funds, &#8220;looking through&#8221; the shares they hold in Dutch investment funds and&#10;broken down by geography. Data are available from the fourth quarter of 2008.&#10;Pension funds invest part of their assets through Dutch investment funds. The&#10;table allocates these investments, where possible, to the instruments in which&#10;these investment funds invest.<br></span><span>Table&#10;8.1BC shows the balance sheet of pension funds without this &#8220;look-through&#8221;.&#10;Data without geographical breakdown are available in Table 8.1.4S. This data is&#10;no longer updated.</span></p><p class="MsoNormal"><span lang="EN-GB"></span></p></p><p><b>Table Number: </b>8.1.4</p><p><b>Unit: </b>EUR millions</p><p><b>Source: </b>DNB</p>
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterGetResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .pension_funds_balance_sheet_including_look_through_participation_in_dutch_investment_funds_quarter_get_response import PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterGetResponse

        return await self.request_adapter.send_async(request_info, PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterGetResponse, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        <p><p class="MsoNormal"><span lang="EN-GB">The table shows the balance sheet of pension&#10;funds, &#8220;looking through&#8221; the shares they hold in Dutch investment funds and&#10;broken down by geography. Data are available from the fourth quarter of 2008.&#10;Pension funds invest part of their assets through Dutch investment funds. The&#10;table allocates these investments, where possible, to the instruments in which&#10;these investment funds invest.<br></span><span>Table&#10;8.1BC shows the balance sheet of pension funds without this &#8220;look-through&#8221;.&#10;Data without geographical breakdown are available in Table 8.1.4S. This data is&#10;no longer updated.</span></p><p class="MsoNormal"><span lang="EN-GB"></span></p></p><p><b>Table Number: </b>8.1.4</p><p><b>Unit: </b>EUR millions</p><p><b>Source: </b>DNB</p>
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilderGetQueryParameters():
        """
        <p><p class="MsoNormal"><span lang="EN-GB">The table shows the balance sheet of pension&#10;funds, &#8220;looking through&#8221; the shares they hold in Dutch investment funds and&#10;broken down by geography. Data are available from the fourth quarter of 2008.&#10;Pension funds invest part of their assets through Dutch investment funds. The&#10;table allocates these investments, where possible, to the instruments in which&#10;these investment funds invest.<br></span><span>Table&#10;8.1BC shows the balance sheet of pension funds without this &#8220;look-through&#8221;.&#10;Data without geographical breakdown are available in Table 8.1.4S. This data is&#10;no longer updated.</span></p><p class="MsoNormal"><span lang="EN-GB"></span></p></p><p><b>Table Number: </b>8.1.4</p><p><b>Unit: </b>EUR millions</p><p><b>Source: </b>DNB</p>
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "page_size":
                return "pageSize"
            if original_name == "sort_direction":
                return "sortDirection"
            if original_name == "page":
                return "page"
            if original_name == "sort":
                return "sort"
            return original_name
        
        # The page number. If the page size is 0, the requested page number should be 1 or left empty. This wil yield all records.
        page: Optional[int] = None

        # The page size. If omitted, will default to 2000. A page size of 0 will yield all records. Please be aware that a page size of 0, or a another large page size, might result in longer response times.
        page_size: Optional[int] = None

        # The default sort direction is ascending and may be omitted. A whitespace is used to separate the field name and the sort direction. The only allowed sort field name and sort directions are 'period desc' and 'period asc', no other field names are allowed. If a sort direction is specified, it overrides the direction specified in the 'sortDirection' parameter
        sort: Optional[str] = None

        # Specifies the default sort direction. If omitted, default to ascending (asc). The value of sortDirection is overridden if the sort direction is already specified in the 'sort' parameter.
        sort_direction: Optional[str] = None

    
    @dataclass
    class PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilderGetRequestConfiguration(RequestConfiguration[PensionFundsBalanceSheetIncludingLookThroughParticipationInDutchInvestmentFundsQuarterRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

