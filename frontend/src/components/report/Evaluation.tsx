// src/components/report/Evaluation.tsx
import React from 'react';
//import 'styles/components/_evaluation.scss';

interface EvaluationProps {
  evaluation: string;
  date?: string;
}

const Evaluation: React.FC<EvaluationProps> = ({ evaluation, date }) => {
  return (
    <div className="evaluation-container">
      <div className="evaluation-header">
        <h3>Analyse IA</h3>
        {date && <span className="evaluation-date">{date}</span>}
      </div>
      
      <div className="evaluation-content">
        {/* On peut formater l'évaluation en sections si elle contient des marqueurs spécifiques */}
        {evaluation.split('\n').map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>
    </div>
  );
};

export default Evaluation;