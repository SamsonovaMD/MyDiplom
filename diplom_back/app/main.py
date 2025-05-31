# diplom_back/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- ИМПОРТИРУЙ ЭТО

from app.core.config import settings
from app.api.v1.api import api_router as api_router_v1

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Настройка CORS
# Список разрешенных origins (источников)
# В режиме разработки можно разрешить все (*) или конкретный порт фронтенда
# В продакшене ОБЯЗАТЕЛЬНО указывай конкретные домены твоего фронтенда
origins = [
    "http://localhost:5173", # Порт твоего Vite dev server
    "http://localhost:3000", # Если бы использовался Create React App
    "http://127.0.0.1:5173",
    "http://185.112.83.189:8080",
    "http://0.0.0.0:8080",
    "*",
    # "https://your-frontend-domain.com", # Для продакшена
]

# Если в режиме разработки хочешь разрешить все (НЕ ДЛЯ ПРОДА!)
# if settings.ENVIRONMENT == "development": # Пример, если у тебя есть такая настройка
#     origins.append("*") # Разрешить все источники (опасно для продакшена)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список разрешенных источников
    allow_credentials=True, # Разрешить куки и заголовки авторизации
    allow_methods=["*"],    # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],    # Разрешить все заголовки
)

# Подключаем роутеры версии 1
app.include_router(api_router_v1, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
