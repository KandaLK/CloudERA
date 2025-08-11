
import React, { ReactNode } from 'react';
import { CloseIcon } from '../icons/Icon';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex justify-center items-center backdrop-blur-sm" onClick={onClose}>
      <div 
        className="bg-light-secondary dark:bg-dark-secondary rounded-xl shadow-2xl w-full max-w-md m-4 transform transition-all duration-300 scale-95 hover:scale-100"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-light-accent dark:border-dark-accent">
          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">{title}</h3>
          <button
            onClick={onClose}
            className="text-light-text-secondary dark:text-dark-text-secondary hover:text-light-text dark:hover:text-dark-text transition-colors"
          >
            <CloseIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
