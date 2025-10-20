from __future__ import annotations
import datetime
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_date_item_request_builder import WithDateItemRequestBuilder

class HistoricalrecordRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/publicregister/{languageCode-id}/Publications/{registerCode}/historicalrecord
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new HistoricalrecordRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/publicregister/{languageCode%2Did}/Publications/{registerCode}/historicalrecord", path_parameters)
    
    def by_date(self,date: datetime.datetime) -> WithDateItemRequestBuilder:
        """
        Gets an item from the dnb_public_register.api.publicregister.item.Publications.item.historicalrecord.item collection
        param date: The date of when the publication was published.
        Returns: WithDateItemRequestBuilder
        """
        if date is None:
            raise TypeError("date cannot be null.")
        from .item.with_date_item_request_builder import WithDateItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["date"] = date
        return WithDateItemRequestBuilder(self.request_adapter, url_tpl_params)
    

