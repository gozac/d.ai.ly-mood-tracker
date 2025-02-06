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
  q1: string;
  q2: string;
  q3: string;
  mood: string;
}

export interface Report {
  id: number;
  date: string;
  answers: DailyAnswers;
  summary: string;
  evaluation?: string;
}