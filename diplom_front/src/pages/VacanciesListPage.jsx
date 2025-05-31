// src/pages/VacanciesListPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getVacancies } from '../services/api';
import { getWorkFormatDisplay, getEmploymentTypeDisplay } from '../utils/translations'; // Import helpers
import './VacanciesListPage.css';

const VacanciesListPage = () => {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchVacancies = async () => {
      try {
        setLoading(true);
        const response = await getVacancies(); // Assuming getVacancies is updated to fetch new fields
        setVacancies(response.data || []);
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

  const formatSalary = (from, to, currency) => {
    if (!from && !to) return 'Не указана';
    let salaryString = '';
    if (from) {
      salaryString += `от ${from.toLocaleString('ru-RU')}`;
    }
    if (to) {
      salaryString += ` до ${to.toLocaleString('ru-RU')}`;
    }
    return `${salaryString} ${currency || 'RUB'}`; // Default to RUB if currency not present
  };

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
              {/* Отображаем новые поля */}
              <p className="vacancy-salary">
                <strong>Зарплата:</strong> {formatSalary(vacancy.salary_from, vacancy.salary_to, vacancy.salary_currency)}
              </p>
              {vacancy.work_format && (
                <p className="vacancy-meta-item">
                  <strong>Формат:</strong> {getWorkFormatDisplay(vacancy.work_format)}
                </p>
              )}
              {vacancy.employment_type && (
                <p className="vacancy-meta-item">
                  <strong>Тип занятости:</strong> {getEmploymentTypeDisplay(vacancy.employment_type)}
                </p>
              )}
              <p className="vacancy-short-description">
                {vacancy.description?.substring(0, 100) || 'Описание отсутствует'}...
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default VacanciesListPage;