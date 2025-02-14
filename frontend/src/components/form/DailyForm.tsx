// src/components/form/DailyForm.tsx
import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { DailyAnswers, Objective } from '../../types';
import QuestionComponent from './Question';
import { submitReport } from '../../services/api';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import ObjectivesManager from './ObjectivesManager';


// Type guard function to check if a string is a key of DailyAnswers
function isKeyOfDailyAnswers(key: string): key is keyof DailyAnswers {
  return ['q1', 'q2', 'q3'].includes(key);
}

const schema = yup.object().shape({
  q1: yup.string().required('Ce champ est requis'),
  q2: yup.string().required('Ce champ est requis'),
  q3: yup.string().required('Ce champ est requis'),
  mood: yup.string().required('Veuillez sélectionner une humeur'),
  objectives: yup.array().of(
    yup.object().shape({
      title: yup.string().required('Le titre de l\'objectif est requis')
    })
  )
}) as yup.ObjectSchema<DailyAnswers>;


const DailyForm: React.FC = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formObjectives, setFormObjectives] = useState<Objective[]>([]);

  const [currentStep, setCurrentStep] = useState(0);

  const navigate = useNavigate();

  const moods = [
    '😊 Heureux',
    '😢 Triste', 
    '😴 Fatigué',
    '😡 Frustré',
    '🤩 Excité'
  ];



  const { register, handleSubmit, control, formState: { errors } } = useForm<DailyAnswers>({
    resolver: yupResolver(schema)
  });


  const questions: Array<{ id: keyof DailyAnswers; text: string }> = [
    { id: 'q1', text: "Comment s'est passée votre journée ?" },
    { id: 'q2', text: "Qu'avez-vous accompli aujourd'hui ?" },
    { id: 'q3', text: "Comment vous sentez-vous ce soir ?" }
  ];

    const persos: Array<{ id: number; name: string; img: string}> = [
    { id: 0, name: "Sean McGuire", img: 'yo.png' },
    { id: 1, name: "The Ancient One", img: 'yo.png' },
    { id: 2, name: "Nelson Mandela", img: 'yo.png' },
    { id: 3, name: "Iroh", img: 'yo.png' },
    { id: 4, name: "Mulan", img: 'yo.png' },
    { id: 5, name: "Ghandalf", img: 'yo.png' },
    { id: 6, name: "Oprah", img: 'yo.png' },
    { id: 7, name: "Yoda", img: 'yo.png' },
    { id: 8, name: "Tyrion Lannister", img: 'yo.png' },
    { id: 9, name: "Tupac", img: 'yo.png' }
  ];


  const handleQuestionComplete = () => {
      setCurrentStep(prev => prev + 1);   
  };

  const handleObjectivesChange = (objectives: Objective[]) => {
    setFormObjectives(objectives);
    console.log(formObjectives);
  };

  const onSubmit = async (data: DailyAnswers) => {
    setIsSubmitting(true);
    try {
      await submitReport(data);
    } finally {
      setIsSubmitting(false);
      navigate('/report'); 
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>

      <ObjectivesManager onObjectivesChange={handleObjectivesChange} />

      {questions.map((q, index: number) => {
        if (!isKeyOfDailyAnswers(q.id)) return null;
        return (
          <div
            key={q.id}
            style={{ 
              display: index <= currentStep ? 'block' : 'block',
              transition: 'opacity 0.3s ease-in-out',
              opacity: index <= currentStep ? 1 : 0 
            }}
          >
            <QuestionComponent
              question={q.text}
              id={q.id}
              register={register}
              error={errors[q.id]?.message}
            />
          </div>
        );
      })}

      {currentStep >= questions.length && (
        <div className="mood-selector">
          <h3>Comment vous sentez-vous ?</h3>
          <Controller
            name="mood"
            control={control}
            render={({ field }) => (
              <div className="mood-buttons">
                {moods.map((mood, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => field.onChange(mood)}
                    className={field.value === mood ? 'selected' : ''}
                  >
                    {mood}
                  </button>
                ))}
              </div>
            )}
          />
          {errors.mood && <p className="error">{errors.mood.message}</p>}
        </div>
      )}

      {currentStep > questions.length && (
        <div className="perso-selector">
          <h3>Choisissez votre conseiller :</h3>
          <Controller
            name="perso"
            control={control}
            render={({ field }) => (
              <div className="perso-buttons">
                {persos.map((perso, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => field.onChange(perso)}
                    className={field.value === perso.id ? 'selected' : ''}
                  >
                    {perso.name}
                  </button>
                ))}
              </div>
            )}
          />
          {errors.perso && <p className="error">{errors.perso.message}</p>}
        </div>
      )}

      {currentStep <= questions.length && (
        <>
          <button onClick={() => handleQuestionComplete()}>Suite</button>
        </>
      )}
      {currentStep > questions.length && (
        <>
          <button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Envoi...' : 'Envoyer'}</button>
        </>
      )}
    </form>
  );
};

export default DailyForm;