import logging
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

from pydantic import BaseModel
from app.core.shared_request_fields import (
    prepare_additional_fields,
    add_fields_from_config,
    build_section,
    prepare_section,
)

log = logging.getLogger(__name__)


# region Enums
class ObituaryStyle(str, Enum):
    CELEBRATORY = "celebratory"
    POETIC = "poetic"
    PROFESSIONAL = "professional"
    RELIGIOUS = "religious"
    TRADITIONAL = "traditional"


class ObituaryLength(str, Enum):
    LONG = "long"
    MEDIUM = "medium"
    SHORT = "short"


class Gender(str, Enum):
    HE_HIM = "he_him"
    SHE_HER = "she_her"
    THEY_THEM = "they_them"
    OTHER = "other"


class ServiceType(str, Enum):
    VISITATION = "visitation"
    CALLING_HOURS = "calling_hours"
    VIGIL = "vigil"
    WAKE = "wake"
    VIEWING = "viewing"
    LYING_IN_STATE = "lying_in_state"
    REPOSING = "reposing"
    REMOVAL = "removal"
    PRAYER_SERVICE = "prayer_service"
    ROSARY = "rosary"
    MEMORIAL_GATHERING = "memorial_gathering"
    SERVICE = "service"
    FUNERAL = "funeral"
    FUNERAL_SERVICE = "funeral_service"
    MEMORIAL_SERVICE = "memorial_service"
    FUNERAL_MASS = "funeral_mass"
    MASS_OF_CHRISTIAN_BURIAL = "mass_of_christian_burial"
    MEMORIAL_MASS = "memorial_mass"
    REQUIEM_MASS = "requiem_mass"
    LITURGY = "liturgy"
    CELEBRATION_OF_LIFE = "celebration_of_life"
    BURIAL = "burial"
    GRAVESIDE_SERVICE = "graveside_service"
    INTERMENT = "interment"
    COMMITTAL = "committal"
    INURNMENT = "inturnment"
    ENTOMBMENT = "entombment"
    SHIVA = "shiva"


# endregion


# region Models
class AdditionalFields(BaseModel):
    salutation: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    maiden_name: Optional[str] = None
    suffix: Optional[str] = None
    gender_pronouns: Optional[Gender] = None
    date_of_birth: Optional[str] = None
    date_of_death: Optional[str] = None
    city_of_death: Optional[str] = None
    region_of_death: Optional[str] = None
    country_of_death: Optional[str] = None
    place_of_birth: Optional[str] = None


# endregion

# region Constants
LENGTH_DEFINITIONS = {
    "short": {"target": 45, "min": 40, "max": 50},
    "medium": {"target": 300, "min": 280, "max": 320},
    "long": {"target": 750, "min": 700, "max": 5000},
}

GENDER_PRONOUNS = {
    "he_him": {"subjective": "he", "objective": "him", "possessive": "his"},
    "she_her": {"subjective": "she", "objective": "her", "possessive": "her"},
    "they_them": {
        "subjective": "they",
        "objective": "them",
        "possessive": "their",
    },
    "other": {"subjective": "they", "objective": "them", "possessive": "their"},
}

