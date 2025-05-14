# diplom_back/app/schemas/application.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.application import ApplicationStatus # Импортируем Enum

class ApplicationBase(BaseModel):
    # candidate_id, vacancy_id, resume_id будут установлены в эндпоинте
    status: Optional[ApplicationStatus] = Field(default=ApplicationStatus.SUBMITTED)
    match_score: Optional[float] = Field(None, example=0.75)
    match_details: Optional[Dict[str, Any]] = Field(None, example={"matching_skills": ["Python"]})

class ApplicationCreate(BaseModel): # Отдельная схема для создания
    vacancy_id: int
    resume_id: int # Кандидат выбирает, какое из своих резюме прикрепить

# ApplicationUpdate может быть более сложной, если статусы меняются разными пользователями
class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    match_score: Optional[float] = None
    match_details: Optional[Dict[str, Any]] = None

class ApplicationInDBBase(ApplicationBase):
    id: int
    candidate_id: int
    vacancy_id: int
    resume_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApplicationSchema(ApplicationInDBBase):
    # Можно добавить детали кандидата, вакансии, резюме, если нужно
    # candidate: Optional[UserSchema] = None
    # vacancy: Optional[VacancySchema] = None
    # resume: Optional[ResumeSchema] = None
    pass