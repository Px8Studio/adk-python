from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class BalanceOfPaymentsYearRecord(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Total or contribution SPE's
    contribution_spes: Optional[str] = None
    # The type of account (current, capital or financial account)
    main_item: Optional[str] = None
    # The reference period
    period: Optional[datetime.datetime] = None
    # The first type of sub item
    sub_item1: Optional[str] = None
    # The second type of sub item
    sub_item2: Optional[str] = None
    # The value of the observation
    value: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BalanceOfPaymentsYearRecord:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BalanceOfPaymentsYearRecord
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BalanceOfPaymentsYearRecord()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "contributionSpes": lambda n : setattr(self, 'contribution_spes', n.get_str_value()),
            "mainItem": lambda n : setattr(self, 'main_item', n.get_str_value()),
            "period": lambda n : setattr(self, 'period', n.get_datetime_value()),
            "subItem1": lambda n : setattr(self, 'sub_item1', n.get_str_value()),
            "subItem2": lambda n : setattr(self, 'sub_item2', n.get_str_value()),
            "value": lambda n : setattr(self, 'value', n.get_float_value()),
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
        writer.write_str_value("contributionSpes", self.contribution_spes)
        writer.write_str_value("mainItem", self.main_item)
        writer.write_datetime_value("period", self.period)
        writer.write_str_value("subItem1", self.sub_item1)
        writer.write_str_value("subItem2", self.sub_item2)
        writer.write_float_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

