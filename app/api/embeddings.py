from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.embeddings import generate_obituary_embedding

router = APIRouter()

@router.post("/generate_embeddings")
def generate_embedding(obituary_id: int, db: Session = Depends(get_db)):
    return generate_obituary_embedding(obituary_id, db)
