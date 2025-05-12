# diplom_back/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole # Импортируем Enum из модели

# Базовая схема с общими полями
class UserBase(BaseModel): # <--- ВОТ ОПРЕДЕЛЕНИЕ UserBase
    email: EmailStr = Field(..., example="user@example.com")
    full_name: Optional[str] = Field(None, example="Иван Иванов")
    role: UserRole = Field(default=UserRole.CANDIDATE, example=UserRole.CANDIDATE.value)
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Схема для создания пользователя (наследуется от UserBase, добавляет пароль)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="SecurePassword123")

# Схема для обновления пользователя (все поля опциональны)
class UserUpdate(BaseModel): # UserUpdate не обязательно наследовать от UserBase, если все поля опциональны
    email: Optional[EmailStr] = Field(None, example="new_user@example.com")
    full_name: Optional[str] = Field(None, example="Петр Петров")
    password: Optional[str] = Field(None, min_length=8, example="NewSecurePassword123")
    role: Optional[UserRole] = Field(None, example=UserRole.EMPLOYER.value)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Базовая схема для пользователя, хранящегося в БД (включает id и другие поля из БД)
class UserInDBBase(UserBase): # UserInDBBase наследуется от UserBase
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # orm_mode = True # Позволяет Pydantic работать с объектами SQLAlchemy
        # Если используете Pydantic v2, orm_mode заменен на from_attributes
        from_attributes = True 

# Схема для возврата пользователя из API (наследуется от UserInDBBase, НЕ включает пароль)
class UserSchema(UserInDBBase):
    pass 

# Схема для внутреннего использования, включая хешированный пароль (не для API ответа)
class UserInDB(UserInDBBase):
    hashed_password: str