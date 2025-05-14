# diplom_back/app/crud/crud_application.py
from sqlalchemy.orm import Session
from typing import List, Optional, Union, Dict, Any

from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationUpdate

def get_application(db: Session, application_id: int) -> Optional[Application]:
    return db.query(Application).filter(Application.id == application_id).first()

def get_applications_for_vacancy(
    db: Session, vacancy_id: int, skip: int = 0, limit: int = 100
) -> List[Application]:
    return db.query(Application).filter(Application.vacancy_id == vacancy_id).order_by(Application.created_at.desc()).offset(skip).limit(limit).all()

def get_applications_by_candidate(
    db: Session, candidate_id: int, skip: int = 0, limit: int = 100
) -> List[Application]:
    return db.query(Application).filter(Application.candidate_id == candidate_id).order_by(Application.created_at.desc()).offset(skip).limit(limit).all()

def create_application(
    db: Session, *, application_in: ApplicationCreate, candidate_id: int,
    initial_status: ApplicationStatus = ApplicationStatus.SUBMITTED,
    match_score: Optional[float] = None, # Добавляется после алгоритма мэтчинга
    match_details: Optional[Dict[str, Any]] = None
) -> Application:
    # Проверка, не подавал ли уже кандидат заявку на эту вакансию с этим резюме
    existing_application = db.query(Application).filter(
        Application.candidate_id == candidate_id,
        Application.vacancy_id == application_in.vacancy_id,
        Application.resume_id == application_in.resume_id 
    ).first()
    if existing_application:
        # Можно вернуть существующий отклик или выбросить ошибку
        # raise HTTPException(status_code=400, detail="Application already exists for this resume and vacancy.")
        return existing_application # Или обновить дату подачи? Решите сами

    db_application = Application(
        candidate_id=candidate_id,
        vacancy_id=application_in.vacancy_id,
        resume_id=application_in.resume_id,
        status=initial_status,
        match_score=match_score,
        match_details=match_details
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_application(
    db: Session,
    *,
    db_application: Application,
    application_in: Union[ApplicationUpdate, Dict[str, Any]]
) -> Application:
    if isinstance(application_in, dict):
        update_data = application_in
    else:
        update_data = application_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_application, field, value)
        
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application