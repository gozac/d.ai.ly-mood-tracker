// src/components/layout/Navbar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Daily Mood</Link>
      <div className="navbar-nav">
        {isAuthenticated ? (
          <>
            <Link to="/form" className="nav-link">Formulaire</Link>
            <Link to="/report" className="nav-link">Rapport</Link>
            <button onClick={logout} className="nav-link">Déconnexion</button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Connexion</Link>
            <Link to="/register" className="nav-link">Inscription</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;