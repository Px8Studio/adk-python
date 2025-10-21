from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Metadata(AdditionalDataHolder, Parsable):
    """
    Metadata
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # When a new version for this endpoint is released (see 'isDeprecated') the data for this API version will be removed on this date.
    expected_removal_date: Optional[datetime.datetime] = None
    # Is a next page available
    has_more_pages: Optional[bool] = None
    # Declares this operation to be deprecated. Consumers SHOULD refrain from usage of the declared operation. Default value is 'false'
    is_deprecated: Optional[bool] = None
    # The release date of the current data exposed by the API
    last_release_date: Optional[datetime.datetime] = None
    # The page number
    page: Optional[int] = None
    # The number of results on this page
    page_size: Optional[int] = None
    # Total records in this set
    total_count: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Metadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Metadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Metadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "expectedRemovalDate": lambda n : setattr(self, 'expected_removal_date', n.get_datetime_value()),
            "hasMorePages": lambda n : setattr(self, 'has_more_pages', n.get_bool_value()),
            "isDeprecated": lambda n : setattr(self, 'is_deprecated', n.get_bool_value()),
            "lastReleaseDate": lambda n : setattr(self, 'last_release_date', n.get_datetime_value()),
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
        writer.write_datetime_value("expectedRemovalDate", self.expected_removal_date)
        writer.write_bool_value("hasMorePages", self.has_more_pages)
        writer.write_bool_value("isDeprecated", self.is_deprecated)
        writer.write_datetime_value("lastReleaseDate", self.last_release_date)
        writer.write_int_value("page", self.page)
        writer.write_int_value("pageSize", self.page_size)
        writer.write_int_value("totalCount", self.total_count)
        writer.write_additional_data_value(self.additional_data)
    

