# AI Surrogate - Complete Setup and Deployment Guide

This guide will help you set up and deploy the complete AI Surrogate application with React Native frontend and FastAPI backend.

## 📁 Project Structure

```
AI Surrogate/
├── ai-surrogate-frontend/     # React Native (Expo) mobile app
├── ai-surrogate-backend/      # FastAPI backend server
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (v16 or later)
2. **Python** (3.11 or later)
3. **Expo CLI**: `npm install -g @expo/cli`
4. **Supabase Account** (free tier)
5. **Google AI Studio API Key** (free tier)

## 🗃️ Database Setup (Supabase)

1. Go to [Supabase](https://supabase.com) and create a new project
2. In the SQL editor, run the schema from `ai-surrogate-backend/supabase_schema.sql`
3. Go to Settings > API to get your:
   - Project URL
   - Anon/Public key
   - Service role key

## ⚙️ Backend Setup

### 1. Install Dependencies

```bash
cd ai-surrogate-backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
cp .env.example .env
```

Update `.env` with your credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
GEMINI_API_KEY=your_gemini_api_key
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
```

### 3. Get API Keys

**Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 4. Run Backend

```bash
python main.py
```

Backend will be available at `http://localhost:8000`

## 📱 Frontend Setup

### 1. Install Dependencies

```bash
cd ai-surrogate-frontend
npm install
```

### 2. Configure Supabase

Update `services/supabase.ts`:

```typescript
const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseAnonKey = 'YOUR_SUPABASE_ANON_KEY';
```

### 3. Update Backend URL

In your chat functionality, update the backend URL:

```typescript
// In ChatScreenSimple.tsx and other API calls
const response = await fetch('http://YOUR_BACKEND_URL/chat', {
  // ... rest of the code
});
```

### 4. Run Frontend

```bash
npm start
```

Choose your platform:
- Press `a` for Android
- Press `i` for iOS (macOS only)
- Press `w` for web

## 🌐 Deployment

### Backend Deployment Options

#### Option 1: Railway (Recommended)

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway up`
4. Set environment variables in Railway dashboard

#### Option 2: Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use Docker deployment
4. Set environment variables

#### Option 3: Docker

```bash
cd ai-surrogate-backend
docker build -t ai-surrogate-backend .
docker run -p 8000:8000 --env-file .env ai-surrogate-backend
```

### Frontend Deployment

#### Build APK (Android)

1. Install EAS CLI: `npm install -g @expo/eas-cli`
2. Login: `eas login`
3. Configure: `eas build:configure`
4. Build: `eas build -p android`

#### Build for iOS

```bash
eas build -p ios
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user

### Chat
- `POST /chat/` - Send text message
- `GET /chat/{thread_id}/messages` - Get conversation history

### Voice
- `POST /voice/transcribe` - Transcribe audio to text
- `POST /voice/speak` - Convert text to speech
- `POST /voice/process` - Full voice conversation flow

### Threads
- `GET /threads/` - Get user's conversation threads
- `POST /threads/` - Create new thread
- `PUT /threads/{thread_id}` - Update thread
- `DELETE /threads/{thread_id}` - Delete thread

### Memory
- `GET /memory/` - Get user memories
- `POST /memory/` - Create memory
- `POST /memory/analyze` - Analyze conversation patterns

## 🎯 Features

### ✅ Implemented
- User authentication (Supabase Auth)
- Text chat with AI (Gemini 1.5 Flash)
- Voice input (Whisper STT)
- Voice output (gTTS TTS)
- Conversation threads
- Memory system
- Emotion analysis
- Multi-agent system (LangGraph)
- Real-time chat updates
- Mobile-responsive UI

### 🔄 Future Enhancements
- Push notifications
- Dark/light theme toggle
- Multiple language support
- File sharing
- Advanced voice features
- Emotion-based responses
- Calendar integration

## 🛠️ Development Tips

### Backend Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (when implemented)
pytest

# Check code style
black . && isort .
```

### Frontend Development

```bash
# Clear cache
npx expo start --clear

# Run on specific device
npx expo start --android
npx expo start --ios

# Check for updates
npx expo install --fix
```

## 🐛 Troubleshooting

### Common Backend Issues

1. **Module import errors**
   ```bash
   export PYTHONPATH=/path/to/ai-surrogate-backend:$PYTHONPATH
   ```

2. **Supabase connection issues**
   - Verify your credentials in `.env`
   - Check if your Supabase project is active

3. **Audio processing issues**
   - Install ffmpeg: `sudo apt-get install ffmpeg`
   - Check file permissions in storage directory

### Common Frontend Issues

1. **Metro bundler issues**
   ```bash
   npx expo start --clear
   npm start -- --reset-cache
   ```

2. **Dependency conflicts**
   ```bash
   npm install --legacy-peer-deps
   ```

3. **iOS build issues**
   ```bash
   cd ios && pod install
   ```

## 📚 Architecture Overview

### Backend Architecture
- **FastAPI** - Modern Python web framework
- **LangGraph** - Agent orchestration and workflow
- **Gemini 1.5 Flash** - AI language model
- **Whisper** - Speech-to-text
- **gTTS** - Text-to-speech
- **Supabase** - Database and authentication

### Frontend Architecture
- **React Native + Expo** - Cross-platform mobile development
- **React Navigation** - Navigation library
- **Supabase JS** - Database client and real-time subscriptions
- **Expo AV** - Audio/video handling

### Data Flow
1. User input (text/voice) → Frontend
2. Frontend → Backend API
3. Backend → AI processing (LangGraph + Gemini)
4. AI response → Backend
5. Backend → Database (Supabase)
6. Response → Frontend (with real-time updates)

## 🔒 Security Considerations

- All API endpoints require authentication
- Row Level Security (RLS) enabled in Supabase
- CORS configured for security
- Rate limiting implemented
- Input validation and sanitization
- Environment variables for sensitive data

## 📈 Monitoring and Analytics

### Backend Monitoring
- Health check endpoint: `/health`
- Error logging and tracking
- Performance monitoring

### Frontend Analytics
- User engagement tracking
- Crash reporting (when implemented)
- Usage analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (when test suite is implemented)
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the GitHub issues
3. Create a new issue with detailed information

## 🎉 Congratulations!

You now have a fully functional AI companion app with:
- Voice and text chat capabilities
- Intelligent AI responses
- Memory and emotion tracking
- Cross-platform mobile interface
- Scalable backend architecture

Happy coding! 🚀