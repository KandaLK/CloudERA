import { useState, useEffect, useRef, useCallback } from 'react';
import { WorkflowState } from '../components/chat/WorkflowStateDisplay';
import { config } from '../utils/config';

interface UseWorkflowStateReturn {
  workflowState: WorkflowState | null;
  isConnected: boolean;
  connectionError: string | null;
  reconnect: () => void;
}

const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const useWorkflowState = (threadId: string | null): UseWorkflowStateReturn => {
  const [workflowState, setWorkflowState] = useState<WorkflowState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldConnectRef = useRef(true);
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      console.log(`[WorkflowState] Disconnecting SSE for thread ${threadId}`);
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (cleanupTimeoutRef.current) {
      clearTimeout(cleanupTimeoutRef.current);
      cleanupTimeoutRef.current = null;
    }
    
    setIsConnected(false);
    setWorkflowState(null);
  }, [threadId]);

  // Clear workflow state when backend sends completion signal
  const clearWorkflowState = useCallback(() => {
    console.log(`[WorkflowState] Clearing workflow state for thread ${threadId}`);
    setWorkflowState(null);
  }, [threadId]);

  const connect = useCallback(() => {
    const authToken = getAuthToken();
    if (!threadId || !authToken) {
      console.log('[WorkflowState] No thread ID or auth token, skipping SSE connection');
      return;
    }

    if (!shouldConnectRef.current) {
      console.log('[WorkflowState] Connection disabled, skipping SSE connection');
      return;
    }

    // Disconnect existing connection
    disconnect();

    console.log(`[WorkflowState] Connecting SSE for thread ${threadId}`);
    
    try {
      const baseUrl = config.apiBaseUrl;
      // Add auth token as query parameter since EventSource doesn't support headers
      const url = `${baseUrl}/api/chat/stream/${threadId}?token=${encodeURIComponent(authToken)}`;
      
      const eventSource = new EventSource(url);

      eventSource.onopen = () => {
        console.log(`[WorkflowState] SSE connection opened for thread ${threadId}`);
        setIsConnected(true);
        setConnectionError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'state_update') {
            const newState: WorkflowState = {
              stage: data.stage,
              message: data.message,
              progress: data.progress,
              details: data.details,
              timestamp: data.timestamp
            };
            
            setWorkflowState(newState);
            console.log(`[WorkflowState] Received state update: ${data.stage} - ${data.message}`);
            
            // Set fallback cleanup timeout (30 seconds)
            if (cleanupTimeoutRef.current) {
              clearTimeout(cleanupTimeoutRef.current);
            }
            cleanupTimeoutRef.current = setTimeout(() => {
              console.log(`[WorkflowState] Fallback cleanup triggered for thread ${threadId}`);
              clearWorkflowState();
            }, 30000);
          } else if (data.type === 'connection') {
            console.log(`[WorkflowState] Connection confirmed: ${data.message}`);
          } else if (data.type === 'completed' || data.type === 'cleanup') {
            // Backend signals workflow completion - clear state
            console.log(`[WorkflowState] Workflow completed, clearing state`);
            clearWorkflowState();
          } else if (data.type === 'ping') {
            // Keepalive ping, no action needed
          }
        } catch (error) {
          console.error('[WorkflowState] Error parsing SSE message:', error, event.data);
        }
      };

      eventSource.onerror = (error) => {
        console.error(`[WorkflowState] SSE error for thread ${threadId}:`, error);
        setConnectionError('Connection error occurred');
        setIsConnected(false);
        
        // Automatic reconnection with exponential backoff
        if (shouldConnectRef.current && eventSource.readyState === EventSource.CLOSED) {
          console.log(`[WorkflowState] Attempting to reconnect in 3 seconds...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            if (shouldConnectRef.current) {
              connect();
            }
          }, 3000);
        }
      };

      eventSourceRef.current = eventSource;

    } catch (error) {
      console.error(`[WorkflowState] Failed to create SSE connection for thread ${threadId}:`, error);
      setConnectionError('Failed to establish connection');
      setIsConnected(false);
    }
  }, [threadId, disconnect]);

  const reconnect = useCallback(() => {
    console.log(`[WorkflowState] Manual reconnection requested for thread ${threadId}`);
    setConnectionError(null);
    connect();
  }, [connect, threadId]);

  // Connect when thread ID changes
  useEffect(() => {
    shouldConnectRef.current = true;
    connect();
    
    return () => {
      shouldConnectRef.current = false;
      disconnect();
    };
  }, [threadId, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      shouldConnectRef.current = false;
      disconnect();
    };
  }, [disconnect]);

  return {
    workflowState,
    isConnected,
    connectionError,
    reconnect
  };
};