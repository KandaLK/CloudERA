import React from 'react';
import Modal from './Modal';
import { User } from '../../types/types';
import { UserAvatarIcon } from '../icons/Icon';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: User | null;
}

const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose, user }) => {
  if (!user) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="User Profile">
      <div className="flex flex-col items-center space-y-4">
        <UserAvatarIcon className="w-24 h-24 rounded-full object-cover" />
        <div className="text-center">
          <h3 className="text-xl font-bold text-light-text dark:text-dark-text">{user.username}</h3>
          <p className="text-light-text-secondary dark:text-dark-text-secondary">{user.email}</p>
        </div>
        <div className="w-full pt-4">
          <div className="flex justify-between py-2 border-b border-light-accent dark:border-dark-accent">
            <span className="font-semibold text-light-text-secondary dark:text-dark-text-secondary">User ID</span>
            <span className="text-sm font-mono text-light-text dark:text-dark-text bg-light-accent/50 dark:bg-dark-accent/50 px-2 py-1 rounded">{user.id}</span>
          </div>
          <div className="flex justify-between py-2">
             <span className="font-semibold text-light-text-secondary dark:text-dark-text-secondary">Member Since</span>
             <span className="text-light-text dark:text-dark-text">
               {user.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { 
                 year: 'numeric', 
                 month: 'long', 
                 day: 'numeric' 
               }) : 'Unknown'}
             </span>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default ProfileModal;