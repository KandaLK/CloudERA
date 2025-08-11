
import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/sidebar/Sidebar';
import ChatArea from '../components/chat/ChatArea';
import SettingsPage from './SettingsPage';
import ChatHeader from '../components/chat/ChatHeader';
import ChatInput from '../components/chat/ChatInput';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import { useToast } from '../hooks/useToast';
import { useThreadState } from '../hooks/useThreadState';
import { ToastType } from '../types/types';
import * as api from '../services/api';
import { ChatThread, Message, MessageAuthor, Theme, User } from '../types/types';

interface HomePageProps {
  user: User;
  onLogout: () => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const HomePage: React.FC<HomePageProps> = ({ user, onLogout, theme, setTheme }) => {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { addToast } = useToast();
  
  // Initialize thread state manager with global language preference fallback
  const globalLanguage = (() => {
    const saved = localStorage.getItem('preferred_language');
    return (saved === 'SIN' || saved === 'ENG') ? saved as 'ENG' | 'SIN' : 'ENG';
  })();
  
  const threadStateManager = useThreadState(globalLanguage);
  
  // State for modals
  const [threadToDelete, setThreadToDelete] = useState<string | null>(null);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
  const [showDeleteAccountConfirm, setShowDeleteAccountConfirm] = useState(false);
  const [smartLearnerUnread, setSmartLearnerUnread] = useState(false);
  const [regeneratingMessageId, setRegeneratingMessageId] = useState<string | null>(null);

  // Use refs to prevent infinite re-renders
  const threadsRef = useRef<ChatThread[]>([]);
  const activeThreadIdRef = useRef<string | null>(null);
  
  // Update refs when state changes
  useEffect(() => {
    threadsRef.current = threads;
  }, [threads]);
  
  useEffect(() => {
    activeThreadIdRef.current = activeThreadId;
  }, [activeThreadId]);

  useEffect(() => {
    const fetchThreads = async () => {
      try {
        const userThreads = await api.getChatThreads(user.id);
        
        // Check if Smart Learner thread has new messages (for educational agent posts)
        const currentSmartLearner = threadsRef.current.find((t: ChatThread) => t.name === 'Smart Learner');
        const newSmartLearner = userThreads.find(t => t.name === 'Smart Learner');
        
        if (currentSmartLearner && newSmartLearner && 
            currentSmartLearner.messageCount !== undefined && 
            newSmartLearner.messageCount !== undefined &&
            newSmartLearner.messageCount > currentSmartLearner.messageCount &&
            activeThreadIdRef.current !== newSmartLearner.id) {
          setSmartLearnerUnread(true);
          addToast('You Have An Unread Message On SMART Learner', ToastType.INFO);
        }
        
        setThreads(userThreads);
      } catch (error) {
        console.error('Error fetching threads:', error);
        addToast('Failed to load chat history.', ToastType.ERROR);
      }
    };
    
    // Initial fetch
    fetchThreads();
    
    // Set up polling to check for new educational posts every 30 seconds
    const interval = setInterval(fetchThreads, 30000);
    return () => {
      clearInterval(interval);
    };
  }, [user.id, addToast]); // Removed threads and activeThreadId from dependencies

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    };
    window.addEventListener('resize', handleResize);
    handleResize(); // Initial check
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const [activeThread, setActiveThread] = useState<ChatThread | null>(null);
  
  // Get current thread state
  const currentThreadState = activeThreadId ? threadStateManager.getThreadState(activeThreadId) : null;
  const isLanguageLocked = activeThread ? (activeThread.messages.length > 1) : false;

