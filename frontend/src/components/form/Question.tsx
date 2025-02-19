// src/components/form/Question.tsx
import React, { useState } from 'react';
import { UseFormRegister } from 'react-hook-form';
import { DailyAnswers } from '../../types';
import '../../styles/components/_Question.scss';

interface QuestionProps {
  question: string;
  id: keyof DailyAnswers;
  register: UseFormRegister<DailyAnswers>;
  error?: string;
}

const Question: React.FC<QuestionProps> = ({ question, id, register, error }) => {
  const [isFocused, setIsFocused] = useState(false);
  const [contentLength, setContentLength] = useState(0);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    register(id).onChange(e);
    setContentLength(e.target.value.length);
    
    // Ajuster automatiquement la hauteur
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  return (
    <div className={`question-container ${isFocused ? 'focused' : ''}`}>
      <label htmlFor={id} className="question-label">
        {question}
      </label>
      <div className="textarea-wrapper">
        <textarea
          {...register(id)}
          id={id}
          className={`question-textarea ${error ? 'error' : ''}`}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Écrivez votre réponse ici..."
          rows={1}
        />
        <div className="character-count">
          {contentLength}/500
        </div>
      </div>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default Question;