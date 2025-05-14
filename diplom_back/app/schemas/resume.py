# diplom_back/app/schemas/resume.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ResumeBase(BaseModel):
    original_pdf_path: Optional[str] = Field(None, example="/path/to/resume.pdf")
    # parsed_data будет получен из парсера или передан напрямую
    parsed_data: Optional[Dict[str, Any]] = Field(None, example={"full_name": "Тест Тестович", "skills": ["Python"]})

class ResumeCreate(ResumeBase):
    # candidate_id будет добавлен из current_user
    # parsed_data может быть опциональным, если парсинг происходит на сервере после загрузки PDF
    pass

# ResumeUpdate не так часто нужен, так как резюме обычно заменяется целиком
# или обновляется через parsed_data. Если нужен, можно создать.

class ResumeInDBBase(ResumeBase):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResumeSchema(ResumeInDBBase):
    pass