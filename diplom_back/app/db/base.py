from sqlalchemy.orm import declarative_base

# Базовый класс для всех моделей SQLAlchemy
# Позже наши модели будут наследоваться от него
Base = declarative_base()

# Здесь можно будет импортировать все модели, чтобы Alembic их видел
# from app.models.user import User # Пример
# from app.models.vacancy import Vacancy # Пример