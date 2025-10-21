from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .child_organization_view import ChildOrganizationView

@dataclass
class RelatedOrganizationView(Parsable):
    """
    The related organization of a different organization
    """
    # The related organization details
    child_organization: Optional[ChildOrganizationView] = None
    # The definitive date that the releated organization is no longer related
    definitive_date: Optional[datetime.datetime] = None
    # The percentage of participation
    percentage_participation: Optional[str] = None
    # the relation code
    register_relation_code: Optional[str] = None
    # The remarks
    remarks: Optional[str] = None
    # The start date of the relation
    start_date: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RelatedOrganizationView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RelatedOrganizationView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RelatedOrganizationView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .child_organization_view import ChildOrganizationView

        from .child_organization_view import ChildOrganizationView

        fields: dict[str, Callable[[Any], None]] = {
            "childOrganization": lambda n : setattr(self, 'child_organization', n.get_object_value(ChildOrganizationView)),
            "definitiveDate": lambda n : setattr(self, 'definitive_date', n.get_datetime_value()),
            "percentageParticipation": lambda n : setattr(self, 'percentage_participation', n.get_str_value()),
            "registerRelationCode": lambda n : setattr(self, 'register_relation_code', n.get_str_value()),
            "remarks": lambda n : setattr(self, 'remarks', n.get_str_value()),
            "startDate": lambda n : setattr(self, 'start_date', n.get_datetime_value()),
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
        writer.write_object_value("childOrganization", self.child_organization)
        writer.write_datetime_value("definitiveDate", self.definitive_date)
        writer.write_str_value("percentageParticipation", self.percentage_participation)
        writer.write_str_value("registerRelationCode", self.register_relation_code)
        writer.write_str_value("remarks", self.remarks)
        writer.write_datetime_value("startDate", self.start_date)
    

