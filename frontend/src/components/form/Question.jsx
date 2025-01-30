// src/components/form/Question.jsx
import React from 'react';
import { UseFormRegister } from 'react-hook-form';
import { DailyAnswers } from '../../types';

interface QuestionProps {
  question: string;
  id: string;
  register: UseFormRegister<DailyAnswers>;
  error?: string;
}

const Question: React.FC<QuestionProps> = ({ question, id, register, error }) => {
  return (
    <div className="form-group">
      <label htmlFor={id}>{question}</label>
      <textarea
        id={id}
        className={`form-control ${error ? 'is-invalid' : ''}`}
        {...register(id, { required: true })}
      />
      {error && <div className="invalid-feedback">{error}</div>}
    </div>
  );
};

export default Question;