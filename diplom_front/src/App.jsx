// src/App.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import VacanciesListPage from './pages/VacanciesListPage';
import VacancyDetailPage from './pages/VacancyDetailPage';
import Navbar from './components/Navbar';
import { useUser } from './context/UserContext';
import { USER_ROLES } from './constants';

// --- Импорт новых страниц ---
import MyApplicationsPage from './pages/MyApplicationsPage';
import MyPostedVacanciesPage from './pages/MyPostedVacanciesPage';
import CreateVacancyPage from './pages/CreateVacancyPage';
// --- Конец импорта новых страниц ---

// Компонент для защищенных роутов по роли
// Оставляем ProtectedRoleRoute здесь или переносим в src/components/, как обсуждали ранее
const ProtectedRoleRoute = ({ children, allowedRoles }) => {
  const { currentUser, token, loading } = useUser();

  if (loading && !currentUser && token) { // Уточнено условие loading, чтобы не показывать "Loading user data..." если пользователь уже загружен
    return <div>Loading user data...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!currentUser || !allowedRoles.includes(currentUser.role)) {
    return <Navigate to="/" replace />;
  }
  return children;
};

function App() {
  const { loading: userContextLoading, currentUser, token } = useUser(); // Переименовал loading для ясности

  // Показываем глобальный лоадер только при самой первой загрузке приложения,
  // пока не определился статус токена или первоначальная загрузка пользователя.
  // ProtectedRoleRoute будет обрабатывать loading для данных пользователя на уровне роута.
  if (userContextLoading && !currentUser && localStorage.getItem('authToken')) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Загрузка приложения...
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/vacancies" element={<VacanciesListPage />} />
          <Route path="/vacancies/:vacancyId" element={<VacancyDetailPage />} />
          
          {/* Роуты для Кандидата */}
          <Route 
            path="/my-applications" 
            element={
              <ProtectedRoleRoute allowedRoles={[USER_ROLES.CANDIDATE]}>
                <MyApplicationsPage /> 
              </ProtectedRoleRoute>
            } 
          />
          
          {/* Роуты для Работодателя */}
          <Route 
            path="/my-posted-vacancies" 
            element={
              <ProtectedRoleRoute allowedRoles={[USER_ROLES.EMPLOYER]}>
                <MyPostedVacanciesPage /> 
              </ProtectedRoleRoute>
            } 
          />
          <Route
            path="/create-vacancy/:vacancyId?" // vacancyId опциональный
            element={
              <ProtectedRoleRoute allowedRoles={[USER_ROLES.EMPLOYER]}>
                <CreateVacancyPage />
              </ProtectedRoleRoute>
            }
          />
        
          <Route path="*" element={<Navigate to="/" replace />} /> 
        </Routes>
      </main>
    </>
  );
}

export default App;