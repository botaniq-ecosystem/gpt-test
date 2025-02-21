from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.scoring import evaluate_obituary

router = APIRouter()

@router.post("/score_obituary")
def score_obituary(obituary_id: int, db: Session = Depends(get_db)):
    return evaluate_obituary(obituary_id, db)
