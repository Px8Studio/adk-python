from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class CoveredBondView(Parsable):
    """
    The covered bond
    """
    # The end date of the covered bond
    end_date: Optional[datetime.datetime] = None
    # Whether or not the covered bond is in accordance with the DNB
    is_in_accordance_with: Optional[bool] = None
    # The start date
    issue_date: Optional[datetime.datetime] = None
    # The monthly investor report
    monthly_investor_report: Optional[str] = None
    # The name of the program
    program_name: Optional[str] = None
    # The date of the registration
    registration_date: Optional[datetime.datetime] = None
    # Any remarks of the covered bond
    remarks: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CoveredBondView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CoveredBondView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CoveredBondView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "endDate": lambda n : setattr(self, 'end_date', n.get_datetime_value()),
            "isInAccordanceWith": lambda n : setattr(self, 'is_in_accordance_with', n.get_bool_value()),
            "issueDate": lambda n : setattr(self, 'issue_date', n.get_datetime_value()),
            "monthlyInvestorReport": lambda n : setattr(self, 'monthly_investor_report', n.get_str_value()),
            "programName": lambda n : setattr(self, 'program_name', n.get_str_value()),
            "registrationDate": lambda n : setattr(self, 'registration_date', n.get_datetime_value()),
            "remarks": lambda n : setattr(self, 'remarks', n.get_str_value()),
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
        writer.write_datetime_value("endDate", self.end_date)
        writer.write_bool_value("isInAccordanceWith", self.is_in_accordance_with)
        writer.write_datetime_value("issueDate", self.issue_date)
        writer.write_str_value("monthlyInvestorReport", self.monthly_investor_report)
        writer.write_str_value("programName", self.program_name)
        writer.write_datetime_value("registrationDate", self.registration_date)
        writer.write_str_value("remarks", self.remarks)
    

