# diplom_back/app/schemas/__init__.py
from .user import UserBase, UserCreate, UserUpdate, UserSchema, UserInDB 
from .token import Token, TokenPayload
from .vacancy import VacancyBase, VacancyCreate, VacancyUpdate, VacancySchema
from .resume import ResumeBase, ResumeCreate, ResumeSchema
from .application import ApplicationBase, ApplicationCreate, ApplicationUpdate, ApplicationSchema
from .matching import MatchedCandidateSchema
# Позже сюда добавятся схемы для Vacancy, Resume, Application