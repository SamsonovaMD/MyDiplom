# diplom_back/app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import resumes, users, login 

api_router = APIRouter()

# Подключаем роутер для резюме
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"]) 
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Сюда же можно будет добавить роутеры для login, vacancies и т.д.
# from .endpoints import login # Пример
# api_router.include_router(login.router, tags=["login"])