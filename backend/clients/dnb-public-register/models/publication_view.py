from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .language_view import LanguageView
    from .organization_view import OrganizationView
    from .pagination_details_view import PaginationDetailsView

@dataclass
class PublicationView(Parsable):
    """
    The publication details of a specific register
    """
    # The pagination details
    _metadata: Optional[PaginationDetailsView] = None
    # The language code of the publication
    language_code: Optional[LanguageView] = None
    # The organizations belonging to the publication
    organizations: Optional[list[OrganizationView]] = None
    # When this publication was published
    publish_date: Optional[datetime.datetime] = None
    # The code of the register
    register_code: Optional[str] = None
    # The name of the register
    register_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PublicationView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PublicationView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PublicationView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .language_view import LanguageView
        from .organization_view import OrganizationView
        from .pagination_details_view import PaginationDetailsView

        from .language_view import LanguageView
        from .organization_view import OrganizationView
        from .pagination_details_view import PaginationDetailsView

        fields: dict[str, Callable[[Any], None]] = {
            "_metadata": lambda n : setattr(self, '_metadata', n.get_object_value(PaginationDetailsView)),
            "languageCode": lambda n : setattr(self, 'language_code', n.get_object_value(LanguageView)),
            "organizations": lambda n : setattr(self, 'organizations', n.get_collection_of_object_values(OrganizationView)),
            "publishDate": lambda n : setattr(self, 'publish_date', n.get_datetime_value()),
            "registerCode": lambda n : setattr(self, 'register_code', n.get_str_value()),
            "registerName": lambda n : setattr(self, 'register_name', n.get_str_value()),
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
        writer.write_object_value("languageCode", self.language_code)
        writer.write_collection_of_object_values("organizations", self.organizations)
        writer.write_datetime_value("publishDate", self.publish_date)
        writer.write_str_value("registerCode", self.register_code)
        writer.write_str_value("registerName", self.register_name)
    

