from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .organizations.organizations_request_builder import OrganizationsRequestBuilder
    from .register_articles.register_articles_request_builder import RegisterArticlesRequestBuilder
    from .registrations.registrations_request_builder import RegistrationsRequestBuilder

class WithRegisterCodeItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/publicregister/{languageCode-id}/{registerCode}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithRegisterCodeItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/publicregister/{languageCode%2Did}/{registerCode}", path_parameters)
    
    @property
    def organizations(self) -> OrganizationsRequestBuilder:
        """
        The Organizations property
        """
        from .organizations.organizations_request_builder import OrganizationsRequestBuilder

        return OrganizationsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def register_articles(self) -> RegisterArticlesRequestBuilder:
        """
        The RegisterArticles property
        """
        from .register_articles.register_articles_request_builder import RegisterArticlesRequestBuilder

        return RegisterArticlesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def registrations(self) -> RegistrationsRequestBuilder:
        """
        The Registrations property
        """
        from .registrations.registrations_request_builder import RegistrationsRequestBuilder

        return RegistrationsRequestBuilder(self.request_adapter, self.path_parameters)
    

