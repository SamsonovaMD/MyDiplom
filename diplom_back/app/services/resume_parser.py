import fitz  # PyMuPDF - оставляем, т.к. эндпоинт все еще ожидает PDF
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone # Добавим timezone для примера с датой
# from calendar import monthrange # Нам это больше не нужно для заглушки

# ... (остальные ваши вспомогательные функции могут остаться, они не будут вызываться заглушкой)
# ... (MONTH_MAP_RU_EN и другие функции)

class ResumeParser: # Или StubResumeParser
    def __init__(self, pdf_file_bytes: bytes):
        # Мы все еще принимаем байты, чтобы сигнатура класса осталась прежней
        # но в заглушке мы их не будем использовать.
        self.pdf_bytes = pdf_file_bytes
        # self.raw_text = extract_text_from_pdf_bytes(self.pdf_bytes) # Это можно закомментировать
        # self.text_lines = self.raw_text.splitlines()
        # self.normalized_full_text_for_search = normalize_text_for_search(self.raw_text)
        # self.known_skills_patterns = [...] # Тоже не нужно для заглушки

    def parse(self) -> Dict[str, Any]:
        """
        Заглушка для парсинга резюме. Возвращает предопределенный JSON.
        """
        print("DEBUG: Using STUB ResumeParser.parse() method.") # Для отладки, чтобы знать, что используется заглушка
        
        # Генерируем примерную текущую дату для поля "end_date" в опыте
        now_iso = datetime.now(timezone.utc).isoformat()

        stub_json = {
            "full_name": "Иван Иванович Тестов (Заглушка)",
            "age": 30,
            "date_of_birth": "01 января 1993",
            "contact_info": {
                "phone": "+79001234567",
                "email": "stub_test@example.com",
                "location": "Город Заглушек"
            },
            "education": [
                {
                    "degree_status": "Высшее (Заглушка)",
                    "institution": "Университет Заглушечных Наук",
                    "faculty_specialization": "Факультет Тестовых Данных, Специальность JSON",
                    "graduation_year": "2015",
                    "location": "Город Заглушек"
                }
            ],
            "work_experience": [
                {
                    "start_date_str": "январь 2020",
                    "end_date_str": "настоящее время",
                    "start_date": datetime(2020, 1, 1).isoformat(), # ISO формат для дат
                    "end_date": now_iso, 
                    "duration_months": 55, # Примерное значение
                    "company_name": "ООО \"Заглушка и Ко\"",
                    "position": "Ведущий специалист по заглушкам",
                    "description": "Создание и поддержка высококачественных заглушек для различных систем. Управление командой заглушек.",
                    "project_skills": ["Заглушкостроение", "API", "JSON"]
                },
                {
                    "start_date_str": "июнь 2018",
                    "end_date_str": "декабрь 2019",
                    "start_date": datetime(2018, 6, 1).isoformat(),
                    "end_date": datetime(2019, 12, 31).isoformat(),
                    "duration_months": 19,
                    "company_name": "Стартап \"Быстрые Заглушки\"",
                    "position": "Младший специалист по заглушкам",
                    "description": "Разработка заглушек на Python.",
                    "project_skills": ["Python", "Тестирование"]
                }
            ],
            "skills": [
                "Python", "FastAPI", "SQL (заглушка)", "Docker (заглушка)", 
                "Заглушкостроение", "API", "JSON", "Анализ данных (заглушка)"
            ],
            "desired_position": "Главный Архитектор Заглушек",
            "desired_salary": "200000 руб"
            # Добавьте другие поля, которые вы ожидаете в своем JSON
        }
        return stub_json

# Ваш эндпоинт в diplom_back/app/api/v1/endpoints/resumes.py уже должен работать с этим.
# Убедитесь, что он импортирует и использует этот ResumeParser.