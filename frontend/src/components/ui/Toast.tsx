
import React, { useState, useEffect } from 'react';
import { ToastMessage, ToastType } from '../../types/types';
import { CheckIcon, WarningIcon, ErrorIcon, InfoIcon, CloseIcon } from '../icons/Icon';

interface ToastProps {
  toast: ToastMessage;
  onDismiss: (id: string) => void;
}

const toastConfig = {
  [ToastType.SUCCESS]: {
    icon: <CheckIcon className="w-6 h-6 text-green-500" />,
    style: 'bg-green-100 dark:bg-green-900/50 border-green-500',
  },
  [ToastType.WARNING]: {
    icon: <WarningIcon className="w-6 h-6 text-yellow-500" />,
    style: 'bg-yellow-100 dark:bg-yellow-900/50 border-yellow-500',
  },
  [ToastType.ERROR]: {
    icon: <ErrorIcon className="w-6 h-6 text-red-500" />,
    style: 'bg-red-100 dark:bg-red-900/50 border-red-500',
  },
  [ToastType.INFO]: {
    icon: <InfoIcon className="w-6 h-6 text-blue-500" />,
    style: 'bg-blue-100 dark:bg-blue-900/50 border-blue-500',
  },
};

const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    setShow(true);
    const timer = setTimeout(() => {
      setShow(false);
      setTimeout(() => onDismiss(toast.id), 300);
    }, 5000);

    return () => clearTimeout(timer);
  }, [toast, onDismiss]);

  const config = toastConfig[toast.type];

  return (
    <div
      className={`flex items-center p-4 mb-4 rounded-lg shadow-lg border-l-4 transition-all duration-300 transform ${config.style} ${show ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}
    >
      <div className="flex-shrink-0">{config.icon}</div>
      <div className="ml-3 text-sm font-medium text-light-text dark:text-dark-text">
        {toast.message}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="ml-auto -mx-1.5 -my-1.5 bg-transparent rounded-lg p-1.5 inline-flex h-8 w-8 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
      >
        <span className="sr-only">Dismiss</span>
        <CloseIcon />
      </button>
    </div>
  );
};

interface ToastContainerProps {
    toasts: ToastMessage[];
    onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed top-5 right-5 z-50 w-full max-w-xs">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
};