SYSTEM_GUIDELINES = (
    "You are an empathetic yet professional obituary assistant. Your role is "
    "to act like a compassionate funeral home director combined with a skilled "
    "newspaper obituary writer who helps the user create a publication-ready "
    "obituary.\n\n"
    "**Key Guidelines:**\n"
    "- **Accurate Representation**: Use only explicitly provided information. "
    "Avoid inferences, assumptions, or speculative phrases about traits, "
    "relationships, events, or achievements.\n"
    "- **Avoid Assumptions**: Mention relationships only if explicitly stated. "
    "Use neutral terms like 'those who knew them' when relationships are "
    "ambiguous.\n"
    "ambiguous.\n"
    "- **Exclude Missing Information**: Do not include placeholders or vague "
    "statements. Write naturally and focus solely on the provided input.\n"
    "- **Adapt to Length**: If input is sparse, prioritize accuracy and brevity "
    "over length. Avoid filler or speculative content. Add a reflective closing "
    "sentence if needed (e.g., 'May their memory bring comfort to those who knew "
    "them').\n"
    "- **Expand Thoughtfully**: Provide context directly tied to the input "
    "without introducing unsupported anecdotes or qualities.\n"
    "- **Format Names**: Use [Salutation] [First Name] [Middle Name] [Nickname] "
    "[Last Name], [Suffix]. Include nicknames in quotes and omit missing parts "
    "naturally without placeholders.\n"
    "- **Language and Flow**: Use varied and engaging language to create a smooth, "
    "respectful narrative. Avoid repetitive or overly generic terms unless "
    "explicitly supported by the input.\n"
    "- **Service Details**: Clearly describe services (e.g., type, venue, date). "
    "Use past tense for completed events and future tense for upcoming ones, "
    "aligned with the current date. Always include full service information, "
    "including address, date, and time if provided in the input and space allows. "
    "If the service was in the past, only include date and location, not time. If "
    "service information is not provided, do not include service details in the "
    "obituary. prioritize service details over filler content.\n"
    "- **Historical Accuracy**: Ensure references, ages, and dates align with the "
    "decedent's birthdate and age. Correct inconsistencies in the input.\n"
    "- **Family Details**: Mention family members only if explicitly stated. Clearly "
    "define relationships without assumptions.\n"
    "- **Pronouns**: Use the pronouns provided in the input. If none are given, use "
    "neutral terms like 'they/them.' Ensure familial terms align with the decedent’s "
    "identity and relationships.\n"
    "- **Strict Focus on Input Data**: Base the obituary solely on the input data. "
    "Avoid external knowledge, assumptions, or generalizations.\n"
    "- **Survival or Predeceased Status**: Avoid phrases like 'is survived by' or "
    "'was predeceased by' unless explicitly stated. Use neutral phrasing if "
    "unclear.\n"
    "unclear.\n"
    "- **THE MOST IMPORTANT RULE**: DO NOT USE PLACEHOLDER PHRASES TO FILL SPACE "
    "IN ORDER TO REACH THE TARGET LENGTH.\n"
    "- **Prohibited Language:**\n"
    "THESE PHRASES AND SIMILAR PHRASES ARE NEVER ALLOWED UNLESS EXPLICITLY PROVIDED "
    "IN THE INPUT:\n"
    "'though not detailed here,' 'Though details of his life are not provided here,' "
    "'details are not provided.' Exclude areas without input and avoid unsupported "
    "emotional assumptions.\n"
    "- ****Reminder****: Do not include language that calls out missing "
    "information or use placeholder phrases."
)

SYSTEM_GUIDELINES_SCRATCHPAD = (
    "--- Instructions to handle unstructured notes ---\n"
    "You will take messy, unstructured notes about the deceased and organize them "
    "into a polished, respectful obituary. Your role is to identify meaningful "
    "details, address inconsistencies, and create a heartfelt narrative that honors "
    "their life. Treat ambiguous or incomplete data with care, prioritizing clarity "
    "and respect.\n\n"
    "**Key Guidelines for Unstructured Notes:**\n"
    "- **Address Formatting Issues**: Transform lists, fragmented sentences, or "
    "inconsistent formatting into a cohesive narrative.\n"
    "  - Example: Convert 'Hobbies: fishing, gardening' into 'John Doe enjoyed "
    "fishing and gardening, which brought him great joy.'\n"
    "- **Fill Gaps Thoughtfully**: Infer logical connections or structure where "
    "possible without making assumptions about specific details. Use neutral phrasing "
    "for unclear relationships (e.g., 'loved ones' or 'close family').\n"
    "- **Highlight Key Details**: Emphasize major achievements, relationships, and "
    "passions to create a vivid, respectful picture of their life.\n"
    "- **Handle Ambiguity with Care**: For unclear or contradictory notes, choose the "
    "most respectful interpretation or emphasize universal sentiments (e.g., 'They "
    "brought joy to all who knew them').\n"
    "- **Ensure Logical Flow**: Organize details into a clear sequence, transitioning "
    "smoothly between personal, professional, and family aspects.\n"
    "- **Adapt Tone and Style**: Match the obituary’s purpose and style (e.g., "
    "celebratory, professional) while maintaining warmth and sensitivity."
)

