# diplom_back/app/crud/crud_vacancy.py
from sqlalchemy.orm import Session
from typing import List, Optional, Union, Dict, Any

from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyCreate, VacancyUpdate

def get_vacancy(db: Session, vacancy_id: int) -> Optional[Vacancy]:
    return db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

def get_vacancies(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    employer_id: Optional[int] = None,
    # TODO: Добавить другие фильтры (например, по навыкам, названию)
) -> List[Vacancy]:
    query = db.query(Vacancy)
    if employer_id is not None:
        query = query.filter(Vacancy.employer_id == employer_id)
    return query.order_by(Vacancy.created_at.desc()).offset(skip).limit(limit).all()

def create_vacancy(db: Session, *, vacancy_in: VacancyCreate, employer_id: int) -> Vacancy:
    db_vacancy_data = vacancy_in.model_dump()
    db_vacancy = Vacancy(**db_vacancy_data, employer_id=employer_id)
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

def update_vacancy(
    db: Session,
    *,
    db_vacancy: Vacancy,
    vacancy_in: Union[VacancyUpdate, Dict[str, Any]]
) -> Vacancy:
    if isinstance(vacancy_in, dict):
        update_data = vacancy_in
    else:
        update_data = vacancy_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_vacancy, field, value)
    
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

def delete_vacancy(db: Session, vacancy_id: int) -> Optional[Vacancy]:
    db_vacancy = db.query(Vacancy).get(vacancy_id)
    if db_vacancy:
        db.delete(db_vacancy)
        db.commit()
    return db_vacancy