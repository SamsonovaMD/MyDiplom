// src/components/Navbar.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { USER_ROLES } from '../constants'; // Импортируем константы ролей
import './Navbar.css';

const Navbar = () => {
  const { currentUser, logoutContext } = useUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    logoutContext();
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        NexITera
      </Link>
      <ul className="navbar-nav">
        <li className="nav-item">
          <Link to="/" className="nav-link">
            Главная
          </Link>
        </li>
        <li className="nav-item">
          <Link to="/vacancies" className="nav-link">
            Вакансии
          </Link>
        </li>

        {currentUser ? (
          <>
            {/* Ссылки для Кандидата */}
            {currentUser.role === USER_ROLES.CANDIDATE && (
              <>
                <li className="nav-item">
                  <Link to="/my-resumes" className="nav-link">
                    Мои резюме
                  </Link>
                </li>
                <li className="nav-item">
                  <Link to="/my-applications" className="nav-link">
                    Мои отклики
                  </Link>
                </li>
              </>
            )}

            {/* Ссылки для Работодателя */}
            {currentUser.role === USER_ROLES.EMPLOYER && (
              <>
                <li className="nav-item">
                  <Link to="/my-posted-vacancies" className="nav-link"> {/* Изменено на my-posted-vacancies для ясности */}
                    Мои вакансии
                  </Link>
                </li>
                {/* Можно добавить ссылку на создание вакансии прямо здесь */}
                <li className="nav-item">
                  <Link to="/create-vacancy" className="nav-link">
                    + Создать вакансию
                  </Link>
                </li>
              </>
            )}
            
            {/* Общая информация и кнопка выхода */}
            <li className="nav-item nav-user-info">
              <span>{currentUser.full_name || currentUser.email} ({currentUser.role})</span>
            </li>
            <li className="nav-item">
              <button onClick={handleLogout} className="nav-link button-link">
                Выйти
              </button>
            </li>
          </>
        ) : (
          <>
            <li className="nav-item">
              <Link to="/login" className="nav-link">
                Войти
              </Link>
            </li>
            <li className="nav-item">
              <Link to="/register" className="nav-link">
                Регистрация
              </Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;