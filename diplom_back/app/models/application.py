# diplom_back/app/models/application.py
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB # Если результат мэтчинга тоже сложный
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    INVITED_TO_INTERVIEW = "invited_to_interview"
    HIRED = "hired"

class Application(Base):
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False) 
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False) # Какое именно резюме было подано

    status = Column(SQLAlchemyEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.SUBMITTED)
    match_score = Column(Float, nullable=True) # Результат мэтчинга (скор)
    match_details = Column(JSONB, nullable=True) # Дополнительные детали мэтчинга (например, какие навыки совпали)
    # cover_letter = Column(Text, nullable=True) # Опционально: сопроводительное письмо

    # Связи
    candidate = relationship("User", back_populates="applications_made")
    vacancy = relationship("Vacancy", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, vacancy_id={self.vacancy_id}, candidate_id={self.candidate_id})>"