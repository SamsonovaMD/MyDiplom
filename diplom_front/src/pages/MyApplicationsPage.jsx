// src/pages/MyApplicationsPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMyApplications } from '../services/api';
import { useUser } from '../context/UserContext';
import { USER_ROLES, APPLICATION_STATUS_DISPLAY } from '../constants';
import './MyApplicationsPage.css';

const getApplicationStatusDisplay = (statusKey) => {
  if (!statusKey || typeof statusKey !== 'string' || statusKey.trim() === '') {
    return 'Статус не определен';
  }
  const lowerStatusKey = statusKey.toLowerCase();
  return APPLICATION_STATUS_DISPLAY[lowerStatusKey] || statusKey;
};

const MyApplicationsPage = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { currentUser } = useUser();

  useEffect(() => {
    const fetchApplications = async () => {
      if (!currentUser || currentUser.role !== USER_ROLES.CANDIDATE) {
        setError('Эта страница доступна только для кандидатов.');
        setApplications([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const response = await getMyApplications();
        // console.log("Fetched applications:", response.data); // Оставьте для отладки при необходимости
        setApplications(response.data || []);
        setError('');
      } catch (err) {
        setError(err.response?.data?.detail || 'Не удалось загрузить ваши отклики.');
        console.error("Error fetching applications:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchApplications();
  }, [currentUser]);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getResumeDisplay = (resume) => {
    if (!resume) return 'Резюме не указано';
    // Приоритет отдаем original_pdf_path, если он есть
    if (resume.original_pdf_path) return resume.original_pdf_path;
    // Затем пробуем title, если есть
    if (resume.title) return resume.title;
    // В крайнем случае ID
    return `Резюме ID: ${resume.id}`;
  };

  if (loading) return <div className="status-message">Загрузка ваших откликов...</div>;
  
  if (!currentUser || currentUser.role !== USER_ROLES.CANDIDATE) {
    // ... (код для неавторизованного или не кандидата пользователя) ...
    return (
      <div className="my-applications-container">
        <h1>Мои отклики</h1>
        <p className="status-message error-message">
          {error || <>Пожалуйста, <Link to={`/login?redirect=/my-applications`}>войдите</Link> или <Link to={`/register?role=${USER_ROLES.CANDIDATE}&redirect=/my-applications`}>зарегистрируйтесь</Link> как кандидат, чтобы просматривать отклики.</>}
        </p>
      </div>
    );
  }

  if (error && applications.length === 0) return <div className="status-message error-message">{error}</div>;

  return (
    <div className="my-applications-container">
      <h1>Мои отклики</h1>
      {error && <p className="status-message error-message list-error">{error}</p>}
      {applications.length === 0 && !loading && !error ? (
        <p>Вы еще не откликались на вакансии. <Link to="/vacancies">Найти вакансии</Link>.</p>
      ) : (
        <ul className="applications-list">
          {applications.map((app) => {
            // Определяем ключ статуса для сравнения (например, "rejected")
            // Это значение должно соответствовать ключу в вашем ApplicationStatus enum на бэкенде
            const IS_REJECTED_STATUS = 'rejected'; // Замените, если ваш ключ статуса "отклонено" другой

            return (
              <li key={app.id} className="application-item">
                <div className="application-main-info">
                  {app.vacancy && app.vacancy.title ? (
                    <Link to={`/vacancies/${app.vacancy.id}`} className="application-vacancy-title">
                      {app.vacancy.title}
                    </Link>
                  ) : (
                    <span className="application-vacancy-title-missing">
                      {app.vacancy_id ? `Вакансия ID: ${app.vacancy_id} (детали не загружены)` : 'Вакансия (детали не загружены)'}
                    </span>
                  )}
                   {app.vacancy?.employer_company_name && (
                    <p className="application-company">{app.vacancy.employer_company_name}</p>
                  )}
                </div>
                <div className="application-details">
                  <p>
                    <strong>Дата отклика:</strong> {formatDate(app.created_at)}
                  </p>
                  {/* Отображение информации о резюме */}
                  {app.resume && (
                    <p>
                      <strong>Резюме:</strong> {getResumeDisplay(app.resume)}
                    </p>
                  )}
                  <p>
                    <strong>Статус:</strong>
                    <span className={`status-badge status-${app.status?.toLowerCase().replace('_', '-')}`}>
                      {getApplicationStatusDisplay(app.status)}
                    </span>
                  </p>
                  {/* Условное отображение причины отклонения */}
                  {app.status?.toLowerCase() === IS_REJECTED_STATUS && app.match_details && app.match_details.reason_summary && (
                    <p className="rejection-reason">
                      <strong>Причина отклонения:</strong> {app.match_details.reason_summary}
                    </p>
                  )}
                  {app.match_score !== null && app.match_score !== undefined && (
                    <p>
                      <strong>Соответствие:</strong> {Math.round(app.match_score)}%
                    </p>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default MyApplicationsPage;