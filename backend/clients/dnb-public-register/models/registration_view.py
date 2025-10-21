from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .allowed_activity_view import AllowedActivityView
    from .allowed_mifid_activity_view import AllowedMifidActivityView
    from .condition_view import ConditionView
    from .country_view import CountryView

@dataclass
class RegistrationView(Parsable):
    """
    The registration
    """
    # The code of the underlying act article
    act_article_code: Optional[str] = None
    # The name of the underlying act article
    act_article_name: Optional[str] = None
    # The department of the act article
    act_department: Optional[str] = None
    # The name of the act
    act_name: Optional[str] = None
    # The allowed activities which this registration contains
    allowed_activities: Optional[list[AllowedActivityView]] = None
    # The allowed mifid activities
    allowed_mifid_activities: Optional[list[AllowedMifidActivityView]] = None
    # The conditions of this registration
    conditions: Optional[list[ConditionView]] = None
    # The country for where the registration has been applied
    country: Optional[CountryView] = None
    # The description of the registration
    description: Optional[str] = None
    # The identifier of the registration as known by DNB
    id: Optional[UUID] = None
    # The product
    involved_product: Optional[str] = None
    # If end data has value the irrevoable date is the time to check if the registration can be closed
    irrevocable_date: Optional[datetime.datetime] = None
    # The code of the group that groups the different register articles together
    register_article_group_code: Optional[str] = None
    # The type of the registration
    registration_type: Optional[str] = None
    # The end date of the registration
    validity_period_end_date: Optional[datetime.datetime] = None
    # The start date of the registration
    validity_period_start_date: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RegistrationView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RegistrationView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RegistrationView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .allowed_activity_view import AllowedActivityView
        from .allowed_mifid_activity_view import AllowedMifidActivityView
        from .condition_view import ConditionView
        from .country_view import CountryView

        from .allowed_activity_view import AllowedActivityView
        from .allowed_mifid_activity_view import AllowedMifidActivityView
        from .condition_view import ConditionView
        from .country_view import CountryView

        fields: dict[str, Callable[[Any], None]] = {
            "actArticleCode": lambda n : setattr(self, 'act_article_code', n.get_str_value()),
            "actArticleName": lambda n : setattr(self, 'act_article_name', n.get_str_value()),
            "actDepartment": lambda n : setattr(self, 'act_department', n.get_str_value()),
            "actName": lambda n : setattr(self, 'act_name', n.get_str_value()),
            "allowedActivities": lambda n : setattr(self, 'allowed_activities', n.get_collection_of_object_values(AllowedActivityView)),
            "allowedMifidActivities": lambda n : setattr(self, 'allowed_mifid_activities', n.get_collection_of_object_values(AllowedMifidActivityView)),
            "conditions": lambda n : setattr(self, 'conditions', n.get_collection_of_object_values(ConditionView)),
            "country": lambda n : setattr(self, 'country', n.get_object_value(CountryView)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "involvedProduct": lambda n : setattr(self, 'involved_product', n.get_str_value()),
            "irrevocableDate": lambda n : setattr(self, 'irrevocable_date', n.get_datetime_value()),
            "registerArticleGroupCode": lambda n : setattr(self, 'register_article_group_code', n.get_str_value()),
            "registrationType": lambda n : setattr(self, 'registration_type', n.get_str_value()),
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
        writer.write_str_value("actArticleCode", self.act_article_code)
        writer.write_str_value("actArticleName", self.act_article_name)
        writer.write_str_value("actDepartment", self.act_department)
        writer.write_str_value("actName", self.act_name)
        writer.write_collection_of_object_values("allowedActivities", self.allowed_activities)
        writer.write_collection_of_object_values("allowedMifidActivities", self.allowed_mifid_activities)
        writer.write_collection_of_object_values("conditions", self.conditions)
        writer.write_object_value("country", self.country)
        writer.write_str_value("description", self.description)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("involvedProduct", self.involved_product)
        writer.write_datetime_value("irrevocableDate", self.irrevocable_date)
        writer.write_str_value("registerArticleGroupCode", self.register_article_group_code)
        writer.write_str_value("registrationType", self.registration_type)
        writer.write_datetime_value("validityPeriodEndDate", self.validity_period_end_date)
        writer.write_datetime_value("validityPeriodStartDate", self.validity_period_start_date)
    

