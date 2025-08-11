import { useState, useCallback, useEffect } from 'react';

export interface ThreadState {
  id: string;
  isProcessing: boolean;
  language: 'ENG' | 'SIN';
  inputMessage: string;
  useWebSearch: boolean;
  isLanguageLocked: boolean;
}

interface ThreadStateManager {
  threadStates: Map<string, ThreadState>;
  getThreadState: (threadId: string) => ThreadState;
  updateThreadState: (threadId: string, updates: Partial<ThreadState>) => void;
  setProcessing: (threadId: string, processing: boolean) => void;
  setLanguage: (threadId: string, language: 'ENG' | 'SIN') => void;
  setInputMessage: (threadId: string, message: string) => void;
  setUseWebSearch: (threadId: string, useWebSearch: boolean) => void;
  clearThreadInput: (threadId: string) => void;
  initializeThread: (threadId: string, defaultLanguage?: 'ENG' | 'SIN') => void;
  cleanupThread: (threadId: string) => void;
  getIsProcessing: (threadId: string) => boolean;
  persistThreadStates: () => void;
  loadThreadStates: () => void;
}

const DEFAULT_THREAD_STATE: Omit<ThreadState, 'id'> = {
  isProcessing: false,
  language: 'ENG',
  inputMessage: '',
  useWebSearch: true,
  isLanguageLocked: false,
};

const STORAGE_KEY = 'thread_states_v1';

export const useThreadState = (defaultLanguage: 'ENG' | 'SIN' = 'ENG'): ThreadStateManager => {
  const [threadStates, setThreadStates] = useState<Map<string, ThreadState>>(new Map());

  // Load thread states from localStorage on initialization
  const loadThreadStates = useCallback(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsedStates = JSON.parse(stored);
        const stateMap = new Map<string, ThreadState>();
        
        Object.entries(parsedStates).forEach(([threadId, state]) => {
          stateMap.set(threadId, {
            ...(state as ThreadState),
            // Reset runtime states
            isProcessing: false,
            inputMessage: '',
          });
        });
        
        setThreadStates(stateMap);
      }
    } catch (error) {
      console.error('Error loading thread states:', error);
    }
  }, []);

  // Persist thread states to localStorage
  const persistThreadStates = useCallback(() => {
    try {
      const statesToPersist: { [key: string]: Partial<ThreadState> } = {};
      
      threadStates.forEach((state, threadId) => {
        // Only persist non-runtime states
        statesToPersist[threadId] = {
          id: state.id,
          language: state.language,
          useWebSearch: state.useWebSearch,
          isLanguageLocked: state.isLanguageLocked,
        };
      });
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(statesToPersist));
    } catch (error) {
      console.error('Error persisting thread states:', error);
    }
  }, [threadStates]);

  // Load states on mount
  useEffect(() => {
    loadThreadStates();
  }, [loadThreadStates]);

  // Persist states whenever they change
  useEffect(() => {
    if (threadStates.size > 0) {
      persistThreadStates();
    }
  }, [threadStates, persistThreadStates]);

  const getThreadState = useCallback((threadId: string): ThreadState => {
    const existing = threadStates.get(threadId);
    if (existing) {
      return existing;
    }

    // Create default state if thread doesn't exist
    const defaultState: ThreadState = {
      id: threadId,
      ...DEFAULT_THREAD_STATE,
      language: defaultLanguage,
    };
    
    return defaultState;
  }, [threadStates, defaultLanguage]);

  const updateThreadState = useCallback((threadId: string, updates: Partial<ThreadState>) => {
    setThreadStates(prev => {
      const newMap = new Map(prev);
      const currentState = prev.get(threadId) || {
        id: threadId,
        ...DEFAULT_THREAD_STATE,
        language: defaultLanguage,
      };
      
      newMap.set(threadId, { ...currentState, ...updates });
      return newMap;
    });
  }, [defaultLanguage]);

  const setProcessing = useCallback((threadId: string, processing: boolean) => {
    updateThreadState(threadId, { isProcessing: processing });
  }, [updateThreadState]);

  const setLanguage = useCallback((threadId: string, language: 'ENG' | 'SIN') => {
    updateThreadState(threadId, { language });
  }, [updateThreadState]);

  const setInputMessage = useCallback((threadId: string, message: string) => {
    updateThreadState(threadId, { inputMessage: message });
  }, [updateThreadState]);

  const setUseWebSearch = useCallback((threadId: string, useWebSearch: boolean) => {
    updateThreadState(threadId, { useWebSearch });
  }, [updateThreadState]);

  const clearThreadInput = useCallback((threadId: string) => {
    updateThreadState(threadId, { inputMessage: '' });
  }, [updateThreadState]);

  const initializeThread = useCallback((threadId: string, threadDefaultLanguage?: 'ENG' | 'SIN') => {
    if (!threadStates.has(threadId)) {
      const initialState: ThreadState = {
        id: threadId,
        ...DEFAULT_THREAD_STATE,
        language: threadDefaultLanguage || defaultLanguage,
      };
      
      setThreadStates(prev => {
        const newMap = new Map(prev);
        newMap.set(threadId, initialState);
        return newMap;
      });
    }
  }, [threadStates, defaultLanguage]);

  const cleanupThread = useCallback((threadId: string) => {
    setThreadStates(prev => {
      const newMap = new Map(prev);
      newMap.delete(threadId);
      return newMap;
    });
  }, []);

  const getIsProcessing = useCallback((threadId: string): boolean => {
    const state = threadStates.get(threadId);
    return state?.isProcessing || false;
  }, [threadStates]);

  return {
    threadStates,
    getThreadState,
    updateThreadState,
    setProcessing,
    setLanguage,
    setInputMessage,
    setUseWebSearch,
    clearThreadInput,
    initializeThread,
    cleanupThread,
    getIsProcessing,
    persistThreadStates,
    loadThreadStates,
  };
};