from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class PaginationDetailsView(Parsable):
    """
    The meta details of the pagination.
    """
    # Whether or not more pages exists.
    has_more_pages: Optional[bool] = None
    # The number of the page. Where 1 indicates the first page.
    page: Optional[int] = None
    # The total records of one page.
    page_size: Optional[int] = None
    # The total amount of records.
    total_count: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PaginationDetailsView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PaginationDetailsView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PaginationDetailsView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "hasMorePages": lambda n : setattr(self, 'has_more_pages', n.get_bool_value()),
            "page": lambda n : setattr(self, 'page', n.get_int_value()),
            "pageSize": lambda n : setattr(self, 'page_size', n.get_int_value()),
            "totalCount": lambda n : setattr(self, 'total_count', n.get_int_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_bool_value("hasMorePages", self.has_more_pages)
        writer.write_int_value("page", self.page)
        writer.write_int_value("pageSize", self.page_size)
        writer.write_int_value("totalCount", self.total_count)
    

