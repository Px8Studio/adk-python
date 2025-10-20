from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class DutchFundUnitHoldingsBySectorOfTheHolderRecord(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The type of instrument
    instrument_type: Optional[str] = None
    # The market value of the observation
    market_value: Optional[float] = None
    # The reference period
    period: Optional[datetime.datetime] = None
    # The institutional sector classification of the holder
    sector_holder: Optional[str] = None
    # The institutional sector classification of the issuer
    sector_issuer: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DutchFundUnitHoldingsBySectorOfTheHolderRecord:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DutchFundUnitHoldingsBySectorOfTheHolderRecord
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DutchFundUnitHoldingsBySectorOfTheHolderRecord()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "instrumentType": lambda n : setattr(self, 'instrument_type', n.get_str_value()),
            "marketValue": lambda n : setattr(self, 'market_value', n.get_float_value()),
            "period": lambda n : setattr(self, 'period', n.get_datetime_value()),
            "sectorHolder": lambda n : setattr(self, 'sector_holder', n.get_str_value()),
            "sectorIssuer": lambda n : setattr(self, 'sector_issuer', n.get_str_value()),
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
        writer.write_str_value("instrumentType", self.instrument_type)
        writer.write_float_value("marketValue", self.market_value)
        writer.write_datetime_value("period", self.period)
        writer.write_str_value("sectorHolder", self.sector_holder)
        writer.write_str_value("sectorIssuer", self.sector_issuer)
        writer.write_additional_data_value(self.additional_data)
    

