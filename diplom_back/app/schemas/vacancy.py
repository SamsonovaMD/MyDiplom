# diplom_back/app/schemas/vacancy.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any, Annotated # Import Annotated
from datetime import datetime
import enum # Для Pydantic Enum

# Определяем Enums для Pydantic (валидация, документация API)
class WorkFormat(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    office = "office"

class EmploymentType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    internship = "internship"

# Словари для отображения (если решите использовать *_display поля)
WORK_FORMAT_DISPLAY_MAP = {
    WorkFormat.remote: "Удаленно",
    WorkFormat.hybrid: "Гибрид",
    WorkFormat.office: "В офисе",
}

EMPLOYMENT_TYPE_DISPLAY_MAP = {
    EmploymentType.full_time: "Полная занятость",
    EmploymentType.part_time: "Частичная занятость",
    EmploymentType.internship: "Стажировка",
}

# Базовая схема для вакансии
class VacancyBase(BaseModel):
    title: str = Field(..., example="Python Developer")
    description: Optional[str] = Field(None, example="Разработка веб-приложений на FastAPI.")
    experience_required: Optional[str] = Field(None, example="От 1 года до 3 лет")
    primary_skills: Optional[Dict[str, List[str]]] = Field(None, example={"required": ["Python", "SQL"], "preferred": ["FastAPI"]})
    nice_to_have_skills: Optional[List[str]] = Field(None, example=["Docker", "Git"])
    
    # Pydantic V2: Используем Annotated для constrained types like conint
    salary_from: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, # explicit default for Field when using Optional[Annotated[...]]
        example=100000,
        description="Зарплата от (в рублях)"
    )
    salary_to: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None,
        example=150000,
        description="Зарплата до (в рублях, если указана, должна быть >= 'от')"
    )
    
    work_format: Optional[WorkFormat] = Field(None, example=WorkFormat.remote, description="Формат работы")
    employment_type: Optional[EmploymentType] = Field(None, example=EmploymentType.full_time, description="Тип занятости")

    @model_validator(mode='after')
    def check_salary_consistency(self) -> 'VacancyBase':
        if self.salary_from is not None and self.salary_to is not None:
            if self.salary_to < self.salary_from:
                raise ValueError('\'Зарплата до\' не может быть меньше \'Зарплата от\'')
        
        if self.salary_to is not None and self.salary_from is None:
            raise ValueError('\'Зарплата от\' должна быть указана, если указана \'Зарплата до\'')
        return self

# Схема для создания вакансии (работодатель будет указывать эти данные)
class VacancyCreate(VacancyBase):
    salary_from: Annotated[int, Field(ge=0)] = Field(
        ..., # Makes it required
        example=120000,
        description="Зарплата от (в рублях, обязательно)"
    )
    
    work_format: WorkFormat = Field(..., example=WorkFormat.hybrid, description="Формат работы (обязательно)")
    employment_type: EmploymentType = Field(..., example=EmploymentType.full_time, description="Тип занятости (обязательно)")

# Схема для обновления вакансии (все поля опциональны)
class VacancyUpdate(VacancyBase):
    title: Optional[str] = Field(None, example="Senior Python Developer")

# Схема для представления вакансии из БД (включает id, employer_id и даты)
class VacancyInDBBase(VacancyBase):
    id: int
    employer_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Схема для возврата вакансии из API
class VacancySchema(VacancyInDBBase):
    salary_currency: Optional[str] = Field("RUB", description="Валюта зарплаты") # По умолчанию RUB

    work_format_display: Optional[str] = None
    employment_type_display: Optional[str] = None

    @model_validator(mode='after')
    def set_display_fields_and_currency(self) -> 'VacancySchema':
        if self.salary_from is None:
            self.salary_currency = None
        else:
            self.salary_currency = "RUB"

        if self.work_format:
            self.work_format_display = WORK_FORMAT_DISPLAY_MAP.get(self.work_format)
        else:
            self.work_format_display = None
        
        if self.employment_type:
            self.employment_type_display = EMPLOYMENT_TYPE_DISPLAY_MAP.get(self.employment_type)
        else:
            self.employment_type_display = None
            
        return self
