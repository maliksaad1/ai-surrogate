# AI Surrogate Backend

FastAPI backend server for AI Surrogate app with custom multi-agent AI system, Gemini AI, and voice processing.

🌐 **Deployed at**: https://ai-surrogate.onrender.com

## Features

- 🤖 Custom multi-agent AI orchestrator (ChatAgent, EmotionAgent, MemoryAgent, SchedulerAgent, DocsAgent)
- 🧠 Google Gemini Flash Latest integration
- 📊 Memory and emotion tracking
- 🔐 Supabase authentication with JWT
- 🚀 FastAPI with async support
- 🌐 Deployed on Render with auto-scaling

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
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key (for admin operations)
- `GEMINI_API_KEY` - Google AI Studio API key

**Note**: All environment variables are configured in Render deployment dashboard.

## API Endpoints

### Health & Diagnostics
- `GET /health` - Health check endpoint
- `GET /debug-ai` - Check AI service configuration
- `GET /test-gemini-direct` - Test Gemini API directly
- `GET /list-models` - List available Gemini models

### Authentication
- `POST /auth/login` - Login user
- `POST /auth/register` - Register user
- `GET /auth/me` - Get current user (requires Bearer token)

### Chat
- `POST /chat` - Send message and get AI response (requires Bearer token)
- `GET /chat/{thread_id}/messages` - Get conversation history

**Note**: User messages are saved by frontend before API call to avoid duplicates.

### Memory
- `GET /memory/` - Get user memories (requires Bearer token)
- `POST /memory/analyze` - Analyze conversation patterns (requires Bearer token)

## Architecture

- **FastAPI** - Modern Python web framework with async support
- **Custom Agent Orchestrator** - Lightweight multi-agent system (alternative to LangGraph)
  - `ChatAgent` - Main conversation handler
  - `EmotionAgent` - Emotion detection and tracking
  - `MemoryAgent` - Long-term memory management
  - `SchedulerAgent` - Task and schedule management
  - `DocsAgent` - Documentation and knowledge retrieval
- **Supabase** - PostgreSQL database, authentication (JWT), and real-time subscriptions
- **Gemini Flash Latest** - AI language model (gemini-flash-latest)
- **Render** - Cloud deployment platform

## Recent Updates & Fixes

### ✅ Fixed Issues:
1. **Model Compatibility** - Updated from `gemini-1.5-flash` to `gemini-flash-latest` for API compatibility
2. **Authentication** - Fixed `get_current_user()` to return dict instead of User object
3. **Supabase Queries** - Changed `.single()` to `.execute()` for proper data access
4. **Duplicate Messages** - Removed user message insertion from backend (frontend handles it)
5. **Error Handling** - Improved error messages and logging throughout

### ⚠️ Known Limitations:
None currently - text chat fully functional!

## Authentication

All protected endpoints require Bearer token authentication:

```bash
Authorization: Bearer <supabase_access_token>
```

Tokens are obtained from Supabase authentication and managed by the frontend.

## Development

### Local Testing
```bash
# Run server
python main.py

# Test AI service
curl http://localhost:8000/debug-ai

# Test Gemini directly
curl http://localhost:8000/test-gemini-direct
```

### Database Schema
Required Supabase tables:
- `profiles` - User profiles
- `threads` - Conversation threads
- `messages` - Chat messages (with RLS policies)
- `memories` - User memory storage
- `emotions` - Emotion tracking

## Deployment on Render

1. Connected to GitHub repository
2. Auto-deploys on push to main branch
3. Environment variables configured in dashboard
4. Health check endpoint: `/health`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Developer

Developed with ❤️ for AI Surrogate mobile app

**Tech Stack**: Python 3.11, FastAPI, Supabase, Google Gemini AI, gTTS