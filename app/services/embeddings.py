from sqlalchemy.orm import Session
from app.core.models import Obituary
import openai

def generate_obituary_embedding(obituary_id: int, db: Session):
    obituary = db.query(Obituary).filter(Obituary.id == obituary_id).first()
    if not obituary:
        return {"error": "Obituary not found"}
    
    # Call OpenAI API to generate embeddings
    response = openai.Embedding.create(
        input=obituary.text,  # Assuming obituary has a text field
        model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]
    
    obituary.embedding = embedding
    db.commit()
    
    return {"message": "Embedding generated successfully", "obituary_id": obituary_id}
