// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom'; // Импортируем Router здесь
import App from './App.jsx';
import { UserProvider } from './context/UserContext.jsx';
import './index.css'; // Глобальные стили
import './App.css'; // Стили для App (можно оставить или перенести)


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Router> {/* Оборачиваем UserProvider и App в Router */}
      <UserProvider>
        <App />
      </UserProvider>
    </Router>
  </React.StrictMode>
);