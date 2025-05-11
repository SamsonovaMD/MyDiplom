# diplom_back/app/models/__init__.py
# from app.db.base_class import Base # Убедитесь, что Base импортируется отсюда или из app.db.base

from .user import User
from .vacancy import Vacancy
from .resume import Resume
from .application import Application