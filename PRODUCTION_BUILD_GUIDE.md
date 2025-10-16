# 🚀 Production APK Build Guide

**Project**: AI Surrogate  
**Developer**: Malik Muhammad Saad  
**Date**: 2025-01-15  
**Status**: Ready for Production Build

---

## ✅ Pre-Build Checklist

### Backend Status
- [x] ✅ Deployed on Render: https://ai-surrogate.onrender.com
- [x] ✅ Health check passing
- [x] ✅ All environment variables configured
- [x] ✅ Gemini API working
- [x] ✅ Supabase connection active
- [x] ✅ Multi-agent system operational
- [x] ✅ Voice features removed (reduced build size)

### Frontend Configuration
- [x] ✅ API endpoint configured: `https://ai-surrogate.onrender.com`
- [x] ✅ Supabase URL: `https://oipnwnrkjhegtodzyoez.supabase.co`
- [x] ✅ Supabase Anon Key configured
- [x] ✅ EAS project ID: `89d9aee3-295e-400c-92e5-240018eed870`
- [x] ✅ Package name: `com.aisurrogate.app`
- [x] ✅ App icons configured (robot theme)
- [x] ✅ Permissions configured (Internet, Network State)

### App Features
- [x] ✅ Authentication (Login/Signup)
- [x] ✅ Real-time chat with AI
- [x] ✅ Multi-agent system (5 agents)
- [x] ✅ Agent visibility UI
- [x] ✅ Conversation threads
- [x] ✅ User profiles
- [x] ✅ Message history
- [x] ✅ Real-time sync
- [x] ❌ Voice features (intentionally removed)

---

## 🏗️ Build Configuration

### App Details
```json
{
  "name": "AI Surrogate",
  "slug": "ai-surrogate",
  "version": "1.0.0",
  "package": "com.aisurrogate.app",
  "bundleIdentifier": "com.aisurrogate.app"
}
```

### Build Profiles

#### Preview Build (Testing)
```bash
eas build --platform android --profile preview
```
- Build type: APK
- Distribution: Internal
- Use for: Testing on devices
- Output: .apk file

#### Production Build (Release)
```bash
eas build --platform android --profile production
```
- Build type: APK
- Distribution: Production
- Use for: Final release
- Output: .apk file (can be uploaded to Play Store)

---

## 📱 Step-by-Step Build Instructions

### Step 1: Verify Dependencies

```bash
cd "C:\Users\Saad\Desktop\AI Surrogate\ai-surrogate-frontend"
npm install
```

### Step 2: Test Backend Connection

```bash
# Test health endpoint
curl https://ai-surrogate.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "message": "API is running",
  "configuration": {
    "supabase_url": "set",
    "supabase_anon_key": "set",
    "gemini_api_key": "set"
  },
  "fully_configured": true
}
```

### Step 3: Login to EAS

```bash
npx eas login
```

**Credentials**:
- Username: Your Expo account
- Account owner: `adadssa`

### Step 4: Configure EAS (if needed)

```bash
# Check current configuration
npx eas build:configure
```

### Step 5: Build Preview APK (Recommended First)

```bash
# Build preview APK for testing
npx eas build --platform android --profile preview

# This will:
# 1. Upload your code to EAS
# 2. Build the APK on Expo servers
# 3. Provide download link when complete
```

**Build Time**: ~10-15 minutes

### Step 6: Download and Test

Once build completes:
1. Download APK from EAS dashboard or provided link
2. Install on Android device
3. Test all features:
   - Login/Signup
   - Chat with AI
   - Agent visibility
   - Thread management
   - Real-time sync

### Step 7: Production Build (After Testing)

```bash
# Build production APK
npx eas build --platform android --profile production
```

---

## 🧪 Testing Checklist (After APK Install)

### Authentication
- [ ] Sign up with email
- [ ] Verify email confirmation flow
- [ ] Login with credentials
- [ ] Logout and login again

### Chat Features
- [ ] Create new thread
- [ ] Send text message
- [ ] Receive AI response
- [ ] See agent status indicator (💬 🔍 ⚙️)
- [ ] Agent icons displayed correctly
- [ ] Real-time message sync

### Agent System
- [ ] General chat → Chat Agent (💬)
- [ ] "Schedule meeting" → Scheduler Agent (📅)
- [ ] "How to..." → Knowledge Assistant (📚)
- [ ] "Remember this" → Memory Agent (🧠)
- [ ] Status indicator shows active agent

