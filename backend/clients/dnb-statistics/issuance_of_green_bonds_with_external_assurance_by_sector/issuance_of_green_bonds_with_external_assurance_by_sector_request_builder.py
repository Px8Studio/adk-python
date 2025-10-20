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
    from .issuance_of_green_bonds_with_external_assurance_by_sector_get_response import IssuanceOfGreenBondsWithExternalAssuranceBySectorGetResponse

class IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /issuance-of-green-bonds-with-external-assurance-by-sector
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/issuance-of-green-bonds-with-external-assurance-by-sector{?page*,pageSize*,sort*,sortDirection*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilderGetQueryParameters]] = None) -> Optional[IssuanceOfGreenBondsWithExternalAssuranceBySectorGetResponse]:
        """
        <p><p class="MsoNormal"><span class="normaltextrun"><span lang="EN-GB">Overview of capital outstanding of bonds with&#10;sustainability characteristics (ESG bonds) expressed in market values, broken&#10;down by type of sustainability characteristics and sector. These debt&#10;securities are issued by Dutch residents and have been labelled as 'green',&#10;'social', 'sustainable' or 'sustainability-linked' by the issuers. Specifically&#10;for green bonds, a breakdown is also made between green bonds with assurance&#10;provided by an external party and those lacking such assurance. Monthly figures&#10;are available from 2017.&#8239;</span></span><span class="eop"><span lang="EN-GB">&#160;</span></span><span class="eop"><span lang="EN-GB"></span></span></p></p><p><b>Table Number: </b>4.5.2</p><p><b>Unit: </b>EUR millions</p><p><b>Source: </b>DNB</p>
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[IssuanceOfGreenBondsWithExternalAssuranceBySectorGetResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .issuance_of_green_bonds_with_external_assurance_by_sector_get_response import IssuanceOfGreenBondsWithExternalAssuranceBySectorGetResponse

        return await self.request_adapter.send_async(request_info, IssuanceOfGreenBondsWithExternalAssuranceBySectorGetResponse, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        <p><p class="MsoNormal"><span class="normaltextrun"><span lang="EN-GB">Overview of capital outstanding of bonds with&#10;sustainability characteristics (ESG bonds) expressed in market values, broken&#10;down by type of sustainability characteristics and sector. These debt&#10;securities are issued by Dutch residents and have been labelled as 'green',&#10;'social', 'sustainable' or 'sustainability-linked' by the issuers. Specifically&#10;for green bonds, a breakdown is also made between green bonds with assurance&#10;provided by an external party and those lacking such assurance. Monthly figures&#10;are available from 2017.&#8239;</span></span><span class="eop"><span lang="EN-GB">&#160;</span></span><span class="eop"><span lang="EN-GB"></span></span></p></p><p><b>Table Number: </b>4.5.2</p><p><b>Unit: </b>EUR millions</p><p><b>Source: </b>DNB</p>
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilderGetQueryParameters():
        """
        <p><p class="MsoNormal"><span class="normaltextrun"><span lang="EN-GB">Overview of capital outstanding of bonds with&#10;sustainability characteristics (ESG bonds) expressed in market values, broken&#10;down by type of sustainability characteristics and sector. These debt&#10;securities are issued by Dutch residents and have been labelled as 'green',&#10;'social', 'sustainable' or 'sustainability-linked' by the issuers. Specifically&#10;for green bonds, a breakdown is also made between green bonds with assurance&#10;provided by an external party and those lacking such assurance. Monthly figures&#10;are available from 2017.&#8239;</span></span><span class="eop"><span lang="EN-GB">&#160;</span></span><span class="eop"><span lang="EN-GB"></span></span></p></p><p><b>Table Number: </b>4.5.2</p><p><b>Unit: </b>EUR millions</p><p><b>Source: </b>DNB</p>
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
    class IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilderGetRequestConfiguration(RequestConfiguration[IssuanceOfGreenBondsWithExternalAssuranceBySectorRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

