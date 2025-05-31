# diplom_back/app/api/v1/endpoints/vacancies.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional
from app import crud, schemas, models # Убедитесь, что все модели и схемы импортированы
from app.api import deps
from app.models.user import UserRole
from app.models.vacancy import WorkFormatModelEnum, EmploymentTypeModelEnum

router = APIRouter()

# --- Ваши существующие эндпоинты (оставляем без изменений) ---
@router.post("/", response_model=schemas.VacancySchema, status_code=status.HTTP_201_CREATED)
def create_new_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_in: schemas.VacancyCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only employers can create vacancies."
        )
    vacancy = crud.create_vacancy(db=db, vacancy_in=vacancy_in, employer_id=current_user.id) # Используем crud.vacancy.create_vacancy
    return vacancy

@router.get("/{vacancy_id}", response_model=schemas.VacancySchema)
def read_vacancy_by_id(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id) # Используем crud.vacancy.get_vacancy
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    return vacancy

@router.get("/", response_model=List[schemas.VacancySchema])
def read_all_vacancies(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    search_query: Optional[str] = Query(None, min_length=1, max_length=100, description="Поисковый запрос по названию или описанию"),
    work_format: Optional[WorkFormatModelEnum] = Query(None, description="Фильтр по формату работы"),
    employment_type: Optional[EmploymentTypeModelEnum] = Query(None, description="Фильтр по типу занятости"),
    min_salary_from: Optional[int] = Query(None, ge=0, description="Минимальная зарплата 'от' (в рублях)"),
) -> Any:
    vacancies = crud.get_vacancies( # Используем crud.vacancy.get_vacancies
        db, 
        skip=skip, 
        limit=limit,
        search_query=search_query,
        work_format=work_format,
        employment_type=employment_type,
        min_salary_from=min_salary_from
    )
    return vacancies

@router.get("/my/", response_model=List[schemas.VacancySchema])
def read_my_vacancies(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
) -> Any:
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employers can view their vacancies.")
    vacancies = crud.get_vacancies(db, employer_id=current_user.id, skip=skip, limit=limit) # Используем crud.vacancy.get_vacancies
    return vacancies

@router.put("/{vacancy_id}", response_model=schemas.VacancySchema)
def update_existing_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_id: int,
    vacancy_in: schemas.VacancyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    db_vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id) # Используем crud.vacancy.get_vacancy
    if not db_vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if db_vacancy.employer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    vacancy = crud.update_vacancy(db=db, db_vacancy=db_vacancy, vacancy_in=vacancy_in) # Используем crud.vacancy.update_vacancy
    return vacancy

@router.delete("/{vacancy_id}", response_model=schemas.VacancySchema) # Можно изменить response_model на что-то вроде Message, если вакансия просто удаляется
def delete_existing_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    db_vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id) # Используем crud.vacancy.get_vacancy
    if not db_vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if db_vacancy.employer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    deleted_vacancy = crud.delete_vacancy(db=db, vacancy_id=vacancy_id) # Используем crud.vacancy.delete_vacancy
    if not deleted_vacancy: # Эта проверка дублирует первую, но не помешает
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy could not be deleted or was already deleted.")
    return deleted_vacancy # Возвращаем удаленный объект для консистентности, хотя можно вернуть и сообщение

# --- НОВЫЙ ЭНДПОИНТ ---
@router.get(
    "/{vacancy_id}/matched-candidates/", 
    response_model=List[schemas.MatchedCandidateSchema], # Убедитесь, что schemas.MatchedCandidateSchema импортирована
    dependencies=[Depends(deps.get_current_active_user)] # Защита роута для работодателей
)
def get_matched_candidates_for_vacancy(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), # Получаем текущего работодателя
    min_match_score: float = Query(0.70, ge=0.0, le=1.0, description="Минимальный балл мэтчинга для отбора кандидатов") # Параметр для гибкости
):
    """
    Получить список кандидатов, которые прошли первичный мэтчинг для вакансии.
    Возвращает ФИО, контакты, краткий опыт и навыки.
    Доступно только работодателю, создавшему вакансию.
    """
    print("TEST MATCHING PATH ACCESSED")
    # 1. Получаем вакансию и проверяем, что она принадлежит текущему работодателю
    vacancy = crud.get_vacancy(db, vacancy_id=vacancy_id) # Используем crud.vacancy.get_vacancy
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if vacancy.employer_id != current_user.id:
        # Эта проверка дублируется зависимостью get_current_active_employer, если она проверяет владение,
        # но явная проверка здесь не помешает, особенно если get_current_active_employer просто проверяет роль.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access candidates for this vacancy")

    # 2. Получаем отклики (Application) на эту вакансию с match_score выше порога
    #    Можно использовать существующую CRUD функцию, если она есть, или прямой запрос.
    #    Предположим, у вас нет специальной CRUD функции для этого, делаем прямой запрос:
    high_match_applications = (
        db.query(models.Application)
        .filter(models.Application.vacancy_id == vacancy_id)
        .filter(models.Application.status == "UNDER_REVIEW")
        .order_by(models.Application.match_score.desc()) # Опционально: сортируем по убыванию балла
        .all()
    )

    if not high_match_applications:
        return [] # Если нет подходящих откликов, возвращаем пустой список

    # 3. Собираем данные о кандидатах и их резюме
    matched_candidates_data = []
    for app_model in high_match_applications:
        # Получаем пользователя-кандидата
        # Убедитесь, что у вас есть crud.user.get или аналогичная функция
        candidate_user = crud.get_user(db, user_id=app_model.candidate_id) # Замените get_user на вашу реальную функцию
        
        # Получаем резюме
        # Убедитесь, что у вас есть crud.resume.get или аналогичная функция
        resume = crud.get_resume(db, resume_id=app_model.resume_id) # Замените get_resume на вашу реальную функцию
        
        if candidate_user and resume:
            # Извлекаем навыки. Предполагаем, что навыки - это связь many-to-many через resume.skills
            # или они хранятся в parsed_data. Адаптируйте под вашу структуру.
            skills_list = []
            parsed_summary = resume.parsed_data.get("work_experience_relative_time") # Или другое имя ключа для summary, например, "objective", "about"
            if parsed_summary:
                summary_text = str(parsed_summary)
            parsed_email = resume.parsed_data.get("email")     # Предполагаем ключ "email"
            parsed_phone = resume.parsed_data.get("phone")   
            if resume.parsed_data: # Если есть распарсенные анные
                # Извлекаем навыки из parsed_data
                parsed_skills = resume.parsed_data.get("skils")
                if isinstance(parsed_skills, list):
                    skills_list = [str(skill) for skill in parsed_skills if skill] # Преобразуем в строки и убираем пустые
                elif isinstance(parsed_skills, str) and parsed_skills: # Если навыки - это одна строка
                    skills_list = [s.strip() for s in parsed_skills.split(',') if s.strip()]

            
            candidate_info = schemas.MatchedCandidateSchema(
                id=candidate_user.id,
                full_name=candidate_user.full_name or "Имя не указано",
                email=parsed_email,
                phone=parsed_phone,
                summary=summary_text or "Резюме не предоставлено",
                skills=skills_list,
                resume_id=resume.id
                # match_details=app_model.match_details, # Раскомментируйте, если нужно и есть в схеме
            )
            matched_candidates_data.append(candidate_info)
    
    return matched_candidates_data