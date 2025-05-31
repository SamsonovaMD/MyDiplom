// src/services/api.js
import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
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
  params.append('username', email);
  params.append('password', password);
  return apiClient.post('/login/access-token', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};

// --- Users ---
export const registerUser = (userData) => apiClient.post('/users/', userData);
export const getCurrentUser = () => apiClient.get('/users/me');
// TODO: Добавить функции для обновления пользователя, если нужно

// --- Vacancies ---
/**
 * Fetches a list of vacancies with optional filtering.
 * @param {object} params - The query parameters.
 * @param {number} [params.skip=0] - Number of items to skip.
 * @param {number} [params.limit=100] - Maximum number of items to return.
 * @param {string} [params.search_query] - Text to search in title/description.
 * @param {string} [params.work_format] - e.g., 'remote', 'hybrid', 'office'.
 * @param {string} [params.employment_type] - e.g., 'full_time', 'part_time'.
 * @param {number} [params.min_salary_from] - Minimum salary "from".
 * @returns {Promise<AxiosResponse<any>>}
 */
export const getVacancies = (params = {}) => {
  // Default skip and limit if not provided in params
  const queryParams = {
    skip: params.skip !== undefined ? params.skip : 0,
    limit: params.limit !== undefined ? params.limit : 100,
    ...params, // Add other filter params
  };
  // Remove undefined or null params to keep URL clean
  Object.keys(queryParams).forEach(key => {
    if (queryParams[key] === undefined || queryParams[key] === null || queryParams[key] === '') {
      delete queryParams[key];
    }
  });
  return apiClient.get('/vacancies/', { params: queryParams });
};

export const getVacancyById = async (vacancyId) => {
  try {
    const response = await apiClient.get(`/vacancies/${vacancyId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching vacancy ${vacancyId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

/**
 * Creates a new vacancy.
 * @param {object} vacancyData - The data for the new vacancy.
 * @param {string} vacancyData.title
 * @param {string} [vacancyData.description]
 * @param {string} [vacancyData.experience_required]
 * @param {object} [vacancyData.primary_skills] - e.g., { required: ["Python"], preferred: ["FastAPI"] }
 * @param {string[]} [vacancyData.nice_to_have_skills] - e.g., ["Docker", "Git"]
 * @param {number} vacancyData.salary_from
 * @param {number} [vacancyData.salary_to]
 * @param {string} vacancyData.work_format - e.g., 'remote'
 * @param {string} vacancyData.employment_type - e.g., 'full_time'
 * @returns {Promise<AxiosResponse<any>>}
 */

export const createVacancy = async (vacancyData) => {
  try {
    const response = await apiClient.post('/vacancies/', vacancyData);
    return response.data;
  } catch (error) {
    console.error('Error creating vacancy:', error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const deleteVacancyById = async (vacancyId) => {
  try {
    const response = await apiClient.delete(`/vacancies/${vacancyId}`);
    return response.data; // Обычно DELETE возвращает 204 No Content или удаленный объект
  } catch (error) {
    console.error(`Error deleting vacancy ${vacancyId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

// --- Resumes (for Candidates) ---
export const uploadAndParseResume = (resumeFile) => {
  const formData = new FormData();
  formData.append('file', resumeFile);
  return apiClient.post('/resumes/upload-and-parse', formData, {
    // Axios will set Content-Type to multipart/form-data automatically for FormData
  });
};

// --- Applications (for Candidates) ---
export const createApplication = (vacancyId, resumeId) => {
  return apiClient.post('/applications/', { vacancy_id: vacancyId, resume_id: resumeId });
};

export const getMyApplications = (params = {}) => {
  const queryParams = {
    skip: params.skip !== undefined ? params.skip : 0,
    limit: params.limit !== undefined ? params.limit : 100,
    ...params,
  };
  Object.keys(queryParams).forEach(key => {
    if (queryParams[key] === undefined || queryParams[key] === null || queryParams[key] === '') {
      delete queryParams[key];
    }
  });
  return apiClient.get('/applications/my/', { params: queryParams });
};

export const updateVacancyById = async (vacancyId, vacancyData) => {
  try {
    const response = await apiClient.put(`/vacancies/${vacancyId}`, vacancyData);
    return response.data;
  } catch (error) {
    console.error(`Error updating vacancy ${vacancyId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const getMyPostedVacancies = async () => {
  try {
    const response = await apiClient.get('/vacancies/my/');
    return response.data;
  } catch (error) {
    console.error("Error fetching posted vacancies:", error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const getMatchedCandidatesForVacancy = async (vacancyId) => {
  try {
    const response = await apiClient.get(`/vacancies/${vacancyId}/matched-candidates/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching matched candidates for vacancy ${vacancyId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export default apiClient;