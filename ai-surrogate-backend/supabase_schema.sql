-- AI Surrogate Database Schema
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Threads table (chat conversations)
CREATE TABLE IF NOT EXISTS public.threads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL DEFAULT 'New Chat',
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    thread_id UUID REFERENCES public.threads(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    emotion TEXT,
    audio_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Memory table (persistent AI memory per user)
CREATE TABLE IF NOT EXISTS public.memory (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    summary TEXT NOT NULL,
    context TEXT,
    importance_score INTEGER DEFAULT 1 CHECK (importance_score BETWEEN 1 AND 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Files table (for voice recordings and other uploads)
CREATE TABLE IF NOT EXISTS public.files (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    thread_id UUID REFERENCES public.threads(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.files ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Users policies
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Threads policies
CREATE POLICY "Users can view own threads" ON public.threads
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own threads" ON public.threads
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own threads" ON public.threads
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own threads" ON public.threads
    FOR DELETE USING (auth.uid() = user_id);

-- Messages policies
CREATE POLICY "Users can view messages from own threads" ON public.messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.threads 
            WHERE threads.id = messages.thread_id 
            AND threads.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages in own threads" ON public.messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.threads 
            WHERE threads.id = messages.thread_id 
            AND threads.user_id = auth.uid()
        )
    );

-- Memory policies
CREATE POLICY "Users can view own memory" ON public.memory
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own memory" ON public.memory
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own memory" ON public.memory
    FOR UPDATE USING (auth.uid() = user_id);

-- Files policies
CREATE POLICY "Users can view own files" ON public.files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own files" ON public.files
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own files" ON public.files
    FOR DELETE USING (auth.uid() = user_id);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS threads_user_id_idx ON public.threads(user_id);
CREATE INDEX IF NOT EXISTS threads_last_message_at_idx ON public.threads(last_message_at DESC);
CREATE INDEX IF NOT EXISTS messages_thread_id_idx ON public.messages(thread_id);
CREATE INDEX IF NOT EXISTS messages_created_at_idx ON public.messages(created_at DESC);
CREATE INDEX IF NOT EXISTS memory_user_id_idx ON public.memory(user_id);
CREATE INDEX IF NOT EXISTS files_user_id_idx ON public.files(user_id);

-- Functions to automatically update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threads_updated_at BEFORE UPDATE ON public.threads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_memory_updated_at BEFORE UPDATE ON public.memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update thread's last_message_at
CREATE OR REPLACE FUNCTION update_thread_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.threads 
    SET last_message_at = NEW.created_at 
    WHERE id = NEW.thread_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update thread timestamp when new message is added
CREATE TRIGGER update_thread_last_message_trigger 
    AFTER INSERT ON public.messages
    FOR EACH ROW EXECUTE FUNCTION update_thread_last_message();

-- Enable realtime for live chat updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;
ALTER PUBLICATION supabase_realtime ADD TABLE public.threads;