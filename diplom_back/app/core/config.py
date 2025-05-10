from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume Matching Service"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env" # Указываем, что нужно читать из .env
        env_file_encoding = 'utf-8'

@lru_cache() # Кэшируем результат, чтобы .env читался один раз
def get_settings() -> Settings:
    return Settings()

settings = get_settings()