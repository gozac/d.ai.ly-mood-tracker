import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app';
import './styles/main.scss';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

//Deprecated
export interface LoginFormData {
  username: string;
  password: string;
}
export interface RegisterFormData extends LoginFormData {
  confirmPassword: string;
}

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);