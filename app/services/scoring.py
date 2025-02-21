from sqlalchemy.orm import Session
from app.core.models import Obituary

def evaluate_obituary(obituary_id: int, db: Session):
    obituary = db.query(Obituary).filter(Obituary.id == obituary_id).first()
    if not obituary:
        return {"error": "Obituary not found"}

    # Placeholder for obituary evaluation logic
    score = 85.0  # Example score (replace with real ML logic)
    obituary.final_score = score
    db.commit()

    return {"message": "Obituary evaluated", "score": score, "obituary_id": obituary_id}
