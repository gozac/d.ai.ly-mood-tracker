// src/services/api.jsx
import axios, { AxiosInstance } from 'axios';
import { DailyAnswers, Report } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const submitReport = async (answers: DailyAnswers): Promise<Report> => {
  const { data } = await api.post<Report>('/submit-report', { answers });
  return data;
};

export const getTodayReport = async (): Promise<Report | null> => {
  const { data } = await api.get<Report>('/get-today-report');
  return data;
};