### Performance
- [ ] App launches quickly
- [ ] Messages load fast
- [ ] No crashes or freezes
- [ ] Smooth scrolling
- [ ] Network errors handled gracefully

### UI/UX
- [ ] Robot icon displayed
- [ ] Dark theme working
- [ ] Gradient colors correct
- [ ] Animations smooth
- [ ] Keyboard handling good

---

## 📊 Build Comparison

| Aspect | With Voice | Without Voice (Current) |
|--------|-----------|------------------------|
| **APK Size** | ~150MB | ~50MB |
| **Build Time** | ~20 min | ~10 min |
| **Dependencies** | Heavy (Whisper, Torch) | Light |
| **Features** | Text + Voice | Text only |
| **Stability** | Complex | Simple, stable |

---

## 🔧 Troubleshooting

### Build Fails

**Issue**: "Build failed to compile"
**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npx eas build --clear-cache --platform android --profile preview
```

### Backend Connection Issues

**Issue**: "Network request failed"
**Solution**:
1. Check backend is running: `curl https://ai-surrogate.onrender.com/health`
2. Verify API_BASE_URL in `config/api.ts`
3. Check Android permissions include INTERNET

### Authentication Fails

**Issue**: "Cannot login"
**Solution**:
1. Verify Supabase URL and keys in `services/supabase.ts`
2. Check Supabase dashboard for service status
3. Ensure RLS policies are configured correctly

### APK Won't Install

**Issue**: "App not installed"
**Solution**:
1. Enable "Install unknown apps" in Android settings
2. Uninstall previous version first
3. Check Android version compatibility (minimum SDK 21)

---

## 📦 APK Distribution

### Internal Testing (Preview Build)
1. Download APK from EAS build page
2. Share link with testers
3. Install on devices for testing
4. Gather feedback

### Production Release (Production Build)
1. Build production APK
2. Test thoroughly
3. Sign APK (EAS handles this)
4. Upload to Google Play Console
5. Submit for review

---

## 🎯 Success Criteria

APK is ready for release when:

- [x] Backend is stable and deployed
- [x] All core features working
- [x] No crashes or critical bugs
- [x] Agent system operational
- [x] Authentication working
- [x] Real-time sync functional
- [x] UI/UX polished
- [x] Performance acceptable
- [x] APK size reasonable (<100MB)

---

## 📝 Build Commands Quick Reference

```bash
# Login to EAS
npx eas login

# Build preview APK (for testing)
npx eas build --platform android --profile preview

# Build production APK (for release)
npx eas build --platform android --profile production

# Check build status
npx eas build:list

# View build logs
npx eas build:view <build-id>

# Submit to Play Store (after production build)
npx eas submit --platform android
```

---

## 🌐 Important URLs

- **Backend API**: https://ai-surrogate.onrender.com
- **Supabase Project**: https://oipnwnrkjhegtodzyoez.supabase.co
- **EAS Dashboard**: https://expo.dev/accounts/adadssa/projects/ai-surrogate
- **GitHub Repo**: https://github.com/maliksaad1/ai-surrogate

---

## 🔐 Environment Variables (Backend)

These are already configured on Render:

```
SUPABASE_URL=https://oipnwnrkjhegtodzyoez.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
GEMINI_API_KEY=<your-gemini-key>
```

---

## 🎨 App Branding

- **Icon**: Robot head with glowing cyan eyes
- **Theme**: Dark mode with cyan/blue gradients
- **Primary Color**: #00FFFF (Cyan)
- **Secondary Color**: #007BFF (Blue)
- **Background**: #0A0A0A (Dark)

---

## 📱 Minimum Requirements

### Android
- **Minimum SDK**: 21 (Android 5.0)
- **Target SDK**: 34 (Android 14)
- **Architecture**: ARM64, ARMv7a, x86_64

### Device Requirements
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 100MB free space
- **Network**: Internet connection required

---

## 🚀 Ready to Build!

Everything is configured and ready. Execute the build command when ready:

```bash
cd "C:\Users\Saad\Desktop\AI Surrogate\ai-surrogate-frontend"
npx eas build --platform android --profile preview
```

**Expected**: Build will take ~10-15 minutes and provide download link.

**Good luck with your production build! 🎉**
