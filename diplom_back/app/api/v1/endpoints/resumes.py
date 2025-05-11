from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.resume_parser import ResumeParser # Убедитесь, что путь правильный
from typing import Dict

router = APIRouter()

@router.post("/resumes/parse", summary="Parse a resume PDF file")
async def parse_resume_file(file: UploadFile = File(..., description="Resume PDF file to parse")):
    """
    Загружает PDF файл резюме и возвращает извлеченную информацию в формате JSON.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    try:
        pdf_bytes = await file.read()
        parser = ResumeParser(pdf_bytes)
        parsed_data = parser.parse()
        if "error" in parsed_data: # Если парсер вернул ошибку
             raise HTTPException(status_code=500, detail=parsed_data["error"])
        return parsed_data
    except HTTPException as e: # Перехватываем свои же HTTPException, чтобы они прошли дальше
        raise e
    except Exception as e:
        # Логирование ошибки здесь было бы полезно
        print(f"Error during resume parsing: {e}") # Просто для примера, лучше использовать logging
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during parsing: {str(e)}")
    finally:
        await file.close()