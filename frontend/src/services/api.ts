import { User, ChatThread, Message, MessageAuthor } from '../types/types';
import { config, logger } from '../utils/config';

// Backend API configuration from environment
const API_BASE_URL = config.apiBaseUrl;

logger.debug('API configured with base URL:', API_BASE_URL);

// Helper functions for token management
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

const setAuthToken = (token: string) => {
  localStorage.setItem('auth_token', token);
};

const removeAuthToken = () => {
  localStorage.removeItem('auth_token');
};

const getStoredUser = (): User | null => {
  try {
    const userJson = localStorage.getItem('current_user');
    return userJson ? JSON.parse(userJson) : null;
  } catch (e) {
    return null;
  }
};

export const getCurrentUser = async (): Promise<User | null> => {
  try {
    const token = getAuthToken();
    if (!token) return null;
    
    const response = await apiRequest('/api/users/me');
    return response as User;
  } catch (error) {
    // If token validation fails, clear stored data
    removeAuthToken();
    localStorage.removeItem('current_user');
    return null;
  }
};

const setCurrentUser = (user: User) => {
  localStorage.setItem('current_user', JSON.stringify(user));
};

// API helper function
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      removeAuthToken();
      localStorage.removeItem('current_user');
      window.location.reload();
    }
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
};


// --- API Functions ---

export const login = async (email: string, password: string): Promise<User> => {
  try {
    const response = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    setAuthToken(response.access_token);
    setCurrentUser(response.user);
    
    return response.user;
  } catch (error) {
    throw new Error('Invalid email or password.');
  }
};

export const signUp = async (username: string, email: string, password: string): Promise<User> => {
  try {
    const response = await apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });

    // Auto-login after successful registration
    const loginResponse = await login(email, password);
    return loginResponse;
  } catch (error) {
    throw new Error('Registration failed. User may already exist.');
  }
};

export const getChatThreads = async (userId: string): Promise<ChatThread[]> => {
  try {
    const response = await apiRequest('/api/threads');
    // Transform backend response to match frontend ChatThread interface
    return response.map((thread: any) => ({
      id: thread.id,
      name: thread.name,
      messages: [], // Messages loaded separately when thread is selected
      lastModified: thread.last_modified,
      language: thread.language || 'ENG',
      messageCount: thread.message_count || 0 // Add message count property for display
    }));
  } catch (error) {
    console.error('Error fetching chat threads:', error);
    return [];
  }
};

export const createChatThread = async (userId: string, name: string, initialMessage?: Message): Promise<ChatThread> => {
  try {
    const response = await apiRequest('/api/threads', {
      method: 'POST',
      body: JSON.stringify({
        name: name,
        language: 'ENG'
      }),
    });

    // Transform response to match frontend interface
    const newThread: ChatThread = {
      id: response.id,
      name: response.name,
      messages: [], // Messages will be loaded when thread is selected
      lastModified: response.last_modified,
      language: response.language || 'ENG',
      messageCount: 1 // Thread created with welcome message
    };
    
    return newThread;
  } catch (error) {
    console.error('Error creating thread:', error);
    throw new Error('Failed to create thread');
  }
};

export const deleteChatThread = async (userId: string, threadId: string): Promise<void> => {
  try {
    await apiRequest(`/api/threads/${threadId}`, {
      method: 'DELETE',
    });
  } catch (error) {
    console.error('Error deleting thread:', error);
    throw new Error('Failed to delete thread');
  }
};

export const renameChatThread = async (userId: string, threadId: string, newName: string): Promise<ChatThread> => {
  try {
    const response = await apiRequest(`/api/threads/${threadId}`, {
      method: 'PUT',
      body: JSON.stringify({
        name: newName
      }),
    });

    // Transform response to match frontend interface
    const updatedThread: ChatThread = {
      id: response.id,
      name: response.name,
      messages: [], // Messages loaded separately when needed
      lastModified: response.last_modified,
      language: response.language || 'ENG',
    };
    
    return updatedThread;
  } catch (error) {
    console.error('Error renaming thread:', error);
    throw new Error('Failed to rename thread');
  }
};

