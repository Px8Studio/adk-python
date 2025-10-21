from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .organization_relation_number_view import OrganizationRelationNumberView
    from .pagination_details_view import PaginationDetailsView

@dataclass
class OrganizationRelationNumbersView(Parsable):
    """
    The relation numbers of the organization in a specific register
    """
    # The pagination details.
    _metadata: Optional[PaginationDetailsView] = None
    # The last date the register has been published
    publish_date: Optional[datetime.datetime] = None
    # The code of the register the relation numbers belong to
    register_code: Optional[str] = None
    # The name of the register
    register_name: Optional[str] = None
    # The relation numbers which belong to the register
    relation_numbers: Optional[list[OrganizationRelationNumberView]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OrganizationRelationNumbersView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OrganizationRelationNumbersView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OrganizationRelationNumbersView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .organization_relation_number_view import OrganizationRelationNumberView
        from .pagination_details_view import PaginationDetailsView

        from .organization_relation_number_view import OrganizationRelationNumberView
        from .pagination_details_view import PaginationDetailsView

        fields: dict[str, Callable[[Any], None]] = {
            "_metadata": lambda n : setattr(self, '_metadata', n.get_object_value(PaginationDetailsView)),
            "publishDate": lambda n : setattr(self, 'publish_date', n.get_datetime_value()),
            "registerCode": lambda n : setattr(self, 'register_code', n.get_str_value()),
            "registerName": lambda n : setattr(self, 'register_name', n.get_str_value()),
            "relationNumbers": lambda n : setattr(self, 'relation_numbers', n.get_collection_of_object_values(OrganizationRelationNumberView)),
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
        writer.write_object_value("_metadata", self._metadata)
        writer.write_datetime_value("publishDate", self.publish_date)
        writer.write_str_value("registerCode", self.register_code)
        writer.write_str_value("registerName", self.register_name)
        writer.write_collection_of_object_values("relationNumbers", self.relation_numbers)
    

