import React from 'react';
import { MenuIcon, CloseIcon, HomeIcon } from '../icons/Icon';

interface ChatHeaderProps {
  threadName: string;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
  onGoHome: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  threadName,
  onToggleSidebar,
  isSidebarOpen,
  onGoHome,
}) => {
  return (
    <div className="flex items-center justify-between p-3 border-b border-light-border dark:border-dark-border bg-light-secondary dark:bg-dark-secondary flex-shrink-0">
      <div className="flex items-center space-x-2">
        <button onClick={onToggleSidebar} className="p-2 -ml-2 text-light-text-secondary dark:text-dark-text-secondary">
          { isSidebarOpen ? <CloseIcon className="w-5 h-5"/> : <MenuIcon className="w-5 h-5" /> }
        </button>
        <button onClick={onGoHome} className="p-2 -ml-1 text-light-text-secondary dark:text-dark-text-secondary">
          <HomeIcon className="w-5 h-5" />
        </button>
        <h2 className="font-semibold text-base sm:text-lg text-light-text dark:text-dark-text truncate">
          {threadName}
        </h2>
      </div>
    </div>
  );
};

export default ChatHeader;