// src/services/api.ts
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { DailyAnswers, Report } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});


// Intercepteur pour ajouter le token à chaque requête
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs et le refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si l'erreur est 401 et qu'on n'a pas déjà essayé de refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Tentative de refresh du token
        const response = await api.post('/refresh-token');
        const { token } = response.data;
        
        localStorage.setItem('token', token);
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Réessayer la requête originale avec le nouveau token
        return api(originalRequest);
      } catch (refreshError) {
        // Si le refresh échoue, déconnexion
        localStorage.removeItem('token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);


export const submitReport = async (answers: DailyAnswers): Promise<Report> => {
  const { data } = await api.post<Report>('/submit-report', { answers });
  return data;
};

export const getTodayReport = async (): Promise<Report | null> => {
  const { data } = await api.get<Report>('/get-today-report');
  return data;
};


// Fonction utilitaire pour vérifier si un token est expiré
export const isTokenExpired = (token: string): boolean => {
  try {
    const [, payload] = token.split('.');
    const decodedPayload = JSON.parse(atob(payload));
    const expirationTime = decodedPayload.exp * 1000; // Conversion en millisecondes
    return Date.now() >= expirationTime;
  } catch {
    return true;
  }
};