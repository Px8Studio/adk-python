from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..models.metadata import Metadata
    from ..models.securitisation_vehicles_balance_sheet_record import SecuritisationVehiclesBalanceSheetRecord

@dataclass
class SecuritisationVehiclesBalanceSheetGetResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Metadata
    _metadata: Optional[Metadata] = None
    # The release date of the current data exposed by the API
    last_release_date: Optional[datetime.datetime] = None
    # Securitisation Vehicles balance sheet
    records: Optional[list[SecuritisationVehiclesBalanceSheetRecord]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SecuritisationVehiclesBalanceSheetGetResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SecuritisationVehiclesBalanceSheetGetResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SecuritisationVehiclesBalanceSheetGetResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from ..models.metadata import Metadata
        from ..models.securitisation_vehicles_balance_sheet_record import SecuritisationVehiclesBalanceSheetRecord

        from ..models.metadata import Metadata
        from ..models.securitisation_vehicles_balance_sheet_record import SecuritisationVehiclesBalanceSheetRecord

        fields: dict[str, Callable[[Any], None]] = {
            "_metadata": lambda n : setattr(self, '_metadata', n.get_object_value(Metadata)),
            "lastReleaseDate": lambda n : setattr(self, 'last_release_date', n.get_datetime_value()),
            "records": lambda n : setattr(self, 'records', n.get_collection_of_object_values(SecuritisationVehiclesBalanceSheetRecord)),
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
        writer.write_object_value("_metadata", self._metadata)
        writer.write_datetime_value("lastReleaseDate", self.last_release_date)
        writer.write_collection_of_object_values("records", self.records)
        writer.write_additional_data_value(self.additional_data)
    

