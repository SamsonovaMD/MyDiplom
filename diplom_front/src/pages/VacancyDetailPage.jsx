// src/pages/VacancyDetailPage.jsx
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVacancyById, uploadAndParseResume, createApplication } from '../services/api';
import { useUser } from '../context/UserContext';
import { USER_ROLES } from '../constants';
import { getWorkFormatDisplay, getEmploymentTypeDisplay } from '../utils/translations'; // Import helpers
import './VacancyDetailPage.css';

const VacancyDetailPage = () => {
  const { vacancyId } = useParams();
  const { currentUser } = useUser();
  // const navigate = useNavigate(); // Not used, can be removed if not needed for other logic
  const [vacancy, setVacancy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [selectedFile, setSelectedFile] = useState(null);
  const [isApplying, setIsApplying] = useState(false);
  const [applyError, setApplyError] = useState('');
  const [applySuccess, setApplySuccess] = useState('');

  useEffect(() => {
    const fetchVacancy = async () => {
      try {
        setLoading(true);
        const response = await getVacancyById(vacancyId);
        setVacancy(response);
        setError('');
      } catch (err) {
        setError(err.response?.data?.detail || `Не удалось загрузить детали вакансии ${vacancyId}.`);
        console.error("Error fetching vacancy details:", err);
      } finally {
        setLoading(false);
      }
    };
    if (vacancyId) {
      fetchVacancy();
    }
  }, [vacancyId]);

  const formatSalaryDetail = (from, to, currency) => {
    if (!from && !to) return 'Не указана';
    let salaryString = '';
    if (from) {
      salaryString += `от ${from.toLocaleString('ru-RU')}`;
    }
    if (to) {
      salaryString += ` до ${to.toLocaleString('ru-RU')}`;
    }
    return `${salaryString} ${currency || 'RUB'}`; // Backend VacancySchema should provide 'RUB'
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setApplyError('');
    setApplySuccess('');
  };

  const handleApply = async () => {
    // ... (existing handleApply logic remains the same)
    if (!selectedFile) {
      setApplyError('Пожалуйста, выберите PDF файл вашего резюме.');
      return;
    }
    if (!currentUser || currentUser.role !== USER_ROLES.CANDIDATE) {
      setApplyError('Только кандидаты могут откликаться на вакансии.');
      return;
    }
    setIsApplying(true);
    setApplyError('');
    setApplySuccess('');
    try {
      const resumeResponse = await uploadAndParseResume(selectedFile);
      const resumeId = resumeResponse.data.id;
      if (!resumeId) {
        throw new Error("Не удалось получить ID резюме после загрузки.");
      }
      await createApplication(vacancyId, resumeId);
      setApplySuccess('Вы успешно откликнулись на вакансию!');
      setSelectedFile(null);
      if (document.getElementById('resume-upload-input')) {
        document.getElementById('resume-upload-input').value = "";
      }
    } catch (err) {
      console.error("Error applying to vacancy:", err.response || err);
      setApplyError(err.response?.data?.detail || err.message || 'Ошибка при отклике. Попробуйте снова.');
    } finally {
      setIsApplying(false);
    }
  };


  if (loading) return <div className="status-message">Загрузка деталей вакансии...</div>;
  if (error) return <div className="status-message error-message">{error}</div>;
  if (!vacancy) return <div className="status-message">Вакансия не найдена.</div>;

  const canApply = currentUser && currentUser.role === USER_ROLES.CANDIDATE;

  return (
    <div className="vacancy-detail-container">
      <Link to="/vacancies" className="back-link">&larr; К списку вакансий</Link>
      <h2>{vacancy.title}</h2>
      
      <div className="vacancy-meta">
        { (vacancy.salary_from || vacancy.salary_to) &&
            <p><strong>Зарплата:</strong> {formatSalaryDetail(vacancy.salary_from, vacancy.salary_to, vacancy.salary_currency)}</p>
        }
        {vacancy.work_format && (
            <p><strong>Формат работы:</strong> {getWorkFormatDisplay(vacancy.work_format)}</p>
        )}
        {vacancy.employment_type && (
            <p><strong>Тип занятости:</strong> {getEmploymentTypeDisplay(vacancy.employment_type)}</p>
        )}
        <p><strong>Требуемый опыт:</strong> {vacancy.experience_required || 'Не указан'}</p>
      </div>
      
      <div className="vacancy-section">
        <h3>Описание вакансии:</h3>
        <p>{vacancy.description || 'Описание отсутствует.'}</p>
      </div>

      {vacancy.primary_skills && (
        <div className="vacancy-section">
          <h3>Основные навыки:</h3>
          {typeof vacancy.primary_skills === 'object' && vacancy.primary_skills !== null ? (
            <>
              {vacancy.primary_skills.required && vacancy.primary_skills.required.length > 0 && (
                <p><strong>Обязательно:</strong> {vacancy.primary_skills.required.join(', ')}</p>
              )}
              {vacancy.primary_skills.preferred && vacancy.primary_skills.preferred.length > 0 && (
                <p><strong>Желательно:</strong> {vacancy.primary_skills.preferred.join(', ')}</p>
              )}
            </>
          ) : typeof vacancy.primary_skills === 'string' ? (
             <p>{vacancy.primary_skills}</p> // Fallback if it's a simple string
          ) : null}
        </div>
      )}

      {vacancy.nice_to_have_skills && vacancy.nice_to_have_skills.length > 0 && (
         <div className="vacancy-section">
          <h3>Будет плюсом:</h3>
          <p>{vacancy.nice_to_have_skills.join(', ')}</p>
        </div>
      )}

      {/* Apply Section and Auth Prompts remain the same */}
      {canApply && (
        <div className="apply-section">
          <h3>Откликнуться на вакансию</h3>
          <input 
            type="file" 
            id="resume-upload-input"
            accept=".pdf" 
            onChange={handleFileChange} 
            disabled={isApplying} 
          />
          <button onClick={handleApply} disabled={isApplying || !selectedFile}>
            {isApplying ? 'Отправка...' : 'Отправить резюме и откликнуться'}
          </button>
          {applyError && <p className="error-message apply-message">{applyError}</p>}
          {applySuccess && <p className="success-message apply-message">{applySuccess}</p>}
        </div>
      )}
      {!currentUser && (
        <p className="auth-prompt">
          Пожалуйста, <Link to={`/login?redirect=/vacancies/${vacancyId}`}>войдите</Link> или <Link to={`/register?role=${USER_ROLES.CANDIDATE}&redirect=/vacancies/${vacancyId}`}>зарегистрируйтесь</Link> как кандидат, чтобы откликнуться.
        </p>
      )}
      {currentUser && currentUser.role !== USER_ROLES.CANDIDATE && (
         <p className="auth-prompt">Только кандидаты могут откликаться на эту вакансию.</p>
      )}
    </div>
  );
};

export default VacancyDetailPage;