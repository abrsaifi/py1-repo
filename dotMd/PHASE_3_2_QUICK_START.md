# Phase 3.2 Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- Node.js 18+ installed on your system
- npm or yarn package manager
- Backend server running on `localhost:5000`

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd web
npm install
```

This installs all required packages:
- React 18.2.0
- React DOM 18.2.0
- React Router DOM 6.20.0
- Socket.io-client 4.7.2
- Axios 1.6.2
- TypeScript 5.2.2
- Vite 5.0.2

### Step 2: Configure Backend URL

The API is configured to proxy calls to `http://localhost:5000` via Vite's configuration. If your backend is on a different port, update `web/vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_PORT', // Change this
      changeOrigin: true,
    },
  },
}
```

### Step 3: Start Development Server

```bash
npm run dev
```

The application will:
- Start on `http://localhost:3000`
- Enable hot module reloading (HMR)
- Show any TypeScript errors in the terminal

### Step 4: Open in Browser

Navigate to: http://localhost:3000

## First Time Usage

1. **Create Account**
   - Click "Register" in the navbar
   - Enter username, email, and password
   - Password must be at least 6 characters
   - Click "Register" to create account

2. **Login**
   - Use the credentials you just created
   - You'll be redirected to the converter page

3. **Test Conversion**
   - Upload a test file (PDF, DOCX, etc.)
   - Select a conversion tool
   - Click "Start Conversion"
   - Watch real-time progress

4. **Check History**
   - Click "History" in the navbar
   - View all your conversions
   - Retry failed conversions
   - Download previous results

## Available Scripts

```bash
# Start development server (with HMR)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run ESLint
npm run lint
```

## Folder Structure

```
web/
├── src/
│   ├── api/              # Backend API calls
│   │   ├── axios.ts
│   │   ├── auth.ts
│   │   ├── conversion.ts
│   │   └── websocket.ts
│   ├── components/       # Reusable components
│   │   ├── Auth/         # Login, Register, ProtectedRoute
│   │   ├── Converter/    # File upload, tool selection, job status
│   │   ├── History/      # History table, status badge, retry button
│   │   └── index.ts
│   ├── hooks/            # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useJobStatus.ts
│   │   ├── useWebSocket.ts
│   │   └── index.ts
│   ├── pages/            # Page components
│   │   ├── ConverterPage.tsx
│   │   ├── HistoryPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── index.ts
│   ├── styles/           # CSS files
│   │   ├── Auth.css
│   │   ├── Converter.css
│   │   ├── JobStatus.css
│   │   ├── History.css
│   │   └── Pages.css
│   ├── types/            # TypeScript interfaces
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── index.html            # HTML template
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## Common Tasks

### Add a New Component

1. Create component file in `src/components/Category/`
2. Export from `src/components/Category/index.ts`
3. Export from main `src/components/index.ts`
4. Import and use in your pages

Example:
```tsx
// src/components/MyCategory/MyComponent.tsx
export default function MyComponent() {
  return <div>My Component</div>
}

// src/components/MyCategory/index.ts
export { default as MyComponent } from './MyComponent'

// src/components/index.ts
export * from './MyCategory'
```

### Create a New Page

1. Create page file in `src/pages/`
2. Export from `src/pages/index.ts`
3. Add route to `src/App.tsx`

Example:
```tsx
// Add to routes
<Route path="/my-page" element={
  <ProtectedRoute>
    <MyPage />
  </ProtectedRoute>
} />
```

### Update API Integration

1. Modify `src/api/[module].ts`
2. Update TypeScript interfaces in `src/types/index.ts`
3. Update components that use the API

### Add Styling

1. Create CSS file in `src/styles/`
2. Import in your component: `import '../styles/MyStyles.css'`
3. Use BEM naming for classes

## Troubleshooting

### "npm: command not found"
- Node.js may not be installed correctly
- Try: `node --version`
- Install from: https://nodejs.org/

### Port 3000 already in use
Change the port in `vite.config.ts`:
```typescript
server: {
  port: 3001, // or any available port
}
```

### Backend connection failed
- Ensure backend is running on `localhost:5000`
- Check proxy configuration in `vite.config.ts`
- Check browser console for network errors (F12 → Network tab)

### TypeScript errors
- Run `npm run lint` to see all errors
- Errors are also shown in the terminal during development
- Check `src/types/index.ts` for interface definitions

### Hot reload not working
- Restart the dev server: `Ctrl+C` then `npm run dev`
- Check that you're editing the correct file

## Building for Production

```bash
# Create optimized build
npm run build

# This creates:
# - dist/index.html
# - dist/assets/[filename].js (minified)
# - dist/assets/[filename].css (minified)

# Preview production build locally
npm run preview
```

## Environment Variables

Create a `.env` file in the `web/` directory:

```env
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Document Converter
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

## Testing the Features

### Authentication Flow
1. Register → Login → Logout
2. Try accessing `/converter` without logging in (should redirect to /login)
3. Check localStorage to see auth token (F12 → Application → Local Storage)

### File Upload
1. Try dragging a file onto the upload area
2. Try clicking to select files
3. Try removing files individually

### Conversion
1. Upload file → Select tool → Start conversion
2. Watch the progress bar update (real-time via WebSocket or polling)
3. Download result when complete

### History
1. Convert some files
2. Go to History page
3. Sort by date/status
4. Retry a conversion (if any failed)

## Performance Tips

1. **Lazy Load Routes**
   ```typescript
   const ConverterPage = lazy(() => import('./pages/ConverterPage'))
   ```

2. **Optimize Images**
   - Use SVG instead of PNG where possible
   - Compress large images

3. **Minimize Bundle Size**
   - Use `npm run build` and check the output size
   - Analyze with: `npm install --save-dev vite-plugin-visualizer`

4. **Enable Compression**
   - Make sure gzip compression is enabled on server

## Useful Keyboard Shortcuts

| Shortcut | Effect |
|----------|--------|
| Ctrl+Shift+K | Open DevTools Console |
| F12 | Open DevTools |
| Ctrl+Shift+I | Open DevTools Inspector |
| Ctrl+Shift+J | Open DevTools Console (Windows) |
| Cmd+Option+J | Open DevTools Console (Mac) |

## Getting Help

### Check the Documentation
- [React Documentation](https://react.dev)
- [React Router Documentation](https://reactrouter.com)
- [Vite Documentation](https://vitejs.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)

### Common Issues

**WebSocket not connecting:**
- Check browser console (F12) for errors
- Ensure backend has Socket.io enabled
- App will fall back to HTTP polling automatically

**CORS errors:**
- Check that proxy is configured in `vite.config.ts`
- Backend should have CORS headers configured

**Token expiration:**
- AuthAPI will redirect to login on 401 response
- Token is stored in localStorage and cleared on logout

## Next Steps

After getting comfortable with the setup:

1. **Modify Components** - Try changing colors, text, layouts
2. **Add New Features** - Create your own custom components
3. **Connect to Real Files** - Test with actual document conversion
4. **Deploy** - Follow deployment guide for production

---

**Phase 3.2 Setup Complete!** 🎉

You now have a fully functional React frontend for the document converter application. Start the development server and begin exploring!
