# diplom_back/app/models/vacancy.py
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Vacancy(Base):
    __tablename__ = "vacancies" # <--- ЯВНО УКАЗЫВАЕМ ИМЯ ТАБЛИЦЫ

    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    experience_required = Column(String, nullable=True)
    primary_skills = Column(JSONB, nullable=True)
    nice_to_have_skills = Column(JSONB, nullable=True)
    
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    employer = relationship("User", back_populates="vacancies_posted")
    applications = relationship("Application", back_populates="vacancy")

    def __repr__(self):
        return f"<Vacancy(id={self.id}, title='{self.title}')>"