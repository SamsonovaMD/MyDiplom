// src/pages/VacanciesListPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getVacancies } from '../services/api';
import './VacanciesListPage.css'; // Создадим файл стилей

const VacanciesListPage = () => {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchVacancies = async () => {
      try {
        setLoading(true);
        const response = await getVacancies();
        setVacancies(response.data || []); // Убедимся, что это массив
        setError('');
      } catch (err) {
        setError(err.response?.data?.detail || 'Не удалось загрузить вакансии.');
        console.error("Error fetching vacancies:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchVacancies();
  }, []);

  if (loading) return <div className="status-message">Загрузка вакансий...</div>;
  if (error) return <div className="status-message error-message">{error}</div>;

  return (
    <div className="vacancies-list-container">
      <h2>Список вакансий</h2>
      {vacancies.length === 0 ? (
        <p>Вакансий пока нет.</p>
      ) : (
        <ul className="vacancies-list">
          {vacancies.map((vacancy) => (
            <li key={vacancy.id} className="vacancy-item">
              <Link to={`/vacancies/${vacancy.id}`} className="vacancy-link">
                <h3>{vacancy.title}</h3>
              </Link>
              {/* Можно добавить краткое описание или компанию, если есть в vacancy.data */}
              <p className="vacancy-company">{vacancy.company_name || 'Компания не указана'}</p>
              <p className="vacancy-short-description">
                {vacancy.description?.substring(0, 150) || 'Описание отсутствует'}...
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default VacanciesListPage;