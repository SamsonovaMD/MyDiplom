# diplom_back/app/api/v1/endpoints/login.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Стандартная форма для логина
from sqlalchemy.orm import Session
from typing import Any, Optional
from datetime import timedelta

from app import crud, models, schemas # Импортируем все для удобства
from app.core.config import settings
from app.core import security # Наши функции для JWT и паролей
from app.api import deps # Для get_db

router = APIRouter()

# Вспомогательная функция аутентификации пользователя в CRUD (если еще не создали)
def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # Данные из формы (username=email, password)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username в форме - это email пользователя.
    """
    user = authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # Изменили с 400 на 401
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}, # Стандартный заголовок для 401
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email, expires_delta=access_token_expires # Используем email как subject
    )
    return {"access_token": access_token, "token_type": "bearer"}