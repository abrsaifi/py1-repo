# DocPro Mobile App

Professional document processing on your mobile device. Built with React Native and TypeScript.

## Features

- 📱 **Cross-platform**: iOS and Android support
- 🔐 **Secure Authentication**: User registration, login, and API key management
- 📄 **Document Processing**: Remove duplicates, validate data, export files
- 📊 **Analytics**: Track file operations and performance metrics
- 🔄 **Real-time Sync**: Seamless sync with backend services
- 🎨 **Modern UI**: Beautiful and responsive interface

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- React Native CLI
- iOS: Xcode (for iOS development)
- Android: Android Studio and Android SDK

### Installation

1. **Install dependencies**:
   ```bash
   cd mobile
   npm install
   ```

2. **Install pods (iOS only)**:
   ```bash
   cd ios
   pod install
   cd ..
   ```

3. **Configure Backend URL**:
   Edit `src/services/ApiClient.ts` and update the `API_BASE_URL`:
   ```typescript
   const API_BASE_URL = 'http://your-backend-url:5000/api';
   ```

### Running the App

**iOS**:
```bash
npm run ios
```

**Android**:
```bash
npm run android
```

**Development Mode** (with Metro bundler):
```bash
npm start
```

## Project Structure

```
mobile/
├── App.tsx                 # Root component with navigation
├── package.json            # Dependencies and scripts
├── src/
│   ├── screens/           # Screen components
│   │   ├── auth/         # Authentication screens
│   │   ├── dashboard/    # Dashboard screen
│   │   ├── features/     # Feature screens
│   │   ├── analytics/    # Analytics screen
│   │   └── settings/     # Settings screens
│   ├── services/         # API client and services
│   ├── types/            # TypeScript type definitions
│   ├── components/       # Reusable components
│   ├── utils/            # Utility functions
│   └── index.ts          # Exports
```

## Authentication

### Login
1. Launch the app
2. Enter your username and password
3. Tap "Sign In"
4. Your API key is automatically stored securely

### Register
1. Tap "Create New Account"
2. Enter username, email, and password
3. Confirm password
4. Tap "Create Account"
5. Login with your new credentials

### API Key Management
View and reset your API key from Settings > Profile Information.

## Features Overview

### Home Screen
- Quick statistics (files, operations, success rate)
- Quick action buttons for main features

### Tools
- **Duplicate Remover**: Remove duplicate records from files
- **Data Validator**: Check data quality and integrity
- **PDF Export**: Convert files to different formats
- **Report Generator**: Create detailed analysis reports

### Analytics
- Total files and operations
- Success rate and performance metrics
- File type distribution
- Operation statistics
- Storage information

### Settings
- User profile management
- API key management
- Password management
- Notification preferences
- Theme selection
- Help and support

## API Integration

The app connects to the DocPro backend API. Key endpoints:

**Authentication**:
- POST `/api/auth/register` - Create account
- POST `/api/auth/login` - Login
- GET `/api/auth/me` - Current user
- POST `/api/auth/reset-api-key` - Reset API key

**Processing**:
- POST `/api/pdf/remove-duplicates` - Remove duplicates
- POST `/api/features/quality-check` - Validate data
- POST `/api/features/export/{format}` - Export files

**Analytics**:
- GET `/api/image/analytics` - Get analytics data

## TypeScript

The app is fully typed with TypeScript. Key types are defined in `src/types/index.ts`:

- `User` - User account information
- `AnalyticsData` - Analytics metrics
- `ConversionResult` - File processing result
- `JobStatus` - Async job status

## Navigation

The app uses React Navigation with:
- **Bottom Tab Navigation** for main sections
- **Stack Navigation** for detailed screens
- **Auth Stack** for login/register

## API Client

Use the `ApiClient` service for all API calls:

```typescript
import ApiClient from '../services/ApiClient';

// Login
await ApiClient.login(username, password);

// Check data quality
const result = await ApiClient.checkQuality(fileId);

// Get analytics
const analytics = await ApiClient.getAnalytics();

// Logout
await ApiClient.logout();
```

## File Handling

The app supports file picking and processing:

```typescript
import DocumentPicker from 'react-native-document-picker';

const result = await DocumentPicker.pick({
  type: [DocumentPicker.types.allFiles],
});

const file = result[0];
const response = await ApiClient.uploadFile(file.uri, file.name);
```

## State Management

Uses React hooks and AsyncStorage:

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Store data
await AsyncStorage.setItem('key', 'value');

// Retrieve data
const value = await AsyncStorage.getItem('key');
```

## Styling

Uses React Native `StyleSheet` for performance-optimized styling. Color scheme:

- **Primary**: `#667eea` (Indigo)
- **Success**: `#10b981` (Emerald)
- **Warning**: `#f59e0b` (Amber)
- **Danger**: `#ef4444` (Red)
- **Background**: `#f8f9ff` (Light Blue)

## Error Handling

All API calls include error handling:

```typescript
try {
  const result = await ApiClient.someMethod();
} catch (error) {
  Alert.alert('Error', error instanceof Error ? error.message : 'Unknown error');
}
```

## Testing

Run tests with:
```bash
npm test
```

## Building

**iOS Production Build**:
```bash
npm run build:ios
```

**Android Production Build**:
```bash
npm run build:android
```

## Deployment

### iOS App Store
1. Create Apple Developer account
2. Create App ID and certificate
3. Build archive and submit to App Store Connect

### Google Play Store
1. Create Google Play Developer account
2. Build signed APK or AAB
3. Upload to Google Play Console

## Troubleshooting

**Metro bundler issues**:
```bash
npm start --reset-cache
```

**Module resolution**:
```bash
npm install
cd ios && pod install && cd ..
npm start
```

**API connection errors**:
- Check backend URL in `src/services/ApiClient.ts`
- Ensure backend is running
- Check network connectivity

## Performance

- Lazy loading of screens
- Optimized re-renders with React hooks
- Efficient API caching
- Minimal bundle size with tree-shaking

## Security

- **HTTPS**: All API calls use HTTPS
- **Token Storage**: API keys stored securely in AsyncStorage
- **Input Validation**: All inputs validated before sending
- **CORS**: Backend configured for mobile app domain

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Support

For support, visit our help center or contact support@docpro.app

## License

© 2024 DocPro. All rights reserved.

## Version

Current version: **1.0.0**

## Changelog

### 1.0.0 (Initial Release)
- Authentication system
- File processing features
- Analytics dashboard
- User settings
- API integration
