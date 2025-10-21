from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .classification_view import ClassificationView
    from .contact_channel_view import ContactChannelView
    from .covered_bond_view import CoveredBondView
    from .official_name_view import OfficialNameView
    from .registration_view import RegistrationView
    from .related_organization_view import RelatedOrganizationView
    from .statutory_name_view import StatutoryNameView
    from .trade_name_view import TradeNameView

@dataclass
class OrganizationView(Parsable):
    """
    A specific organization
    """
    # The branch number of the organization.
    branch_number: Optional[str] = None
    # The number as known in the chamber of commerce
    chamber_of_commerce: Optional[str] = None
    # The classifications of the organization
    classifications: Optional[list[ClassificationView]] = None
    # The addresses of the organization
    contact_channels: Optional[list[ContactChannelView]] = None
    # The covered bonds of the organization
    covered_bonds: Optional[list[CoveredBondView]] = None
    # When the bankruptcy got declared
    date_of_liquidation: Optional[datetime.datetime] = None
    # Whether or not the organization has declared bankruptcy
    is_in_liquidation: Optional[bool] = None
    # Whether or not this organization is the parent organization
    is_main: Optional[bool] = None
    # The legal duration of the organization
    legal_duration: Optional[str] = None
    # The LEI code of the organization
    lei_code: Optional[str] = None
    # The official names of the organization
    official_names: Optional[list[OfficialNameView]] = None
    # The registrations of the organizations
    registrations: Optional[list[RegistrationView]] = None
    # The related organizations belonging to this organization
    related_organizations: Optional[list[RelatedOrganizationView]] = None
    # The relation number as known by the DNB
    relation_number: Optional[str] = None
    # The RSIN code of the organization
    rsin_code: Optional[str] = None
    # The statutory country of the organization
    statutory_country: Optional[str] = None
    # The statutory names of the organization
    statutory_names: Optional[list[StatutoryNameView]] = None
    # The statutory place of the organization
    statutory_place: Optional[str] = None
    # The trade names of the organization
    trade_names: Optional[list[TradeNameView]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OrganizationView:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OrganizationView
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OrganizationView()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .classification_view import ClassificationView
        from .contact_channel_view import ContactChannelView
        from .covered_bond_view import CoveredBondView
        from .official_name_view import OfficialNameView
        from .registration_view import RegistrationView
        from .related_organization_view import RelatedOrganizationView
        from .statutory_name_view import StatutoryNameView
        from .trade_name_view import TradeNameView

        from .classification_view import ClassificationView
        from .contact_channel_view import ContactChannelView
        from .covered_bond_view import CoveredBondView
        from .official_name_view import OfficialNameView
        from .registration_view import RegistrationView
        from .related_organization_view import RelatedOrganizationView
        from .statutory_name_view import StatutoryNameView
        from .trade_name_view import TradeNameView

        fields: dict[str, Callable[[Any], None]] = {
            "branchNumber": lambda n : setattr(self, 'branch_number', n.get_str_value()),
            "chamberOfCommerce": lambda n : setattr(self, 'chamber_of_commerce', n.get_str_value()),
            "classifications": lambda n : setattr(self, 'classifications', n.get_collection_of_object_values(ClassificationView)),
            "contactChannels": lambda n : setattr(self, 'contact_channels', n.get_collection_of_object_values(ContactChannelView)),
            "coveredBonds": lambda n : setattr(self, 'covered_bonds', n.get_collection_of_object_values(CoveredBondView)),
            "dateOfLiquidation": lambda n : setattr(self, 'date_of_liquidation', n.get_datetime_value()),
            "isInLiquidation": lambda n : setattr(self, 'is_in_liquidation', n.get_bool_value()),
            "isMain": lambda n : setattr(self, 'is_main', n.get_bool_value()),
            "legalDuration": lambda n : setattr(self, 'legal_duration', n.get_str_value()),
            "leiCode": lambda n : setattr(self, 'lei_code', n.get_str_value()),
            "officialNames": lambda n : setattr(self, 'official_names', n.get_collection_of_object_values(OfficialNameView)),
            "registrations": lambda n : setattr(self, 'registrations', n.get_collection_of_object_values(RegistrationView)),
            "relatedOrganizations": lambda n : setattr(self, 'related_organizations', n.get_collection_of_object_values(RelatedOrganizationView)),
            "relationNumber": lambda n : setattr(self, 'relation_number', n.get_str_value()),
            "rsinCode": lambda n : setattr(self, 'rsin_code', n.get_str_value()),
            "statutoryCountry": lambda n : setattr(self, 'statutory_country', n.get_str_value()),
            "statutoryNames": lambda n : setattr(self, 'statutory_names', n.get_collection_of_object_values(StatutoryNameView)),
            "statutoryPlace": lambda n : setattr(self, 'statutory_place', n.get_str_value()),
            "tradeNames": lambda n : setattr(self, 'trade_names', n.get_collection_of_object_values(TradeNameView)),
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
        writer.write_str_value("branchNumber", self.branch_number)
        writer.write_str_value("chamberOfCommerce", self.chamber_of_commerce)
        writer.write_collection_of_object_values("classifications", self.classifications)
        writer.write_collection_of_object_values("contactChannels", self.contact_channels)
        writer.write_collection_of_object_values("coveredBonds", self.covered_bonds)
        writer.write_datetime_value("dateOfLiquidation", self.date_of_liquidation)
        writer.write_bool_value("isInLiquidation", self.is_in_liquidation)
        writer.write_bool_value("isMain", self.is_main)
        writer.write_str_value("legalDuration", self.legal_duration)
        writer.write_str_value("leiCode", self.lei_code)
        writer.write_collection_of_object_values("officialNames", self.official_names)
        writer.write_collection_of_object_values("registrations", self.registrations)
        writer.write_collection_of_object_values("relatedOrganizations", self.related_organizations)
        writer.write_str_value("relationNumber", self.relation_number)
        writer.write_str_value("rsinCode", self.rsin_code)
        writer.write_str_value("statutoryCountry", self.statutory_country)
        writer.write_collection_of_object_values("statutoryNames", self.statutory_names)
        writer.write_str_value("statutoryPlace", self.statutory_place)
        writer.write_collection_of_object_values("tradeNames", self.trade_names)
    

