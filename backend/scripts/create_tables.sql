-- PostgreSQL Table Creation Script for Cloud ERA
-- Run this script after creating the database and user
-- Connect as: psql -U cloud_era_user -d "cloud-web" -f create_tables.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE thread_type AS ENUM (
    'AWS_DISCUSSION',
    'AZURE_DISCUSSION', 
    'SMART_LEARNER'
);

CREATE TYPE message_author AS ENUM (
    'user',
    'assistant'
);

CREATE TYPE reaction_type AS ENUM (
    'like',
    'dislike'
);

CREATE TYPE reaction_log_type AS ENUM (
    'like',
    'dislike',
    'removed'
);

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    theme VARCHAR(10) DEFAULT 'light',
    preferred_language VARCHAR(3) DEFAULT 'ENG'
);

-- Create indexes for users table
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create chat_threads table
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_modified TIMESTAMPTZ DEFAULT NOW(),
    language VARCHAR(3) DEFAULT 'ENG',
    is_permanent BOOLEAN DEFAULT FALSE NOT NULL,
    thread_type thread_type,
    is_active BOOLEAN DEFAULT FALSE NOT NULL
);

-- Create indexes for chat_threads table
CREATE INDEX idx_chat_threads_user_id ON chat_threads(user_id);
CREATE INDEX idx_chat_threads_created_at ON chat_threads(created_at);
CREATE INDEX idx_chat_threads_last_modified ON chat_threads(last_modified);
CREATE INDEX idx_chat_threads_thread_type ON chat_threads(thread_type);

-- Create trigger to update last_modified
CREATE OR REPLACE FUNCTION update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chat_threads_last_modified
    BEFORE UPDATE ON chat_threads
    FOR EACH ROW
    EXECUTE FUNCTION update_last_modified();

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    author message_author NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    reaction reaction_type
);

-- Create indexes for messages table
CREATE INDEX idx_messages_thread_id ON messages(thread_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_author ON messages(author);

-- Create user_reaction_logs table
CREATE TABLE user_reaction_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_name VARCHAR(50) NOT NULL,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    question_content TEXT,
    response_content TEXT NOT NULL,
    reaction_type reaction_log_type NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    session_info JSONB
);

-- Create indexes for user_reaction_logs table
CREATE INDEX idx_user_reaction_logs_user_id ON user_reaction_logs(user_id);
CREATE INDEX idx_user_reaction_logs_message_id ON user_reaction_logs(message_id);
CREATE INDEX idx_user_reaction_logs_thread_id ON user_reaction_logs(thread_id);
CREATE INDEX idx_user_reaction_logs_reaction_type ON user_reaction_logs(reaction_type);
CREATE INDEX idx_user_reaction_logs_timestamp ON user_reaction_logs(timestamp);

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts with authentication and preferences';
COMMENT ON TABLE chat_threads IS 'Conversation threads organized by user and type';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE user_reaction_logs IS 'Permanent audit log of user feedback on responses';

COMMENT ON COLUMN users.preferred_language IS 'User language preference: ENG or SIN';
COMMENT ON COLUMN chat_threads.thread_type IS 'Type of discussion: AWS_DISCUSSION, AZURE_DISCUSSION, or SMART_LEARNER';
COMMENT ON COLUMN messages.author IS 'Message sender: user or assistant';
COMMENT ON COLUMN user_reaction_logs.session_info IS 'Additional context stored as JSON';