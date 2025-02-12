// src/components/form/DailyForm.tsx
import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
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
  const [formObjectives, setFormObjectives] = useState<Objective[]>([]); //maybe useState<Objective[]>([]); but deprecated

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

  // Gestion dynamique des objectifs -- Deprecated
  // const { fields, append, remove, update } = useFieldArray({
  //   control,
  //   name: 'objectives'
  // });

  const questions: Array<{ id: keyof DailyAnswers; text: string }> = [
    { id: 'q1', text: "Comment s'est passée votre journée ?" },
    { id: 'q2', text: "Qu'avez-vous accompli aujourd'hui ?" },
    { id: 'q3', text: "Comment vous sentez-vous ce soir ?" }
  ];


  // Deprecated
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
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {questions.map(q => {
        if (!isKeyOfDailyAnswers(q.id)) return null;
        return (
          <QuestionComponent
            key={q.id}
            question={q.text}
            id={q.id}
            register={register}
            error={errors[q.id]?.message}
          />
        );
      })}

      <br/>

      <ObjectivesManager onObjectivesChange={handleObjectivesChange} />

      <br/>

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

      <br/>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Envoi...' : 'Envoyer'}
      </button>
    </form>
  );
};

export default DailyForm;