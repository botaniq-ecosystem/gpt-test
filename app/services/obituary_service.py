from sqlalchemy.orm import Session
from app.core.models import Obituary
from app.core.schemas import ObituaryCreate, ObituaryResponse
import openai
import json
import numpy as np
import app.core.config as config

# Initialize OpenAI client
client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

def generate_obituary_service(obit_data: dict, db: Session) -> ObituaryResponse:
    """Generates an obituary using OpenAI and stores it in the database."""

    # Construct a user prompt from the input data
    prompt = f"""
    Generate a well-structured obituary for {obit_data.get('name', 'an individual')}.
    Birth Year: {obit_data.get('birth_year', 'Unknown')}
    Death Year: {obit_data.get('death_year', 'Unknown')}
    Career: {obit_data.get('career', 'Not mentioned')}
    Achievements: {', '.join(obit_data.get('achievements', []))}
    Community Impact: {', '.join(obit_data.get('community_impact', []))}
    Services: {', '.join(obit_data.get('services', []))}
    """

    # Call OpenAI's API to generate the obituary text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an obituary writer."},
                  {"role": "user", "content": prompt}]
    )

    generated_text = response.choices[0].message.content.strip()

    # Store in database
    obituary = Obituary(
        input_data=json.dumps(obit_data),
        generated_text=generated_text,
        openai_score=np.random.uniform(70, 100),  # Placeholder for scoring logic
        teacher_score=None,
        final_score=None
    )
    db.add(obituary)
    db.commit()
    db.refresh(obituary)

    return ObituaryResponse(
        id=obituary.id,
        name=obit_data.get("name", "Unknown"),
        birth_year=obit_data.get("birth_year", 1900),
        death_year=obit_data.get("death_year", 2000),
        career=obit_data.get("career", "Unknown"),
        achievements=obit_data.get("achievements", []),
        community_impact=obit_data.get("community_impact", []),
        services=obit_data.get("services", []),
        gender_pronouns=obit_data.get("gender_pronouns"),
        generated_text=generated_text
    )
