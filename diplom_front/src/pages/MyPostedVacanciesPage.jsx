// src/pages/MyPostedVacanciesPage.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate }
from 'react-router-dom'; // Для перенаправления
import {
  getMyPostedVacancies,
  getMatchedCandidatesForVacancy,
  deleteVacancyById // Импортируем новую функцию
} from '../services/api';
import { useUser } from '../context/UserContext';
import { USER_ROLES } from '../constants';
import './MyPostedVacanciesPage.css';

const MyPostedVacanciesPage = () => {
  const { currentUser } = useUser();
  const navigate = useNavigate();
  const [vacancies, setVacancies] = useState([]);
  const [selectedVacancy, setSelectedVacancy] = useState(null); // Для хранения ID вакансии, чьих кандидатов смотрим
  const [matchedCandidates, setMatchedCandidates] = useState([]);
  const [isLoadingVacancies, setIsLoadingVacancies] = useState(true);
  const [isLoadingCandidates, setIsLoadingCandidates] = useState(false);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null); 


  const fetchVacancies = useCallback(async () => {
    setIsLoadingVacancies(true);
    setError('');
    try {
      const data = await getMyPostedVacancies();
      setVacancies(data || []); // Убедимся, что data это массив
    } catch (err) {
      setError('Не удалось загрузить ваши вакансии. Пожалуйста, попробуйте позже.');
      console.error(err);
    } finally {
      setIsLoadingVacancies(false);
    }
  }, []);

  useEffect(() => {
    if (currentUser && currentUser.role === USER_ROLES.EMPLOYER) {
      fetchVacancies();
    }
  }, [currentUser, fetchVacancies]);

  const handleViewMatchedCandidates = async (vacancyId) => {
    setSelectedVacancy(vacancyId);
    setIsLoadingCandidates(true);
    setMatchedCandidates([]); // Очищаем предыдущих кандидатов
    setError('');
    try {
      const data = await getMatchedCandidatesForVacancy(vacancyId);
      setMatchedCandidates(data || []); // Убедимся, что data это массив
    } catch (err) {
      setError(`Не удалось загрузить кандидатов для вакансии ID ${vacancyId}.`);
      console.error(err);
    } finally {
      setIsLoadingCandidates(false);
    }
  };

  const handleEditVacancy = (vacancyId) => {
    navigate(`/create-vacancy/${vacancyId}`); // Перенаправляем на страницу создания/редактирования
                                            // CreateVacancyPage должна будет обработать этот ID
  };

  const handleDeleteVacancy = async (vacancyId) => {
    if (window.confirm('Вы уверены, что хотите удалить эту вакансию?')) {
      setDeletingId(vacancyId);
      setError('');
      try {
        await deleteVacancyById(vacancyId);
        setVacancies(prevVacancies => prevVacancies.filter(v => v.id !== vacancyId));
        if (selectedVacancy === vacancyId) { // Если удаляем вакансию, для которой смотрели кандидатов
            setSelectedVacancy(null);
            setMatchedCandidates([]);
        }
      } catch (err) {
        setError(`Не удалось удалить вакансию ID ${vacancyId}. Пожалуйста, попробуйте позже.`);
        console.error(err);
      } finally {
        setDeletingId(null);
      }
    }
  };

  if (!currentUser || currentUser.role !== USER_ROLES.EMPLOYER) {
    // Эта проверка дублируется ProtectedRoleRoute, но может быть полезна
    // если компонент теоретически может быть отрендерен без него.
    return <p>У вас нет доступа к этой странице.</p>;
  }

  if (isLoadingVacancies) {
    return <div className="loading-message">Загрузка ваших вакансий...</div>;
  }

  if (error && !vacancies.length) { // Если ошибка и нет вакансий для отображения
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="my-posted-vacancies-page">
        <h1>Мои опубликованные вакансии</h1>
        {error && <div className="error-message" style={{ marginBottom: '15px' }}>{error}</div>}

        {vacancies.length === 0 && !isLoadingVacancies && (
        <p>У вас пока нет опубликованных вакансий. <a href="/create-vacancy">Создать вакансию?</a></p>
        )}

        <div className="vacancies-list">
        {vacancies.map((vacancy) => (
            <div key={vacancy.id} className="vacancy-card-employer">
            <h2>{vacancy.title}</h2>
            {/* Другая информация о вакансии */}

            {/* Контейнер для всех кнопок */}
            <div className="vacancy-buttons-container">
                <button
                onClick={() => handleViewMatchedCandidates(vacancy.id)}
                disabled={isLoadingCandidates && selectedVacancy === vacancy.id}
                className="vacancy-card-button" // Общий класс для кнопок
                >
                {isLoadingCandidates && selectedVacancy === vacancy.id ? 'Загрузка...' : 'Просмотреть подходящих кандидатов'}
                </button>

                {/* Ряд для кнопок Редактировать и Удалить */}
                <div className="vacancy-actions-row">
                <button
                    onClick={() => handleEditVacancy(vacancy.id)}
                    className="vacancy-card-button" // Общий класс
                    disabled={deletingId === vacancy.id}
                >
                    Редактировать
                </button>
                <button
                    onClick={() => handleDeleteVacancy(vacancy.id)}
                    className="vacancy-card-button" // Общий класс
                    disabled={deletingId === vacancy.id}
                >
                    {deletingId === vacancy.id ? 'Удаление...' : 'Удалить'}
                </button>
                </div>
            </div>

            {selectedVacancy === vacancy.id && (
                <div className="matched-candidates-section">
                <h3>Подходящие кандидаты для "{vacancy.title}"</h3>
                {isLoadingCandidates && <div className="loading-message">Загрузка кандидатов...</div>}
                {!isLoadingCandidates && error && selectedVacancy === vacancy.id && ( /* Показываем ошибку именно для этой секции */
                    <div className="error-message">{error}</div>
                )}
                {!isLoadingCandidates && !error && matchedCandidates.length === 0 && selectedVacancy === vacancy.id && (
                    <p>Подходящих кандидатов не найдено.</p>
                )}
                {!isLoadingCandidates && !error && matchedCandidates.length > 0 && selectedVacancy === vacancy.id && (
                    <ul className="candidates-list">
                    {matchedCandidates.map((candidate) => (
                        <li key={candidate.id} className="candidate-item">
                        <h4>{candidate.full_name}</h4>
                        <p><strong>Email:</strong> {candidate.email}</p>
                        {candidate.phone && <p><strong>Телефон:</strong> {candidate.phone}</p>}
                        <p><strong>Краткий опыт:</strong> {candidate.summary || 'Не указан'}</p>
                        <p><strong>Навыки:</strong> {candidate.skills?.join(', ') || 'Не указаны'}</p>
                        </li>
                    ))}
                    </ul>
                )}
                </div>
            )}
            </div>
        ))}
        </div>
    </div>
    );
};

export default MyPostedVacanciesPage;