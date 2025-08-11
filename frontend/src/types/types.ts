
export enum Theme {
  LIGHT = "light",
  DARK = "dark",
}

export enum MessageAuthor {
  USER = "user",
  ASSISTANT = "assistant",
}

export interface Message {
  id: string;
  author: MessageAuthor;
  content: string;
  timestamp: string;
  reaction?: 'like' | 'dislike' | null;
}

export interface ChatThread {
  id: string;
  name: string;
  messages: Message[];
  lastModified: string;
  language?: 'ENG' | 'SIN';
  messageCount?: number; // For display in thread list
}

export interface User {
  id: string;
  username: string;
  email: string;
  created_at?: string;
  theme?: string;
  language?: string;
  is_admin?: boolean;
}

export enum ToastType {
  SUCCESS = 'SUCCESS',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  INFO = 'INFO',
}

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
}


export interface OnboardingStep {
  selector: string;
  title: string;
  description: string;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'bottom-left-corner';
}