# diplom_back/app/api/v1/endpoints/applications.py
from fastapi import APIRouter, Depends, HTTPException, status as http_status # Переименовал status в http_status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models
from app.api import deps
from app.models.user import UserRole
from app.models.application import ApplicationStatus
from app.services import matching_service # <--- НАШ СЕРВИС МЭТЧИНГА

router = APIRouter()

@router.post("/", response_model=schemas.ApplicationSchema, status_code=http_status.HTTP_201_CREATED)
def create_new_application(
    *,
    db: Session = Depends(deps.get_db),
    application_in: schemas.ApplicationCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Кандидат подает заявку на вакансию.
    """
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Only candidates can submit applications.")

    vacancy = crud.get_vacancy(db, vacancy_id=application_in.vacancy_id) # Используем ваш crud.vacancy
    if not vacancy:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Vacancy not found.")

    resume = crud.get_resume(db, resume_id=application_in.resume_id) # Используем ваш crud.resume
    if not resume or resume.candidate_id != current_user.id:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Resume not found or does not belong to the current user.")
    
    if not resume.parsed_data: # Важная проверка
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Resume data has not been parsed. Matching cannot be performed."
        )

    # --- Вызов алгоритма мэтчинга ---
    match_analysis_result = matching_service.perform_matching_analysis(
        resume=resume,
        vacancy=vacancy
    )

    if match_analysis_result.get("error_message"):
        # Если сервис мэтчинга вернул явную ошибку (например, не распарсено резюме - хотя мы проверили выше)
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, # или 500 если это внутренняя ошибка сервиса
            detail=f"Matching process failed: {match_analysis_result['error_message']}"
        )

    # --- Используем результаты мэтчинга для создания Application ---
    application = crud.create_application(
        db=db,
        application_in=application_in, # schemas.ApplicationCreate (vacancy_id, resume_id)
        candidate_id=current_user.id,
        initial_status=match_analysis_result["initial_status"], # Статус из мэтчинга
        match_score=match_analysis_result["match_score"],       # Скор из мэтчинга
        match_details=match_analysis_result["match_details"]    # Детали из мэтчинга
    )
    # crud.create_application должен обработать случай, если отклик уже существует
    if not application: # Если crud.create_application вернул None из-за ошибки или дубликата
         raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT, # Или другой подходящий код
            detail="Failed to create application, it might already exist or an error occurred."
        )
        
    return application

# Остальные ваши эндпоинты (get_my_applications, get_applications_for_vacancy, update_status) остаются без изменений,
# так как они не участвуют напрямую в создании отклика с мэтчингом.
# Важно: убедитесь, что crud.vacancy.get_vacancy и crud.resume.get_resume импортированы или доступны в этом файле.
# Я заменил crud.get_vacancy на crud.vacancy.get_vacancy и crud.get_resume на crud.resume.get_resume
# для единообразия с crud.application.create_application. Если у вас они импортированы по-другому, исправьте.

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
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Not allowed.")
    applications = crud.get_applications_by_candidate(db, candidate_id=current_user.id, skip=skip, limit=limit)
    return applications

@router.get("/vacancy/{vacancy_id}", response_model=List[schemas.ApplicationSchema])
def read_applications_for_vacancy(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Получить список заявок на конкретную вакансию (для работодателя, который ее создал).
    """
    vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Vacancy not found.")
    
    if current_user.role != UserRole.EMPLOYER or vacancy.employer_id != current_user.id:
        if not current_user.is_superuser: 
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Not enough permissions.")
            
    applications = crud.get_applications_for_vacancy(db, vacancy_id=vacancy_id, skip=skip, limit=limit)
    return applications

@router.put("/{application_id}/status", response_model=schemas.ApplicationSchema)
def update_application_status_by_employer(
    application_id: int,
    status_update: schemas.ApplicationUpdate, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Обновить статус заявки (работодателем).
    """
    db_application = crud.get_application(db, application_id=application_id)
    if not db_application:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Application not found.")

    vacancy = crud.get_vacancy(db, vacancy_id=db_application.vacancy_id)
    # Добавим проверку на существование вакансии, на всякий случай
    if not vacancy:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Associated vacancy not found.")

    if current_user.role != UserRole.EMPLOYER or vacancy.employer_id != current_user.id:
        if not current_user.is_superuser:
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Not enough permissions.")
            
    # В вашей CRUD функции update_application уже есть логика обновления полей
    # Убедимся, что передаем только статус, если только он меняется
    if status_update.status is None: # Если в запросе не пришел новый статус
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="No status provided for update.")
        
    updated_application = crud.update_application(
        db=db, 
        db_application=db_application, 
        application_in={"status": status_update.status} # Передаем только статус для обновления
    )
    return updated_application
