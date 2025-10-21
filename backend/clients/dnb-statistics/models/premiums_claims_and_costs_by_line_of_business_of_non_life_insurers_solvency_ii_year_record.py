from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRecord(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The datapoint corresponding to template, row, and column definitions in taxonomies (Solvency II, Insurers National)
    datapointid: Optional[str] = None
    # The insurance category
    level1: Optional[str] = None
    # The financial component of the insurance category
    level2: Optional[str] = None
    # The type of amount
    level3: Optional[str] = None
    # The reference period
    period: Optional[datetime.datetime] = None
    # The value of the observation
    value: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRecord:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRecord
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PremiumsClaimsAndCostsByLineOfBusinessOfNonLifeInsurersSolvencyIiYearRecord()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "datapointid": lambda n : setattr(self, 'datapointid', n.get_str_value()),
            "level1": lambda n : setattr(self, 'level1', n.get_str_value()),
            "level2": lambda n : setattr(self, 'level2', n.get_str_value()),
            "level3": lambda n : setattr(self, 'level3', n.get_str_value()),
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
        writer.write_str_value("datapointid", self.datapointid)
        writer.write_str_value("level1", self.level1)
        writer.write_str_value("level2", self.level2)
        writer.write_str_value("level3", self.level3)
        writer.write_datetime_value("period", self.period)
        writer.write_float_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

