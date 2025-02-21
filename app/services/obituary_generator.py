import logging
from sqlalchemy.orm import Session
from app.core.models import Obituary
from app.core.schemas import ObituaryCreate, ObituaryResponse
from app.services.prompt_builder import build_user_prompt_for_obit_from_structured_data as generate_prompt
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_obituary(input_data: dict, db: Session) -> ObituaryResponse:
    """Generate an obituary using GPT and store it in the database."""

    # Convert input_data dictionary to Pydantic model
    obit_data = ObituaryCreate(**input_data)

    # Generate the obituary text using the prompt builder
    prompt = generate_prompt(obit_data)
    
    # ✅ Log the generated prompt before sending it to OpenAI
    logger.info(f"Generated Prompt: {prompt}")

    # Call OpenAI API to generate obituary text
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful obituary writer."},
            {"role": "user", "content": prompt},
        ]
    )

    # Extract generated text from OpenAI response
    generated_text = response.choices[0].message.content.strip()

    # ✅ Store full input_data as JSON in the database
    obituary = Obituary(
        input_data=input_data,
        generated_text=generated_text,
        openai_score=None,
        teacher_score=None,
        final_score=None
    )

    db.add(obituary)
    db.commit()
    db.refresh(obituary)

    # ✅ Extract fields from `input_data` to match `ObituaryResponse` schema
    return ObituaryResponse(
        id=obituary.id,
        name=input_data["name"],
        birth_year=input_data["birth_year"],
        death_year=input_data["death_year"],
        career=input_data["career"],
        achievements=input_data.get("achievements", []),
        community_impact=input_data.get("community_impact", []),
        services=input_data.get("services", []),
        gender_pronouns=input_data.get("gender_pronouns"),
        generated_text=generated_text
    )
