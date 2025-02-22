// src/context/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../services/api';

// Interface pour définir la forme des données du contexte
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

// Interface pour le token décodé -- Deprecated
/*interface DecodedToken {
  exp: number;
  user_id: number;
}*/

// Création du contexte
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Props du provider
interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');

    if (token) {
      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await api.get('/verify-token');
        setUser(response.data.user);
      } catch (err) {
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
        setUser(null);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    checkAuth();
  }, []);

  // Fonction de connexion
  const login = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      setError(null);
      const response = await api.post('token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      console.log(response.data);
      const { access_token, token_type, user } = response.data;

      // Sauvegarder le token
      localStorage.setItem('token', access_token);
      
      // Configurer le token dans les headers axios
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Mettre à jour l'état
      setUser(user);

      return user;
    } catch (err) {
      setError('Identifiants invalides');
      throw err;
    }
  };

  // Fonction de déconnexion
  const logout = () => {
    // Supprimer le token
    localStorage.removeItem('token');
    
    // Réinitialiser les headers axios
    delete api.defaults.headers.common['Authorization'];
    
    // Réinitialiser l'état
    setUser(null);
    setError(null);
  };

  // Vérifier si l'utilisateur est authentifié
  const isAuthenticated = !!user;

  // Valeur du contexte
  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

/* Ajouter la gestion du rafraîchissement du token -- Deprecated ?
const refreshToken = async () => {
  try {
    const response = await api.post('/refresh-token');
    const { token } = response.data;
    localStorage.setItem('token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } catch (error) {
    //logout();
  }
};*/

// Hook personnalisé pour utiliser le contexte
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};