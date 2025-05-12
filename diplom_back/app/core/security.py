# diplom_back/app/core/security.py
from datetime import datetime, timedelta, timezone # Добавим timezone
from typing import Optional, Any, Union

from jose import jwt, JWTError # Убедитесь, что python-jose[cryptography] установлен
from passlib.context import CryptContext

from app.core.config import settings # Наши настройки

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256" # Алгоритм для подписи JWT

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)} # 'sub' - это "subject", обычно ID пользователя или email
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)