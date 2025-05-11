# diplom_back/app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import resumes # <--- УБЕДИТЕСЬ, ЧТО ЭТА СТРОКА ЕСТЬ И ПРАВИЛЬНАЯ

api_router = APIRouter()

# Подключаем роутер для резюме
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"]) # <--- УБЕДИТЕСЬ, ЧТО ЭТА СТРОКА ЕСТЬ

# Сюда же можно будет добавить роутеры для login, vacancies и т.д.
# from .endpoints import login # Пример
# api_router.include_router(login.router, tags=["login"])