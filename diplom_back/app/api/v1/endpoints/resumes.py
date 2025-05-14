# diplom_back/app/api/v1/endpoints/resumes.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.services.resume_parser import ResumeParser # Ваш парсер (или заглушка)
from app import crud, schemas, models
from app.api import deps
from app.models.user import UserRole

router = APIRouter()

@router.post("/upload-and-parse", response_model=schemas.ResumeSchema, status_code=status.HTTP_201_CREATED)
async def upload_parse_and_create_resume(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(..., description="Resume PDF file to parse and save"),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Кандидат загружает PDF, он парсится, и создается запись Resume.
    """
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can upload resumes.")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only PDF is allowed.")

    try:
        pdf_bytes = await file.read()
        parser = ResumeParser(pdf_bytes) # Используем ваш парсер
        parsed_data_dict = parser.parse() # Парсер должен возвращать dict

        if "error" in parsed_data_dict:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=parsed_data_dict["error"])
        
        # Создаем объект ResumeCreate из распарсенных данных
        resume_in_create = schemas.ResumeCreate(
            parsed_data=parsed_data_dict,
            original_pdf_path=file.filename # Опционально, если хотите хранить имя файла
        )
        
        resume = crud.create_resume(db=db, resume_in=resume_in_create, candidate_id=current_user.id)
        return resume
    except HTTPException as e:
        raise e
    except Exception as e:
        # import traceback
        # traceback.print_exc() # Для отладки
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    finally:
        await file.close()


@router.get("/my/", response_model=List[schemas.ResumeSchema])
def read_my_resumes(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 10
) -> Any:
    """
    Получить список резюме текущего кандидата.
    """
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can view their resumes.")
    resumes = crud.get_resumes_by_candidate(db, candidate_id=current_user.id, skip=skip, limit=limit)
    return resumes

@router.get("/{resume_id}", response_model=schemas.ResumeSchema)
def read_resume_by_id(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user) # Проверка доступа
) -> Any:
    """
    Получить конкретное резюме по ID.
    Доступно кандидату (если это его резюме) или работодателю (если есть отклик с этим резюме - логика позже).
    """
    resume = crud.get_resume(db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    if resume.candidate_id != current_user.id and current_user.role != UserRole.EMPLOYER and not current_user.is_superuser:
        # Работодатель сможет видеть резюме, только если оно привязано к отклику на его вакансию.
        # Эту логику нужно будет добавить при реализации откликов.
        # Пока простой доступ для владельца или админа.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return resume