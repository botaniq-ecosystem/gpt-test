from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models import Obituary

# Sample obituary data
new_obituary = {
    "name": "Jane Doe",
    "birth_year": 1950,
    "death_year": 2023,
    "career": "doctor",
}

generated_text = "Dr. Jane Doe was a dedicated physician who served her community for over 40 years."
openai_score = 88.0
teacher_score = 82.0
final_score = 85.0

# Insert obituary into database
def insert_obituary():
    db: Session = next(get_db())  # Get a database session
    obituary = Obituary(
        input_data=new_obituary,
        generated_text=generated_text,
        openai_score=openai_score,
        teacher_score=teacher_score,
        final_score=final_score
    )
    db.add(obituary)
    db.commit()
    db.refresh(obituary)
    print(f"Inserted obituary with ID: {obituary.id}")

if __name__ == "__main__":
    insert_obituary()
