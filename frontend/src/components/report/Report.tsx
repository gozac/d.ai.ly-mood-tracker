// src/components/report/Report.tsx
import React, { useEffect, useState } from 'react';
import { Report as ReportType } from '../../types';
import { getTodayReport } from '../../services/api';
import Evaluation from './Evaluation';
import axios from 'axios'
//import './Report.scss';

const Report: React.FC = () => {
  const [report, setReport] = useState<ReportType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        const data = await getTodayReport();
        setReport(data);
      } catch (err) {
        if (axios.isAxiosError(err)) {
          setError(err.response?.data?.message || 'Erreur lors du chargement du rapport');
        } else {
          setError('Une erreur inattendue est survenue');
        }
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
            <h2>Rapport du {new Date(report.date).toLocaleDateString('fr-FR', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}</h2>
          </div>

          <br />
          
          <div className="report-content">

            <div className="report-summary">
              <h3>Résumé</h3>
              <p>{report.summary}</p>
            </div>

            <br />

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