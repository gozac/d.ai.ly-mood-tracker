// src/components/form/Question.tsx
import React from 'react';
import { UseFormRegister } from 'react-hook-form';
import { DailyAnswers } from '../../types';

interface QuestionProps {
  question: string;
  id: keyof DailyAnswers;
  register: UseFormRegister<DailyAnswers>;
  error?: string;
}

const Question: React.FC<QuestionProps> = ({ question, id, register, error }) => {

  return (
    <div className="question form-group">
      <label htmlFor={id}>{question}</label>
      <textarea
        {...register(id)}
        id={id}
        onChange={(e) => {
          register(id).onChange(e);
        }}
      />
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default Question;