SYSTEM_GUIDELINES_STRUCTURED_DATA = (
    "--- Instructions to handle structured data ---\n"
    "Your role is to transform structured data into a polished, respectful, and "
    "engaging obituary. Focus on integrating the provided details into a cohesive "
    "narrative while ensuring clarity, accuracy, and adherence to the specified style."
    "\n\n"
    "**Key Guidelines for Structured Data:**\n"
    "- **Avoid Factual Overload**: Prevent overly factual or list-like language. "
    "Combine individual data points into smooth, natural sentences.\n"
    "- **Exclude Missing Information**: Do not reference missing fields or use "
    "placeholders. Write naturally based only on the provided details.\n"
    "- **Verify Consistency**: Ensure historical references, ages, and dates align "
    "accurately with the input data. Resolve inconsistencies respectfully.\n"
    "- **Focus on Relationships**: Mention family members only if explicitly stated. "
    "Use neutral terms like 'they/them' when pronouns are not provided.\n"
    "- **Format Service Details Clearly**: Clearly describe services (e.g., type, "
    "venue, date). Use past tense for completed events and future tense for "
    "upcoming ones, aligned with the current date.\n"
    "- **Adapt to Length**: Adjust narrative length based on the data provided. For "
    "sparse data, prioritize brevity and accuracy. Avoid adding filler or "
    "speculative content.\n"
    "- **Create a Narrative Flow**: Organize structured details into personal, "
    "professional, and family sections. Use transitions to connect these aspects "
    "seamlessly and tell a compelling story.\n"
    "- **Respect Tone and Style**: Match the specified tone (e.g., celebratory, "
    "traditional) while maintaining professionalism and warmth.\n"
    "- **Polish Language**: Use proper grammar, varied sentence structures, and "
    "engaging language to ensure the obituary is suitable for publication."
)

SYSTEM_GUIDELINES_PREWRITTEN_OBITUARY = (
    "--- Instructions to handle refining pre-written obituary ---\n"
    "Refine and improve the following pre-written obituary based only on the exact "
    "details provided. Your goal is to create a respectful, coherent, and "
    "publication-ready obituary while strictly adhering to the specified style and "
    "length.\n\n"
    "**Key Guidelines for Refinement:**\n"
    "- **Preserve the Original Intent**: Retain the core message and sentiments of "
    "the pre-written obituary while enhancing readability and flow.\n"
    "- **Align with Structured Data**: Cross-check the content with the provided "
    "structured details to ensure accuracy and consistency. Resolve conflicts by "
    "prioritizing the structured data.\n"
    "- **Enhance Clarity and Flow**: Improve sentence structure, transitions, and "
    "overall readability to create a smooth, engaging narrative.\n"
    "- **Respect Style and Length**: Adhere to the specified style (e.g., celebratory, "
    "professional) and target length. Make thoughtful edits to match the desired "
    "tone and format.\n"
    "- **Avoid Speculative Content**: Do not introduce new details, inferred traits, "
    "or assumptions. Focus solely on refining what is explicitly provided.\n"
    "- **Polish Language and Grammar**: Ensure proper grammar, varied sentence "
    "structure, and engaging language to make the obituary suitable for publication."
)

