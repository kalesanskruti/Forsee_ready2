import axios from 'axios';

// Create a centralized Axios instance
export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Inject JWT token if available
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('forsee_access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Clear token and redirect to login
            localStorage.removeItem('forsee_access_token');
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);
