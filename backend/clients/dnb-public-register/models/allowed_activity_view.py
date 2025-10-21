from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class AllowedActivityView(Parsable):
    """
    The allowed activity
    """
    # The name of the Act Activity which is the parent of the Allowed Activity
    act_activity_name: Optional[str] = None
    # If end data has value the definitive date is the time to check if the allowed activity can be closed
    definitive_date: Optional[datetime.datetime] = None
    # The end date of the allowed activity
    validity_period_end_date: Optional[datetime.datetime] = None
    # The start date of the allowed activity
    validity_period_start_date: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AllowedActivityView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AllowedActivityView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AllowedActivityView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "actActivityName": lambda n : setattr(self, 'act_activity_name', n.get_str_value()),
            "definitiveDate": lambda n : setattr(self, 'definitive_date', n.get_datetime_value()),
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
        writer.write_str_value("actActivityName", self.act_activity_name)
        writer.write_datetime_value("definitiveDate", self.definitive_date)
        writer.write_datetime_value("validityPeriodEndDate", self.validity_period_end_date)
        writer.write_datetime_value("validityPeriodStartDate", self.validity_period_start_date)
    

