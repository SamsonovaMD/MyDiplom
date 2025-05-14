// src/constants.js

export const USER_ROLES = {
  CANDIDATE: 'candidate',
  EMPLOYER: 'employer',
  ADMIN: 'admin',
};

export const APPLICATION_STATUS_DISPLAY = {
  submitted: 'Подана',
  viewed: 'Просмотрена',
  under_review: 'На рассмотрении',
  shortlisted: 'В шорт-листе',
  rejected: 'Отклонена',
  invited_to_interview: 'Приглашен(а) на собеседование',
  hired: 'Принят(а) на работу',
  // Добавь другие статусы из твоего enum ApplicationStatus, если они есть
};