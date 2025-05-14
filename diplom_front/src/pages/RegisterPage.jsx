// src/pages/RegisterPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../services/api';
import { USER_ROLES } from '../constants'; // Импортируем роли
import { useUser } from '../context/UserContext';

const RegisterPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState(USER_ROLES.CANDIDATE); // По умолчанию кандидат
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginContext, fetchUser } = useUser(); // Для автоматического логина после регистрации

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const userData = {
        full_name: fullName,
        email,
        password,
        role,
      };
      await registerUser(userData);
      // Опционально: автоматический логин после успешной регистрации
      // Для этого можно либо сразу получить токен от эндпоинта регистрации
      // Либо сделать отдельный запрос на логин. Пока просто перенаправляем.
      alert('Регистрация прошла успешно! Теперь вы можете войти.');
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации. Попробуйте снова.');
      console.error("Registration error:", err.response || err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Регистрация</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fullName">Полное имя:</label>
          <input
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Пароль:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength="8"
            required
          />
        </div>
        <div>
          <label htmlFor="role">Я:</label>
          <select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value={USER_ROLES.CANDIDATE}>Кандидат</option>
            <option value={USER_ROLES.EMPLOYER}>Работодатель</option>
          </select>
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
};

export default RegisterPage;