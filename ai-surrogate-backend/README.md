# AI Surrogate Backend

FastAPI backend server for AI Surrogate app with LangGraph agents, Gemini AI, and voice processing.

## Features

- 🤖 Multi-agent AI system with LangGraph
- 🧠 Google Gemini 1.5 Flash integration
- 🎤 Whisper speech-to-text
- 🔊 gTTS text-to-speech
- 📊 Memory and emotion tracking
- 🔐 Supabase authentication
- 🚀 FastAPI with async support

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the server:
```bash
python main.py
```

Server will be available at `http://localhost:8000`

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

### Docker
```bash
docker build -t ai-surrogate-backend .
docker run -p 8000:8000 --env-file .env ai-surrogate-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## Environment Variables

Required environment variables:

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `GEMINI_API_KEY` - Google AI Studio API key

## API Endpoints

### Authentication
- `POST /auth/login` - Login user
- `POST /auth/register` - Register user
- `GET /auth/me` - Get current user

### Chat
- `POST /chat/` - Send message and get AI response
- `GET /chat/{thread_id}/messages` - Get conversation history

### Voice
- `POST /voice/transcribe` - Transcribe audio to text
- `POST /voice/speak` - Convert text to speech
- `POST /voice/process` - Full voice conversation flow

### Memory
- `GET /memory/` - Get user memories
- `POST /memory/analyze` - Analyze conversation patterns

## Architecture

- **FastAPI** - Modern Python web framework
- **LangGraph** - Agent orchestration system
- **Supabase** - Database and authentication
- **Whisper** - Local speech recognition
- **gTTS** - Text-to-speech synthesis
- **Gemini 1.5 Flash** - AI language model