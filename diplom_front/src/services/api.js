// src/services/api.js
import axios from 'axios';

// ВАЖНО: Замени на URL твоего бэкенда!
// Если бэкенд запущен локально на порту 8000, и API_V1_STR = "/api/v1"
const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Перехватчик для добавления токена авторизации и Content-Type
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    // Устанавливаем Content-Type в application/json по умолчанию,
    // если это не FormData (которая сама установит multipart/form-data)
    // и не application/x-www-form-urlencoded для логина
    if (
      !(config.data instanceof FormData) &&
      config.headers['Content-Type'] !== 'application/x-www-form-urlencoded'
    ) {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Authentication ---
export const loginUser = (email, password) => {
  const params = new URLSearchParams();
  params.append('username', email); // FastAPI OAuth2PasswordRequestForm ожидает 'username'
  params.append('password', password);
  return apiClient.post('/login/access-token', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};

// --- Users ---
// userData: {email, password, full_name, role}
export const registerUser = (userData) => apiClient.post('/users/', userData);
export const getCurrentUser = () => apiClient.get('/users/me');
// TODO: Добавить функции для обновления пользователя, если нужно

// --- Vacancies ---
export const getVacancies = (skip = 0, limit = 100) =>
  apiClient.get('/vacancies/', { params: { skip, limit } });
export const getVacancyById = (id) => apiClient.get(`/vacancies/${id}`);
// TODO: Добавить функции для создания, обновления, удаления вакансий (для работодателей)
// export const createVacancy = (vacancyData) => apiClient.post('/vacancies/', vacancyData);

// --- Resumes (for Candidates) ---
export const uploadAndParseResume = (resumeFile) => {
  const formData = new FormData();
  // Имя поля 'file' должно совпадать с тем, что ожидает FastAPI: `File(..., alias="file")` или `file: UploadFile = File(...)`
  formData.append('file', resumeFile);
  return apiClient.post('/resumes/upload-and-parse', formData, {
    headers: {
      'Content-Type': 'multipart/form-data', // Axios обычно сам ставит это для FormData
    },
  });
};
export const getMyResumes = (skip = 0, limit = 10) =>
  apiClient.get('/resumes/my/', { params: { skip, limit } });

// --- Applications (for Candidates) ---
export const createApplication = (vacancyId, resumeId) => {
  return apiClient.post('/applications/', { vacancy_id: vacancyId, resume_id: resumeId });
};
export const getMyApplications = (skip = 0, limit = 100) =>
  apiClient.get('/applications/my/', { params: { skip, limit } });

// TODO: Добавить эндпоинты для работодателей (просмотр откликов на вакансию, обновление статуса и т.д.)

export default apiClient;