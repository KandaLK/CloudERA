import React from 'react';
import { ChatThread, Theme, User } from '../../types/types';
import ChatThreadItem from './ChatThreadItem';
import { SettingsIcon, ThemeToggleIcon, CloudEraIcon, UserAvatarIcon } from '../icons/Icon';
import Logo from '../ui/Logo';

interface SidebarProps {
  user: User | null;
  threads: ChatThread[];
  activeThreadId: string | null;
  onSelectThread: (id: string) => void;
  onDeleteThread: (id: string) => void;
  onShowSettings: () => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isOpen: boolean;
  smartLearnerUnread?: boolean;
  isAnyThreadProcessing?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  user,
  threads,
  activeThreadId,
  onSelectThread,
  onDeleteThread,
  onShowSettings,
  theme,
  setTheme,
  isOpen,
  smartLearnerUnread = false,
  isAnyThreadProcessing = false,
}) => {
    
  const handleThemeChange = () => {
    const newTheme = theme === Theme.LIGHT ? Theme.DARK : Theme.LIGHT;
    setTheme(newTheme);
  };
    
  return (
    <div className={`absolute inset-y-0 left-0 z-30 flex flex-col w-80 bg-light-secondary dark:bg-dark-secondary text-light-text-secondary dark:text-dark-text-secondary p-3 transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full'} border-r border-light-border dark:border-dark-border`}>
        {/* Header */}
        <div className="flex items-center justify-between p-2 mb-2">
            <Logo theme={theme} size="md" showText={true} className="flex-shrink-0" />
        </div>

        {/* Permanent threads - no new chat creation needed */}

        <div id="chat-history-list" className="flex-1 overflow-y-auto pr-2" style={{'scrollbarWidth': 'thin', 'scrollbarColor': 'var(--tw-dark-text-secondary) var(--tw-dark-secondary)'}}>
          {/* Cloud Chats Section */}
          <div className="mb-6">
            <div className="flex items-center mb-3">
              <h3 className="text-sm font-semibold text-light-text dark:text-dark-text opacity-70 uppercase tracking-wider">
                Cloud Chats
              </h3>
            </div>
            <div className="space-y-3">
              {threads.filter(thread => 
                thread.name === 'AWS Discussion' || thread.name === 'Azure Discussion'
              ).map((thread) => (
                <ChatThreadItem
                  key={thread.id}
                  thread={thread}
                  isActive={thread.id === activeThreadId}
                  onClick={() => onSelectThread(thread.id)}
                  onDelete={onDeleteThread}
                  isAnyThreadProcessing={isAnyThreadProcessing}
                />
              ))}
            </div>
          </div>

          {/* Learn Section */}
          <div className="mb-4">
            <div className="flex items-center mb-3">
              <h3 className="text-sm font-semibold text-light-text dark:text-dark-text opacity-70 uppercase tracking-wider">
                Learn
              </h3>
            </div>
            <div className="space-y-3">
              {threads.filter(thread => 
                thread.name === 'Smart Learner'
              ).map((thread) => (
                <ChatThreadItem
                  key={thread.id}
                  thread={thread}
                  isActive={thread.id === activeThreadId}
                  onClick={() => onSelectThread(thread.id)}
                  onDelete={onDeleteThread}
                  isSmartLearnerUnread={smartLearnerUnread}
                  isAnyThreadProcessing={isAnyThreadProcessing}
                />
              ))}
            </div>
          </div>
        </div>


        {/* Footer */}
        <div id="sidebar-footer" className="pt-2 mt-auto border-t border-light-border dark:border-dark-border">
          {user && (
            <div className="flex items-center w-full p-2.5 rounded-lg">
                <UserAvatarIcon className="w-8 h-8 mr-3 text-light-text dark:text-dark-text"/>
                <span className="font-medium text-sm text-light-text dark:text-dark-text truncate">{user.username}</span>
                 <div className="ml-auto flex items-center">
                    <button onClick={handleThemeChange} className="p-2 rounded-md hover:bg-light-accent dark:hover:bg-dark-accent">
                        <ThemeToggleIcon className="w-5 h-5" theme={theme} />
                    </button>
                    <button onClick={onShowSettings} className="p-2 rounded-md hover:bg-light-accent dark:hover:bg-dark-accent">
                        <SettingsIcon className="w-5 h-5" />
                    </button>
                </div>
            </div>
          )}
        </div>
      </div>
  );
};

export default Sidebar;