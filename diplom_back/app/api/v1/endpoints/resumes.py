# diplom_back/app/api/v1/endpoints/resumes.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.resume_parser import ResumeParser # Убедитесь, что путь к ResumeParser правильный
from typing import Dict, Any # Any если ваш парсер возвращает Dict[str, Any]

router = APIRouter() # Убедитесь, что роутер создается

@router.post("/parse", summary="Parse a resume PDF file") # Путь будет /resumes/parse из-за префикса в api.py
async def parse_resume_file(file: UploadFile = File(..., description="Resume PDF file to parse")) -> Dict[str, Any]: # Укажите тип возвращаемых данных
    """
    Загружает PDF файл резюме и возвращает извлеченную информацию в формате JSON.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    try:
        pdf_bytes = await file.read()
        parser = ResumeParser(pdf_bytes) # Используется ваш ResumeParser (заглушка или реальный)
        parsed_data = parser.parse()
        if "error" in parsed_data:
             raise HTTPException(status_code=500, detail=parsed_data["error"])
        return parsed_data
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error during resume parsing endpoint: {e}") # Логирование для отладки
        # import traceback
        # traceback.print_exc() # Для детальной ошибки в консоли
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during parsing: {str(e)}")
    finally:
        await file.close()