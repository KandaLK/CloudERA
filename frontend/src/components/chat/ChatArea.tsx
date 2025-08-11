import React, { useEffect, useRef } from 'react';
import { ChatThread, MessageAuthor } from '../../types/types';
import ChatMessage from './ChatMessage';
import WelcomeScreen from './WelcomeScreen';
import WorkflowStateDisplay from './WorkflowStateDisplay';
import { useWorkflowState } from '../../hooks/useWorkflowState';

interface ChatAreaProps {
  activeThread: ChatThread | null;
  onSendMessage: (content: string, language: 'ENG' | 'SIN') => void;
  onEditMessage: (messageId: string, newContent: string) => void;
  onReactMessage: (messageId: string, reaction: 'like' | 'dislike') => void;
  onRetryMessage: (content: string, messageId: string) => void;
  onFAQClick: (question: string, targetThread: string) => void;
  isProcessing: boolean;
  userEmail: string;
  regeneratingMessageId: string | null;
}

const ChatArea: React.FC<ChatAreaProps> = ({ 
  activeThread, 
  onSendMessage, 
  onEditMessage,
  onReactMessage,
  onRetryMessage,
  onFAQClick,
  isProcessing,
  userEmail,
  regeneratingMessageId
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Use workflow state hook for real-time updates
  const { workflowState, isConnected, connectionError, reconnect } = useWorkflowState(
    activeThread?.id || null
  );

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activeThread?.messages, isProcessing, workflowState]);
  
  const handleRetry = (content: string, messageId: string) => {
      onRetryMessage(content, messageId);
  }

  // Filter messages to hide assistant responses after regenerating message
  const getVisibleMessages = () => {
    if (!activeThread || !regeneratingMessageId) {
      return activeThread?.messages || [];
    }
    
    const regeneratingIndex = activeThread.messages.findIndex(msg => msg.id === regeneratingMessageId);
    if (regeneratingIndex === -1) {
      return activeThread.messages;
    }
    
    // Keep messages up to and including the regenerating user message
    // Hide any assistant messages that come after it
    const visibleMessages = [];
    for (let i = 0; i < activeThread.messages.length; i++) {
      const message = activeThread.messages[i];
      if (i <= regeneratingIndex) {
        visibleMessages.push(message);
      } else if (message.author === MessageAuthor.USER) {
        // Keep user messages after the regenerating point
        visibleMessages.push(message);
      }
      // Skip assistant messages after the regenerating point
    }
    return visibleMessages;
  };

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto p-2 sm:p-4" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
      {!activeThread ? (
          <WelcomeScreen onPromptClick={onFAQClick} userEmail={userEmail}/>
      ) : (
        <div className="max-w-3xl mx-auto">
          <div>
            {getVisibleMessages().map((msg) => {
              const visibleMessages = getVisibleMessages();
              const userMessages = visibleMessages.filter(m => m.author === MessageAuthor.USER);
              const isLatestUserMessage = msg.author === MessageAuthor.USER && msg.id === userMessages[userMessages.length - 1]?.id;
              return (
                <ChatMessage 
                  key={msg.id} 
                  message={msg} 
                  isLatestUserMessage={isLatestUserMessage}
                  onRetry={handleRetry}
                  onEdit={onEditMessage}
                  onReact={onReactMessage}
                  isProcessing={isProcessing}
                />
              )
            })}
          </div>
          {/* Show workflow card only when processing */}
          {isProcessing && (
            <>
              <WorkflowStateDisplay 
                state={workflowState} 
                isConnected={isConnected} 
              />
              {connectionError && (
                <div className="flex items-center justify-center p-2">
                  <button 
                    onClick={reconnect}
                    className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    Connection lost - Click to reconnect
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatArea;