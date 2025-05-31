from PyPDF2 import PdfReader # Используется вашим кодом
import io # Для работы с байтами PDF как с файлом
import re
import json # Используется для финальной структуры, но parse вернет dict
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone # Может понадобиться для обработки дат, если будете добавлять
# import fitz  # PyMuPDF - пока не используется вашим основным кодом

# --- Ваши функции парсинга, адаптированные как вспомогательные ---
def _clear_list(text_lines: List[str]) -> List[str]:
    target_clear = ["\xa0", ]
    cleaned_array = []
    for item in text_lines:
        for target in target_clear:
            item = item.replace(target, ' ')
        item = re.sub(r'Резюме обновлено\s+\d{1,2}\s+\S+\s+\d{4}\s+в\s+\d{2}:\d{2}', '', item)
        cleaned_array.append(item)
    return cleaned_array

def _get_all_position_index(text_lines: List[str]) -> List[List[str]]: # Renamed param to text_lines for clarity
    """
    :param text_lines: The list of lines from the resume.
    :return: [info, job_experience, education, course, skils]
    """
    target_list = ["Опыт работы", "Образование", "Повышение квалификации, курсы", "Навыки", "Дополнительная информация"]
    result_indices = [] # Stores the indices of the target sections
    for target in target_list:
        # Find the first occurrence of the target string
        found_index = -1
        for i, item in enumerate(text_lines):
            if target in item:
                found_index = i
                break
        result_indices.append(found_index)
    
    idx_opyt = result_indices[0] if result_indices[0] != -1 else len(text_lines)
    idx_obrazovanie = result_indices[1] if result_indices[1] != -1 else len(text_lines)
    idx_kursy = result_indices[2] if result_indices[2] != -1 else len(text_lines)
    idx_navyki = result_indices[3] if result_indices[3] != -1 else len(text_lines)
    idx_dop_info = result_indices[4] if result_indices[4] != -1 else len(text_lines)

    info = text_lines[0 : max(0, idx_opyt)]
    job_experience = text_lines[max(0, idx_opyt) : max(idx_opyt, idx_obrazovanie)]
    education = text_lines[max(idx_opyt, idx_obrazovanie) : max(idx_obrazovanie, idx_kursy)]
    # Adjust start for course and skils based on your original logic (+1)
    course_start_idx = max(idx_obrazovanie, idx_kursy)
    if result_indices[2] != -1 : # Only add 1 if "Повышение квалификации, курсы" was actually found
        course_start_idx = result_indices[2] +1

    skills_start_idx = max(idx_kursy, idx_navyki)
    if result_indices[3] != -1: # Only add 1 if "Навыки" was actually found
        skills_start_idx = result_indices[3] + 1
    
    course = text_lines[course_start_idx : max(course_start_idx, idx_navyki)]
    skils = text_lines[skills_start_idx : max(skills_start_idx, idx_dop_info)]
    
    # print(result_indices) # This prints the found indices like [14, 35, 40, 50, 55]
    return [info, job_experience, education, course, skils]


def _parse_resume_info(lines: List[str]) -> Dict[str, Any]:
    result = {
        "full_name": None,
        "gender": None,
        "age": None,
        "date_of_birth": None,
        "phone": None,
        "email": None,
        "location": None,
        "citizenship": None,
        "permission_for_work": None,
        "busyness": None,
        "work_schedule": None,
    }
    if lines: # Check if lines is not empty
        result["full_name"] = lines[0].strip() # Use strip for safety
    else: # Handle empty info section gracefully
        result["full_name"] = "N/A (Info Section Empty)"

    for text in lines:
        match = re.search(r'(Мужчина|Женщина),\s*(\d+)\s*год(?:а|ов)?,\s*родил(?:ся|ась)\s*(\d{1,2}\s+\S+\s+\d{4})', text)
        if match:
            result["gender"] = match.group(1)
            result["age"] = int(match.group(2))
            result["date_of_birth"] = match.group(3)
        match = re.search(r'(\+7\s*\(\d{3}\)\s*\d{6,})', text)
        if match:
            result["phone"] = match.group(1).replace(' ', '')
        match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        if match and not result["email"]: # Take the first email found
            result["email"] = match.group(0)
        match = re.search(r'Проживает:\s*(.+)', text)
        if match:
            result["location"] = match.group(1).strip()
        match = re.search(r'Гражданство:\s*([^,]+)(?:,\s*есть разрешение на работу:\s*(.+))?', text) # Made permission optional
        if match:
            result["citizenship"] = match.group(1).strip()
            if match.group(2):
                result["permission_for_work"] = match.group(2).strip()
        match = re.search(r'Занятость:\s*(.+)', text)
        if match:
            result["busyness"] = match.group(1).strip()
        match = re.search(r'График работы:\s*(.+)', text)
        if match:
            result["work_schedule"] = match.group(1).strip()
    return result

