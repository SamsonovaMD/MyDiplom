// src/pages/HomePage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import './HomePage.css'; // Создадим этот файл для стилей

// Можно вынести иконки или использовать SVG/FontAwesome если подключены
const CheckIcon = () => (
  <span role="img" aria-label="check mark" style={{ color: '#28a745', marginRight: '8px' }}>
    ✔
  </span>
);
const PartnerIcon = () => (
  <span role="img" aria-label="partner icon" style={{ color: '#007bff', marginRight: '8px' }}>
    🔹
  </span>
);
const ValueIcon = ({ emoji, label }) => (
  <span role="img" aria-label={label} style={{ marginRight: '8px' }}>
    {emoji}
  </span>
);

const HomePage = () => {
  const { currentUser } = useUser();

  return (
    <div className="home-page">
      <header className="home-header">
        <h1>NexITera – Инновационные IT-решения для цифрового будущего</h1>
        <p className="tagline">Ваш проводник в мире цифровых технологий!</p>
        {currentUser ? (
          <p className="user-greeting">
            Добро пожаловать, {currentUser.full_name || currentUser.email}! ({currentUser.role})
          </p>
        ) : (
          <div className="auth-actions">
            <Link to="/login" className="btn btn-primary">Войти</Link>
            <Link to="/register" className="btn btn-secondary">Зарегистрироваться</Link>
          </div>
        )}
         <Link to="/vacancies" className="btn btn-cta">
            Посмотреть актуальные вакансии
        </Link>
      </header>

      <section className="about-company">
        <h2>О компании</h2>
        <p>
          NexITera – это динамично развивающаяся IT-компания, специализирующаяся на разработке передовых технологических решений для бизнеса. Мы объединяем экспертизу в области искусственного интеллекта, облачных вычислений, кибербезопасности и автоматизации, чтобы помочь компаниям трансформироваться в эпоху цифровизации.
        </p>
      </section>

      <section className="services">
        <h2>Основные направления деятельности</h2>
        <ul>
          <li><CheckIcon /><strong>Разработка программного обеспечения</strong> – создание корпоративных и пользовательских решений под ключ.</li>
          <li><CheckIcon /><strong>Искусственный интеллект и машинное обучение</strong> – внедрение AI в бизнес-процессы.</li>
          <li><CheckIcon /><strong>Кибербезопасность</strong> – защита данных и инфраструктуры от современных угроз.</li>
          <li><CheckIcon /><strong>Облачные решения</strong> – миграция, оптимизация и управление облачными сервисами (AWS, Azure, GCP).</li>
          <li><CheckIcon /><strong>Аналитика больших данных</strong> – обработка и визуализация данных для принятия решений.</li>
          <li><CheckIcon /><strong>IoT и автоматизация</strong> – умные системы для промышленности и логистики.</li>
        </ul>
      </section>

      <section className="partners">
        <h2>Ключевые партнеры и клиенты</h2>
        <ul>
          <li><PartnerIcon /><strong>Корпоративный сектор:</strong> банки, телеком-операторы, ритейл.</li>
          <li><PartnerIcon /><strong>Стартапы:</strong> акселерация технологических проектов.</li>
          <li><PartnerIcon /><strong>Государственные организации:</strong> цифровизация госуслуг.</li>
          <li><PartnerIcon /><strong>Технологические гиганты:</strong> интеграция с платформами Microsoft, Google, Oracle.</li>
        </ul>
      </section>
      
      <section className="company-values">
        <h2>Наши ценности</h2>
        <div className="values-grid">
            <div className="value-item">
                <ValueIcon emoji="🚀" label="innovation" />
                <h3>Инновации</h3>
                <p>Всегда на шаг впереди.</p>
            </div>
            <div className="value-item">
                <ValueIcon emoji="🔒" label="reliability" />
                <h3>Надежность</h3>
                <p>Безопасность и стабильность решений.</p>
            </div>
            <div className="value-item">
                <ValueIcon emoji="🤝" label="partnership" />
                <h3>Партнерство</h3>
                <p>Индивидуальный подход к каждому клиенту.</p>
            </div>
        </div>
      </section>

      <footer className="home-footer">
        <h2>Контакты</h2>
        <p>🌐 <strong>Сайт:</strong> <a href="http://www.NexITera.com" target="_blank" rel="noopener noreferrer">www.NexITera.com</a></p>
        <p>📧 <strong>Email:</strong> <a href="mailto:info@NexITera.com">info@NexITera.com</a></p>
        <p>📞 <strong>Телефон:</strong> +7 (XXX) XXX-XX-XX</p>
        <p>📍 <strong>Адрес:</strong> Москва, Пресненская наб., 10</p>
        <p>💼 <strong>LinkedIn:</strong> <a href="#" target="_blank" rel="noopener noreferrer">NexITera Official</a> {/* Замени # на реальную ссылку */}</p>
      </footer>
    </div>
  );
};

export default HomePage;