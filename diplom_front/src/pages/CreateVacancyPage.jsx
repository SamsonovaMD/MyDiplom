// src/pages/CreateVacancyPage.jsx
import React, { useState, useEffect } from 'react'; // Добавили useEffect
import { useNavigate, useParams } from 'react-router-dom'; // Добавили useParams
import {
  createVacancy,
  getVacancyById,     // API-функция для получения данных вакансии
  updateVacancyById   // API-функция для обновления вакансии
} from '../services/api';
import { WORK_FORMAT_DISPLAY, EMPLOYMENT_TYPE_DISPLAY } from '../utils/translations';
import { useUser } from '../context/UserContext';
import { USER_ROLES } from '../constants';
import './CreateVacancyPage.css';

const workFormatOptions = Object.keys(WORK_FORMAT_DISPLAY);
const employmentTypeOptions = Object.keys(EMPLOYMENT_TYPE_DISPLAY);

const CreateVacancyPage = () => {
  const { vacancyId } = useParams(); // Получаем ID из URL для режима редактирования
  const navigate = useNavigate();
  const { currentUser } = useUser();

  const isEditMode = Boolean(vacancyId);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    experience_required: '',
    primary_skills_required: '',
    primary_skills_preferred: '',
    nice_to_have_skills: '',
    salary_from: '',
    salary_to: '',
    work_format: workFormatOptions[0] || '',
    employment_type: employmentTypeOptions[0] || '',
    // Не добавляем is_active и location, так как их нет в текущей форме
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [pageTitle, setPageTitle] = useState(
    isEditMode ? 'Редактирование вакансии' : 'Создание новой вакансии'
  );

  const skillsArrayToString = (skillsArray) => skillsArray ? skillsArray.join(', ') : '';

  // Загрузка данных вакансии для редактирования
  useEffect(() => {
    if (isEditMode) {
      setPageTitle('Редактирование вакансии'); // Обновляем заголовок, если в режиме редактирования
      setIsLoading(true);
      getVacancyById(vacancyId)
        .then(data => {
          setFormData({
            title: data.title || '',
            description: data.description || '',
            experience_required: data.experience_required || '',
            primary_skills_required: skillsArrayToString(data.primary_skills?.required),
            primary_skills_preferred: skillsArrayToString(data.primary_skills?.preferred),
            nice_to_have_skills: skillsArrayToString(data.nice_to_have_skills),
            salary_from: data.salary_from === null || data.salary_from === undefined ? '' : data.salary_from.toString(),
            salary_to: data.salary_to === null || data.salary_to === undefined ? '' : data.salary_to.toString(),
            work_format: data.work_format || workFormatOptions[0] || '',
            employment_type: data.employment_type || employmentTypeOptions[0] || '',
            // Убедитесь, что эти поля соответствуют тому, что возвращает ваш API
          });
        })
        .catch(err => {
          console.error("Failed to fetch vacancy for editing:", err.response || err);
          setError('Не удалось загрузить данные вакансии для редактирования.');
        })
        .finally(() => setIsLoading(false));
    }
  }, [vacancyId, isEditMode]); // Зависимости useEffect

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!currentUser || currentUser.role !== USER_ROLES.EMPLOYER) {
      setError("Только работодатели могут создавать или редактировать вакансии.");
      setIsLoading(false);
      return;
    }

    const skillsToArray = (skillsString) => skillsString ? skillsString.split(',').map(skill => skill.trim()).filter(skill => skill) : [];

    const vacancyDataPayload = {
      title: formData.title,
      description: formData.description,
      experience_required: formData.experience_required,
      primary_skills: {
        required: skillsToArray(formData.primary_skills_required),
        preferred: skillsToArray(formData.primary_skills_preferred),
      },
      nice_to_have_skills: skillsToArray(formData.nice_to_have_skills),
      salary_from: formData.salary_from ? parseInt(formData.salary_from, 10) : null,
      salary_to: formData.salary_to ? parseInt(formData.salary_to, 10) : null,
      work_format: formData.work_format,
      employment_type: formData.employment_type,
      // Не включаем is_active и location, если их нет в схемах Create/Update
      // или если они не управляются через эту форму
    };
    
    // Убираем поля, которые null, если API их не ожидает или это мешает (особенно для PUT с exclude_unset=True на бэке)
    // Однако, если бэкэнд ожидает null для сброса значений, то это не нужно.
    // Для простоты, пока оставим как есть, но это место для возможной доработки в зависимости от API.
    // Object.keys(vacancyDataPayload).forEach(key => {
    //   if (vacancyDataPayload[key] === null || vacancyDataPayload[key] === '') {
    //     delete vacancyDataPayload[key]; // Осторожно с этим, если null имеет значение для API
    //   }
    // });


    console.log(`Submitting vacancyData (${isEditMode ? 'update' : 'create'}):`, JSON.stringify(vacancyDataPayload, null, 2));

    // Валидация
    if (!vacancyDataPayload.title || vacancyDataPayload.salary_from === null || !vacancyDataPayload.work_format || !vacancyDataPayload.employment_type) {
      setError('Пожалуйста, заполните все обязательные поля: Название, Зарплата от, Формат работы, Тип занятости.');
      setIsLoading(false);
      return;
    }
    if (vacancyDataPayload.salary_to !== null && vacancyDataPayload.salary_from > vacancyDataPayload.salary_to) {
      setError('Зарплата "до" не может быть меньше зарплаты "от".');
      setIsLoading(false);
      return;
    }

    try {
      //let response; // 'response' больше не нужна, если мы не используем ее для навигации
      if (isEditMode) {
        await updateVacancyById(vacancyId, vacancyDataPayload); // response не присваиваем
        alert('Вакансия успешно обновлена!');
      } else {
        await createVacancy(vacancyDataPayload); // response не присваиваем
        alert('Вакансия успешно создана!');
      }
      
      // Всегда переходим на страницу "Мои вакансии" после успешного создания/обновления
      navigate('/my-posted-vacancies'); 

    } catch (err) {
      console.error(`Error ${isEditMode ? 'updating' : 'creating'} vacancy:`, err.response || err);
      const errorMessage = err.response?.data?.detail || `Не удалось ${isEditMode ? 'обновить' : 'создать'} вакансию. Проверьте введенные данные.`;
      
      if (Array.isArray(errorMessage)) {
        setError(errorMessage.map(e => e.msg || JSON.stringify(e)).join('; '));
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentUser || currentUser.role !== USER_ROLES.EMPLOYER) {
    return (
      <div className="create-vacancy-container status-message error-message">
        У вас нет прав для этой операции. Пожалуйста, войдите как работодатель.
      </div>
    );
  }
  
  if (isLoading && isEditMode && !formData.title) {
    return <div className="create-vacancy-container status-message">Загрузка данных вакансии...</div>;
  }

  return (
    <div className="create-vacancy-container">
      <h2>{pageTitle}</h2>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit} className="vacancy-form">
        {/* Поля формы остаются такими же, как в вашем коде */}
        <div className="form-group">
          <label htmlFor="title">Название вакансии *</label>
          <input type="text" id="title" name="title" value={formData.title} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label htmlFor="description">Описание</label>
          <textarea id="description" name="description" value={formData.description} onChange={handleChange} rows="5"></textarea>
        </div>
        <div className="form-group">
          <label htmlFor="experience_required">Требуемый опыт</label>
          <input type="text" id="experience_required" name="experience_required" value={formData.experience_required} onChange={handleChange} placeholder="Например, от 1 до 3 лет" />
        </div>
        <div className="form-group">
          <label htmlFor="salary_from">Зарплата от (RUB) *</label>
          <input type="number" id="salary_from" name="salary_from" value={formData.salary_from} onChange={handleChange} min="0" required />
        </div>
        <div className="form-group">
          <label htmlFor="salary_to">Зарплата до (RUB)</label>
          <input type="number" id="salary_to" name="salary_to" value={formData.salary_to} onChange={handleChange} min={formData.salary_from || 0} />
        </div>
        <div className="form-group">
          <label htmlFor="work_format">Формат работы *</label>
          <select id="work_format" name="work_format" value={formData.work_format} onChange={handleChange} required>
            {workFormatOptions.map(option => (
              <option key={option} value={option}>{WORK_FORMAT_DISPLAY[option]}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="employment_type">Тип занятости *</label>
          <select id="employment_type" name="employment_type" value={formData.employment_type} onChange={handleChange} required>
            {employmentTypeOptions.map(option => (
              <option key={option} value={option}>{EMPLOYMENT_TYPE_DISPLAY[option]}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="primary_skills_required">Основные навыки (обязательные, через запятую)</label>
          <input type="text" id="primary_skills_required" name="primary_skills_required" value={formData.primary_skills_required} onChange={handleChange} placeholder="Python, SQL, FastAPI"/>
        </div>
        <div className="form-group">
          <label htmlFor="primary_skills_preferred">Основные навыки (желательные, через запятую)</label>
          <input type="text" id="primary_skills_preferred" name="primary_skills_preferred" value={formData.primary_skills_preferred} onChange={handleChange} placeholder="Docker, Kubernetes"/>
        </div>
        <div className="form-group">
          <label htmlFor="nice_to_have_skills">Будет плюсом (навыки, через запятую)</label>
          <input type="text" id="nice_to_have_skills" name="nice_to_have_skills" value={formData.nice_to_have_skills} onChange={handleChange} placeholder="Git, CI/CD"/>
        </div>
        
        <button type="submit" disabled={isLoading} className="submit-button">
          {isLoading ? (isEditMode ? 'Сохранение...' : 'Создание...') : (isEditMode ? 'Сохранить изменения' : 'Создать вакансию')}
        </button>
      </form>
    </div>
  );
};

export default CreateVacancyPage;