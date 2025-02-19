// src/components/form/DailyForm.tsx
import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { DailyAnswers, Objective } from '../../types';
import QuestionComponent from './Question';
import { submitReport,getAdvise } from '../../services/api';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import ObjectivesManager from './ObjectivesManager';

import '../../styles/components/_DailyForm.scss';
import { motion, AnimatePresence } from 'framer-motion';


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

  const { register, handleSubmit, control, formState: { errors }, trigger } = useForm<DailyAnswers>({
    resolver: yupResolver(schema)
  });

  const handleObjectivesChange = (objectives: Objective[]) => {
    setFormObjectives(objectives);
    console.log(formObjectives);
  };


  const questions: Array<{ id: keyof DailyAnswers; text: string }> = [
    { id: 'q1', text: "Qu'avez-vous accompli aujourd'hui ?" },
    { id: 'q2', text: "Comment s'est passée votre journée ?" },
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


  const handleNext = async () => {
    const currentFieldId = steps[currentStep].id;
    const isValid = await trigger(currentFieldId as keyof DailyAnswers);
    
    if (isValid) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1);
  };


  const onSubmit = async (data: DailyAnswers) => {
    setIsSubmitting(true);
    console.log("data: " + data);
    try {
      // Destructurer pour séparer perso du reste des réponses
      const { perso, ...answers } = data;

      if (perso) {
        await getAdvise(perso.id);
        navigate('/report');
      } else {
        await submitReport(data);
      }
    } catch (error) {
      console.error('Error submitting report:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const steps = [
    {
      id: 'objectives',
      component: <ObjectivesManager onObjectivesChange={handleObjectivesChange} />
    },
    ...questions.map(q => ({
      id: q.id,
      component: (
        <QuestionComponent
          question={q.text}
          id={q.id}
          register={register}
          error={errors[q.id]?.message}
        />
      )
    })),
    {
      id: 'mood',
      component: (
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
      )
    },
    {
      id: 'perso',
      component: (
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
                    className={field.value === perso ? 'selected' : ''}
                  >
                    {perso.name}
                  </button>
                ))}
              </div>
            )}
          />
        </div>
      )
    }
  ];

 
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="form-container">
      <div className="progress-bar">
        <div 
          className="progress"
          style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -100, opacity: 0 }}
          transition={{ type: "spring", stiffness: 30}}
          className="step-container"
        >
          {steps[currentStep].component}
        </motion.div>
      </AnimatePresence>

      <div className="navigation-buttons">
        {currentStep > 0 && (
          <button
            type="button"
            onClick={handlePrevious}
            className="nav-button prev"
          >
            Précédent
          </button>
        )}
        
        {currentStep < steps.length - 1 ? (
          <button
            type="button"
            onClick={handleNext}
            className="nav-button next"
          >
            Suivant
          </button>
        ) : (
          <button
            type="submit"
            disabled={isSubmitting}
            className="nav-button submit"
          >
            {isSubmitting ? 'Chargement...' : 'Terminer'}
          </button>
        )}
      </div>
    </form>
  );

};

export default DailyForm;