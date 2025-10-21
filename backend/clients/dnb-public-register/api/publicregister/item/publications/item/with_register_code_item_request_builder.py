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
    from ......models.bad_response_view import BadResponseView
    from ......models.problem_details import ProblemDetails
    from ......models.publication_view import PublicationView
    from .historicalrecord.historicalrecord_request_builder import HistoricalrecordRequestBuilder

class WithRegisterCodeItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/publicregister/{languageCode-id}/Publications/{registerCode}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithRegisterCodeItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/publicregister/{languageCode%2Did}/Publications/{registerCode}{?page*,pageSize*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithRegisterCodeItemRequestBuilderGetQueryParameters]] = None) -> Optional[PublicationView]:
        """
        Gets the latest publication for the specified language code and register code.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[PublicationView]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.bad_response_view import BadResponseView
        from ......models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": BadResponseView,
            "404": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.publication_view import PublicationView

        return await self.request_adapter.send_async(request_info, PublicationView, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithRegisterCodeItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Gets the latest publication for the specified language code and register code.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WithRegisterCodeItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithRegisterCodeItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithRegisterCodeItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def historicalrecord(self) -> HistoricalrecordRequestBuilder:
        """
        The historicalrecord property
        """
        from .historicalrecord.historicalrecord_request_builder import HistoricalrecordRequestBuilder

        return HistoricalrecordRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithRegisterCodeItemRequestBuilderGetQueryParameters():
        """
        Gets the latest publication for the specified language code and register code.
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
            if original_name == "page":
                return "page"
            return original_name
        
        # The page number. Where 1 indicates the first page. Defaults to the first page.
        page: Optional[int] = None

        # The amount of records one page contains. Defaults to 10 records. Maximum of 25 records is allowed.
        page_size: Optional[int] = None

    
    @dataclass
    class WithRegisterCodeItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithRegisterCodeItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

