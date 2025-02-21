from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.core.database import get_db
from app.core.models import Obituary
from app.core.schemas import ObituaryCreate, ObituaryResponse
from app.services.obituary_service import generate_obituary_service
from app.core.scratchpad_notes_request import ScratchpadNotesRequest
from app.services.prompt_builder import (
    build_user_prompt_for_obit_from_scratchpad_notes,
    SYSTEM_GUIDELINES_SCRATCHPAD
)
import json
import openai
import app.core.config as config
import numpy as np
import logging
import time
import socket
import os

router = APIRouter()

# Initialize OpenAI client
client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

# Hosted Graphite Configuration
GRAPHITE_HOST = "carbon.hostedgraphite.com"
GRAPHITE_PORT = 2003
GRAPHITE_API_KEY = os.getenv("GRAPHITE_API_KEY")
GRAPHITE_PREFIX = f"{GRAPHITE_API_KEY}.api.scratchpad"

log = logging.getLogger(__name__)

class HostedGraphiteTCPClient:
    def __init__(self, host, port, api_key):
        self.host = host
        self.port = port
        self.api_key = api_key

    def send_metric(self, metric_name, value):
        try:
            message = f"{self.api_key}.{metric_name} {value}\n"
            with socket.create_connection((self.host, self.port)) as sock:
                sock.sendall(message.encode("utf-8"))
            print(f"✅ Sent: {message.strip()}")
        except Exception as e:
            print(f"❌ Failed to send metric: {e}")

graphite_client = HostedGraphiteTCPClient(GRAPHITE_HOST, GRAPHITE_PORT, GRAPHITE_API_KEY)

def get_embedding(text):
    """Generate OpenAI embeddings and return as a list of floats."""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding  # Returns list of floats

@router.post("/generate_embeddings/{obituary_id}")
def generate_embeddings_for_obituary(obituary_id: int, db: Session = Depends(get_db)):
    """Generate embeddings for a specific obituary and store them in the database."""
    obituary = db.query(Obituary).filter(Obituary.id == obituary_id).first()

    if not obituary:
        raise HTTPException(status_code=404, detail="Obituary not found.")

    embedding = get_embedding(obituary.generated_text)
    obituary.embedding = embedding
    db.commit()

    return {"message": f"Generated embedding for obituary ID {obituary_id}."}

@router.post("/generate_embeddings")
def generate_embeddings(db: Session = Depends(get_db)):
    """Retrieve obituaries without embeddings, generate them, and store in the database."""
    obituaries = db.query(Obituary).filter(Obituary.embedding.is_(None)).all()

    if not obituaries:
        return {"message": "No obituaries found that need embeddings."}

    updated_count = 0
    for obit in obituaries:
        embedding = get_embedding(obit.generated_text)
        obit.embedding = embedding
        db.commit()
        updated_count += 1

    return {"message": f"Updated embeddings for {updated_count} obituaries."}

@router.post("/generate_obituary", response_model=ObituaryResponse)
def generate_obituary_endpoint(obit_data: ObituaryCreate, db: Session = Depends(get_db)):
    return generate_obituary_service(obit_data.dict(), db)

