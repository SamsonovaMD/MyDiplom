# diplom_back/app/schemas/__init__.py
from .user import UserBase, UserCreate, UserUpdate, UserSchema, UserInDB 
from .token import Token, TokenPayload
# Позже сюда добавятся схемы для Vacancy, Resume, Application