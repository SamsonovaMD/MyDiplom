from fastapi import FastAPI
from app.core.config import settings  # Убедитесь, что этот импорт работает
from app.api.v1.api import api_router as api_router_v1 # И этот тоже

# Вот эта строка определяет ваш объект 'app'
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Подключаем роутеры
app.include_router(api_router_v1, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"]) # Это тестовый эндпоинт
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Если вы хотите запускать через python app/main.py (не обязательно при использовании uvicorn app.main:app)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)