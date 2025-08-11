
import React, { ReactNode } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  icon?: ReactNode;
}

const Input: React.FC<InputProps> = ({ label, id, icon, ...props }) => {
  return (
    <div>
      {label && <label htmlFor={id} className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">{label}</label>}
      <div className="relative">
        {icon && <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">{icon}</div>}
        <input
          id={id}
          className={`w-full ${icon ? 'pl-10' : 'pl-4'} pr-4 py-2 bg-light-accent/50 dark:bg-dark-accent/50 border border-light-accent dark:border-dark-accent rounded-lg text-light-text dark:text-dark-text focus:outline-none focus:ring-2 focus:ring-brand-blue dark:focus:border-brand-blue transition-colors`}
          {...props}
        />
      </div>
    </div>
  );
};

export default Input;