def _parse_work_preferences(work_schedule_str: Optional[str], busyness_str: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Извлекает предпочтительный формат работы и тип занятости из строк.
    Значения приводятся к тем, что используются в Enum в matching_service (lowercase).
    """
    preferences = {
        "preferred_work_format": None,
        "preferred_employment_type": None,
    }

    # Сначала объединим обе строки, если они есть, для поиска
    combined_text_lower = ""
    if work_schedule_str:
        combined_text_lower += work_schedule_str.lower() + " "
    if busyness_str:
        combined_text_lower += busyness_str.lower()

    # Ключевые слова для формата работы (сопоставляем с вашими Enum значениями)
    work_format_map = {
        "удаленная работа": "remote",
        "удаленно": "remote",
        "дистанционно": "remote",
        "гибрид": "hybrid",
        "гибридный график": "hybrid",
        "в офисе": "office",
        "офис": "office",
    }
    # Ключевые слова для типа занятости
    employment_type_map = {
        "полный день": "full_time",       # Часто встречается в "График работы"
        "полная занятость": "full_time", # Часто встречается в "Занятость"
        "частичная занятость": "part_time",
        "неполный день": "part_time",
        "стажировка": "internship",
        # "проектная работа": "project_work", # Если нужно
        # "волонтерство": "volunteer",      # Если нужно
    }

    for keyword, value in work_format_map.items():
        if keyword in combined_text_lower:
            preferences["preferred_work_format"] = value
            break 

    for keyword, value in employment_type_map.items():
        if keyword in combined_text_lower:
            preferences["preferred_employment_type"] = value
            break
            
    return preferences


def _parse_resume_job_experience(lines: List[str]) -> Dict[str, Any]:
    years_, months_ = 0,0
    company_ = ""
    result = {
        "work_experience": None,
        "work_experience_relative_time": None,
        "work_experience_relative": [],
    }
    pattern = r'(?:(?P<years>\d+)\s*год(?:а|ов)?)?\s*(?:(?P<months>\d+)\s*месяц(?:а|ев)?)?(?P<company>.+)?'
    sum_time = 0
    first_line_experience_text = ""
    if lines: # Check if lines is not empty
        first_line_experience_text = lines[0]

    for text in lines:
        match = re.match(pattern, text)
        # "Информационные технологии," seems too specific for general HH, but keeping your logic
        relevant_match = re.search(r'(Информационные технологии,)', text)
        if match:
            years = int(match.group('years')) if match.group('years') else 0
            months = int(match.group('months')) if match.group('months') else 0
            company = match.group('company').strip() if match.group('company') else None
            if years or months:
                months_ = (int(years) * 12 + int(months))
                if company: # Only assign company_ if it's found on the same line as duration
                    company_ = company

        if relevant_match: # This condition might be too strict or specific
            # If relevant_match is the primary way to identify a job entry,
            # ensure company_ and months_ are correctly associated with it.
            # The current logic for company_ might pick up a company from a previous line.
            result["work_experience_relative"].append({
                "company": company_ if company_ else "Unknown Company", # Provide a default
                "time_month": months_
            })
            sum_time += months_
            # Reset for next potential entry if company was tied to this relevant_match
            # company_ = ""
            # months_ = 0


    result["work_experience_relative_time"] = sum_time
    
    if first_line_experience_text: # Use the stored first line
        find = re.search(r'Опыт работы\s*—\s*(?:(\d+)\s*год(?:а|ов)?)?\s*?(?:(\d+)\s*месяц(?:а|ев)?)?', first_line_experience_text)
        if find:
            years = int(find.group(1)) if find.group(1) else 0
            months = int(find.group(2)) if find.group(2) else 0
            result["work_experience"] = years * 12 + months
    return result

def _parse_resume_education(lines: List[str]) -> Dict[str, Any]:
    result = {
        "degree_status": lines[1],
        "year": None,
        "name": None,
        "city": None,
        "faculty": None,
        "degree": None,
    }
    all_education = " "
    for text in lines:
        all_education += text + ' '

    # print(all_education)

    match = re.search(r'(\d{4})\s+([^,]+),\s*([^\s,]+)?\s+([^,]+),', all_education)
    find = re.search(r'([^,]+),\s*([^,]+)(?:\s*\([^)]+\))?$', all_education)

    if match and find:
        result["year"] = match.group(1)
        result["name"] = match.group(2)
        result["city"] = match.group(3)
        result["faculty"] = match.group(4)
        result["degree"] = find.group(2)
    return result

def _parse_resume_course(lines: List[str]) -> Dict[str, Any]:
    result = {
        "course": [],
    }
    
    current_year = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Проверяем, начинается ли строка с года (4 цифры)
        year_match = re.match(r'^(\d{4})\s+(.*)', line)
        if year_match:
            current_year = year_match.group(1)
            remaining_text = year_match.group(2)
            
            # Разделяем оставшийся текст на название курса и место
            # Предполагаем, что название курса идет до места, разделенного запятой или просто до конца строки
            if ',' in remaining_text:
                course_name, place = remaining_text.split(',', 1)
                place = place.strip()
            else:
                course_name = remaining_text
                place = ""
                
            result["course"].append({
                "year": current_year,
                "name": course_name.strip(),
                "place": place
            })
        else:
            # Если строка не начинается с года, но есть текущий год,
            # это может быть продолжение места обучения
            if current_year and result["course"]:
                last_course = result["course"][-1]
                if not last_course["place"]:
                    last_course["place"] = line
                else:
                    last_course["place"] += " " + line
    
    return result

def _parse_resume_skils(lines: List[str]) -> Dict[str, Any]:
    result = {
        "skils": None,
    }
    pos = next((i for i, item in enumerate(lines) if "Навыки" in item), -1)
    lines = lines[pos:]
    all_skils = " "
    for text in lines:
        all_skils += text + ' '
    skils = all_skils.split("  ")
    skils = skils[1:]
    result["skils"] = [item.strip() for item in skils if item.strip()]
    return result

def _parse_desired_salary(lines: List[str]) -> Dict[str, Any]:
    salary_data = {"desired_salary": {"amount": None, "currency": None}}
    
    for i, line in enumerate(lines):
        if "Желательное время в пути до работы:" in line:
            match_amount = re.search(r'([\d\s]+\d)\s*$', line) 
            if not match_amount: 
                 match_amount = re.search(r'(\d+)\s*$', line)

            if match_amount:
                amount_str = match_amount.group(1).replace(" ", "")  # Remove spaces for clean integer conversion
                
                if i + 1 < len(lines):
                    next_line_stripped = lines[i+1].strip()
                    known_currencies = ["₽", "руб.", "руб", "рублей", "USD", "$", "EUR", "€"]
                    if next_line_stripped in known_currencies:
                        try:
                            salary_data["desired_salary"]["amount"] = int(amount_str)
                            salary_data["desired_salary"]["currency"] = next_line_stripped
                            return salary_data
                        except ValueError:
                            pass 
    return salary_data


# --- Класс ResumeParser ---
class ResumeParser:
    def __init__(self, pdf_file_bytes: bytes):
        self.pdf_bytes = pdf_file_bytes
        self.prepared_text_lines: List[str] = []

    def _extract_and_prepare_text(self):
        """Извлекает текст из PDF и подготавливает его."""
        raw_full_text = ""
        try:
            pdf_stream = io.BytesIO(self.pdf_bytes)
            reader = PdfReader(pdf_stream)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    raw_full_text += page_text + "\n" # Добавляем перенос строки между страницами
        except Exception as e:
            print(f"Error reading PDF content with PyPDF2: {e}")
            # Fallback or alternative library could be attempted here, e.g., fitz
            raw_full_text = "" # Ensure it's empty if PyPDF2 fails
            try:
                print("Attempting fallback with fitz (PyMuPDF)...")
                import fitz # PyMuPDF
                with fitz.open(stream=self.pdf_bytes, filetype="pdf") as doc:
                    for page in doc:
                        raw_full_text += page.get_text() + "\n"
                print("Fallback with fitz successful.")
            except Exception as e_fitz:
                print(f"Error reading PDF content with fitz: {e_fitz}")
                self.prepared_text_lines = []
                return

        self.prepared_text_lines = _clear_list(raw_full_text.splitlines())

    def parse(self) -> Dict[str, Any]:
        """
        Основной метод парсинга. Возвращает структурированный словарь (JSON).
        """
        self._extract_and_prepare_text()
        if not self.prepared_text_lines:
            return {"error": "Failed to extract or prepare text from PDF."}

        sections_from_pdf = _get_all_position_index(self.prepared_text_lines)

        # Defensive check for section lengths
        if len(sections_from_pdf) < 5:
            return {"error": f"Could not identify all resume sections. Found {len(sections_from_pdf)}."}

        parsed_info = _parse_resume_info(sections_from_pdf[0])

        result_dict = {
            **parsed_info,
            **_parse_resume_job_experience(sections_from_pdf[1]),
            **_parse_resume_education(sections_from_pdf[2]),
            **_parse_resume_course(sections_from_pdf[3]),
            **_parse_resume_skils(sections_from_pdf[4]),
        }

        work_preferences = _parse_work_preferences(
            work_schedule_str=parsed_info.get("work_schedule"), # Берем из уже распарсенной информации
            busyness_str=parsed_info.get("busyness")         # Также берем "Занятость"
        )
        result_dict.update(work_preferences) 

        desired_salary_info = _parse_desired_salary(self.prepared_text_lines)
        result_dict.update(desired_salary_info)
        return result_dict

# --- Блок для локального тестирования ---
# if __name__ == "__main__":
#     test_pdf_path = "C:\\Users\\user\\Downloads\\Самсонова Мария.pdf"
#     # Пример из вашего кода
#     try:
#         with open(test_pdf_path, "rb") as f:
#             pdf_bytes = f.read()

#         parser = ResumeParser(pdf_file_bytes=pdf_bytes)
#         parsed_result = parser.parse()

#         print(json.dumps(parsed_result, ensure_ascii=False, indent=4))
#     except FileNotFoundError:
#         print(f"Ошибка: Тестовый PDF файл не найден по пути: {test_pdf_path}")
#     except Exception as e:
#         print(f"Произошла непредвиденная ошибка: {e}")
#         import traceback
#         traceback.print_exc()