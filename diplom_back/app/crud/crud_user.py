# diplom_back/app/crud/crud_user.py
from sqlalchemy.orm import Session
from typing import Optional, List, Union, Dict, Any

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.security import verify_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    # Создаем словарь без оригинального пароля, но с хешированным
    db_user_data = user_in.model_dump(exclude={"password"}) 
    db_user_data["hashed_password"] = hashed_password
    
    db_user = User(**db_user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    *,
    db_user: User, # Объект пользователя из БД, который нужно обновить
    user_in: Union[UserUpdate, Dict[str, Any]] # Данные для обновления
) -> User:
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.model_dump(exclude_unset=True) # exclude_unset=True чтобы обновлять только переданные поля

    if "password" in update_data and update_data["password"]: # Если пароль передан и он не пустой
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"] # Удаляем оригинальный пароль из данных для обновления
        update_data["hashed_password"] = hashed_password # Добавляем хешированный

    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = db.query(User).get(user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Можно добавить функцию для аутентификации (проверки email и пароля)
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user