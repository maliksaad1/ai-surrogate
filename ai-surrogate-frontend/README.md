# AI Surrogate Frontend

React Native mobile app for AI Surrogate - your personal AI companion.

## Features

- 🎨 Futuristic cyan neon theme
- 💬 Text and voice chat with AI
- 🧠 Persistent memory and context
- 😊 Emotion detection and response
- 📱 Cross-platform (iOS & Android)
- 🔄 Real-time message synchronization

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure Supabase:
   - Update `services/supabase.ts` with your Supabase credentials

3. Update backend URL:
   - Update API calls in chat screens to point to your backend

4. Run the app:
```bash
npm start
```

## Building

### Android APK
```bash
eas build -p android
```

### iOS
```bash
eas build -p ios
```

## Configuration

- Edit `app.json` for app metadata
- Edit `eas.json` for build configuration
- Update theme colors in `constants/theme.ts`

## Screens

- **Onboarding**: Welcome screen with app introduction
- **Auth**: Login and signup with Supabase
- **Home**: List of conversation threads
- **Chat**: Main chat interface with voice support
- **Settings**: App preferences and toggles
- **Profile**: User profile and statistics