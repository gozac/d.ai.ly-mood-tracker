// src/components/form/DailyForm.jsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { DailyAnswers, Question } from '../../types';
import QuestionComponent from './Question';
import { submitReport } from '../../services/api';

const DailyForm: React.FC = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<DailyAnswers>();

  const questions: Question[] = [
    { id: 'q1', text: "Comment s'est passée votre journée ?" },
    { id: 'q2', text: "Qu'avez-vous accompli aujourd'hui ?" },
    { id: 'q3', text: "Comment vous sentez-vous ce soir ?" }
  ];

  const onSubmit = async (data: DailyAnswers) => {
    setIsSubmitting(true);
    try {
      await submitReport(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {questions.map(q => (
        <QuestionComponent
          key={q.id}
          question={q.text}
          id={q.id}
          register={register}
          error={errors[q.id]?.message}
        />
      ))}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Envoi...' : 'Envoyer'}
      </button>
    </form>
  );
};

export default DailyForm;