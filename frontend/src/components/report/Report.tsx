import React, { useEffect, useState } from 'react';
import { Report as ReportType } from '../../types';
import { getTodayReport } from '../../services/api';
import Evaluation from './Evaluation';
import './Report.scss';

const Report: React.FC = () => {
  const [report, setReport] = useState<ReportType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await getTodayReport();
        setReport(data);
      } catch (err) {
        setError('Erreur lors du chargement du rapport');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  if (loading) {
    return (
      <div className="report-loading">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div className="report-container">
      {report ? (
        <>
          <div className="report-header">
            <h2>Rapport du {new Date(report.date).toLocaleDateString()}</h2>
          </div>
          
          <div className="report-content">
            <div className="report-answers">
              <h3>Vos réponses</h3>
              {Object.entries(report.answers).map(([question, answer]) => (
                <div key={question} className="answer-item">
                  <strong>{question}:</strong>
                  <p>{answer}</p>
                </div>
              ))}
            </div>

            <div className="report-summary">
              <h3>Résumé</h3>
              <p>{report.summary}</p>
            </div>

            {report.evaluation && <Evaluation evaluation={report.evaluation} />}
          </div>
        </>
      ) : (
        <div className="no-report">
          <h3>Aucun rapport pour aujourd'hui</h3>
          <p>Complétez le formulaire quotidien pour voir votre rapport.</p>
        </div>
      )}
    </div>
  );
};

export default Report;