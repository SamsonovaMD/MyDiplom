# diplom_back/app/api/v1/api.py
from fastapi import APIRouter

api_router = APIRouter()

# Сюда будем импортировать и подключать другие роутеры (например, для вакансий, пользователей)
# from .endpoints import login, vacancies # Пример
# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])