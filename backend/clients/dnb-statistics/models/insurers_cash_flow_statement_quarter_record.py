from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class InsurersCashFlowStatementQuarterRecord(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Breakdown of the types of instruments
    breakdown: Optional[str] = None
    # The type of instrument
    instrument: Optional[str] = None
    # The reference period
    period: Optional[datetime.datetime] = None
    # The type of transaction
    transactions: Optional[str] = None
    # The value of the observation
    value: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> InsurersCashFlowStatementQuarterRecord:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: InsurersCashFlowStatementQuarterRecord
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return InsurersCashFlowStatementQuarterRecord()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "breakdown": lambda n : setattr(self, 'breakdown', n.get_str_value()),
            "instrument": lambda n : setattr(self, 'instrument', n.get_str_value()),
            "period": lambda n : setattr(self, 'period', n.get_datetime_value()),
            "transactions": lambda n : setattr(self, 'transactions', n.get_str_value()),
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
        writer.write_str_value("breakdown", self.breakdown)
        writer.write_str_value("instrument", self.instrument)
        writer.write_datetime_value("period", self.period)
        writer.write_str_value("transactions", self.transactions)
        writer.write_float_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

