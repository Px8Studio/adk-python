from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class AllowedMifidActivityView(Parsable):
    """
    The allowed mifid activity. Is specific for Banks and other institutions that need to follow the MIFID rules
    """
    # The code of the parent Act Activity
    act_activity_register_code: Optional[str] = None
    # The name of the Allowed Activity
    allowed_activity_name: Optional[str] = None
    # The instrument
    financial_instrument: Optional[str] = None
    # The end date of the allowed activity
    validity_period_end_date: Optional[datetime.datetime] = None
    # The start date of the allowed activity
    validity_period_start_date: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AllowedMifidActivityView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AllowedMifidActivityView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AllowedMifidActivityView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "actActivityRegisterCode": lambda n : setattr(self, 'act_activity_register_code', n.get_str_value()),
            "allowedActivityName": lambda n : setattr(self, 'allowed_activity_name', n.get_str_value()),
            "financialInstrument": lambda n : setattr(self, 'financial_instrument', n.get_str_value()),
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
        writer.write_str_value("actActivityRegisterCode", self.act_activity_register_code)
        writer.write_str_value("allowedActivityName", self.allowed_activity_name)
        writer.write_str_value("financialInstrument", self.financial_instrument)
        writer.write_datetime_value("validityPeriodEndDate", self.validity_period_end_date)
        writer.write_datetime_value("validityPeriodStartDate", self.validity_period_start_date)
    