export const addMessageToThread = async (userId: string, threadId: string, message: Message): Promise<ChatThread> => {
  // Messages are now handled through the chat endpoint, not directly added to threads
  // This function is for compatibility - in practice, messages are added via sendMessage
  try {
    const thread = await getThreadWithMessages(threadId);
    thread.messages.push(message);
    thread.lastModified = new Date().toISOString();
    return thread;
  } catch (error) {
    console.error('Error adding message to thread:', error);
    throw new Error('Failed to add message');
  }
};

export const getThreadWithMessages = async (threadId: string): Promise<ChatThread> => {
  try {
    const response = await apiRequest(`/api/threads/${threadId}`);
    
    // Transform backend response to frontend format
    const thread: ChatThread = {
      id: response.id,
      name: response.name,
      messages: response.messages.map((msg: any) => ({
        id: msg.id,
        author: msg.author,
        content: msg.content,
        timestamp: msg.timestamp,
        reaction: msg.reaction
      })),
      lastModified: response.last_modified,
      language: response.language || 'ENG'
    };
    
    return thread;
  } catch (error) {
    console.error('Error fetching thread with messages:', error);
    throw new Error('Failed to fetch thread');
  }
};

export const getAssistantResponse = async (
    content: string, 
    useWebSearch: boolean, 
    language: 'ENG' | 'SIN',
    userId?: string,
    threadId?: string,
    chatHistory?: Message[]
): Promise<Message> => {
    try {
        // Call the backend chat API
        const response = await apiRequest('/api/chat', {
            method: 'POST',
            body: JSON.stringify({
                message: content,
                thread_id: threadId,
                language: language,
                use_web_search: useWebSearch
            }),
        });

        const assistantMessage: Message = {
            id: response.message_id,
            author: MessageAuthor.ASSISTANT,
            content: response.response || 'I apologize, but I received an empty response.',
            timestamp: response.created_at,
            reaction: null,
        };

        return assistantMessage;
        
    } catch (error) {
        console.error('Error calling backend:', error);
        
        // Fallback response
        let responseContent = `I encountered an issue connecting to the Cloud & Security AI assistant. Please check your connection and try again.`;
        
        if (language === 'SIN') {
            responseContent = `වලාකුළු සහ ජාල AI සහායකයා සමඟ සම්බන්ධ වීමේදී ගැටලුවක් ඇති විය. කරුණාකර නැවත උත්සාහ කරන්න.`;
        }
        
        const assistantMessage: Message = {
            id: `msg-asst-${Date.now()}`,
            author: MessageAuthor.ASSISTANT,
            content: responseContent,
            timestamp: new Date().toISOString(),
            reaction: null,
        };
        
        return assistantMessage;
    }
};

export const editMessage = async (userId: string, threadId: string, messageId: string, newContent: string): Promise<void> => {
  try {
    await apiRequest(`/api/chat/messages/${messageId}`, {
      method: 'PUT',
      body: JSON.stringify({ content: newContent }),
    });
  } catch (error) {
    console.error('Error editing message:', error);
    throw new Error('Failed to edit message');
  }
};

export const reactToMessage = async (userId: string, threadId: string, messageId: string, reaction: 'like' | 'dislike'): Promise<void> => {
  try {
    await apiRequest('/api/reactions', {
      method: 'POST',
      body: JSON.stringify({
        message_id: messageId,
        reaction_type: reaction,
      }),
    });
  } catch (error) {
    console.error('Error saving reaction:', error);
    throw new Error('Failed to save reaction');
  }
};

export const logout = (): void => {
  removeAuthToken();
  localStorage.removeItem('current_user');
};

export const setThreadLanguage = async (userId: string, threadId: string, language: 'ENG' | 'SIN'): Promise<void> => {
  // Language setting can be implemented later if needed
  console.log(`Setting thread ${threadId} language to ${language}`);
};

export const deleteAllChatsForUser = async (userId: string): Promise<void> => {
  try {
    const threads = await getChatThreads(userId);
    for (const thread of threads) {
      await deleteChatThread(userId, thread.id);
    }
  } catch (error) {
    console.error('Error deleting all chats:', error);
    throw new Error('Failed to delete all chats');
  }
};

export const deleteUserAccount = async (userId: string): Promise<void> => {
  try {
    await apiRequest('/api/users/me', {
      method: 'DELETE',
    });
  } catch (error) {
    console.error('Error deleting account:', error);
    throw new Error('Failed to delete account');
  }
};

// Export User type as it's expected by consuming components
export type { User };