STYLE_GUIDELINES = {
    ObituaryStyle.POETIC: (
        "Crafted with a flowing, emotional, and artistic tone, this style uses "
        "vivid imagery and metaphors to paint a picture of the person’s life. "
        "The language should evoke deep emotions and present the individual's "
        "story in a heartfelt way, capturing the essence of their spirit and "
        "journey. Aim for soft, lyrical phrasing and avoid overly factual "
        "language to maintain a warm and evocative mood. This style should feel "
        "like a tribute written by a close friend or family member."
    ),
    ObituaryStyle.CELEBRATORY: (
        "An uplifting tone that focuses on the joyful moments, positive impact, "
        "and achievements of the individual’s life. Use vibrant language that "
        "celebrates the legacy and cherished memories they leave behind. Avoid "
        "somber language; instead, focus on highlighting happy memories and proud "
        "milestones. This style should feel like a joyful remembrance written "
        "for family and friends who want to remember their loved one in a positive "
        "light."
    ),
    ObituaryStyle.PROFESSIONAL: (
        "A formal and concise tone that highlights the individual’s accomplishments, "
        "life events, and milestones in a structured and factual way. Use clear, "
        "straightforward language that is respectful and polished. This style is "
        "ideal for those who wish for a reserved tribute, focused on accuracy and "
        "free from embellishment. Avoid flowery or overly emotional language; keep "
        "sentences direct, with a professional tone appropriate for publication."
    ),
    ObituaryStyle.RELIGIOUS: (
        "Infused with a spiritual tone, this style incorporates religious themes, "
        "focusing on the individual’s faith, devotion, and connection to their "
        "religious beliefs. The obituary should offer comfort and a sense of peace, "
        "emphasizing that they are at rest in the afterlife or with a higher power. "
        "Include references to religious beliefs or practices, using gentle language "
        "that provides spiritual closure. This style should bring comfort to family "
        "and friends, reflecting their loved one’s faith journey."
    ),
    ObituaryStyle.TRADITIONAL: (
        "A respectful and conventional tone that adheres to the standard obituary "
        "format, covering all key aspects of the individual's life in a balanced "
        "way. Use clear, dignified language that reflects respect and formality. "
        "Focus on life milestones, family connections, and noteworthy achievements. "
        "This style should provide a well-rounded view of the person’s life, giving "
        "a sense of closure for readers. It is appropriate for both print and online "
        "publication, as well as traditional audiences seeking a timeless tribute."
    ),
}

SECTION_PRIORITY_GUIDELINES = (
    "--- Instructions for handling obituary sections ---\n"
    "Organize obituary sections by prioritizing essential information. Condense "
    "or omit lower-priority details to fit the target word count. Each section is "
    "assigned a priority number; lower numbers indicate higher importance. Always "
    "fully include high-priority sections. Avoid adding filler content that could "
    "compromise higher-priority details. Ensure the obituary remains polished, "
    "respectful, and concise while preserving tone and intent.\n\n"
    "**Key Guidelines for Handling Sections (by Priority):**\n"
    "1. **Announcement of Death**: Include name, date, and place of death. Mention "
    "   the cause only if relevant and space allows. This section is never omitted.\n"
    "2. **Family Information**: List immediate family (e.g., spouse, children). Use "
    "   general phrases for extended family (e.g., 'numerous grandchildren').\n"
    "3. **Service Details**: Describe services (type, venue, date). Use past tense "
    "   for completed events and future tense for upcoming ones. Include full info "
    "   (address, date, time) if provided and space allows. Omit if no service info "
    "   is given.\n"
    "4. **Biographical Information**: Focus on milestones (birth, education, job). "
    "   Omit minor details to save space for more significant content.\n"
    "5. **Personal Legacy**: Highlight major achievements and contributions. Retain "
    "   only impactful details when condensing for limited space.\n"
    "6. **Hobbies and Interests**: Mention defining hobbies only. Skip generic or "
    "   minor interests in shorter formats to prioritize essential sections.\n"
    "7. **Special Requests**: Condense donation requests to one sentence. Omit this "
    "   section entirely if space is critical or details are unavailable.\n"
    "8. **Closing Message**: Add a note or quote if space allows. Omit this section "
    "   first in limited-space scenarios to preserve higher-priority sections.\n\n"
    "Use priority numbers to guide edits: retain high-priority sections fully and "
    "condense or omit lower-priority sections as needed to meet word limits. Avoid "
    "filler text that detracts from essential details."
)

