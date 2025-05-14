# diplom_back/app/crud/crud_resume.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate # ResumeUpdate если будет

def get_resume(db: Session, resume_id: int) -> Optional[Resume]:
    return db.query(Resume).filter(Resume.id == resume_id).first()

def get_resumes_by_candidate(db: Session, candidate_id: int, skip: int = 0, limit: int = 10) -> List[Resume]:
    return db.query(Resume).filter(Resume.candidate_id == candidate_id).order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()

def create_resume(db: Session, *, resume_in: ResumeCreate, candidate_id: int) -> Resume:
    db_resume_data = resume_in.model_dump()
    db_resume = Resume(**db_resume_data, candidate_id=candidate_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

# def update_resume(...) # Если нужно
# def delete_resume(...) # Если нужно