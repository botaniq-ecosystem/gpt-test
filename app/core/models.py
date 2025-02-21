from sqlalchemy import Column, Integer, String, JSON, Float
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector  # ✅ Import Vector from pgvector

Base = declarative_base()

class Obituary(Base):
    __tablename__ = "obituaries"

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(JSON, nullable=False)
    generated_text = Column(String, nullable=False)
    openai_score = Column(Float, nullable=True)
    teacher_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    embedding = Column(Vector(1536), nullable=True)  # ✅ Use pgvector's Vector type
    obit_metadata = Column(JSON, nullable=True)  # ✅ Rename metadata to obit_metadata
