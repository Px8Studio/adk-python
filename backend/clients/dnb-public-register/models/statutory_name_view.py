from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class StatutoryNameView(Parsable):
    """
    The statutory name details
    """
    # The statutory name
    name: Optional[str] = None
    # The end date of the name
    validity_period_end_date: Optional[datetime.datetime] = None
    # The start date of the name
    validity_period_start_date: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> StatutoryNameView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: StatutoryNameView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return StatutoryNameView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "validityPeriodEndDate": lambda n : setattr(self, 'validity_period_end_date', n.get_datetime_value()),
            "validityPeriodStartDate": lambda n : setattr(self, 'validity_period_start_date', n.get_datetime_value()),
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
        writer.write_str_value("name", self.name)
        writer.write_datetime_value("validityPeriodEndDate", self.validity_period_end_date)
        writer.write_datetime_value("validityPeriodStartDate", self.validity_period_start_date)
    

