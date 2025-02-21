from pydantic import BaseModel
from typing import Optional, List


def prepare_additional_fields(additional_fields):
    """
    Prepare a list of additional fields (only those provided) as strings.
    """
    if not additional_fields:
        return ""

    # Configuration for additional fields
    additional_fields_config = [
        ("Salutation", "salutation"),
        ("First Name", "first_name"),
        ("Middle Name", "middle_name"),
        ("Last Name", "last_name"),
        ("Nickname", "nickname"),
        ("Maiden Name", "maiden_name"),
        ("Suffix", "suffix"),
        ("Date of Birth", "date_of_birth"),
        ("Date of Death", "date_of_death"),
        ("City of Death", "city_of_death"),
        ("Region of Death", "region_of_death"),
        ("Country of Death", "country_of_death"),
        ("Place of Birth", "place_of_birth"),
    ]

    additional_fields_list = []

    # Helper function to populate fields
    add_fields_from_config(
        additional_fields_config, additional_fields, additional_fields_list
    )

    return "\n".join(additional_fields_list) if additional_fields_list else ""


def append_field_to_list(
    label: str, value: Optional[str], fields_list: List[str]
) -> None:
    """
    Adds a formatted field to a list if the value exists.
    """
    if value:
        fields_list.append(f"{label}: {value}")


def add_fields_from_config(
    config: List[tuple], source: BaseModel, target: List[str]
) -> None:
    """
    Adds fields from a configuration to a target list based on the source 
    attributes.
    """
    for label, attribute in config:
        value = getattr(source, attribute, None)
        append_field_to_list(label, value, target)


def build_section(title: str, content: str) -> str:
    """
    Builds a formatted section with a title and content.
    """
    return f"--- {title} ---\n{content}\n\n" if content else ""


def prepare_section(title, fields, source_data):
    """
    Populates sections based on the provided fields and source data
    """
    section_data = []
    add_fields_from_config(fields, source_data, section_data)
    return (
        build_section(title, "\n".join(section_data))
        if section_data
        else ""
    )
