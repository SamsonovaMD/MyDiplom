# diplom_back/app/models/user.py
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum, Boolean
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base # Импортируем наш Base

class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    ADMIN = "admin" # Можно добавить админа

class User(Base):
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True) # Может быть ФИО или Название компании для работодателя
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.CANDIDATE)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False) # Если у вас будет суперпользователь

    # Связи (relationships)
    # Если пользователь - работодатель, у него могут быть вакансии
    vacancies_posted = relationship("Vacancy", back_populates="employer", foreign_keys="[Vacancy.employer_id]")
    # Если пользователь - кандидат, у него могут быть резюме и заявки
    resumes_owned = relationship("Resume", back_populates="candidate", foreign_keys="[Resume.candidate_id]")
    applications_made = relationship("Application", back_populates="candidate", foreign_keys="[Application.candidate_id]")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"