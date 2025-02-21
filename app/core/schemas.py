from pydantic import BaseModel
from typing import Optional, List
from app.services.prompt_builder import Gender  # Ensure Gender Enum is imported

class ServiceInfo(BaseModel):
    service_type: str
    date: Optional[str] = None
    location: Optional[str] = None

class ObituaryCreate(BaseModel):
    name: str
    birth_year: int
    death_year: int
    career: str
    achievements: Optional[List[str]] = []
    community_impact: Optional[List[str]] = []
    services: Optional[List[ServiceInfo]] = []  # ✅ Add services if needed
    gender_pronouns: Optional[Gender] = None  # ✅ Added this field

class ObituaryResponse(ObituaryCreate):
    id: int
    generated_text: str
