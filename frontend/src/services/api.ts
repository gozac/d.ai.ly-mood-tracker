// src/services/api.ts
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { DailyAnswers, Report, Objective } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
//const isDevelopment = process.env.NODE_ENV === 'development';

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Authorization': axios.defaults.headers.common['Authorization'],
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Same-site': 'None; Secure',
    'Access-Control-Request-Private-Network': 'true',
  }
});


// Intercepteur pour ajouter le token à chaque requête
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    config.withCredentials = true;
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
    // if (error.message?.includes('mixed content')) {
    //   console.warn('Mixed content error detected, using private network URL');
    //   // Retry the request with explicit HTTP
    //   const retryConfig = {
    //     ...error.config,
    //     url: error.config?.url?.replace('https://', 'http://')
    //   };
    //   return axios(retryConfig);
    // }

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


interface ObjResponse {
  message: string;
  goal: Objective;
}

export const fetchUserObjectives = async (): Promise<Objective[]> => {
  try {
    const { data } = await api.get<Objective[]>('/get-goals');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Erreur lors de la récupération des objectifs', error);
    return [];
  }
};

export const createObjective = async (objective: Omit<Objective, 'id'>): Promise<Objective> => {
  try {
    const { data } = await api.post<ObjResponse>('/add-goal', { objective });
    return data.goal;
  } catch (error) {
    console.error('Erreur lors de la création de l\'objectif', error);
    throw error;
  }
};

export const updateObjective = async (id: string, objective: Partial<Objective>): Promise<Objective> => {
  try {
    const { data } = await api.post<Objective>(`/update-goal/${id}`, { objective });
    return data;
  } catch (error) {
    console.error('Erreur lors de la mise à jour de l\'objectif', error);
    throw error;
  }
};

export const deleteObjective = async (id: string): Promise<void> => {
  try {
    await api.delete(`/delete-goal/${id}`);
  } catch (error) {
    console.error('Erreur lors de la suppression de l\'objectif', error);
    throw error;
  }
};


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