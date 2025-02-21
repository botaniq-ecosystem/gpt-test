from pydantic import BaseModel, Field
from typing import Optional

from app.services.prompt_builder import (
    ObituaryLength,
    ObituaryStyle,
    AdditionalFields,
)


class ScratchpadNotesRequest(BaseModel):
    unstructured_notes: str = Field(
        ..., description="Unstructured notes about the obituary content"
    )
    obituary_style: Optional[ObituaryStyle] = (
        ObituaryStyle.TRADITIONAL
    )  # Default tone style
    obituary_length: Optional[ObituaryLength] = (
        ObituaryLength.LONG  # Default length
    )
    additional_fields: Optional[AdditionalFields] = None
    should_stream: Optional[bool] = (
        True  # Add should_stream as optional with a default value
    )

    class Config:
        json_schema_extra = {
            "example": {
                "unstructured_notes": "John Doe passed away on September 20, 2023, in Denver, CO.",  # noqa E501
                "obituary_style": "poetic",
                "obituary_length": "long",
                "should_stream": False,
                "additional_fields": {
                    "salutation": "Mr.",
                    "first_name": "John",
                    "middle_name": "A.",
                    "last_name": "Doe",
                    "nickname": "Johnny",
                    "date_of_birth": "1950-01-15",
                    "date_of_death": "2023-09-20",
                    "city_of_death": "Denver",
                    "region_of_death": "Colorado",
                    "country_of_death": "United States",
                    "place_of_birth": "New York, NY",
                },
            }
        }
