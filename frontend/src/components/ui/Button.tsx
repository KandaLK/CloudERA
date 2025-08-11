import React, { ReactNode } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', size = 'md', className = '', ...props }) => {
  const baseStyle = "inline-flex items-center justify-center font-semibold rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-dark-main transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform";

  const variantStyles = {
    primary: 'bg-brand-blue text-white focus:ring-brand-blue shadow-lg shadow-lg-blue hover:bg-blue-500 hover:-translate-y-0.5',
    secondary: 'bg-dark-accent hover:bg-gray-600/50 dark:bg-dark-accent dark:hover:bg-gray-700 text-dark-text dark:text-dark-text focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    ghost: 'bg-transparent hover:bg-gray-500/10 text-light-text-secondary dark:text-dark-text-secondary dark:hover:bg-gray-500/20 focus:ring-gray-400',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyle} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;