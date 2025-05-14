// src/pages/LoginPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { loginUser, getCurrentUser } from '../services/api';
import { useUser } from '../context/UserContext';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { loginContext, currentUser, token } = useUser();

  const redirectPath = location.state?.from?.pathname || '/';

  useEffect(() => {
    // Если пользователь уже залогинен (например, открыл страницу логина в новой вкладке)
    if (currentUser && token) {
      navigate(redirectPath, { replace: true });
    }
  }, [currentUser, token, navigate, redirectPath]);


  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const loginResponse = await loginUser(email, password);
      const newToken = loginResponse.data.access_token;
      if (newToken) {
        localStorage.setItem('authToken', newToken); // Сохраняем токен перед getCurrentUser
        
        // Получаем данные пользователя
        const userDetailsResponse = await getCurrentUser();
        loginContext(userDetailsResponse.data, newToken); // Обновляем контекст
        
        navigate(redirectPath, { replace: true }); // Перенаправляем
      } else {
        setError('Не удалось получить токен.');
      }
    } catch (err) {
      console.error("Login error:", err.response || err);
      setError(err.response?.data?.detail || 'Ошибка входа. Проверьте email и пароль.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Вход</h2>
      <form onSubmit={handleSubmit}>
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
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Вход...' : 'Войти'}
        </button>
      </form>
      <p>
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </p>
    </div>
  );
};

export default LoginPage;