from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class FinancialDataOfIndividualBanksHalfYearRecord(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The subject area of the item
    area: Optional[str] = None
    # The basis of the reporting standard
    basis: Optional[str] = None
    # The type of main item
    main_item: Optional[str] = None
    # The name of the reporting bank
    name_of_bank: Optional[str] = None
    # The reference period
    period: Optional[datetime.datetime] = None
    # The type of sub item
    sub_item: Optional[str] = None
    # The value of the observation
    value: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FinancialDataOfIndividualBanksHalfYearRecord:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FinancialDataOfIndividualBanksHalfYearRecord
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FinancialDataOfIndividualBanksHalfYearRecord()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "area": lambda n : setattr(self, 'area', n.get_str_value()),
            "basis": lambda n : setattr(self, 'basis', n.get_str_value()),
            "mainItem": lambda n : setattr(self, 'main_item', n.get_str_value()),
            "nameOfBank": lambda n : setattr(self, 'name_of_bank', n.get_str_value()),
            "period": lambda n : setattr(self, 'period', n.get_datetime_value()),
            "subItem": lambda n : setattr(self, 'sub_item', n.get_str_value()),
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
        writer.write_str_value("area", self.area)
        writer.write_str_value("basis", self.basis)
        writer.write_str_value("mainItem", self.main_item)
        writer.write_str_value("nameOfBank", self.name_of_bank)
        writer.write_datetime_value("period", self.period)
        writer.write_str_value("subItem", self.sub_item)
        writer.write_float_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

