# diplom_back/app/api/v1/endpoints/vacancies.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models
from app.api import deps
from app.models.user import UserRole # Для проверки роли

router = APIRouter()

@router.post("/", response_model=schemas.VacancySchema, status_code=status.HTTP_201_CREATED)
def create_new_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_in: schemas.VacancyCreate,
    current_user: models.User = Depends(deps.get_current_active_user) # Нужен залогиненный пользователь
) -> Any:
    """
    Создать новую вакансию (только для работодателей).
    """
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only employers can create vacancies."
        )
    vacancy = crud.create_vacancy(db=db, vacancy_in=vacancy_in, employer_id=current_user.id)
    return vacancy

@router.get("/{vacancy_id}", response_model=schemas.VacancySchema)
def read_vacancy_by_id(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
    # current_user: Optional[models.User] = Depends(deps.get_current_user) # Опционально, если нужна аутентификация для просмотра
) -> Any:
    """
    Получить вакансию по ID (доступно всем).
    """
    vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    return vacancy

@router.get("/", response_model=List[schemas.VacancySchema])
def read_all_vacancies( # Переименовал для ясности
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # TODO: Добавить параметры фильтрации (поиск по названию, навыкам и т.д.)
    # current_user: Optional[models.User] = Depends(deps.get_current_user)
) -> Any:
    """
    Получить список всех активных вакансий (доступно всем).
    """
    vacancies = crud.get_vacancies(db, skip=skip, limit=limit)
    return vacancies

@router.get("/my/", response_model=List[schemas.VacancySchema])
def read_my_vacancies(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Получить список вакансий, созданных текущим работодателем.
    """
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employers can view their vacancies.")
    vacancies = crud.get_vacancies(db, employer_id=current_user.id, skip=skip, limit=limit)
    return vacancies


@router.put("/{vacancy_id}", response_model=schemas.VacancySchema)
def update_existing_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_id: int,
    vacancy_in: schemas.VacancyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Обновить вакансию (только для работодателя, который ее создал).
    """
    db_vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id)
    if not db_vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if db_vacancy.employer_id != current_user.id and not current_user.is_superuser: # Или если админ
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    vacancy = crud.update_vacancy(db=db, db_vacancy=db_vacancy, vacancy_in=vacancy_in)
    return vacancy

@router.delete("/{vacancy_id}", response_model=schemas.VacancySchema) # Можно возвращать статус или сообщение
def delete_existing_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Удалить вакансию (только для работодателя, который ее создал, или админа).
    """
    db_vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id)
    if not db_vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if db_vacancy.employer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    deleted_vacancy = crud.delete_vacancy(db=db, vacancy_id=vacancy_id)
    if not deleted_vacancy: # На всякий случай, хотя get_vacancy уже проверил
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found during delete operation")
    return deleted_vacancy # Возвращаем удаленную вакансию (или можно просто {"detail": "Vacancy deleted"})