# diplom_back/app/services/matching_service.py

import re
from typing import Dict, Any, List, Optional, Tuple

from app.models.resume import Resume
from app.models.vacancy import Vacancy, WorkFormatModelEnum, EmploymentTypeModelEnum
from app.models.application import ApplicationStatus

# --- Конфигурация мэтчинга ---
WEIGHTS = {
    "experience": 20,
    "skill_required": 15,
    "skill_preferred": 7,
    "skill_nice_to_have": 3,
    "salary": 10,
    "work_format": 5,
    "employment_type": 5,
}
MATCH_THRESHOLD_PERCENT = 65.0
EXPERIENCE_DEFICIT_ALLOWED_MONTHS = 2 

# --- Вспомогательные функции ---

def normalize_skill(skill: Optional[str]) -> str:
    if not skill:
        return ""
    return skill.lower().strip()

def parse_vacancy_experience(exp_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    # (Без изменений)
    if not exp_str: return None, None
    exp_str_lower = exp_str.lower()
    if "нет опыта" in exp_str_lower or "0 лет" in exp_str_lower: return 0, 0
    min_years, max_years = None, None
    match_range = re.search(r"(?:от\s*)?(\d+)\s*(?:до|-)\s*(\d+)\s*год(?:а|лет)?", exp_str_lower)
    if match_range:
        min_years = int(match_range.group(1)); max_years = int(match_range.group(2))
        return min_years, max_years
    match_min = re.search(r"(?:от|более)\s*(\d+)\s*год(?:а|лет)?", exp_str_lower)
    if match_min:
        min_years = int(match_min.group(1))
        return min_years, None
    match_max = re.search(r"до\s*(\d+)\s*год(?:а|лет)?", exp_str_lower)
    if match_max:
        max_years = int(match_max.group(1))
        return 0, max_years
    match_exact = re.search(r"(\d+)\s*год(?:а|лет)?", exp_str_lower)
    if match_exact:
        exact_years = int(match_exact.group(1))
        return exact_years, exact_years
    return None, None

# --- Основная функция мэтчинга ---
def perform_matching_analysis(
    resume: Resume,
    vacancy: Vacancy
) -> Dict[str, Any]:
    achieved_score = 0
    max_possible_score = 0
    missing_mandatory_skills = []

    match_details_for_db = {
        "experience": {"required_str": vacancy.experience_required, "candidate_months": None, "matched": False, "score": 0, "message": ""},
        "salary": {"vacancy_from": vacancy.salary_from, "vacancy_to": vacancy.salary_to, "candidate_desired": None, "matched": False, "score": 0, "message": ""},
        "work_format": {"vacancy_format": vacancy.work_format.value if vacancy.work_format else None, "candidate_preference": None, "matched": False, "score": 0, "message": ""},
        "employment_type": {"vacancy_type": vacancy.employment_type.value if vacancy.employment_type else None, "candidate_preference": None, "matched": False, "score": 0, "message": ""},
        "skills_required": [],
        "skills_preferred": [],
        "skills_nice_to_have": [],
        "achieved_score": 0,
        "max_possible_score": 0,
        "match_percentage": 0.0,
        "reason_summary": "",
        "raw_candidate_skills": [],
    }

    if not resume.parsed_data:
        return {
            "initial_status": ApplicationStatus.SUBMITTED,
            "match_score": 0.0,
            "match_details": {"error": "Данные резюме не распарсены или отсутствуют."},
            "error_message": "Данные резюме не распарсены или отсутствуют."
        }

    parsed_resume_data = resume.parsed_data
    
    # 1. ОПЫТ (логика без изменений, как в предыдущем ответе)
    candidate_experience_months = parsed_resume_data.get("work_experience") # Это общее кол-во месяцев
    match_details_for_db["experience"]["candidate_months"] = candidate_experience_months
    
    min_req_years, max_req_years = parse_vacancy_experience(vacancy.experience_required)
    experience_criterion_met = False # Будет True, если опыт соответствует (с учетом гибкости)
                                    # или если опыт не требуется/0 лет

    if vacancy.experience_required:
        max_possible_score += WEIGHTS["experience"] # Балл за опыт всегда учитывается в max, если требование есть
        
        min_req_months_for_comparison = None
        if min_req_years is not None:
            min_req_months_for_comparison = min_req_years * 12

        if candidate_experience_months is not None:
            # Логика соответствия опыта
            if min_req_months_for_comparison is None or min_req_months_for_comparison == 0:
                # Если опыт не требуется или "от 0 лет", любой опыт кандидата (даже None) подходит
                experience_criterion_met = True
                match_details_for_db["experience"]["message"] = "Опыт соответствует (требуется 0 лет или не указан)."
            elif candidate_experience_months >= min_req_months_for_comparison:
                # Опыт кандидата больше или равен требуемому минимуму
                experience_criterion_met = True
                match_details_for_db["experience"]["message"] = "Опыт соответствует."
            elif (min_req_months_for_comparison - candidate_experience_months) <= EXPERIENCE_DEFICIT_ALLOWED_MONTHS:
                # Опыт кандидата чуть меньше, но в рамках допустимого дефицита
                experience_criterion_met = True # Считаем, что для авто-фильтра это ОК
                match_details_for_db["experience"]["message"] = (
                    f"Опыт кандидата (~{(candidate_experience_months / 12):.1f} лет) немного ниже требуемого "
                    f"({vacancy.experience_required}), но в пределах допустимого дефицита "
                    f"({EXPERIENCE_DEFICIT_ALLOWED_MONTHS} мес.). Считаем соответствующим."
                )
            else:
                # Опыт кандидата значительно меньше требуемого (даже с учетом дефицита)
                experience_criterion_met = False
                match_details_for_db["experience"]["message"] = (
                    f"Опыт кандидата (~{(candidate_experience_months / 12):.1f} лет) ниже требуемого "
                    f"({vacancy.experience_required}) с учетом допустимого дефицита."
                )

            # Начисление баллов за опыт, если критерий выполнен
            if experience_criterion_met:
                achieved_score += WEIGHTS["experience"]
                match_details_for_db["experience"]["matched"] = True
                match_details_for_db["experience"]["score"] = WEIGHTS["experience"]

        else: # candidate_experience_months is None (опыт у кандидата не указан в резюме)
            if min_req_months_for_comparison is None or min_req_months_for_comparison == 0:
                # Если опыт не требуется или "от 0 лет", то отсутствие опыта у кандидата - ОК
                experience_criterion_met = True
                match_details_for_db["experience"]["message"] = "Опыт не требуется / 0 лет, у кандидата не указан. Считаем соответствующим."
                # Можно дать баллы, если опыт не требовался, а кандидат не указал (нейтрально)
                achieved_score += WEIGHTS["experience"] # Даем баллы, так как требование "0 лет" выполнено
                match_details_for_db["experience"]["matched"] = True
                match_details_for_db["experience"]["score"] = WEIGHTS["experience"]
            else:
                # Если опыт требовался (больше 0), а у кандидата не указан - это не соответствует
                experience_criterion_met = False
                match_details_for_db["experience"]["message"] = (
                    f"Требуется опыт ({vacancy.experience_required}), но у кандидата он не указан."
                )
    else: # vacancy.experience_required is None (в вакансии опыт не указан)
        match_details_for_db["experience"]["message"] = "Опыт не требуется вакансией. Считаем соответствующим."
        experience_criterion_met = True
        # Если опыт не требуется вакансией, можно добавить кандидату баллы за этот критерий,
        # так как он "соответствует" отсутствию требования
        max_possible_score += WEIGHTS["experience"] # Добавляем в max, чтобы не искажать процент
        achieved_score += WEIGHTS["experience"]
        match_details_for_db["experience"]["matched"] = True
        match_details_for_db["experience"]["score"] = WEIGHTS["experience"]


    # 2. ЗАРПЛАТА (логика без изменений, как в предыдущем ответе)
    desired_salary_data = parsed_resume_data.get("desired_salary") # Это будет dict или None
    candidate_desired_amount = None
    if isinstance(desired_salary_data, dict):
        candidate_desired_amount = desired_salary_data.get("amount")
        # Можно также учесть currency, если это важно и вакансия имеет другую валюту, но пока упростим

    match_details_for_db["salary"]["candidate_desired_data"] = desired_salary_data # Сохраняем всю структуру
    match_details_for_db["salary"]["candidate_desired_amount_extracted"] = candidate_desired_amount

    if vacancy.salary_from is not None: # Если в вакансии указана зарплата (хотя бы "от")
        max_possible_score += WEIGHTS["salary"]
        salary_matched_for_points = False # Флаг, давать ли баллы

        if candidate_desired_amount is None:
            # ПРАВИЛО 1: Кандидат не указал ожидания - считаем совпадением
            match_details_for_db["salary"]["message"] = "Кандидат не указал зарплатные ожидания. Считаем совпадением."
            salary_matched_for_points = True
        else:
            # ПРАВИЛО 2: Кандидат указал ожидания
            if vacancy.salary_to is not None: # Есть вилка "от" и "до"
                if candidate_desired_amount <= vacancy.salary_to: # Ожидания кандидата не превышают ВЕРХНЮЮ границу вакансии
                    # Дополнительно проверяем, что ожидания не НИЖЕ нижней границы, если это важно
                    if candidate_desired_amount >= vacancy.salary_from:
                         match_details_for_db["salary"]["message"] = f"Ожидания ({candidate_desired_amount}) в рамках вилки вакансии ({vacancy.salary_from} - {vacancy.salary_to})."
                         salary_matched_for_points = True
                    else: # Ожидания ниже вилки - тоже считаем совпадением по вашему правилу
                         match_details_for_db["salary"]["message"] = f"Ожидания ({candidate_desired_amount}) ниже вилки вакансии ({vacancy.salary_from} - {vacancy.salary_to}). Считаем совпадением."
                         salary_matched_for_points = True
                else:
                    match_details_for_db["salary"]["message"] = f"Ожидания кандидата ({candidate_desired_amount}) ВЫШЕ вилки вакансии ({vacancy.salary_from} - {vacancy.salary_to}). Не совпадает."
                    salary_matched_for_points = False
            else: # Есть только "от" (vacancy.salary_from)
                if candidate_desired_amount <= vacancy.salary_from: # Ожидания кандидата МЕНЬШЕ ИЛИ РАВНЫ предложению вакансии
                    match_details_for_db["salary"]["message"] = f"Ожидания кандидата ({candidate_desired_amount}) не превышают предложение вакансии (от {vacancy.salary_from}). Считаем совпадением."
                    salary_matched_for_points = True
                else: # Ожидания выше, чем "от"
                    match_details_for_db["salary"]["message"] = f"Ожидания кандидата ({candidate_desired_amount}) ВЫШЕ предложения вакансии (от {vacancy.salary_from}). Не совпадает."
                    salary_matched_for_points = False
        
        if salary_matched_for_points:
            achieved_score += WEIGHTS["salary"]
            match_details_for_db["salary"]["matched"] = True
            match_details_for_db["salary"]["score"] = WEIGHTS["salary"]
            # Сообщение уже установлено выше
    else: # В вакансии не указана зарплата
        match_details_for_db["salary"]["message"] = "В вакансии не указана зарплата. Считаем нейтральным (не влияет на балл)."


    # 3. ФОРМАТ РАБОТЫ (логика без изменений, как в предыдущем ответе)
    candidate_pref_work_format = normalize_skill(parsed_resume_data.get("preferred_work_format"))
    match_details_for_db["work_format"]["candidate_preference"] = candidate_pref_work_format
    if vacancy.work_format:
        max_possible_score += WEIGHTS["work_format"]
        vacancy_work_format_value = vacancy.work_format.value
        if not candidate_pref_work_format:
            match_details_for_db["work_format"]["message"] = "Кандидат не указал формат. Считаем приемлемым."
            achieved_score += WEIGHTS["work_format"]
            match_details_for_db["work_format"]["matched"] = True
            match_details_for_db["work_format"]["score"] = WEIGHTS["work_format"]
        elif candidate_pref_work_format == vacancy_work_format_value:
            achieved_score += WEIGHTS["work_format"]
            match_details_for_db["work_format"]["matched"] = True
            match_details_for_db["work_format"]["score"] = WEIGHTS["work_format"]
            match_details_for_db["work_format"]["message"] = "Формат работы совпадает."
        else:
            match_details_for_db["work_format"]["message"] = f"Формат вакансии ({vacancy_work_format_value}) не совпадает с ({candidate_pref_work_format})."
    else:
        match_details_for_db["work_format"]["message"] = "В вакансии не указан формат работы."


    # 4. ТИП ЗАНЯТОСТИ (логика без изменений, как в предыдущем ответе)
    candidate_pref_emp_type = normalize_skill(parsed_resume_data.get("preferred_employment_type"))
    match_details_for_db["employment_type"]["candidate_preference"] = candidate_pref_emp_type
    if vacancy.employment_type:
        max_possible_score += WEIGHTS["employment_type"]
        vacancy_emp_type_value = vacancy.employment_type.value
        if not candidate_pref_emp_type:
            match_details_for_db["employment_type"]["message"] = "Кандидат не указал тип занятости. Считаем приемлемым."
            achieved_score += WEIGHTS["employment_type"]
            match_details_for_db["employment_type"]["matched"] = True
            match_details_for_db["employment_type"]["score"] = WEIGHTS["employment_type"]
        elif candidate_pref_emp_type == vacancy_emp_type_value:
            achieved_score += WEIGHTS["employment_type"]
            match_details_for_db["employment_type"]["matched"] = True
            match_details_for_db["employment_type"]["score"] = WEIGHTS["employment_type"]
            match_details_for_db["employment_type"]["message"] = "Тип занятости совпадает."
        else:
            match_details_for_db["employment_type"]["message"] = f"Тип занятости вакансии ({vacancy_emp_type_value}) не совпадает с ({candidate_pref_emp_type})."
    else:
        match_details_for_db["employment_type"]["message"] = "В вакансии не указан тип занятости."


    # 5. НАВЫКИ (измененная логика без SKILL_GROUPS, используется подстрока)
    candidate_skills_raw = parsed_resume_data.get("skils", [])
    match_details_for_db["raw_candidate_skills"] = candidate_skills_raw
    
    # Нормализуем навыки кандидата один раз
    candidate_skills_normalized_list = [normalize_skill(s) for s in candidate_skills_raw if normalize_skill(s)]

    skill_categories = {
        "skills_required": (vacancy.primary_skills.get("required", []) if vacancy.primary_skills else [], WEIGHTS["skill_required"]),
        "skills_preferred": (vacancy.primary_skills.get("preferred", []) if vacancy.primary_skills else [], WEIGHTS["skill_preferred"]),
        "skills_nice_to_have": (vacancy.nice_to_have_skills or [], WEIGHTS["skill_nice_to_have"]),
    }

    for category_name, (skills_list_from_vacancy, weight) in skill_categories.items():
        for skill_from_vacancy_raw in skills_list_from_vacancy:
            norm_skill_vacancy = normalize_skill(skill_from_vacancy_raw)
            if not norm_skill_vacancy: continue

            max_possible_score += weight # Добавляем к максимально возможному баллу в любом случае
            
            skill_found_in_candidate = False
            matched_candidate_skill_for_log = None # Для логгирования, какой навык кандидата подошел

            for norm_skill_candidate in candidate_skills_normalized_list:
                # Проверяем, является ли нормализованный навык из ВАКАНСИИ
                # подстрокой нормализованного навыка из РЕЗЮМЕ
                if norm_skill_vacancy in norm_skill_candidate:
                    skill_found_in_candidate = True
                    matched_candidate_skill_for_log = norm_skill_candidate
                    break # Нашли совпадение для этого навыка вакансии, переходим к следующему навыку вакансии
            
            detail = {
                "skill": skill_from_vacancy_raw, 
                "matched": skill_found_in_candidate, 
                "score": 0
            }
            if matched_candidate_skill_for_log:
                detail["matched_with"] = matched_candidate_skill_for_log
            
            if skill_found_in_candidate:
                achieved_score += weight
                detail["score"] = weight
            elif category_name == "skills_required": # Если обязательный навык не найден
                missing_mandatory_skills.append(skill_from_vacancy_raw)
            
            match_details_for_db[category_name].append(detail)


    # 6. Расчет процента и определение статуса
    # (логика без изменений, как в предыдущем ответе)
    match_percentage_calc = 0.0
    if max_possible_score > 0:
        match_percentage_calc = (achieved_score / max_possible_score) * 100
    elif achieved_score > 0: # Нет требований в вакансии, но есть навыки у кандидата
        match_percentage_calc = 100.0
    # Если max_possible_score == 0 и achieved_score == 0, то 0% 
    # (или 100% если считать, что "ничего не требуется - ничего нет" = идеально, но 0% более консервативно)
    if max_possible_score == 0: # Кейс, когда вакансия вообще без требований к скорингу
        match_percentage_calc = 100.0 if achieved_score > 0 else 0.0

    recommended_status = ApplicationStatus.SUBMITTED # Дефолтный статус
    reason_summary = ""

    # --- ПРОВЕРКИ ДЛЯ ОТКАЗА ---
    if missing_mandatory_skills:
        recommended_status = ApplicationStatus.REJECTED
        reason_summary = f"Отсутствуют обязательные навыки: {', '.join(missing_mandatory_skills)}."
    
    elif vacancy.experience_required and \
         (min_req_years is not None and min_req_years > 0) and \
         not experience_criterion_met:
        
        recommended_status = ApplicationStatus.REJECTED
        # Используем уже сформированное сообщение из деталей опыта
        reason_summary = match_details_for_db["experience"]["message"] 

    # Приоритет 3 (если предыдущие не сработали): Низкий общий процент совпадения
    else:
        if match_percentage_calc >= MATCH_THRESHOLD_PERCENT:
            recommended_status = ApplicationStatus.UNDER_REVIEW # Прошел авто-фильтр
            reason_summary = f"Процент совпадения ({match_percentage_calc:.2f}%) соответствует порогу."
        else:
            recommended_status = ApplicationStatus.REJECTED # Не прошел по общему порогу
            reason_summary = f"Процент совпадения ({match_percentage_calc:.2f}%) ниже порога ({MATCH_THRESHOLD_PERCENT}%)."
            if max_possible_score == 0 and achieved_score == 0 and not reason_summary: # Если вакансия "пустая" и кандидат тоже
                reason_summary = "Специфических требований в вакансии и навыков у кандидата не указано для автоматической оценки."
                # В этом случае, возможно, лучше не REJECTED, а SUBMITTED или UNDER_REVIEW для ручного просмотра,
                # так как автоматика не смогла ничего оценить. Но для консистентности с "ниже порога" можно оставить REJECTED.
                # Давайте изменим на SUBMITTED, если порог не пройден из-за нулевых скоров при пустой вакансии.
                if match_percentage_calc < MATCH_THRESHOLD_PERCENT : # Уточняем это условие
                     recommended_status = ApplicationStatus.SUBMITTED # Для ручного разбора

    # Запись финальных результатов в детали
    match_details_for_db["achieved_score"] = achieved_score
    match_details_for_db["max_possible_score"] = max_possible_score
    match_details_for_db["match_percentage"] = round(match_percentage_calc, 2)
    match_details_for_db["reason_summary"] = reason_summary
    match_details_for_db["evaluated_status_by_system"] = recommended_status.value # Сохраняем строковое значение Enum

    return {
        "initial_status": recommended_status,
        "match_score": round(match_percentage_calc, 2), # Это пойдет в Application.match_score
        "match_details": match_details_for_db, # Это пойдет в Application.match_details (JSONB)
        "error_message": None
    }