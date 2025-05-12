# diplom_back/app/schemas/token.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str # Обычно "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None # "Subject" токена, обычно email пользователя