LENGTH_GUIDELINES: Dict[ObituaryLength, str] = {
    ObituaryLength.SHORT: (
        "A very brief obituary designed for print death notices or limited-space "
        "announcements. Prioritizes essential details: name, date of death, location, "
        "and immediate family. Strictly adheres to the target word count, ensuring "
        "brevity while including style-specific tone. Use a style-specific phrasing "
        "that captures the tone and length of examples such as 'entered eternal rest' "
        "for religious or 'a guiding star' for poetic, but encourage varied phrasing "
        "where possible. Prioritize brevity over elaboration.\n"
        f"Target length is **{LENGTH_DEFINITIONS['short']['target']} words**, "
        f"between **{LENGTH_DEFINITIONS['short']['min']} and "
        f"{LENGTH_DEFINITIONS['short']['max']} words**."
    ),
    ObituaryLength.MEDIUM: (
        "A moderately detailed obituary intended for full print obituaries, balancing "
        "cost constraints with meaningful content. Includes major life events, key "
        "achievements, and close family connections. Focuses on summarizing impactful "
        "events while maintaining the requested tone and style. Adhere to the target "
        "word count by prioritizing the most relevant details based on the chosen "
        "style:\n"
        "- **Traditional**: Focus on life milestones, family connections, and major "
        "achievements. Summarize hobbies or secondary relationships briefly if "
        "needed.\n"
        "- **Poetic**: Highlight emotional resonance and imagery to paint a vivid "
        "picture of the decedent’s life, ensuring key milestones are woven into a "
        "lyrical narrative.\n"
        "- **Celebratory**: Emphasize joyful memories and impactful achievements, "
        "using concise language to avoid excessive elaboration.\n"
        "- **Professional**: Prioritize career accomplishments and contributions to "
        "their field. Personal elements (e.g., family, hobbies) should support the "
        "narrative without overshadowing professional achievements.\n"
        "- **Religious**: Emphasize faith, spiritual reflections, and family "
        "relationships while maintaining succinctness.\n"
        "If insufficient information is provided, "
        "naturally adjust to a shorter format without compromising accuracy or "
        "sincerity. Avoid artificial lengthening strategies. If the word count "
        "exceeds the target, condense less critical anecdotes, hobbies, or secondary "
        "details, ensuring major themes remain intact.\nDO NOT ADD ANYTHING THAT WAS "
        "NOT PROVIDED.\nDO NOT INFER ANYTHING.\nThe final obituary should be an "
        "accurate reflection of the information provided. The final obituary can be "
        "significantly shorter than the target word count if the information provided "
        "is limited.\n"
        f"Target length is **{LENGTH_DEFINITIONS['medium']['target']} words**, "
        f"between **{LENGTH_DEFINITIONS['medium']['min']} and "
        f"{LENGTH_DEFINITIONS['medium']['max']} words**."
    ),
    ObituaryLength.LONG: (
        "A comprehensive obituary ideal for online publication, where longer tributes "
        "are encouraged. Covers all aspects of the individual's life in depth, "
        "including detailed descriptions of achievements, relationships, anecdotes, "
        "and legacy. Encourage rich storytelling to expand on provided details, using "
        "transitions to connect milestones meaningfully. Use style-specific tone to "
        "enhance emotional resonance, adding context and significance to events. For "
        "example, highlight hobbies with vivid descriptions or discuss family "
        "relationships in greater depth. If insufficient information is provided, "
        "naturally adjust to a shorter format without compromising accuracy or "
        "sincerity. Avoid artificial lengthening strategies. If the word count "
        "exceeds the target, condense less critical anecdotes, hobbies, or secondary "
        "details, ensuring major themes remain intact.\nDO NOT ADD ANYTHING THAT WAS "
        "NOT PROVIDED.\nDO NOT INFER ANYTHING.\nThe final obituary should be an "
        "accurate reflection of the information provided. The final obituary can be "
        "significantly shorter than the target word count if the information provided "
        "is limited.\n"
        f"Target length is **{LENGTH_DEFINITIONS['long']['target']} words**, "
        f"between **{LENGTH_DEFINITIONS['long']['min']} and "
        f"{LENGTH_DEFINITIONS['long']['max']} words**."
    ),
}

STOP_PHRASE = "[Final Output Begins Here]"
# endregion


# region Prompt Builders
def build_user_prompt_for_obit_from_scratchpad_notes(data):
    additional_fields_str = prepare_additional_fields(data.additional_fields)
    additional_fields_section = (
        (
            "--- Additional Details ---\n"
            "(Overwrite conflicting values from unstructured notes "
            "with these details):\n"
            f"{additional_fields_str}\n\n"
        )
        if additional_fields_str
        else ""
    )

    # Gender and pronouns information
    pronouns_section = (
        build_pronouns_section(data.additional_fields.gender_pronouns)
        if data.additional_fields
        else ""
    )

    prompt = (
        "--- Instructions (Reference Only - Do Not Include in Output) ---\n"
        "--- Unstructured Notes ---\n"
        f"{data.unstructured_notes}\n\n"
        f"{additional_fields_section}"
        f"{pronouns_section}"
        f"{STOP_PHRASE}\n"
    )

    return prompt


