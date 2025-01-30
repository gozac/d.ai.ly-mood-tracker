// src/types/index.ts
export interface User {
  id: number;
  username: string;
}

export interface Question {
  id: string;
  text: string;
}

export interface DailyAnswers {
  [key: string]: string;
}

export interface Report {
  id: number;
  date: string;
  answers: DailyAnswers;
  summary: string;
  evaluation?: string;
}