export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  preferences?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Thread {
  id: string;
  user_id: string;
  title: string;
  last_message_at: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface Message {
  id: string;
  thread_id: string;
  role: 'user' | 'assistant';
  content: string;
  emotion?: string;
  audio_url?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Memory {
  id: string;
  user_id: string;
  summary: string;
  context?: string;
  importance_score: number;
  created_at: string;
  updated_at: string;
}

export interface FileRecord {
  id: string;
  user_id: string;
  thread_id?: string;
  file_url: string;
  file_type: string;
  file_size?: number;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface ChatState {
  threads: Thread[];
  currentThread?: Thread;
  messages: Message[];
  isLoading: boolean;
  isRecording: boolean;
  user?: User;
}

export interface VoiceRecording {
  uri: string;
  duration: number;
  size: number;
}

export type RootStackParamList = {
  Onboarding: undefined;
  Auth: undefined;
  Main: undefined;
  Chat: { threadId?: string };
  Settings: undefined;
  Profile: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Settings: undefined;
  Profile: undefined;
};