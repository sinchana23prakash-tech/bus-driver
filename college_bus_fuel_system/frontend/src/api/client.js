import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('college_fuel_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect if we are checking setup status or attempting login
      const url = error.config ? error.config.url : '';
      if (!url.includes('/auth/login') && !url.includes('/auth/setup-status')) {
        localStorage.removeItem('college_fuel_token');
        localStorage.removeItem('college_fuel_user');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/initial-setup') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
