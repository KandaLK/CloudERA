import React, { useState, useRef, useEffect } from 'react';
import { SendIcon, WebSearchIcon, LanguageIcon } from '../icons/Icon';

interface ChatInputProps {
  onSendMessage: (message: string, language: 'ENG' | 'SIN') => void;
  isProcessing: boolean;
  useWebSearch: boolean;
  setUseWebSearch: (value: boolean) => void;
  language: 'ENG' | 'SIN';
  setLanguage: (language: 'ENG' | 'SIN') => void;
  isLanguageLocked: boolean;
  message: string;
  setMessage: (message: string) => void;
  onClearMessage: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  isProcessing,
  useWebSearch,
  setUseWebSearch,
  language,
  setLanguage,
  isLanguageLocked,
  message,
  setMessage,
  onClearMessage
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !isProcessing) {
      onSendMessage(message.trim(), language);
      onClearMessage();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      const scrollHeight = ta.scrollHeight;
      const maxHeight = 256; // Corresponds to max-h-64
      ta.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [message]);

  return (
    <div className="flex-shrink-0 px-2 sm:px-4 pb-3 sm:pb-4 pt-2 bg-transparent w-full">
        <div className="w-full max-w-3xl mx-auto">
            <div className="relative bg-light-secondary/70 dark:bg-dark-secondary/70 backdrop-blur-xl border border-light-border/80 dark:border-dark-border/80 rounded-2xl shadow-2xl">
                <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message here..."
                className="w-full bg-transparent p-5 pr-16 text-light-text dark:text-dark-text placeholder-light-text-secondary dark:placeholder-dark-text-secondary focus:outline-none resize-none max-h-64 text-base"
                rows={1}
                disabled={isProcessing}
                />
                <button
                onClick={handleSend}
                disabled={isProcessing || !message.trim()}
                className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center justify-center w-10 h-10 rounded-lg bg-light-text dark:bg-dark-text text-light-secondary dark:text-dark-secondary disabled:bg-light-text-secondary dark:disabled:bg-dark-text-secondary disabled:opacity-50 transition-all hover:scale-105 active:scale-100"
                aria-label="Send message"
                >
                <SendIcon className="w-5 h-5" />
                </button>
            </div>
             <div className="flex justify-between items-center px-2 pt-2">
                <div className="flex items-center space-x-3">
                    <button
                        id="web-search-toggle"
                        onClick={() => setUseWebSearch(!useWebSearch)}
                        className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors border ${
                        useWebSearch
                            ? 'bg-accent-light-blue text-brand-blue border-brand-blue/30'
                            : 'bg-transparent text-light-text-secondary dark:text-dark-text-secondary border-light-border dark:border-dark-border hover:bg-light-accent dark:hover:bg-dark-accent'
                        }`}
                    >
                        <WebSearchIcon className="w-4 h-4" />
                        <span>Web Search</span>
                    </button>
                    
                    <div id="language-toggle" className={`flex items-center p-0.5 bg-light-accent dark:bg-dark-accent rounded-full border border-light-border/50 dark:border-dark-border/50 ${isLanguageLocked ? 'opacity-70' : ''}`}>
                        <button 
                            onClick={() => setLanguage('ENG')} 
                            className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${language === 'ENG' ? 'bg-accent-light-blue text-brand-blue shadow' : 'text-light-text-secondary dark:text-dark-text-secondary'} disabled:cursor-not-allowed`}
                            disabled={isLanguageLocked}
                        >
                            ENG
                        </button>
                        <button 
                            onClick={() => setLanguage('SIN')} 
                            className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${language === 'SIN' ? 'bg-accent-light-blue text-brand-blue shadow' : 'text-light-text-secondary dark:text-dark-text-secondary'} disabled:cursor-not-allowed`}
                            disabled={isLanguageLocked}
                        >
                            SIN
                        </button>
                    </div>
                </div>
                <p className="text-xs text-light-text-secondary dark:text-dark-text-secondary">
                    Shift+Enter for new line.
                </p>
            </div>
        </div>
    </div>
  );
};

export default ChatInput;