def build_user_prompt_for_obit_from_prewritten_obituary(data):
    additional_fields_str = prepare_additional_fields(data.additional_fields)
    additional_fields_section = (
        (
            "--- Additional Details ---\n"
            "(Overwrite any conflicting values from the pre-written "
            "obituary with these values):\n"
            f"{additional_fields_str}\n\n"
        )
        if additional_fields_str
        else ""
    )

    # Gender and pronouns information
    pronouns_section = (
        build_pronouns_section(data.additional_fields.gender_pronouns)
        if data.additional_fields
        else ""
    )

    prompt = (
        "--- Instructions (Reference Only - Do Not Include in Output) ---\n"
        "--- Original Obituary ---\n"
        f"{data.prewritten_obituary}\n\n"
        f"{additional_fields_section}"
        f"{pronouns_section}"
        f"{STOP_PHRASE}\n"
    )

    return prompt


def build_user_prompt_for_obit_from_structured_data(data):
    """
    Builds a prompt for generating an obituary based on the provided structured data.
    """

    # Configurations for sections
    decedent_fields = [
        ("First Name", "first_name"),
        ("Middle Name", "middle_name"),
        ("Last Name", "last_name"),
        ("Nickname", "nickname"),
        ("Salutation", "salutation"),
        ("Suffix", "suffix"),
        ("Maiden Name", "maiden_name"),
        ("Age", "age"),
    ]

    death_fields = [
        ("Date of Death", "date_of_death"),
        ("City of Death", "city_of_death"),
        ("Region of Death", "region_of_death"),
        ("Country of Death", "country_of_death"),
    ]

    birth_fields = [
        ("Date of Birth", "date_of_birth"),
        ("City of Birth", "city_of_birth"),
        ("Region of Birth", "region_of_birth"),
        ("Country of Birth", "country_of_birth"),
    ]

    additional_fields = [
        ("Education", "education"),
        ("Career", "career"),
        ("Surviving Family", "surviving_family"),
        ("Predeceased Family", "predeceased_family"),
        ("Hobbies", "hobbies"),
        ("Military Service", "military_service"),
        ("Places of Worship", "places_of_worship"),
        ("Other Information", "other_information"),
    ]

    service_fields = [
        ("Service Date", "service_date"),
        ("Start Time", "service_start_time"),
        ("End Time", "service_end_time"),
        ("Venue Name", "venue_name"),
        ("Venue Address", "venue_address"),
        ("Venue City", "venue_city"),
        ("Venue Region", "venue_region"),
        ("Venue Postal Code", "venue_postal_code"),
        ("Additional Notes", "service_notes"),
    ]

    # Build sections
    decedent_section = prepare_section("Decedent Information", decedent_fields, data)
    death_section = prepare_section("Death Information", death_fields, data)
    birth_section = prepare_section("Birth Information", birth_fields, data)
    additional_section = prepare_section(
        "Additional Information", additional_fields, data
    )

    # Process service information
    service_information = []
    if data.services:
        for service in data.services:
            service_details = []
            if service.service_type:
                formatted_type = service.service_type.value.replace("_", " ")
                formatted_type = formatted_type.title()
                service_details.append(f"Service Type: {formatted_type}")
            add_fields_from_config(service_fields, service, service_details)
            service_information.append("\n".join(service_details))

    service_section = build_section(
        "Service Information",
        "\n\n".join(service_information) if service_information else "",
    )

    # Gender and pronouns information
    pronouns_section = build_pronouns_section(data.gender_pronouns)

    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Final prompt assembly
    prompt = (
        "--- Instructions (Reference Only - Do Not Include in Output) ---\n"
        f"Current Date: {current_date}\n\n"
        + decedent_section
        + pronouns_section
        + death_section
        + birth_section
        + additional_section
        + service_section
        + STOP_PHRASE
    )

    return prompt


