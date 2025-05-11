# diplom_back/app/models/resume.py
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Resume(Base):
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_pdf_path = Column(String, nullable=True) # Путь к файлу, если храните их
    # Распарсенные данные храним в JSONB
    parsed_data = Column(JSONB, nullable=True)

    # Связи
    candidate = relationship("User", back_populates="resumes_owned")
    applications = relationship("Application", back_populates="resume")

    def __repr__(self):
        return f"<Resume(id={self.id}, candidate_id={self.candidate_id})>"