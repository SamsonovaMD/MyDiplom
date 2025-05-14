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

// --- Компоненты-заглушки для новых страниц ---
const MyResumesPage = () => <div><h1>Мои резюме</h1><p>Здесь будут ваши резюме.</p></div>;
const MyApplicationsPage = () => <div><h1>Мои отклики</h1><p>Здесь будут ваши отклики на вакансии.</p></div>;
const MyPostedVacanciesPage = () => <div><h1>Мои опубликованные вакансии</h1><p>Здесь будут вакансии, которые вы разместили.</p></div>;
const CreateVacancyPage = () => <div><h1>Создание новой вакансии</h1><p>Форма для создания вакансии.</p></div>;
// --- Конец заглушек ---


// Компонент для защищенных роутов по роли
const ProtectedRoleRoute = ({ children, allowedRoles }) => {
  const { currentUser, token, loading } = useUser();

  if (loading) {
    return <div>Loading user data...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!currentUser || !allowedRoles.includes(currentUser.role)) {
    // Если роль не разрешена, можно перенаправить на главную или показать сообщение
    // alert('У вас нет доступа к этой странице.'); // Не очень хороший UX
    return <Navigate to="/" replace />; // Перенаправляем на главную
  }

  return children;
};


function App() {
  const { loading } = useUser();

  if (loading) {
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
            path="/my-resumes" 
            element={
              <ProtectedRoleRoute allowedRoles={[USER_ROLES.CANDIDATE]}>
                <MyResumesPage /> 
              </ProtectedRoleRoute>
            } 
          />
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
            path="/create-vacancy" 
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