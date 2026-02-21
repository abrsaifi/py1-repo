# DocPro Mobile App - Complete Setup & Development Guide

## Overview

DocPro Mobile is a React Native application that provides professional document processing on iOS and Android devices. It connects to the DocPro backend API to offer file processing, analytics, and user management features.

## Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React Native | 0.72.1 |
| Language | TypeScript | Latest |
| Navigation | React Navigation | 6.x |
| UI Components | react-native-elements | 3.4.2 |
| State Management | AsyncStorage + React Hooks | - |
| API Client | axios | 1.6.0 |
| Icons | FontAwesome 6 | Latest |
| File Handling | react-native-document-picker | 9.0.1 |

### Project Structure

```
mobile/
├── App.tsx                      # Root app component & navigation setup
├── package.json                 # Dependencies & scripts
├── tsconfig.json               # TypeScript config
├── babel.config.js             # Babel transpiler config
├── metro.config.js             # Metro bundler config
├── .eslintrc.json              # ESLint configuration
├── .prettierrc.json            # Code formatter config
├── README.md                   # Quick start guide
├── MOBILE_SETUP.md            # This file
├── app.json                    # React Native app config
├── index.js                    # App entry point
│
├── src/
│   ├── index.ts               # Main exports
│   │
│   ├── screens/               # Screen components
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   └── SplashScreen.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardScreen.tsx
│   │   ├── features/
│   │   │   ├── DuplicateRemoverScreen.tsx
│   │   │   ├── DataValidatorScreen.tsx
│   │   │   ├── PDFExportScreen.tsx
│   │   │   └── ReportGeneratorScreen.tsx
│   │   ├── analytics/
│   │   │   └── AnalyticsScreen.tsx
│   │   └── settings/
│   │       ├── SettingsScreen.tsx
│   │       └── ProfileScreen.tsx
│   │
│   ├── services/
│   │   └── ApiClient.ts       # API communication layer
│   │
│   ├── types/
│   │   └── index.ts           # TypeScript interfaces
│   │
│   ├── components/            # Reusable UI components (future)
│   ├── utils/                 # Utility functions (future)
│   └── navigation/            # Navigation configuration (future)
│
└── [iOS]/                     # iOS project (generated)
└── [Android]/                 # Android project (generated)
```

## Features Implemented

### 1. Authentication System

**Login Screen** (`src/screens/auth/LoginScreen.tsx`)
- Username and password input
- Error handling and validation
- Automatic API key storage
- Navigation to dashboard on success

**Register Screen** (`src/screens/auth/RegisterScreen.tsx`)
- Username, email, and password input
- Password confirmation
- Email validation
- Account creation with success feedback

**Splash Screen** (`src/screens/auth/SplashScreen.tsx`)
- Session restoration on app launch
- Automatic navigation based on auth state
- Loading animation

### 2. Dashboard

**Home Screen** (`src/screens/dashboard/DashboardScreen.tsx`)
- API usage statistics
- Success rate tracking
- Processing time metrics
- Storage usage information
- Quick action buttons to main features
- Pull-to-refresh functionality

### 3. Feature Screens

**Duplicate Remover** (`src/screens/features/DuplicateRemoverScreen.tsx`)
- File selection with document picker
- Duplicate removal options
- Results display with metrics
- Processing feedback

**Data Validator** (`src/screens/features/DataValidatorScreen.tsx`)
- Data quality checking
- Duplicate detection
- Missing value identification
- Data type validation
- Quality score calculation

**PDF Export** (`src/screens/features/PDFExportScreen.tsx`)
- Multiple export formats (PDF, Excel, JSON)
- Format selection UI
- Export options (headers, compression)
- File processing

**Report Generator** (`src/screens/features/ReportGeneratorScreen.tsx`)
- Multiple report types (Summary, Detailed, Comparative)
- Report contents selection
- Analysis generation
- Export functionality

### 4. Analytics Screen

**Analytics** (`src/screens/analytics/AnalyticsScreen.tsx`)
- Total files and operations metrics
- Success rate visualization
- Average processing time
- Storage usage statistics
- File type distribution
- Operations by type breakdown
- Pull-to-refresh

### 5. Settings & Profile

**Settings Screen** (`src/screens/settings/SettingsScreen.tsx`)
- User profile card
- Account settings
- API & Integration management
- App preferences
- Help & Support links
- Logout functionality

**Profile Screen** (`src/screens/settings/ProfileScreen.tsx`)
- User account information
- Email display
- Account creation date
- API key management (view, copy, reset)
- Password change options
- Security settings
- Danger zone (delete account)

## API Integration

### ApiClient Service

Location: `src/services/ApiClient.ts`

**Initialization**:
```typescript
import ApiClient from '../services/ApiClient';

// Automatically configured with headers and interceptors
```