def build_system_prompt_for_obit_request(data, input_type_guidelines):
    """
    Builds a prompt for generating an obituary based on the provided structured data.
    """

    prompt = {
        f"{SYSTEM_GUIDELINES}\n"
        f"{input_type_guidelines}\n"
        f"{SECTION_PRIORITY_GUIDELINES}\n"
        f"--- Obituary tone and style ---\n{data.obituary_style.value} - "
        f"{STYLE_GUIDELINES.get(data.obituary_style)}\n\n"
        f"--- Obituary length ---\n{data.obituary_length.value} - "
        f"{LENGTH_GUIDELINES.get(data.obituary_length)}\n\n"
    }

    return prompt


# endregion


# region Helper Functions
def get_pronouns(gender: Gender) -> Dict[str, str]:
    """
    Returns a dictionary of pronouns based on the input gender.
    """
    return GENDER_PRONOUNS.get(
        gender.value, GENDER_PRONOUNS[Gender.THEY_THEM.value]
    )


def get_target_tokens(length: str) -> int:
    """
    Get the target token count based on the requested length using LENGTH_DEFINITIONS.
    """
    medium_target = LENGTH_DEFINITIONS["medium"]["target"]
    return LENGTH_DEFINITIONS.get(length, {}).get("target", medium_target)


def calculate_data_sufficiency_ratio(
    data_tokens: int, target_tokens: int
) -> float:
    """Calculate the data sufficiency ratio."""
    return data_tokens / target_tokens


def get_base_value(style: ObituaryStyle, parameter: str) -> float:
    """Get the base value for a specific parameter based on the style."""
    base_values = {
        "temperature": {
            ObituaryStyle.CELEBRATORY: 0.5,
            ObituaryStyle.POETIC: 0.7,
            ObituaryStyle.PROFESSIONAL: 0.1,
            ObituaryStyle.RELIGIOUS: 0.4,
            ObituaryStyle.TRADITIONAL: 0.3,
        },
        "top_p": {
            ObituaryStyle.CELEBRATORY: 0.9,
            ObituaryStyle.POETIC: 0.9,
            ObituaryStyle.PROFESSIONAL: 0.8,
            ObituaryStyle.RELIGIOUS: 0.85,
            ObituaryStyle.TRADITIONAL: 0.8,
        },
        "frequency_penalty": {
            ObituaryStyle.CELEBRATORY: 0.3,
            ObituaryStyle.POETIC: 0.3,
            ObituaryStyle.PROFESSIONAL: 0.2,
            ObituaryStyle.RELIGIOUS: 0.25,
            ObituaryStyle.TRADITIONAL: 0.2,
        },
        "presence_penalty": {
            ObituaryStyle.CELEBRATORY: 0.4,
            ObituaryStyle.POETIC: 0.4,
            ObituaryStyle.PROFESSIONAL: 0.2,
            ObituaryStyle.RELIGIOUS: 0.3,
            ObituaryStyle.TRADITIONAL: 0.2,
        },
    }
    return base_values.get(parameter, {}).get(style, 0.3)  # Default is 0.3


