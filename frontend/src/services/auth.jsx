// src/services/auth.jsx
import axios from 'axios';
import { User } from '../types';

interface AuthResponse {
  token: string;
  user: User;
}

interface LoginCredentials {
  username: string;
  password: string;
}

export const loginUser = async (credentials: LoginCredentials): Promise<User> => {
  const { data } = await axios.post<AuthResponse>('/login', credentials);
  localStorage.setItem('token', data.token);
  return data.user;
};