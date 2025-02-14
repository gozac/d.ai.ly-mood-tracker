// src/types/index.ts
export interface User {
  id: number;
  username: string;
}


// Deprecated
export interface Question {
  id: string;
  text: string;
}

export interface Objective {
  id: string;
  title: string;
  isCompleted?: boolean;
}

export interface DailyAnswers {
  q1: string;
  q2: string;
  q3: string;
  mood: string;
  perso: number;
  objectives: Objective[];
}

export interface Report {
  id: number;
  date: string;
  answers: DailyAnswers;
  summary: string;
  evaluation?: string;
}