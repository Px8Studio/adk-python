from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ContactChannelView(Parsable):
    """
    The address, emailaddress or URL
    """
    # The city
    city: Optional[str] = None
    # The type indicating what kind of address the contact channel is
    contact_channel_type: Optional[str] = None
    # A two letter iso code indicating the country of where the address is located
    country_iso_code: Optional[str] = None
    # Any remarks which belong to the address
    description: Optional[str] = None
    # The email address
    email_address: Optional[str] = None
    # The house number
    house_number: Optional[str] = None
    # The house number addition
    house_number_addition: Optional[str] = None
    # Whether or not the address is a postbox
    is_post_office_box: Optional[bool] = None
    # The location
    location: Optional[str] = None
    # The phone number
    phone_number: Optional[str] = None
    # The postbox number
    post_office_number: Optional[str] = None
    # The postal code of the address
    postal_code: Optional[str] = None
    # The name of the street
    street: Optional[str] = None
    # The website
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ContactChannelView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ContactChannelView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ContactChannelView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "city": lambda n : setattr(self, 'city', n.get_str_value()),
            "contactChannelType": lambda n : setattr(self, 'contact_channel_type', n.get_str_value()),
            "countryIsoCode": lambda n : setattr(self, 'country_iso_code', n.get_str_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "emailAddress": lambda n : setattr(self, 'email_address', n.get_str_value()),
            "houseNumber": lambda n : setattr(self, 'house_number', n.get_str_value()),
            "houseNumberAddition": lambda n : setattr(self, 'house_number_addition', n.get_str_value()),
            "isPostOfficeBox": lambda n : setattr(self, 'is_post_office_box', n.get_bool_value()),
            "location": lambda n : setattr(self, 'location', n.get_str_value()),
            "phoneNumber": lambda n : setattr(self, 'phone_number', n.get_str_value()),
            "postOfficeNumber": lambda n : setattr(self, 'post_office_number', n.get_str_value()),
            "postalCode": lambda n : setattr(self, 'postal_code', n.get_str_value()),
            "street": lambda n : setattr(self, 'street', n.get_str_value()),
            "url": lambda n : setattr(self, 'url', n.get_str_value()),
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
        writer.write_str_value("city", self.city)
        writer.write_str_value("contactChannelType", self.contact_channel_type)
        writer.write_str_value("countryIsoCode", self.country_iso_code)
        writer.write_str_value("description", self.description)
        writer.write_str_value("emailAddress", self.email_address)
        writer.write_str_value("houseNumber", self.house_number)
        writer.write_str_value("houseNumberAddition", self.house_number_addition)
        writer.write_bool_value("isPostOfficeBox", self.is_post_office_box)
        writer.write_str_value("location", self.location)
        writer.write_str_value("phoneNumber", self.phone_number)
        writer.write_str_value("postOfficeNumber", self.post_office_number)
        writer.write_str_value("postalCode", self.postal_code)
        writer.write_str_value("street", self.street)
        writer.write_str_value("url", self.url)
    

