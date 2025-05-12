# diplom_back/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED)
def create_new_user( # Регистрация должна быть доступна без токена
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.create_user(db=db, user_in=user_in)
    return user

@router.get("/me", response_model=schemas.UserSchema)
def read_current_user(
    current_user: models.User = Depends(deps.get_current_active_user), # Защищено
) -> Any:
    """
    Получить текущего пользователя (по токену).
    """
    return current_user

@router.put("/me", response_model=schemas.UserSchema)
def update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate, # Данные для обновления
    current_user: models.User = Depends(deps.get_current_active_user), # Защищено
) -> Any:
    """
    Обновить данные текущего пользователя.
    """
    user = crud.update_user(db=db, db_user=current_user, user_in=user_in)
    return user

# Эндпоинты для администрирования (требуют прав суперпользователя)
@router.get("/", response_model=List[schemas.UserSchema])
def read_users_list( # Переименовал для ясности
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser) # Только для суперпользователя
) -> Any:
    """
    Получить список пользователей (только для суперпользователя).
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.UserSchema)
def read_user_by_id_admin( # Переименовал для ясности
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser) # Только для суперпользователя
) -> Any:
    """
    Получить пользователя по ID (только для суперпользователя).
    """
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserSchema)
def update_user_by_id_admin( # Переименовал для ясности
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser) # Только для суперпользователя
) -> Any:
    """
    Обновить пользователя по ID (только для суперпользователя).
    """
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.update_user(db=db, db_user=db_user, user_in=user_in)
    return user