**Authentication Methods**:
- `register(username, email, password)` - Create new account
- `login(username, password)` - Authenticate user
- `logout()` - End session
- `getCurrentUser()` - Get user details
- `resetApiKey()` - Generate new API key
- `restoreSession()` - Resume previous session

**File Operations**:
- `uploadFile(filepath, filename)` - Upload file
- `downloadFile(fileId, filename)` - Download processed file

**Processing Features**:
- `removeDuplicates(fileId)` - Remove duplicate records
- `validateData(fileId, rules)` - Check data quality
- `exportToFormat(fileId, options)` - Export in different formats
- `generateReport(fileId, reportType)` - Create analysis report

**Advanced Features**:
- `checkQuality(fileId)` - Quality metrics
- `bulkProcess(fileIds, operation)` - Process multiple files
- `estimateProcessingTime(fileId, operation)` - Time prediction

**Job Management**:
- `scheduleJob(operation, parameters)` - Schedule async task
- `getJobStatus(jobId)` - Check job progress

**Analytics**:
- `getAnalytics()` - Fetch analytics data
- `getCacheStats()` - Get cache information
- `clearCache()` - Clear cached results

### API Endpoints (Backend)

**Auth** (`/api/auth/`)
- POST `/register` - Register new user
- POST `/login` - Login
- POST `/logout` - Logout
- GET `/me` - Current user info
- POST `/reset-api-key` - New API key
- GET `/verify-api-key/<key>` - Verify key

**Processing** (`/api/`)
- POST `/pdf/remove-duplicates` - Remove duplicates
- POST `/features/quality-check` - Validate data
- POST `/features/export/{format}` - Export files
- POST `/features/bulk-process` - Batch processing

**Analytics** (`/api/image/`)
- GET `/analytics` - Analytics dashboard data

## Navigation Structure

### Root Navigator
- **Splash Screen** - _Initial load state_
- **Auth Stack** - _Login/Register flow_
  - Login Screen
  - Register Screen
- **Main App** - _Authenticated user_
  - Bottom Tab Navigator
    - Home (Dashboard + Stack)
    - Tools (Features + Stack)
    - Analytics
    - Settings (+ Stack for Profile)

### Navigation Flow

```
App Launch
    ↓
[Splash Screen - Session Check]
    ↓
┌─→ No Session → Auth Stack → Login/Register → [Success]
└─→ Has Session → Main App (Tabs)
                    ├─ Home Tab (Dashboard)
                    ├─ Tools Tab
                    │   ├─ Duplicate Remover
                    │   ├─ Data Validator
                    │   ├─ PDF Export
                    │   └─ Report Generator
                    ├─ Analytics Tab
                    └─ Settings Tab
                        ├─ Settings
                        └─ Profile
```

## Setup & Installation

### 1. Prerequisites

```bash
# Node.js and npm (required)
node --version  # >= 16.0.0
npm --version   # >= 8.0.0

# Xcode (macOS for iOS)
xcode-select --install

# Android Studio (for Android)
# Download from: https://developer.android.com/studio
```

### 2. Installation

```bash
# Clone or navigate to mobile directory
cd mobile

# Install dependencies
npm install

# Install iOS pods
cd ios
pod install
cd ..
```

### 3. Configuration

**Update Backend URL** in `src/services/ApiClient.ts`:
```typescript
const API_BASE_URL = 'http://your-server:5000/api';
// For iOS simulator: http://localhost:5000/api
// For Android emulator: http://10.0.2.2:5000/api
```

### 4. Running the App

**iOS**:
```bash
npm run ios
# or with specific simulator:
npm run ios -- --simulator="iPhone 15"
```

**Android**:
```bash
npm run android
# Make sure Android emulator or device is running
```

**Development**:
```bash
npm start
# Then press:
# i - launch iOS
# a - launch Android
# r - reload app
# m - open menu
```

## Development Workflow

### File Watch & Reload
```bash
npm start
```
- Metro bundler starts
- Press `r` to reload
- Press `m` to open menu

### Type Checking
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
# or
npx eslint src/
```

### Code Formatting
```bash
npx prettier --write src/
```

## Build & Deployment

### iOS

**Development Build**:
```bash
npm run ios
```

**Production Build**:
```bash
cd ios
xcodebuild -exportArchive \
  -archivePath ./build/DocPro.xcarchive \
  -exportPath ./build \
  -exportOptionsPlist ./ExportOptions.plist
```

**App Store Upload**:
1. Create Apple Developer account
2. Register app bundle ID: `com.docpro.mobile`
3. Create app in App Store Connect
4. Generate distribution certificate and provisioning profile
5. Upload with Xcode or `xcrun altool`

### Android

**Debug Build**:
```bash
cd android
./gradlew assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

