# app/schemas/matching.py (или где вы решите ее разместить)
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class MatchedCandidateSchema(BaseModel):
    id: int  # ID пользователя-кандидата
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    summary: Optional[str] = None  # Краткий опыт/о себе из резюме
    skills: List[str] = []        # Список навыков из резюме
    resume_id: int                # ID резюме, по которому был мэтчинг
    match_score: Optional[float] = None # Оценка мэтчинга от Application
    # match_details: Optional[dict] = None # Детали мэтчинга, если нужны на фронте

    class Config:
        orm_mode = True # Если вы будете создавать экземпляры схемы из ORM-моделей напрямую