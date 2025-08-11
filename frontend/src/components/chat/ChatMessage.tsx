import React, { useState } from 'react';
import { Message, MessageAuthor } from '../../types/types';
import { useToast } from '../../hooks/useToast';
import { ToastType } from '../../types/types';
import { 
  CopyIcon, RetryIcon, EditIcon, ThumbsUpIcon, ThumbsDownIcon 
} from '../icons/Icon';
import OutputParser from '../output-parser/OutputParser';

interface ChatMessageProps {
  message: Message;
  isLatestUserMessage: boolean;
  onRetry: (content: string, messageId: string) => void;
  onEdit: (messageId: string, newContent: string) => void;
  onReact: (messageId: string, reaction: 'like' | 'dislike') => void;
  isProcessing?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isLatestUserMessage, onRetry, onEdit, onReact, isProcessing = false }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(message.content);
  const { addToast } = useToast();
  
  const isUser = message.author === MessageAuthor.USER;


  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editedContent.trim() && editedContent.trim() !== message.content) {
      onEdit(message.id, editedContent.trim());
      // Toast message and processing indication handled in HomePage.tsx
    }
    setIsEditing(false);
  };
  
  const bubbleStyles = isUser 
    ? 'bg-brand-user-bg dark:bg-brand-user-bg-dark' 
    : 'bg-light-secondary dark:bg-dark-secondary';

  const renderMessageContent = () => {
    if (isEditing) {
      return (
        <div className={`relative rounded-2xl p-4 shadow-sm w-full ${bubbleStyles}`}>
            <form onSubmit={handleEditSubmit}>
            <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="w-full bg-light-main dark:bg-dark-main border border-light-border dark:border-dark-border focus:ring-2 focus:ring-brand-blue focus:outline-none text-light-text dark:text-dark-text text-base rounded-lg p-3"
                rows={4}
                autoFocus
            />
            <div className="flex justify-end space-x-2 mt-2">
                <button type="button" onClick={() => setIsEditing(false)} className="px-3 py-1 text-sm font-semibold rounded-md bg-light-accent dark:bg-dark-accent hover:opacity-80">Cancel</button>
                <button type="submit" className="px-3 py-1 text-sm font-semibold rounded-md bg-brand-blue text-white hover:opacity-90">Save & Submit</button>
            </div>
            </form>
        </div>
      );
    }
    return (
        <div className={`relative rounded-2xl p-4 shadow-sm ${bubbleStyles}`}>
            {isUser ? (
                <div className="prose prose-base dark:prose-invert max-w-none break-words whitespace-pre-wrap text-light-text dark:text-dark-text">
                    {message.content}
                </div>
            ) : (
                <OutputParser 
                    content={message.content}
                    className="text-light-text dark:text-dark-text"
                />
            )}
        </div>
    );
  };
  

  // Clean handler functions without processing blocks
  const copyMessageToClipboard = async (content: string) => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(content);
        addToast('Copied to clipboard!', ToastType.SUCCESS);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textArea = document.createElement('textarea');
        textArea.value = content;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          const successful = document.execCommand('copy');
          if (successful) {
            addToast('Copied to clipboard!', ToastType.SUCCESS);
          } else {
            addToast('Could not copy to clipboard', ToastType.ERROR);
          }
        } catch (fallbackError) {
          addToast('Could not copy to clipboard', ToastType.ERROR);
        }
        
        document.body.removeChild(textArea);
      }
    } catch (error) {
      console.error('Copy failed:', error);
      addToast('Could not copy to clipboard', ToastType.ERROR);
    }
  };

  // Independent icon button components
  const IconButtonBase = ({ onClick, title, children, className = '', buttonType }: {
    onClick: () => void;
    title: string;
    children: React.ReactNode;
    className?: string;
    buttonType?: string;
  }) => (
    <button
      onClick={(e) => {
        try {
          e.preventDefault();
          e.stopPropagation();
          console.log(`[ChatMessage] ${title} clicked - Processing: ${isProcessing}`);
          onClick();
        } catch (error) {
          console.error(`[ChatMessage] Error in ${title} button:`, error);
          addToast(`Error with ${title.toLowerCase()} action`, ToastType.ERROR);
        }
      }}
      title={title}
      className={`p-1.5 rounded-lg hover:bg-light-accent dark:hover:bg-dark-accent transition-all duration-200 transform hover:scale-110 active:scale-95 cursor-pointer ${className}`}
      type="button"
      data-button-type={buttonType}
      style={{ 
        zIndex: 999, 
        position: 'relative',
        pointerEvents: 'auto'
      }}
    >
      {children}
    </button>
  );

  const EditIconButton = ({ onClick }: { onClick: () => void }) => (
    <IconButtonBase onClick={onClick} title="Edit" buttonType="edit" className="text-light-text-secondary dark:text-dark-text-secondary hover:text-light-text dark:hover:text-dark-text">
      <EditIcon className="w-5 h-5" />
    </IconButtonBase>
  );

  const RetryIconButton = ({ onClick }: { onClick: () => void }) => (
    <IconButtonBase onClick={onClick} title="Retry" buttonType="retry" className="text-light-text-secondary dark:text-dark-text-secondary hover:text-light-text dark:hover:text-dark-text">
      <RetryIcon className="w-5 h-5" />
    </IconButtonBase>
  );

  const CopyIconButton = ({ onClick }: { onClick: () => void }) => (
    <IconButtonBase onClick={onClick} title="Copy to clipboard" buttonType="copy" className="text-light-text-secondary dark:text-dark-text-secondary hover:text-light-text dark:hover:text-dark-text">
      <CopyIcon className="w-5 h-5" />
    </IconButtonBase>
  );

  const LikeIconButton = ({ onClick, active }: { onClick: () => void; active: boolean }) => (
    <IconButtonBase 
      onClick={onClick} 
      title="Like" 
      buttonType="like"
      className={active 
        ? 'bg-green-100 dark:bg-green-900/30 border border-green-500/50 text-green-600 dark:text-green-400' 
        : 'text-light-text-secondary dark:text-dark-text-secondary hover:text-green-600 dark:hover:text-green-400'
      }
    >
      <ThumbsUpIcon className="w-5 h-5" />
    </IconButtonBase>
  );

  const DislikeIconButton = ({ onClick, active }: { onClick: () => void; active: boolean }) => (
    <IconButtonBase 
      onClick={onClick} 
      title="Dislike" 
      buttonType="dislike"
      className={active 
        ? 'bg-red-100 dark:bg-red-900/30 border border-red-500/50 text-red-600 dark:text-red-400' 
        : 'text-light-text-secondary dark:text-dark-text-secondary hover:text-red-600 dark:hover:text-red-400'
      }
    >
      <ThumbsDownIcon className="w-5 h-5" />
    </IconButtonBase>
  );

  const isLiked = message.reaction === 'like';
  const isDisliked = message.reaction === 'dislike';

  return (
    <div className={`group flex items-start space-x-4 py-4 message-slide-in ${isUser ? 'justify-end' : ''}`}>
      <div className={`flex flex-col max-w-3xl w-full ${isUser ? 'items-end' : 'items-start'}`}>
        {renderMessageContent()}
        
        {/* Action Buttons - With error boundaries and guaranteed visibility */}
        <div className={`flex items-center space-x-1 mt-2 relative ${!isEditing ? 'opacity-0 group-hover:opacity-100 transition-opacity duration-300' : ''}`}
             style={{ zIndex: 998, position: 'relative', pointerEvents: 'auto' }}>
          {/* User message actions */}
          {isUser && isLatestUserMessage && !isEditing && (
            <>
              <EditIconButton onClick={() => {
                try {
                  setIsEditing(true);
                } catch (error) {
                  console.error('Edit button error:', error);
                  addToast('Error opening editor', ToastType.ERROR);
                }
              }} />
              <RetryIconButton onClick={() => {
                try {
                  onRetry(message.content, message.id);
                } catch (error) {
                  console.error('Retry button error:', error);
                  addToast('Error retrying message', ToastType.ERROR);
                }
              }} />
            </>
          )}
          
          {/* Assistant message actions */}
          {!isUser && !isEditing && (
            <>
              <span className="text-xs mr-2 text-light-text-secondary dark:text-dark-text-secondary">Was this helpful?</span>
              <LikeIconButton onClick={() => {
                try {
                  onReact(message.id, 'like');
                } catch (error) {
                  console.error('Like button error:', error);
                  addToast('Error saving reaction', ToastType.ERROR);
                }
              }} active={isLiked} />
              <DislikeIconButton onClick={() => {
                try {
                  onReact(message.id, 'dislike');
                } catch (error) {
                  console.error('Dislike button error:', error);
                  addToast('Error saving reaction', ToastType.ERROR);
                }
              }} active={isDisliked} />
            </>
          )}
          
          {/* Copy button - always available except during editing */}
          {!isEditing && (
            <CopyIconButton onClick={() => {
              try {
                copyMessageToClipboard(message.content);
              } catch (error) {
                console.error('Copy button error:', error);
                addToast('Error copying to clipboard', ToastType.ERROR);
              }
            }} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;