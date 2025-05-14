# diplom_back/app/schemas/vacancy.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Базовая схема для вакансии
class VacancyBase(BaseModel):
    title: str = Field(..., example="Python Developer")
    description: Optional[str] = Field(None, example="Разработка веб-приложений на FastAPI.")
    experience_required: Optional[str] = Field(None, example="От 1 года до 3 лет")
    # JSONB поля могут быть словарями или списками, в зависимости от вашей структуры
    primary_skills: Optional[Dict[str, List[str]]] = Field(None, example={"required": ["Python", "SQL"], "preferred": ["FastAPI"]})
    nice_to_have_skills: Optional[List[str]] = Field(None, example=["Docker", "Git"])

# Схема для создания вакансии (работодатель будет указывать эти данные)
class VacancyCreate(VacancyBase):
    pass # employer_id будет добавляться из current_user в эндпоинте

# Схема для обновления вакансии (все поля опциональны)
class VacancyUpdate(VacancyBase):
    title: Optional[str] = Field(None, example="Senior Python Developer")
    # Можно сделать все поля опциональными, если это необходимо
    description: Optional[str] = None
    experience_required: Optional[str] = None
    primary_skills: Optional[Dict[str, List[str]]] = None
    nice_to_have_skills: Optional[List[str]] = None

# Схема для представления вакансии из БД (включает id, employer_id и даты)
class VacancyInDBBase(VacancyBase):
    id: int
    employer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Для Pydantic v2 (замените orm_mode=True если v1)

# Схема для возврата вакансии из API
class VacancySchema(VacancyInDBBase):
    # Можно добавить сюда информацию о работодателе, если нужно
    # employer: Optional[UserSchema] = None # Если хотите возвращать детали работодателя
    pass