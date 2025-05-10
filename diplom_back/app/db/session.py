from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Импортируем наши настройки

# Создаем движок SQLAlchemy
# Для SQLite: connect_args={"check_same_thread": False} нужен для FastAPI
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL, connect_args={"check_same_thread": False}
    )
else: # Для PostgreSQL и других
    engine = create_engine(settings.DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция-генератор для получения сессии БД в зависимостях FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()