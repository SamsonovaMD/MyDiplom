# diplom_back/app/api/v1/endpoints/applications.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models
from app.api import deps
from app.models.user import UserRole
from app.models.application import ApplicationStatus # Для обновления статуса

router = APIRouter()

@router.post("/", response_model=schemas.ApplicationSchema, status_code=status.HTTP_201_CREATED)
def create_new_application(
    *,
    db: Session = Depends(deps.get_db),
    application_in: schemas.ApplicationCreate, # Кандидат передает vacancy_id и resume_id
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Кандидат подает заявку на вакансию.
    """
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can submit applications.")

    # Проверить, существует ли вакансия
    vacancy = crud.get_vacancy(db, vacancy_id=application_in.vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found.")

    # Проверить, принадлежит ли резюме текущему кандидату
    resume = crud.get_resume(db, resume_id=application_in.resume_id)
    if not resume or resume.candidate_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found or does not belong to the current user.")
    
    # TODO: Здесь (или в CRUD) можно добавить вызов вашего алгоритма мэтчинга
    # match_score, match_details = run_matching_algorithm(resume.parsed_data, vacancy)
    # Пока оставляем пустыми или заглушками
    match_score_stub = 0.0 # Заглушка
    match_details_stub = {"message": "Matching pending"} # Заглушка

    application = crud.create_application(
        db=db, 
        application_in=application_in, 
        candidate_id=current_user.id,
        match_score=match_score_stub, # Передаем результат мэтчинга
        match_details=match_details_stub
    )
    return application

@router.get("/my/", response_model=List[schemas.ApplicationSchema])
def read_my_applications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Получить список заявок текущего кандидата.
    """
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed.")
    applications = crud.get_applications_by_candidate(db, candidate_id=current_user.id, skip=skip, limit=limit)
    return applications

@router.get("/vacancy/{vacancy_id}", response_model=List[schemas.ApplicationSchema])
def read_applications_for_vacancy(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Работодатель
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Получить список заявок на конкретную вакансию (для работодателя, который ее создал).
    """
    vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found.")
    
    if current_user.role != UserRole.EMPLOYER or vacancy.employer_id != current_user.id:
        if not current_user.is_superuser: # Админ может видеть все
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions.")
            
    applications = crud.get_applications_for_vacancy(db, vacancy_id=vacancy_id, skip=skip, limit=limit)
    return applications

# Эндпоинт для обновления статуса заявки (например, работодателем)
@router.put("/{application_id}/status", response_model=schemas.ApplicationSchema)
def update_application_status_by_employer(
    application_id: int,
    status_update: schemas.ApplicationUpdate, # Передаем новый статус
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Обновить статус заявки (работодателем).
    """
    db_application = crud.get_application(db, application_id=application_id)
    if not db_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    # Проверить, что текущий пользователь - работодатель и владелец вакансии
    vacancy = crud.get_vacancy(db, vacancy_id=db_application.vacancy_id)
    if not vacancy or vacancy.employer_id != current_user.id:
        if not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions.")
            
    if current_user.role != UserRole.EMPLOYER and not current_user.is_superuser:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employers can update application status.")

    updated_application = crud.update_application(db=db, db_application=db_application, application_in=status_update)
    return updated_application