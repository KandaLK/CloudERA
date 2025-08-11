import React from 'react';
import { ChatThread } from '../../types/types';
import { DeleteIcon } from '../icons/Icon';

interface ChatThreadItemProps {
  thread: ChatThread;
  isActive: boolean;
  onClick: () => void;
  onDelete: (id: string) => void;
  isSmartLearnerUnread?: boolean;
  isAnyThreadProcessing?: boolean;
}

const ChatThreadItem: React.FC<ChatThreadItemProps> = ({ thread, isActive, onClick, onDelete, isSmartLearnerUnread = false, isAnyThreadProcessing = false }) => {

  const formatDate = (dateString: string) => {
      const date = new Date(dateString);
      const now = new Date();
      const diffSeconds = Math.round((now.getTime() - date.getTime()) / 1000);
      const diffMinutes = Math.round(diffSeconds / 60);
      const diffHours = Math.round(diffMinutes / 60);
      const diffDays = Math.round(diffHours / 24);
      
      if (diffSeconds < 60) return "Just now";
      if (diffMinutes < 60) return `${diffMinutes}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 30) return `${diffDays}d ago`;
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }

  // Special styling for Smart Learner when unread
  const isSmartLearner = thread.name === 'Smart Learner';
  const shouldGlow = isSmartLearner && isSmartLearnerUnread && !isActive;
  
  const activeStyle = 'bg-blue-50/80 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800/50 shadow-sm backdrop-blur-sm';
  const inactiveStyle = 'bg-light-secondary/60 dark:bg-dark-secondary/60 border-light-border/50 dark:border-dark-border/50 hover:bg-light-accent/80 dark:hover:bg-dark-accent/80 hover:border-blue-400/60 dark:hover:border-blue-400/60 hover:shadow-md text-light-text dark:text-dark-text backdrop-blur-sm';
  const glowStyle = 'bg-gradient-to-r from-green-50/90 to-emerald-50/90 dark:from-green-900/30 dark:to-emerald-900/30 border-green-300/70 dark:border-green-600/70 text-green-800 dark:text-green-300 shadow-lg shadow-green-200/50 dark:shadow-green-800/30 animate-pulse backdrop-blur-sm';
  const disabledStyle = 'bg-light-secondary/40 dark:bg-dark-secondary/40 border-light-border/30 dark:border-dark-border/30 text-light-text-secondary/50 dark:text-dark-text-secondary/50 cursor-not-allowed opacity-60';


  return (
    <div
      className={`group relative rounded-xl transition-all duration-300 ${
        isAnyThreadProcessing ? 'cursor-not-allowed' : 'cursor-pointer'
      }`}
      onClick={() => {
        if (!isAnyThreadProcessing) {
          onClick();
        }
      }}
    >
      <div className={`p-4 rounded-xl border transition-all duration-300 ${
        isAnyThreadProcessing ? disabledStyle :
        isActive ? activeStyle : 
        shouldGlow ? glowStyle : inactiveStyle
      }`}>
        <p className="font-semibold text-base truncate mb-2">{thread.name}</p>
        <div className={`flex justify-between items-center text-sm ${
          isActive ? 'text-blue-600/80 dark:text-blue-300/80' : 
          shouldGlow ? 'text-green-700/90 dark:text-green-300/90' :
          'text-light-text-secondary dark:text-dark-text-secondary'
        }`}>
          {!isSmartLearner && (
            <span className="font-medium">{thread.messageCount ?? thread.messages.length} messages</span>
          )}
          {isSmartLearner && (
            <span className="font-medium text-emerald-600 dark:text-emerald-400">📚 Learning Hub</span>
          )}
          <span className="opacity-75">{formatDate(thread.lastModified)}</span>
        </div>
      </div>

      {/* Only show delete button (clear messages) for permanent threads */}
      <div className="absolute top-1/2 -right-1 group-hover:right-3 -translate-y-1/2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-all duration-300">
        <button 
          onClick={(e) => { e.stopPropagation(); onDelete(thread.id); }} 
          className="p-2 rounded-lg bg-red-50/90 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/50 shadow-lg backdrop-blur-sm border border-red-200/50 dark:border-red-800/50"
          title="Clear Messages"
        >
          <DeleteIcon />
        </button>
      </div>
    </div>
  );
};

export default ChatThreadItem;