def adjust_value(
    base_value: float, 
    data_sufficiency_ratio: float, 
    parameter: str, 
    dependencies: dict
) -> float:
    """
    Adjust the base value based on the data sufficiency ratio and dependencies.
    """
    dependent_temperature = dependencies.get("temperature", base_value)
    dependent_top_p = dependencies.get("top_p", base_value)

    if parameter == "temperature":
        if data_sufficiency_ratio < 0.5:  # Sparse data
            return max(base_value - 0.3, 0.1)  # Reduce temperature further
        elif data_sufficiency_ratio > 1.5:  # Rich data
            return min(base_value + 0.1, 0.7)
    elif parameter == "top_p":
        if (
            dependent_temperature > 0.7
        ):  # High temperature should balance with low top_p
            return max(base_value - 0.1, 0.7)
        if data_sufficiency_ratio < 0.5:  # Sparse data
            return max(base_value - 0.2, 0.6)  # Reduce top_p for tighter control
        elif data_sufficiency_ratio > 1.5:  # Rich data
            return min(base_value + 0.1, 0.95)
    elif parameter == "frequency_penalty":
        if dependent_top_p < 0.8:  # Low top_p demands stricter penalties
            return min(base_value + 0.1, 1.0)
        if data_sufficiency_ratio < 0.5:  # Sparse data
            return min(base_value + 0.2, 1.0)
        elif data_sufficiency_ratio > 1.5:  # Rich data
            return max(base_value - 0.1, 0.0)
    elif parameter == "presence_penalty":
        if dependent_top_p < 0.8:  # Low top_p benefits from encouraging novelty
            return min(base_value + 0.1, 1.0)
        if data_sufficiency_ratio < 0.5:  # Sparse data
            return min(base_value + 0.2, 1.0)
        elif data_sufficiency_ratio > 1.5:  # Rich data
            return max(base_value - 0.1, 0.0)

    return base_value  # Adequate data, no adjustment


def adjust_obituary_length(length: str, data_sufficiency_ratio: float) -> str:
    """
    Adjust the requested obituary length based on the data sufficiency ratio.
    """
    if length == ObituaryLength.LONG:
        if data_sufficiency_ratio < 0.02:
            return ObituaryLength.SHORT
        elif data_sufficiency_ratio < 0.05:
            return ObituaryLength.MEDIUM
    elif length == ObituaryLength.MEDIUM:
        if data_sufficiency_ratio < 0.05:
            return ObituaryLength.SHORT
    return length


def calculate_parameter(
    style: ObituaryStyle,
    length: str,
    data_tokens: int,
    parameter: str,
    dependencies: dict = None,
) -> float:
    """
    Generalized calculation function for parameters.
    Allows for interdependencies between parameters.
    """
    target_tokens = get_target_tokens(length)
    data_sufficiency_ratio = calculate_data_sufficiency_ratio(
        data_tokens, target_tokens
    )
    base_value = get_base_value(style, parameter)

    return adjust_value(
        base_value, data_sufficiency_ratio, parameter, dependencies or {}
    )


def calculate_all_parameters(
    style: ObituaryStyle, length: str, data_tokens: int
) -> dict:
    """
    Calculate all key parameters (temperature, top_p, frequency_penalty, presence_penalty)
    with adjustments for sparse data and interdependencies.
    """
    # Calculate target tokens and sufficiency ratio
    target_tokens = get_target_tokens(length)
    data_sufficiency_ratio = calculate_data_sufficiency_ratio(
        data_tokens, target_tokens
    )

    # Adjust temperature based on sufficiency
    temperature = adjust_value(
        get_base_value(style, "temperature"), data_sufficiency_ratio, "temperature", {}
    )

    # Adjust top_p with dependency on temperature
    top_p = adjust_value(
        get_base_value(style, "top_p"),
        data_sufficiency_ratio,
        "top_p",
        dependencies={"temperature": temperature},
    )

    # Adjust frequency penalty with dependency on top_p
    frequency_penalty = adjust_value(
        get_base_value(style, "frequency_penalty"),
        data_sufficiency_ratio,
        "frequency_penalty",
        dependencies={"top_p": top_p},
    )

    # Adjust presence penalty with dependency on top_p
    presence_penalty = adjust_value(
        get_base_value(style, "presence_penalty"),
        data_sufficiency_ratio,
        "presence_penalty",
        dependencies={"top_p": top_p},
    )

    return {
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
    }


def build_pronouns_section(gender_pronouns):
    """
    Generates the pronouns section for a given set of gender pronouns.

    Args:
        gender_pronouns: The input gender pronouns (can be None).

    Returns:
        A string containing the formatted pronouns section,
        or an empty string if no pronouns are provided.
    """
    if gender_pronouns is not None:
        pronouns = get_pronouns(gender_pronouns)
        return build_section(
            "Gender and Pronouns Information",
            (
                f"Subjective Pronoun: {pronouns['subjective']}\n"
                f"Objective Pronoun: {pronouns['objective']}\n"
                f"Possessive Pronoun: {pronouns['possessive']}\n"
            ),
        )
    return ""


# endregion
