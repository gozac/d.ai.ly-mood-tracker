// src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import PageTransition from './components/PageTransition';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/layout/Navbar';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import DailyForm from './components/form/DailyForm';
import Report from './components/report/Report';
import ProtectedRoute from './components/layout/ProtectedRoute';
import './styles/main.scss';


const AnimatedRoutes = () => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route 
          path="/login" 
          element={
            <PageTransition>
              <Login />
            </PageTransition>
          } 
        />
        <Route 
          path="/register" 
          element={
            <PageTransition>
              <Register />
            </PageTransition>
          } 
        />
        <Route
          path="/form"
          element={
            <ProtectedRoute>
              <PageTransition>
                <DailyForm />
              </PageTransition>
            </ProtectedRoute>
          }
        />
        <Route 
              path="/report" 
              element={
                <ProtectedRoute>
                  <PageTransition>
                    <Report />
                  </PageTransition>
                </ProtectedRoute>
              } 
        />
        <Route path="/" element={<Navigate to="/form" replace />} />
      </Routes>
    </AnimatePresence>
  );
};


const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <AnimatedRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;