from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRecord(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The item on the balance sheet
    balance_sheet_item: Optional[str] = None
    # The side of the balance sheet (assets or liabilities)
    balance_sheet_side: Optional[str] = None
    # The name of the geographical region
    geography: Optional[str] = None
    # The reference period
    period: Optional[datetime.datetime] = None
    # The value of the observation
    value: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRecord:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRecord
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BalanceSheetOfOtherFinancialIntermediariesByGeographyQuarterRecord()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "balanceSheetItem": lambda n : setattr(self, 'balance_sheet_item', n.get_str_value()),
            "balanceSheetSide": lambda n : setattr(self, 'balance_sheet_side', n.get_str_value()),
            "geography": lambda n : setattr(self, 'geography', n.get_str_value()),
            "period": lambda n : setattr(self, 'period', n.get_datetime_value()),
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
        writer.write_str_value("balanceSheetItem", self.balance_sheet_item)
        writer.write_str_value("balanceSheetSide", self.balance_sheet_side)
        writer.write_str_value("geography", self.geography)
        writer.write_datetime_value("period", self.period)
        writer.write_float_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