@router.get("/obituaries", response_model=list[ObituaryResponse])
def get_obituaries(db: Session = Depends(get_db)):
    obituaries = db.query(Obituary).all()
 
    def ensure_list(value):
        """Ensures the value is always returned as a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        return []

    return [
        ObituaryResponse(
            id=obit.id,
            name=(json.loads(obit.input_data).get("name") if isinstance(obit.input_data, str) else obit.input_data.get("name")) or "Unknown",
            birth_year=(json.loads(obit.input_data).get("birth_year") if isinstance(obit.input_data, str) else obit.input_data.get("birth_year")) or 1900,
            death_year=(json.loads(obit.input_data).get("death_year") if isinstance(obit.input_data, str) else obit.input_data.get("death_year")) or 2000,
            career=(json.loads(obit.input_data).get("career") if isinstance(obit.input_data, str) else obit.input_data.get("career")) or "Unknown",
            achievements=ensure_list(json.loads(obit.input_data).get("achievements", [])) if isinstance(obit.input_data, str) else ensure_list(obit.input_data.get("achievements", [])),
            community_impact=ensure_list(json.loads(obit.input_data).get("community_impact", [])) if isinstance(obit.input_data, str) else ensure_list(obit.input_data.get("community_impact", [])),
            services=ensure_list(json.loads(obit.input_data).get("services", [])) if isinstance(obit.input_data, str) else ensure_list(obit.input_data.get("services", [])),
            gender_pronouns=(json.loads(obit.input_data).get("gender_pronouns") if isinstance(obit.input_data, str) else obit.input_data.get("gender_pronouns")) or None,
            generated_text=obit.generated_text or "No obituary available"
        )
        for obit in obituaries
    ]

@router.post("/scratchpad")
def generate_scratchpad_prompt(request: ScratchpadNotesRequest, db: Session = Depends(get_db)):
    """Generate an obituary from scratchpad notes, store in DB, and generate embeddings."""
    try:
        start_time = time.time()
        prompt = build_user_prompt_for_obit_from_scratchpad_notes(request)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_GUIDELINES_SCRATCHPAD},
                {"role": "user", "content": prompt}
            ]
        )

        generated_text = response.choices[0].message.content.strip()
        
        # Store in Database
        obituary = Obituary(
            input_data=json.dumps(request.dict()),
            generated_text=generated_text,
            openai_score=np.random.uniform(70, 100),
            teacher_score=np.random.uniform(60, 100),
            final_score=None  # Can be updated later
        )
        db.add(obituary)
        db.commit()
        db.refresh(obituary)

        # Generate and store embeddings
        embedding = get_embedding(generated_text)
        obituary.embedding = embedding
        db.commit()

        elapsed_time = time.time() - start_time
        graphite_client.send_metric("api.scratchpad.generated_by_code.response_time", elapsed_time * 1000)
        graphite_client.send_metric("api.scratchpad.generated_by_code.calls", 1)

        return {
            "prompt": prompt,
            "response": generated_text,
            "obituary_id": obituary.id
        }

    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        graphite_client.send_metric("api.scratchpad.errors", 1)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search_obituaries", response_model=list[ObituaryResponse])
def search_obituaries(request: dict, db: Session = Depends(get_db)):
    """Search for obituaries similar to the given query using pgvector."""
    try:
        query_text = request.get("query", "")
        query_embedding = get_embedding(query_text)  # List of floats

        # Convert to NumPy array, ensuring float32 format
        query_embedding_np = np.array(query_embedding, dtype=np.float32)

        # Construct SQL query correctly
        sql = """
        SELECT id, input_data, generated_text, openai_score, teacher_score, final_score, embedding
        FROM obituaries
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT 2;
        """

        # Execute query and retrieve results using `.mappings()` to return dictionaries
        result = db.execute(
            text(sql),
            {"embedding": f"[{', '.join(map(str, query_embedding_np.tolist()))}]"}  # Ensure proper vector formatting
        ).mappings().all()

        return [
            ObituaryResponse(
                id=row["id"],
                name=json.loads(row["input_data"]).get("name", "Unknown") if isinstance(row["input_data"], str) else row["input_data"].get("name", "Unknown"),
                birth_year=json.loads(row["input_data"]).get("birth_year", 1900) if isinstance(row["input_data"], str) else row["input_data"].get("birth_year", 1900),
                death_year=json.loads(row["input_data"]).get("death_year", 2000) if isinstance(row["input_data"], str) else row["input_data"].get("death_year", 2000),
                career=json.loads(row["input_data"]).get("career", "Unknown") if isinstance(row["input_data"], str) else row["input_data"].get("career", "Unknown"),
                achievements=json.loads(row["input_data"]).get("achievements", []) if isinstance(row["input_data"], str) else row["input_data"].get("achievements", []),
                community_impact=json.loads(row["input_data"]).get("community_impact", []) if isinstance(row["input_data"], str) else row["input_data"].get("community_impact", []),
                services=json.loads(row["input_data"]).get("services", []) if isinstance(row["input_data"], str) else row["input_data"].get("services", []),
                gender_pronouns=json.loads(row["input_data"]).get("gender_pronouns") if isinstance(row["input_data"], str) else row["input_data"].get("gender_pronouns"),
                generated_text=row["generated_text"] or "No obituary available"
            )
            for row in result
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in search: {str(e)}")

@router.post("/generate_sample_scratchpad_obit")
def generate_sample_scratchpad_obit(
    count: int = Query(1, ge=1, le=10, description="Number of sample obituaries to generate (1-10)"),
    db: Session = Depends(get_db)
):
    """
    Generates multiple sample scratchpad obituary inputs using GPT, processes them through
    the standard scratchpad obituary generation flow, generates embeddings, and stores in the database.
    
    The 'count' parameter controls how many obituaries to generate (max 10 at a time).
    """
    try:
        generated_results = []

        for _ in range(count):
            # Step 1: Generate a structured JSON input using GPT-4
            prompt = """
            Generate a fictional obituary input as a JSON object, with realistic variations in structure and style.
            The JSON should include:
            - "unstructured_notes": A natural, varied obituary note (casual, formal, poetic, bulleted, etc.), as a string.
            - "obituary_style": One of ["celebratory", "poetic", "professional", "religious", "traditional"].
            - "obituary_length": One of ["short", "medium", "long"].
            - "should_stream": false.
            - "additional_fields": A dictionary with details including:
              - "salutation": One of ["Mr.", "Ms.", "Dr.", "Rev."].  
              - "first_name": A realistic first name.
              - "middle_name": (Optional) A common middle name.
              - "last_name": A realistic last name.
              - "nickname": (Optional) A short form or alternate name.
              - "maiden_name": (Optional) A former surname if applicable.
              - "suffix": (Optional) One of ["Jr.", "III", "None"].
              - "date_of_death": A realistic date.
              - "city_of_death", "region_of_death", "country_of_death": Realistic location fields.
              - "date_of_birth", "place_of_birth": Realistic birth details.
            Return only the JSON object with no extra text.
            """

            gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an obituary data generator."},
                          {"role": "user", "content": prompt}]
            )

            sample_input = json.loads(gpt_response.choices[0].message.content.strip())

            # ✅ Fix: Ensure `unstructured_notes` is always a string
            if isinstance(sample_input.get("unstructured_notes"), dict):
                # GPT returned a nested dict; extract first key's value
                sample_input["unstructured_notes"] = next(iter(sample_input["unstructured_notes"].values()), "")

            if not isinstance(sample_input.get("unstructured_notes"), str):
                raise ValueError(f"Invalid format for unstructured_notes: {sample_input.get('unstructured_notes')}")

            # Step 2: Convert generated JSON into a ScratchpadNotesRequest object
            scratchpad_request = ScratchpadNotesRequest(**sample_input)

            # Step 3: Call the existing scratchpad endpoint to generate the obituary
            obituary_result = generate_scratchpad_prompt(scratchpad_request, db)

            # Step 4: Retrieve the newly created obituary from the DB
            obituary = db.query(Obituary).filter(Obituary.id == obituary_result["obituary_id"]).first()

            if not obituary:
                raise HTTPException(status_code=500, detail="Generated obituary not found in database.")

            # Step 5: Generate embeddings for the obituary text
            embedding = get_embedding(obituary.generated_text)
            obituary.embedding = embedding
            db.commit()

            # Append to results list
            generated_results.append({
                "generated_scratchpad_input": sample_input,
                "generated_obituary": obituary_result,
                "message": f"Obituary ID {obituary.id} saved with embeddings."
            })

        return {"generated_obituaries": generated_results}

    except Exception as e:
        log.error(f"Error generating sample scratchpad obituaries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
