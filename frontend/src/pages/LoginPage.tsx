
import React, { useState } from 'react';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useToast } from '../hooks/useToast';
import { ToastType } from '../types/types';
import * as api from '../services/api';

interface LoginPageProps {
  onLoginSuccess: (user: api.User) => void;
  onSwitchToSignUp: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onSwitchToSignUp }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { addToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const user = await api.login(email, password);
      addToast('Login successful! Welcome back.', ToastType.SUCCESS);
      onLoginSuccess(user);
    } catch (error: any) {
      addToast(error.message || 'Login failed. Please check your credentials.', ToastType.ERROR);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-light-main dark:bg-dark-main">
      <div className="w-full max-w-md p-8 space-y-8 bg-light-secondary dark:bg-dark-secondary rounded-2xl shadow-2xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-light-text dark:text-dark-text">Welcome Back</h1>
          <p className="text-light-text-secondary dark:text-dark-text-secondary mt-2">Sign in to continue to your chatbot</p>
        </div>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <Input
            id="email"
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />
          <Input
            id="password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
          <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>
        </form>
        <p className="text-center text-sm text-light-text-secondary dark:text-dark-text-secondary">
          Don't have an account?{' '}
          <button onClick={onSwitchToSignUp} className="font-medium text-brand-blue hover:underline">
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;