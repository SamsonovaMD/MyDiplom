# diplom_back/app/models/vacancy.py
import enum # Для определения Python Enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class WorkFormatModelEnum(str, enum.Enum):
    # Имена членов теперь тоже lowercase
    remote = "remote" 
    hybrid = "hybrid"
    office = "office"

class EmploymentTypeModelEnum(str, enum.Enum):
    # Имена членов теперь тоже lowercase
    full_time = "full_time"
    part_time = "part_time"
    internship = "internship"

class Vacancy(Base):
    __tablename__ = "vacancies"
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    experience_required = Column(String, nullable=True)
    primary_skills = Column(JSONB, nullable=True)
    nice_to_have_skills = Column(JSONB, nullable=True)
    salary_from = Column(Integer, nullable=True, comment="Зарплата от (в рублях)")
    salary_to = Column(Integer, nullable=True, comment="Зарплата до (в рублях, опционально)")

    work_format = Column(
        SQLAlchemyEnum(
            WorkFormatModelEnum,
            name="work_format_enum_type",     
            create_type=False,
            native_enum=False            
        ),
        nullable=True,
        comment="Формат работы"
    )
    employment_type = Column(
        SQLAlchemyEnum(
            EmploymentTypeModelEnum,
            name="employment_type_enum_type", 
            create_type=False,
            native_enum=False                
        ),
        nullable=True,
        comment="Тип занятости"
    )
    
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employer = relationship("User", back_populates="vacancies_posted")
    applications = relationship(
        "Application", 
        back_populates="vacancy", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Vacancy(id={self.id}, title='{self.title}')>"
