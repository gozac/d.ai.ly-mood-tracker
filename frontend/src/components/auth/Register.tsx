// src/components/auth/Register.jsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { registerUser } from '../../services/auth';

interface RegisterFormInputs {
  username: string;
  password: string;
  confirmPassword: string;
}

const Register: React.FC = () => {
  // Component implementation
};

export default Register;