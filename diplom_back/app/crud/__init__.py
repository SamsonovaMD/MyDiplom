from .crud_user import (
    get_user,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    delete_user,
    authenticate_user # Добавьте эту функцию, если вы ее определили в crud_user.py
)

from .crud_vacancy import (
    get_vacancy,
    get_vacancies,
    create_vacancy,
    update_vacancy,
    delete_vacancy
)

from .crud_resume import (
    get_resume,
    get_resumes_by_candidate,
    create_resume
)

from .crud_application import (
    get_application,
    get_applications_for_vacancy,
    get_applications_by_candidate,
    create_application,
    update_application
)