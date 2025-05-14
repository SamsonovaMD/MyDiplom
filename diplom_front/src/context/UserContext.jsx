// src/context/UserContext.jsx
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import apiClient, { getCurrentUser as fetchCurrentUser } from '../services/api'; // Импорт функции API
import { useNavigate } from 'react-router-dom';

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [loading, setLoading] = useState(true); // Для начальной загрузки пользователя
  const navigate = useNavigate();

  const fetchUser = useCallback(async () => {
    const currentToken = localStorage.getItem('authToken');
    if (currentToken) {
      setToken(currentToken); // Убедимся, что токен в стейте
      try {
        const response = await fetchCurrentUser();
        setCurrentUser(response.data);
      } catch (error) {
        console.error("Failed to fetch current user:", error);
        localStorage.removeItem('authToken');
        setToken(null);
        setCurrentUser(null);
        // Опционально: navigate('/login'); если токен невалиден
      }
    }
    setLoading(false);
  }, []);


  useEffect(() => {
    fetchUser();
  }, [fetchUser]); // Зависимость fetchUser, т.к. она создается через useCallback

  const loginContext = (userData, newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
    setCurrentUser(userData); // userData должен приходить из /users/me после логина
  };

  const logoutContext = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setCurrentUser(null);
    delete apiClient.defaults.headers.common['Authorization']; // Удаляем заголовок из axios
    navigate('/login'); // Перенаправляем на страницу логина
  };

  return (
    <UserContext.Provider value={{ currentUser, token, loginContext, logoutContext, loading, setCurrentUser, setToken, fetchUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};