**Release Build**:
```bash
# Create keystore (first time only)
keytool -genkey -v -keystore docpro.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 -alias docpro

# Sign release APK
cd android
./gradlew assembleRelease \
  -PMYAPP_RELEASE_STORE_FILE=../docpro.keystore \
  -PMYAPP_RELEASE_STORE_PASSWORD=password \
  -PMYAPP_RELEASE_KEY_ALIAS=docpro \
  -PMYAPP_RELEASE_KEY_PASSWORD=password
```

**Play Store Upload**:
1. Create Google Play Developer account
2. Create app
3. Generate signing key (above)
4. Upload signed APK or AAB to Play Store Console

## Backend Integration

### Authentication Flow

```
Mobile App                              Backend
    │                                      │
    ├─→ POST /auth/register ──────────────→ │
    │                        (user data)    │
    │  ← Create user, return api_key ─────←  │
    │                                      │
    ├─→ POST /auth/login ───────────────────→ │
    │        (username, password)           │
    │  ← Return api_key ─────────────────←  │
    │                                      │
    ├─→ API Request + Authorization Header───→ │
    │        (Accept: application/json)    │
    │  ← API Response ────────────────────←  │
    │                                      │
    └─→ POST /auth/logout ────────────────→ │
         Clear session                      │
```

### Error Handling

**401 Unauthorized**:
```typescript
// Token expired or invalid
// Interceptor catches this and triggers logout
```

**400 Bad Request**:
```typescript
// Validation error
// Display error message from response
```

**500 Server Error**:
```typescript
// Server-side error
// Show generic error message
```

## Data Storage

### AsyncStorage

Secure storage of session data:

```typescript
// Stored on login
- userToken (API key)
- userId (User ID)
- username (Username)
- userEmail (Email)

// Cleared on logout
```

### Session Restoration

On app launch:
1. Check AsyncStorage for tokens
2. Verify token validity with `/auth/me`
3. Navigate based on auth state

## Performance Optimization

### Code Splitting
- Lazy load feature screens
- Stack-based navigation isolation

### Rendering
- Use React.memo for expensive components
- Optimize FlatList with keyExtractor
- Debounce API calls

### Caching
- API response caching with axios interceptors
- AsyncStorage for persistent data
- Memory cache for frequently accessed data

### Bundle Size
- Tree-shaking unused code
- Minify production builds
- Remove dev dependencies

## Security

### API Communication
- HTTPS only in production
- Disable HTTP for production

### Token Management
- Store API keys in AsyncStorage (encrypted on iOS keychain, Android keystore)
- Include in Authorization header for all requests
- Validate before use

### Input Validation
- Validate email format
- Check password length (min 6 chars)
- Sanitize file data

### Environment Variables
```bash
# Create .env file (not included in git)
REACT_APP_API_URL=https://api.docpro.app
REACT_APP_ENV=production
```

## Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### E2E Tests
```bash
npm run test:e2e
```

## Troubleshooting

### Metro Bundler Issues

**Clear cache**:
```bash
npm start --reset-cache
```

**Port already in use**:
```bash
npm start -- -p 8081
```

### iOS Build Issues

**CocoaPods problems**:
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

**Xcode cache**:
```bash
cd ios
xcodebuild clean -workspace DocProMobile.xcworkspace -scheme DocProMobile
cd ..
npm run ios
```

### Android Build Issues

**Gradle cache**:
```bash
cd android
./gradlew clean
cd ..
npm run android
```

**SDK not found**:
```bash
# Update Android SDK manager with latest SDK tools
# Check android/local.properties points to correct SDK
```

### API Connection Issues

**Backend not responding**:
- Ensure backend is running on correct port
- Check firewall settings
- Verify API_BASE_URL is correct

**CORS issues**:
- Backend should accept requests from mobile app domain
- Check backend CORS configuration

**Network timeout**:
- Check network connectivity
- Increase timeout in ApiClient (default: 30s)

## Contributing

### Code Style
- Follow ESLint rules
- Format code with Prettier
- Use TypeScript strict mode

### Branch Naming
- `feature/` - new features
- `fix/` - bug fixes
- `docs/` - documentation
- `refactor/` - code refactoring

### Commit Messages
```
feature: Add duplicate remover screen
fix: Resolve API timeout issue
docs: Update README
refactor: Simplify API client
```

## Resources

- [React Native Docs](https://reactnative.dev)
- [React Navigation](https://reactnavigation.org)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Axios Documentation](https://axios-http.com)

## Support

For issues or questions:
1. Check troubleshooting section
2. Review code comments
3. Check React Native docs
4. File GitHub issue with:
   - React Native version
   - Device/simulator info
   - Steps to reproduce
   - Error logs

## License

© 2024 DocPro. All rights reserved.

## Version History

### 1.0.0 (Initial Release - Feb 2024)
- Complete authentication system
- All feature screens implemented
- Analytics dashboard
- User settings
- API integration complete
- iOS and Android support
- TypeScript type definitions
- Comprehensive documentation
