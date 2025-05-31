# app/crud/crud_vacancy.py
from sqlalchemy.orm import Session
import sqlalchemy as sa
import enum 

from typing import List, Optional, Union, Dict, Any

from app.models.vacancy import Vacancy , WorkFormatModelEnum, EmploymentTypeModelEnum 
from app.schemas.vacancy import VacancyCreate, VacancyUpdate


def get_vacancy(db: Session, vacancy_id: int) -> Optional[Vacancy]:
    return db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

def get_vacancies(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    employer_id: Optional[int] = None,
    search_query: Optional[str] = None,
    # Для фильтрации мы все еще используем модельные Enum, это нормально
    work_format: Optional[WorkFormatModelEnum] = None, 
    employment_type: Optional[EmploymentTypeModelEnum] = None,
    min_salary_from: Optional[int] = None,
) -> List[Vacancy]:
    # ... (код get_vacancies остается таким же) ...
    query = db.query(Vacancy)
    if employer_id is not None:
        query = query.filter(Vacancy.employer_id == employer_id)
    if search_query:
        query = query.filter(
            sa.or_(
                Vacancy.title.ilike(f"%{search_query}%"),
                Vacancy.description.ilike(f"%{search_query}%")
            )
        )
    if work_format is not None: # work_format здесь это экземпляр WorkFormatModelEnum
        query = query.filter(Vacancy.work_format == work_format) 
    if employment_type is not None: # employment_type здесь это экземпляр EmploymentTypeModelEnum
        query = query.filter(Vacancy.employment_type == employment_type)
    if min_salary_from is not None:
        query = query.filter(Vacancy.salary_from.isnot(None), Vacancy.salary_from >= min_salary_from)
    return query.order_by(Vacancy.created_at.desc()).offset(skip).limit(limit).all()


def create_vacancy(db: Session, *, vacancy_in: VacancyCreate, employer_id: int) -> Vacancy:
    raw_dict_from_schema = vacancy_in.model_dump()

    data_for_sqlalchemy_model = {}
    for key, value in raw_dict_from_schema.items():
        if isinstance(value, enum.Enum): 
            data_for_sqlalchemy_model[key] = value.value 
        else:
            data_for_sqlalchemy_model[key] = value
            

    db_vacancy = Vacancy(**data_for_sqlalchemy_model, employer_id=employer_id)
    db.add(db_vacancy)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise
        
    db.refresh(db_vacancy)
    return db_vacancy

# Обновите update_vacancy аналогично
def update_vacancy(
    db: Session,
    *,
    db_vacancy: Vacancy, # Объект Vacancy, который мы обновляем (уже загружен из БД)
    vacancy_in: Union[VacancyUpdate, Dict[str, Any]] # Данные для обновления из Pydantic схемы или словаря
) -> Vacancy: # Важно: функция должна возвращать обновленный объект Vacancy
    update_data_raw: Dict[str, Any]
    if isinstance(vacancy_in, dict):
        update_data_raw = vacancy_in
    else:
        # Используем model_dump с exclude_unset=True, чтобы обновлять только переданные поля
        update_data_raw = vacancy_in.model_dump(exclude_unset=True)

    processed_update_data = {}
    for field, value in update_data_raw.items():
        # Проверяем, есть ли такой атрибут в модели, чтобы не пытаться установить лишнее
        if hasattr(db_vacancy, field):
            if isinstance(value, enum.Enum):
                # Если значение - это Enum, берем его .value для записи в БД
                processed_update_data[field] = value.value
            else:
                processed_update_data[field] = value
        # else:
            # Опционально: логирование или обработка, если приходят поля, которых нет в модели
            # print(f"Warning: Field '{field}' not found in Vacancy model.")

    # Обновляем атрибуты объекта db_vacancy
    for field_name, value_to_set in processed_update_data.items():
        setattr(db_vacancy, field_name, value_to_set)

    db.add(db_vacancy) # Добавляем измененный объект в сессию SQLAlchemy (она отследит изменения)
    try:
        db.commit()      # Фиксируем изменения в базе данных
        db.refresh(db_vacancy) # Обновляем объект db_vacancy данными из БД (важно, если есть триггеры или default значения)
    except Exception as e:
        db.rollback()    # Откатываем транзакцию в случае ошибки
        raise e          # Перевыбрасываем исключение, чтобы его обработал FastAPI
        
    return db_vacancy    # Возвращаем обновленный объект Vacancy

def delete_vacancy(db: Session, vacancy_id: int) -> Optional[Vacancy]:
    # ... (код без изменений) ...
    db_vacancy = db.query(Vacancy).get(vacancy_id) 
    if db_vacancy:
        db.delete(db_vacancy)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise
    return db_vacancy