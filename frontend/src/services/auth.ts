// src/services/auth.ts
import axios, { AxiosInstance } from 'axios';
import { User } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

interface AuthResponse {
  message: string;
  token: string;
  user: User;
}

interface Credentials {
  username: string;
  password: string;
}

// Deprecated
export const loginUser = async (credentials: Credentials): Promise<User> => {
  const { data } = await api.post<AuthResponse>('/login', credentials);
  if (data.token) {
    localStorage.setItem('token', data.token);
    // Configurer le token dans les headers axios
    api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;
  }
  return data.user;
};


export const registerUser = async (credentials: Credentials): Promise<User> => {
  const { data } = await api.post<AuthResponse>('/register', credentials);
  if (data.token) {
    localStorage.setItem('token', data.token);
    // Configurer le token dans les headers axios
    api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;
  }
  return data.user;
};