from sqlalchemy.orm import Session
from app.core.models import Obituary

def generate_obituary_embedding(obituary_id: int, db: Session):
    obituary = db.query(Obituary).filter(Obituary.id == obituary_id).first()
    if not obituary:
        return {"error": "Obituary not found"}
    
    # Placeholder for embedding logic
    embedding = [0.1, 0.2, 0.3]  # Replace with real embedding
    obituary.embedding = embedding
    db.commit()
    
    return {"message": "Embedding generated successfully", "obituary_id": obituary_id}
