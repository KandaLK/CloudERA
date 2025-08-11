
import React, { useState } from 'react';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useToast } from '../hooks/useToast';
import { ToastType } from '../types/types';
import * as api from '../services/api';

interface SignUpPageProps {
  onSignUpSuccess: (user: api.User) => void;
  onSwitchToLogin: () => void;
}

const SignUpPage: React.FC<SignUpPageProps> = ({ onSignUpSuccess, onSwitchToLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { addToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 6) {
        addToast('Password must be at least 6 characters long.', ToastType.WARNING);
        return;
    }
    setIsLoading(true);
    try {
      const user = await api.signUp(username, email, password);
      addToast('Account created successfully! Please log in.', ToastType.SUCCESS);
      onSignUpSuccess(user);
    } catch (error: any) {
      addToast(error.message || 'Sign up failed. Please try again.', ToastType.ERROR);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-light-main dark:bg-dark-main">
      <div className="w-full max-w-md p-8 space-y-8 bg-light-secondary dark:bg-dark-secondary rounded-2xl shadow-2xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-light-text dark:text-dark-text">Create an Account</h1>
          <p className="text-light-text-secondary dark:text-dark-text-secondary mt-2">Start your journey with our AI chatbot</p>
        </div>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <Input
            id="username"
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Your Name"
            required
          />
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
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </Button>
        </form>
        <p className="text-center text-sm text-light-text-secondary dark:text-dark-text-secondary">
          Already have an account?{' '}
          <button onClick={onSwitchToLogin} className="font-medium text-brand-blue hover:underline">
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};

export default SignUpPage;