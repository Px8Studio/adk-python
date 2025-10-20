from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.language_code_item_request_builder import LanguageCodeItemRequestBuilder
    from .registers.registers_request_builder import RegistersRequestBuilder
    from .supported_languages.supported_languages_request_builder import SupportedLanguagesRequestBuilder

class PublicregisterRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/publicregister
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new PublicregisterRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/publicregister", path_parameters)
    
    def by_language_code_id(self,language_code_id: str) -> LanguageCodeItemRequestBuilder:
        """
        Gets an item from the dnb_public_register_client.api.publicregister.item collection
        param language_code_id: The language code.
        Returns: LanguageCodeItemRequestBuilder
        """
        if language_code_id is None:
            raise TypeError("language_code_id cannot be null.")
        from .item.language_code_item_request_builder import LanguageCodeItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["languageCode%2Did"] = language_code_id
        return LanguageCodeItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def registers(self) -> RegistersRequestBuilder:
        """
        The Registers property
        """
        from .registers.registers_request_builder import RegistersRequestBuilder

        return RegistersRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def supported_languages(self) -> SupportedLanguagesRequestBuilder:
        """
        The SupportedLanguages property
        """
        from .supported_languages.supported_languages_request_builder import SupportedLanguagesRequestBuilder

        return SupportedLanguagesRequestBuilder(self.request_adapter, self.path_parameters)
    