  const handleSendMessage = async (content: string, lang: 'ENG' | 'SIN', threadIdOverride?: string) => {
    let currentThreadId = threadIdOverride || activeThreadId;

    // Require an active thread - no more automatic thread creation
    if (!currentThreadId) {
        addToast('Please select a thread before sending a message.', ToastType.WARNING);
        return;
    }

    // Create user message immediately and show it
    const userMessage: Message = {
        id: `msg-user-${Date.now()}`,
        author: MessageAuthor.USER,
        content: content,
        timestamp: new Date().toISOString(),
        reaction: null,
    };

    // Add user message to UI immediately
    if (activeThread) {
        setActiveThread(prev => prev ? {
            ...prev,
            messages: [...prev.messages, userMessage]
        } : null);
    } else {
        // If no active thread (new thread scenario), create a temporary one with the user message
        const tempThread: ChatThread = {
            id: currentThreadId,
            name: "New Conversation",
            messages: [userMessage],
            lastModified: new Date().toISOString(),
            language: 'ENG'
        };
        setActiveThread(tempThread);
    }

    // Start processing indicator for current thread
    if (activeThreadId) {
        threadStateManager.setProcessing(activeThreadId, true);
    }

    try {
        // Add a minimum delay to make the interaction feel more natural
        const startTime = Date.now();
        
        // Send message and get AI response via backend
        const currentState = threadStateManager.getThreadState(currentThreadId);
        const assistantMessage = await api.getAssistantResponse(
            content, 
            currentState.useWebSearch, 
            lang, 
            user.id, 
            currentThreadId,
            activeThread?.messages || []
        );

        // Ensure minimum processing time of 1.5 seconds for better UX
        const elapsed = Date.now() - startTime;
        const minDelay = 1500;
        if (elapsed < minDelay) {
            await new Promise(resolve => setTimeout(resolve, minDelay - elapsed));
        }

        // Reload the complete thread to get the actual messages from backend
        const updatedThread = await api.getThreadWithMessages(currentThreadId);
        setActiveThread(updatedThread);
        
        // Update threads list with new message count and timestamp
        setThreads(prev => prev.map(t => t.id === currentThreadId ? {
          ...t,
          lastModified: updatedThread.lastModified,
          messageCount: updatedThread.messages.length
        } : t));
        
        // Clear regeneration state when new response is successfully generated
        setRegeneratingMessageId(null);
        
        // Check if Smart Learner thread got a new message and show notification
        const updatedThreadData = threads.find(t => t.id === currentThreadId);
        if (updatedThreadData?.name === 'Smart Learner' && currentThreadId !== activeThreadId) {
          setSmartLearnerUnread(true);
          addToast('You Have An Unread Message On SMART Learner', ToastType.INFO);
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        addToast('Error sending message. Please try again.', ToastType.ERROR);
        
        // Remove the optimistically added user message on error
        setActiveThread(prev => {
            if (!prev) return null;
            const filteredMessages = prev.messages.filter(m => m.id !== userMessage.id);
            // If this was a temporary thread with only the failed message, clear it
            if (filteredMessages.length === 0 && prev.name === "New Conversation") {
                return null;
            }
            return { ...prev, messages: filteredMessages };
        });
    } finally {
        if (activeThreadId) {
            threadStateManager.setProcessing(activeThreadId, false);
        }
        // Clear regeneration state regardless of success or failure
        setRegeneratingMessageId(null);
    }
  };
  
  // Thread creation removed - users now have permanent threads
  
  const handleSelectThread = async (id: string) => {
      // Prevent thread switching during message processing
      const isAnyThreadProcessing = Array.from(threadStateManager.threadStates.values())
        .some(state => state.isProcessing);
      
      if (isAnyThreadProcessing) {
        addToast('Please wait for the current message to complete before switching threads.', ToastType.WARNING);
        return;
      }

      // Allow switching to the same thread (refresh)
      if (activeThreadId === id) {
        try {
          const threadWithMessages = await api.getThreadWithMessages(id);
          setActiveThread(threadWithMessages);
        } catch (error) {
          console.error('Error refreshing thread:', error);
          addToast('Failed to refresh chat thread.', ToastType.ERROR);
        }
        return;
      }

      try {
        setActiveThreadId(id);
        setActiveThread(null); // Clear current thread while loading
        
        // Load thread with messages
        const threadWithMessages = await api.getThreadWithMessages(id);
        setActiveThread(threadWithMessages);
        // Keep user's preferred language selection - don't reset based on thread
        setShowSettings(false);
        
        // Clear Smart Learner unread status when thread is selected
        if (threadWithMessages.name === 'Smart Learner') {
          setSmartLearnerUnread(false);
        }
        
        if(window.innerWidth < 768) {
          setSidebarOpen(false);
        }
      } catch (error) {
        console.error('Error loading thread:', error);
        addToast('Failed to load chat thread.', ToastType.ERROR);
      }
  }

  const handleDeleteThread = async () => {
    if(!threadToDelete) return;
    const isActiveThread = activeThreadId === threadToDelete;
    
    try {
        // Clear messages from thread (thread remains permanent)
        await api.deleteChatThread(user.id, threadToDelete);
        
        // Update thread in state to show 0 messages
        setThreads(prev => prev.map(t => t.id === threadToDelete ? {
          ...t,
          messageCount: 0,
          lastModified: new Date().toISOString()
        } : t));
        
        // If clearing the active thread, immediately clear the UI
        if (isActiveThread) {
            setActiveThreadId(null);
            setActiveThread(null);
            // Keep user's preferred language - don't reset
            setShowSettings(false); // Ensure we're not in settings view
        }
        
        addToast('Thread messages cleared successfully.', ToastType.SUCCESS);
    } catch (error) {
        addToast('Failed to clear thread messages.', ToastType.ERROR);
    } finally {
        setThreadToDelete(null);
    }
  };
  
  // Thread renaming removed - permanent threads cannot be renamed
  
  const handleEditMessage = async (messageId: string, newContent: string) => {
      if(!activeThreadId || !activeThread) {
        addToast('No active thread selected.', ToastType.ERROR);
        return;
      }

      try {
        // Set regeneration state to hide subsequent assistant messages
        setRegeneratingMessageId(messageId);
        
        // Find the message and any subsequent AI responses to remove them
        const messageIndex = activeThread.messages.findIndex(msg => msg.id === messageId);
        if (messageIndex === -1) {
          addToast('Message not found.', ToastType.ERROR);
          setRegeneratingMessageId(null);
          return;
        }
        
        // Keep messages up to and including the edited user message
        const messagesUpToUser = activeThread.messages.slice(0, messageIndex + 1);
        
        // Update the user message content locally first
        messagesUpToUser[messageIndex] = { 
          ...messagesUpToUser[messageIndex], 
          content: newContent 
        };
        
        // Update UI to show only messages up to the edited user message
        setActiveThread(prev => prev ? { ...prev, messages: messagesUpToUser } : null);
        
        // Update the message content in backend
        await api.editMessage(user.id, activeThreadId, messageId, newContent);
        
        addToast('Message updated. Generating new response...', ToastType.INFO);
        
        // Send the edited message as a new request (reprocess the question)
        await handleSendMessage(newContent, activeThread.language || 'ENG');
        
      } catch (error) {
          console.error('Error editing message:', error);
          addToast('Failed to edit message. Please try again.', ToastType.ERROR);
          setRegeneratingMessageId(null);
      }
  }

  const handleReactMessage = async (messageId: string, reaction: 'like' | 'dislike') => {
      if(!activeThreadId || !activeThread) {
        addToast('No active thread selected.', ToastType.ERROR);
        return;
      }
      
      try {
          await api.reactToMessage(user.id, activeThreadId, messageId, reaction);
          
          // Update the reaction in the local state immediately
          const updatedMessages = activeThread.messages.map(msg => 
            msg.id === messageId ? { ...msg, reaction } : msg
          );
          setActiveThread({ ...activeThread, messages: updatedMessages });
          
          // Show success message
          addToast('Thank you for your feedback!', ToastType.SUCCESS);
          
      } catch (error) {
          console.error('Error saving reaction:', error);
          addToast('Failed to save your reaction. Please try again.', ToastType.ERROR);
      }
  }

  const handleRetryMessage = async (userMessageContent: string, userMessageId: string) => {
      if(!activeThreadId || !activeThread) return;
      
      // Set regeneration state to hide subsequent assistant messages
      setRegeneratingMessageId(userMessageId);
      
      // Start processing indicator for current thread
      if (activeThreadId) {
          threadStateManager.setProcessing(activeThreadId, true);
      }
      
      try {
          // Find the user message and any subsequent AI responses to remove them
          const messageIndex = activeThread.messages.findIndex(msg => msg.id === userMessageId);
          if (messageIndex === -1) return;
          
          // Keep messages up to and including the user message, remove any AI responses after it
          const messagesUpToUser = activeThread.messages.slice(0, messageIndex + 1);
          
          // Update UI to show only messages up to the user message
          setActiveThread(prev => prev ? { ...prev, messages: messagesUpToUser } : null);
          
          // Add minimum delay for better UX
          const startTime = Date.now();
          
          // Generate new AI response
          const currentState = threadStateManager.getThreadState(activeThreadId);
          const assistantMessage = await api.getAssistantResponse(
              userMessageContent, 
              currentState.useWebSearch, 
              activeThread.language || 'ENG', 
              user.id, 
              activeThreadId,
              messagesUpToUser
          );

          // Ensure minimum processing time
          const elapsed = Date.now() - startTime;
          const minDelay = 1500;
          if (elapsed < minDelay) {
              await new Promise(resolve => setTimeout(resolve, minDelay - elapsed));
          }

          // Reload the complete thread to get the updated messages
          const updatedThread = await api.getThreadWithMessages(activeThreadId);
          setActiveThread(updatedThread);
          
          // Update threads list
          setThreads(prev => prev.map(t => t.id === activeThreadId ? {
            ...t,
            lastModified: updatedThread.lastModified,
            messageCount: updatedThread.messages.length
          } : t));
          
          // Clear regeneration state when retry is successful
          setRegeneratingMessageId(null);
          
          // This is for retry functionality on the current active thread
          // No notification needed since user is already on this thread
          
      } catch (error) {
          console.error('Error retrying message:', error);
          addToast('Error generating new response. Please try again.', ToastType.ERROR);
      } finally {
          if (activeThreadId) {
              threadStateManager.setProcessing(activeThreadId, false);
          }
          // Clear regeneration state regardless of success or failure
          setRegeneratingMessageId(null);
      }
  }

    const handleDeleteAllChats = async () => {
        try {
            await api.deleteAllChatsForUser(user.id);
            // Update threads to show 0 messages (threads remain permanent)
            setThreads(prev => prev.map(t => ({
              ...t,
              messageCount: 0,
              lastModified: new Date().toISOString()
            })));
            setActiveThreadId(null);
            setActiveThread(null);
            // Keep user's preferred language - don't reset
            setShowSettings(false);
            addToast('All thread messages cleared successfully.', ToastType.SUCCESS);
        } catch (error) {
            addToast('Failed to clear all thread messages.', ToastType.ERROR);
        } finally {
            setShowDeleteAllConfirm(false);
        }
    };

    const handleDeleteAccount = async () => {
        try {
            await api.deleteUserAccount(user.id);
            addToast('Your account has been successfully deleted.', ToastType.SUCCESS);
            onLogout(); // Log out the user after deletion
        } catch (error) {
            addToast('Failed to delete your account.', ToastType.ERROR);
        } finally {
            setShowDeleteAccountConfirm(false);
        }
    };
    
    const handleGoHome = () => {
      setActiveThreadId(null);
      setActiveThread(null);
      setShowSettings(false);
    };

    const handleFAQClick = async (question: string, targetThread: string) => {
      try {
        // Find the thread that matches the target thread type
        const targetThreadObj = threads.find(thread => {
          // Map targetThread to the actual thread names
          const threadMapping = {
            'AWS_DISCUSSION': 'AWS Discussion',
            'AZURE_DISCUSSION': 'Azure Discussion', 
            'SMART_LEARNER': 'Smart Learner'
          };
          return thread.name === threadMapping[targetThread as keyof typeof threadMapping];
        });

        if (!targetThreadObj) {
          addToast('Thread not found. Please try again.', ToastType.ERROR);
          return;
        }

        // Navigate to the thread
        await handleSelectThread(targetThreadObj.id);
        
        // Send the FAQ question as a message with thread's language
        const targetState = threadStateManager.getThreadState(targetThreadObj.id);
        handleSendMessage(question, targetState.language, targetThreadObj.id);
      } catch (error) {
        console.error('Error handling FAQ click:', error);
        addToast('Error starting conversation. Please try again.', ToastType.ERROR);
      }
    };


  return (
    <div className="flex h-screen w-screen bg-light-main dark:bg-dark-main overflow-hidden text-light-text dark:text-dark-text relative">
      <Sidebar
        user={user}
        threads={threads}
        activeThreadId={activeThreadId}
        onSelectThread={handleSelectThread}
        onDeleteThread={(id) => setThreadToDelete(id)}
        onShowSettings={() => { setShowSettings(true); setActiveThreadId(null); }}
        theme={theme}
        setTheme={setTheme}
        isOpen={sidebarOpen}
        smartLearnerUnread={smartLearnerUnread}
        isAnyThreadProcessing={Array.from(threadStateManager.threadStates.values()).some(state => state.isProcessing)}
      />
      <div className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${sidebarOpen ? 'md:ml-80' : 'ml-0'}`}>
        <ChatHeader 
            threadName={activeThread?.name || 'Cloud ERA'}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            isSidebarOpen={sidebarOpen}
            onGoHome={handleGoHome}
        />
        {showSettings ? (
          <SettingsPage 
              user={user} 
              onLogout={() => setShowLogoutConfirm(true)} 
              theme={theme} 
              setTheme={setTheme}
              onDeleteAllChats={() => setShowDeleteAllConfirm(true)}
              onDeleteAccount={() => setShowDeleteAccountConfirm(true)}
          />
        ) : (
          <div className="flex flex-col h-full overflow-hidden">
            <ChatArea
              activeThread={activeThread}
              onSendMessage={handleSendMessage}
              onEditMessage={handleEditMessage}
              onReactMessage={handleReactMessage}
              onRetryMessage={handleRetryMessage}
              onFAQClick={handleFAQClick}
              isProcessing={activeThreadId ? threadStateManager.getIsProcessing(activeThreadId) : false}
              userEmail={user.email}
              regeneratingMessageId={regeneratingMessageId}
            />
            <ChatInput 
              onSendMessage={handleSendMessage} 
              isProcessing={activeThreadId ? threadStateManager.getIsProcessing(activeThreadId) : false}
              useWebSearch={currentThreadState?.useWebSearch ?? true}
              setUseWebSearch={(value: boolean) => {
                if (activeThreadId) threadStateManager.setUseWebSearch(activeThreadId, value);
              }}
              language={currentThreadState?.language ?? 'ENG'}
              setLanguage={(lang: 'ENG' | 'SIN') => {
                if (activeThreadId) threadStateManager.setLanguage(activeThreadId, lang);
              }}
              isLanguageLocked={isLanguageLocked}
              message={currentThreadState?.inputMessage ?? ''}
              setMessage={(message: string) => {
                if (activeThreadId) threadStateManager.setInputMessage(activeThreadId, message);
              }}
              onClearMessage={() => {
                if (activeThreadId) threadStateManager.clearThreadInput(activeThreadId);
              }}
            />
          </div>
        )}
      </div>
      
      {/* Modals */}
      <Modal isOpen={!!threadToDelete} onClose={() => setThreadToDelete(null)} title="Clear Messages">
          <p className="text-light-text-secondary dark:text-dark-text-secondary mb-6">Are you sure you want to clear all messages from this chat thread? This action cannot be undone.</p>
          <div className="flex justify-end space-x-3"><Button variant="secondary" onClick={() => setThreadToDelete(null)}>Cancel</Button><Button variant="danger" onClick={handleDeleteThread}>Clear Messages</Button></div>
      </Modal>

      <Modal isOpen={showLogoutConfirm} onClose={() => setShowLogoutConfirm(false)} title="Confirm Logout">
           <p className="text-light-text-secondary dark:text-dark-text-secondary mb-6">Are you sure you want to log out?</p>
           <div className="flex justify-end space-x-3"><Button variant="secondary" onClick={() => setShowLogoutConfirm(false)}>Cancel</Button><Button variant="danger" onClick={() => {setShowLogoutConfirm(false); onLogout();}}>Log Out</Button></div>
      </Modal>

      <Modal isOpen={showDeleteAllConfirm} onClose={() => setShowDeleteAllConfirm(false)} title="Clear All Messages?">
           <p className="text-light-text-secondary dark:text-dark-text-secondary mb-6">This will permanently clear all messages from your conversation threads. The thread structure will remain. This action cannot be undone.</p>
           <div className="flex justify-end space-x-3"><Button variant="secondary" onClick={() => setShowDeleteAllConfirm(false)}>Cancel</Button><Button variant="danger" onClick={handleDeleteAllChats}>Clear All Messages</Button></div>
      </Modal>
      
      <Modal isOpen={showDeleteAccountConfirm} onClose={() => setShowDeleteAccountConfirm(false)} title="Delete Your Account?">
           <p className="text-light-text-secondary dark:text-dark-text-secondary mb-6">Are you sure? This will permanently delete your account and all associated data, including your chat history. This action is irreversible.</p>
           <div className="flex justify-end space-x-3"><Button variant="secondary" onClick={() => setShowDeleteAccountConfirm(false)}>Cancel</Button><Button variant="danger" onClick={handleDeleteAccount}>Yes, Delete My Account</Button></div>
      </Modal>

    </div>
  );
};

export default HomePage;
