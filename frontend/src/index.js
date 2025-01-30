import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app.jsx';
//import { AuthProvider } from './context/AuthContext';
import './styles/main.scss';

const root = ReactDOM.createRoot(
  document.getElementById('root')
);

root.render(
  <React.StrictMode>
    <div>
      <App />
    </div>
  </React.StrictMode>
);