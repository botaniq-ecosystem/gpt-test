import openai
import app.core.config as config  # Import the config file
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models import Obituary
import numpy as np

# Initialize OpenAI client with API key from config
client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

def get_embedding(text):
    """Generate OpenAI embeddings for the given text using the new API format."""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def update_obituary_embeddings():
    """Retrieve obituaries without embeddings, generate them, and store in the database."""
    db: Session = next(get_db())
    obituaries = db.query(Obituary).filter(Obituary.embedding == None).all()  # Find obits without embeddings

    if not obituaries:
        print("No obituaries found that need embeddings.")
        return

    print(f"Found {len(obituaries)} obituaries to process.")

    for obit in obituaries:
        print(f"Generating embedding for: {obit.generated_text[:50]}...")
        embedding = get_embedding(obit.generated_text)  # Generate embedding for obituary text
        obit.embedding = embedding  # Store in database
        db.commit()
        print(f"Updated obituary ID {obit.id} with embeddings.")

if __name__ == "__main__":
    print("Starting obituary embedding update...")
    update_obituary_embeddings()
    print("Embedding update complete.")
