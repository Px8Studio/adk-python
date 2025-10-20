from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_register_code_item_request_builder import WithRegisterCodeItemRequestBuilder
    from .organizations.organizations_request_builder import OrganizationsRequestBuilder
    from .publications.publications_request_builder import PublicationsRequestBuilder

class LanguageCodeItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/publicregister/{languageCode-id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new LanguageCodeItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/publicregister/{languageCode%2Did}", path_parameters)
    
    def by_register_code(self,register_code: str) -> WithRegisterCodeItemRequestBuilder:
        """
        Gets an item from the dnb_public_register_client.api.publicregister.item.item collection
        param register_code: The register code.
        Returns: WithRegisterCodeItemRequestBuilder
        """
        if register_code is None:
            raise TypeError("register_code cannot be null.")
        from .item.with_register_code_item_request_builder import WithRegisterCodeItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["registerCode"] = register_code
        return WithRegisterCodeItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def organizations(self) -> OrganizationsRequestBuilder:
        """
        The Organizations property
        """
        from .organizations.organizations_request_builder import OrganizationsRequestBuilder

        return OrganizationsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def publications(self) -> PublicationsRequestBuilder:
        """
        The Publications property
        """
        from .publications.publications_request_builder import PublicationsRequestBuilder

        return PublicationsRequestBuilder(self.request_adapter, self.path_parameters)
    

