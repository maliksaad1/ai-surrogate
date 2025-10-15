# AI Surrogate Frontend

React Native mobile app for AI Surrogate - your personal AI companion powered by Google Gemini AI.

## ✨ Features

### 🤖 AI Chat
- 💬 **Real-time text chat** with Google Gemini AI
- 🧠 **Multi-agent system** - Intelligent routing to specialized agents:
  - Chat Agent: General conversation
  - Emotion Agent: Emotional analysis and support
  - Memory Agent: Context retention
  - Scheduler Agent: Time management
  - Docs Agent: Information retrieval
- 🎯 **Context-aware responses** with conversation history
- ⚡ **Real-time synchronization** via Supabase

### 🎨 User Experience
- 🎨 **Futuristic cyan neon theme** with dark mode
- 🤖 **Custom robotic head icon** with glowing cyan eyes
- 📱 **Cross-platform** (iOS & Android)
- 🔐 **Secure authentication** with Supabase Auth
- 👤 **User profiles** with statistics

### 🎤 Voice Features (In Development)
- 🎙️ Voice recording interface (UI ready)
- 🔊 Text-to-speech responses (backend ready)
- ⚠️ **Note**: Voice upload currently disabled - requires additional native module setup

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn
- Expo CLI
- EAS CLI (for building APKs)

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
   - Backend API is deployed at: `https://ai-surrogate.onrender.com`
   - Supabase credentials are already configured in `services/supabase.ts`

3. **Run development server:**
```bash
npx expo start
```

## 📱 Building APK

### Android APK (Production)
```bash
npx eas build --platform android --profile preview
```

### Download Latest APK
Check the EAS build dashboard for the latest build:
```
https://expo.dev/accounts/adadssa/projects/ai-surrogate/builds
```

## 🏗️ Project Structure

```
ai-surrogate-frontend/
├── screens/          # App screens
│   ├── AuthScreen.tsx        # Login/Signup
│   ├── HomeScreen.tsx        # Thread list
│   ├── ChatScreen.tsx        # Main chat interface
│   ├── ProfileScreen.tsx     # User profile
│   └── SettingsScreen.tsx    # App settings
├── services/         # External services
│   └── supabase.ts           # Supabase client
├── contexts/         # React contexts
│   └── AuthContext.tsx       # Authentication state
├── constants/        # App constants
│   └── theme.ts              # Theme colors and styles
├── config/           # Configuration
│   └── api.ts                # API endpoints
├── assets/           # Images and icons
│   ├── icon.png              # App icon (1024x1024)
│   ├── adaptive-icon.png     # Android adaptive icon
│   └── splash-icon.png       # Splash screen icon
└── types/            # TypeScript types
```

## 🔧 Configuration

### Theme Customization
Edit `constants/theme.ts` to customize:
- Colors (primary cyan: `#00FFFF`, secondary: `#007BFF`)
- Fonts and sizes
- Spacing and border radius

### API Configuration
Edit `config/api.ts` to change backend URL:
```typescript
const config = {
  production: {
    API_BASE_URL: 'https://ai-surrogate.onrender.com'
  }
};
```

### App Metadata
Edit `app.json` for:
- App name and description
- Icon and splash screen
- Android/iOS specific settings

## 📚 Screens Overview

### 🔐 AuthScreen
- Login and signup with email/password
- Email verification flow
- Integration with Supabase Auth

### 🏠 HomeScreen
- List of conversation threads
- Create new conversations
- Real-time thread updates

### 💬 ChatScreen
- GiftedChat interface with custom styling
- Real-time message synchronization
- AI-powered responses from Gemini
- Voice recording UI (upload disabled)
- Message history and context

### 👤 ProfileScreen
- User statistics (conversation count, message count)
- Profile editing
- Account information

### ⚙️ SettingsScreen
- App preferences
- Theme selection (coming soon)
- Voice mode toggle
- Account management

## 🔗 Backend Integration

### Endpoints Used
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/confirm` - Email confirmation
- `POST /chat` - Send message and get AI response
- `GET /chat/{thread_id}/messages` - Get conversation history
- `POST /voice/process` - Voice processing (disabled in frontend)

### Authentication
All API calls include Bearer token in headers:
```typescript
headers: {
  'Authorization': `Bearer ${session.access_token}`
}
```

## 🐛 Known Issues

### Voice Upload
**Status**: Temporarily disabled  
**Reason**: Network request failures in production APK  
**Cause**: React Native file upload requires additional native module setup  
**Workaround**: Voice button shows friendly placeholder message  
**Solution**: Requires:
- Proper Android permissions configuration
- Native audio module setup
- File upload handling for production builds

### Supabase Storage
**Status**: ✅ Configured  
**Impact**: Audio files now properly uploaded to Supabase storage  
**Note**: Voice upload still disabled in frontend due to React Native production build issues

## 🔄 Recent Updates

### Latest Changes
- ✅ Fixed duplicate message issue
- ✅ Fixed authentication with Bearer tokens
- ✅ Switched from mock to real ChatScreen
- ✅ Enhanced robotic icon with glowing eyes
- ✅ Fixed email confirmation redirect loop
- ✅ Temporarily disabled voice upload to prevent errors
- ✅ Connected to production backend on Render

## 🎨 Custom Icon

The app features a custom-designed robotic head icon:
- Metallic dark gray body
- Glowing cyan eyes with highlights
- Circuit patterns on sides
- Glowing antenna
- Segmented mouth display
- 'AI' text with shadow effect

Generate new icons with:
```bash
python create_robot_icon.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - feel free to use this project for learning and development.

## 👨‍💻 Developer

**Malik Muhammad Saad**  
Email: saad.shafiq11052004@gmail.com

## 🔗 Related Repositories

- Backend: `ai-surrogate-backend` (FastAPI + Gemini AI)
- Deployed: https://ai-surrogate.onrender.com

---

**Built with React Native, Expo, Supabase, and Google Gemini AI** 🚀