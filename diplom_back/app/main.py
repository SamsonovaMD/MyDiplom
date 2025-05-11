# diplom_back/app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router as api_router_v1 # <--- Убедитесь, что это импортируется

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Подключаем роутеры версии 1
app.include_router(api_router_v1, prefix=settings.API_V1_STR) # <--- Убедитесь, что эта строка есть и API_V1_STR правильный (обычно "/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}