// src/context/UserContext.jsx
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import apiClient, { getCurrentUser as fetchCurrentUser } from '../services/api';
import { useNavigate } from 'react-router-dom';

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const setupApiClientAuthHeader = (currentToken) => {
    if (currentToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${currentToken}`;
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
    }
  };

  const fetchUser = useCallback(async () => {
    const currentToken = localStorage.getItem('authToken');
    if (currentToken) {
      setToken(currentToken); // Убедимся, что токен в стейте
      setupApiClientAuthHeader(currentToken); // <--- Устанавливаем заголовок здесь
      try {
        const response = await fetchCurrentUser(); // Которая теперь будет использовать заголовок
        setCurrentUser(response.data);
      } catch (error) {
        console.error("Failed to fetch current user:", error);
        localStorage.removeItem('authToken');
        setToken(null);
        setCurrentUser(null);
        setupApiClientAuthHeader(null); // <--- Убираем заголовок при ошибке
        // Опционально: navigate('/login'); если токен невалиден
      }
    }
    setLoading(false);
  }, []); // navigate не нужен в зависимостях, если используется только при ошибке

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const loginContext = (userData, newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
    setCurrentUser(userData);
    setupApiClientAuthHeader(newToken); // <--- Устанавливаем заголовок при логине
  };

  const logoutContext = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setCurrentUser(null);
    setupApiClientAuthHeader(null); // <--- Используем общую функцию для удаления заголовка
    navigate('/login');
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