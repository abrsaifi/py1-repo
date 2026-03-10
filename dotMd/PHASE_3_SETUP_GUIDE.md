# Phase 3: React Migration - Setup & Getting Started

## 🎉 Phase 3.1 Foundation Complete!

The React web application foundation has been established with:
- ✅ Vite + React + TypeScript project structure
- ✅ Complete API integration layer
- ✅ Custom React hooks for state management
- ✅ WebSocket client with fallback to polling
- ✅ Authentication flow integration
- ✅ Comprehensive type definitions
- ✅ Production-ready configuration

**Status:** Foundation ready for component development  
**Next Step:** Create authentication UI components

---

## Prerequisites

Before starting, ensure you have:
- **Node.js** 16+ installed ([download](https://nodejs.org))
- **npm** or **yarn** package manager
- **Git** for version control
- **Backend API** running on `http://localhost:5000`

### Verify Installation

```bash
node --version    # Should show v16.0.0 or higher
npm --version     # Should show 8.0.0 or higher
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd web
npm install
```

This installs:
- `react` & `react-dom` - React framework
- `socket.io-client` - Real-time communication
- `axios` - HTTP client
- TypeScript, Vite, ESLint development tools

**Time:** ~2-3 minutes (first time)

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local` if needed (default localhost:5000 should work):

```
VITE_API_URL=http://localhost:5000
VITE_WS_URL=http://localhost:5000
```

### 3. Start Development Server

```bash
npm run dev
```

Output will show:
```
  VITE v5.0.0  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

**Open browser:** http://localhost:3000

### 4. Verify Connection

When you open the app:
- You should see the Document Converter header
- Navigation bar with Home, Login prompt
- WebSocket indicator (🔗 or ⚠️) in top-right
- No errors in browser console

---

## Project Structure

```
web/
├── src/
│   ├── api/                    # Backend communication
│   │   ├── axios.ts           # HTTP client with auth
│   │   ├── auth.ts            # Login/register/profile
│   │   ├── conversion.ts       # File conversion operations
│   │   └── websocket.ts        # Real-time updates
│   │
│   ├── components/             # React UI components (to create)
│   │   ├── Auth/              # Login/Register forms
│   │   ├── Converter/         # File upload & conversion
│   │   ├── History/           # Conversion history
│   │   └── Common/            # Reusable components
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts         # Auth state management
│   │   ├── useJobStatus.ts    # Job polling
│   │   └── useWebSocket.ts    # WebSocket events
│   │
│   ├── types/                  # TypeScript interfaces
│   │   └── index.ts           # All type definitions
│   │
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # App styling
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
│
├── index.html                  # HTML template
├── package.json                # Dependencies & scripts
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript config
├── .eslintrc.cjs               # Code quality rules
├── .env.example                # Environment template
└── README.md                   # Detailed documentation
```

---

## Development Workflow

### Making Changes

1. **Edit a file** in `src/` (e.g., modify App.tsx)
2. **Save the file**
3. **Browser automatically refreshes** (Hot Module Reload)
4. **Changes appear instantly** (component state may be preserved)

### Running Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server (localhost:3000) |
| `npm run build` | Create optimized production build |
| `npm run preview` | Test production build locally |
| `npm run lint` | Check code quality with ESLint |
| `npm run lint -- --fix` | Auto-fix common linting issues |

### Using Developer Tools

**Browser DevTools:**
```
F12 or Right-click → Inspect
```

**React DevTools Extension:**
- Type `$r` in console to inspect selected component
- View hooks, props, and state in DevTools panel
- Time-travel debugging for state changes

**Console Tips:**
- Any errors will show with red background
- API calls visible in Network tab
- WebSocket activity in Network tab (also shows WS messages)

---

## Next: Building Components

### Phase 3.2 - Core Components

Follow this order for maximum productivity:

### 1. Authentication Components (2-3 hours)

**Files to create:**
- `src/components/Auth/Login.tsx` - Login form
- `src/components/Auth/Register.tsx` - Registration form  
- `src/components/Auth/ProtectedRoute.tsx` - Route guard
- `src/components/Auth/AuthContext.tsx` - Global auth state

**Starter template:**
```typescript
import React from 'react'
import { login } from '../../api/auth'
import './Login.css'

interface LoginProps {
  onSuccess?: () => void
}

export const Login: React.FC<LoginProps> = ({ onSuccess }) => {
  const [username, setUsername] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await login(username, password)
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-form">
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  )
}
```

### 2. File Upload Components (2-3 hours)

**Files to create:**
- `src/components/Converter/FileUpload.tsx` - Drag-drop upload
- `src/components/Converter/ToolSelector.tsx` - Choose conversion tool
- `src/components/Converter/ParameterForm.tsx` - Tool settings

### 3. Progress & Results (1-2 hours)

**Files to create:**
- `src/components/Converter/ProgressBar.tsx` - Job progress
- `src/components/Converter/ResultDownload.tsx` - Download files

### 4. History Components (2-3 hours)

**Files to create:**
- `src/components/History/HistoryTable.tsx` - Conversion list
- `src/components/History/JobStatusBadge.tsx` - Status indicator

---

## API Integration Example

### Using the API

```typescript
import { startConversion, getJobStatus } from '../api/conversion'

// Start a conversion
const response = await startConversion('To PDF', files, {
  quality: 'high',
  margin: '10mm'
})

console.log('Job started:', response.job_id)

// Get status
const job = await getJobStatus(response.job_id)
console.log('Progress:', job.progress)
```

### Using Custom Hooks

```typescript
import { useJobStatus, useAuth } from '../hooks'

function MyComponent() {
  const { user, isAuthenticated } = useAuth()
  const { job, isLoading, error } = useJobStatus(jobId)

  return (
    <div>
      {isLoading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {job && <p>Progress: {job.progress}%</p>}
    </div>
  )
}
```

### Using WebSocket

```typescript
import { useWebSocketJob } from '../hooks'

function JobMonitor({ jobId }) {
  useWebSocketJob(jobId, (data) => {
    if (data.status === 'complete') {
      console.log('Job completed!', data.result)
    }
  })

  return <p>Listening for updates...</p>
}
```

---

## Troubleshooting

### Issue: "Module not found" or "Cannot find module"

**Solution:**
```bash
npm install
```

Then restart dev server:
```bash
npm run dev
```

### Issue: "Port 3000 already in use"

**Solution 1:** Kill the existing process
```bash
# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -i :3000
kill -9 <PID>
```

**Solution 2:** Use different port
```bash
npm run dev -- --port 3001
```

### Issue: API requests failing / CORS error

**Verify:**
1. Backend running: `python server.py` on port 5000
2. Check `.env.local` has `VITE_API_URL=http://localhost:5000`
3. Check Network tab in DevTools for request details
4. Restart both backend and frontend

### Issue: WebSocket not connecting

**Check:**
- Backend has Socket.io enabled (should see `WEBSOCKET_ENABLED = True` in logs)
- Browser tab shows 🔗 (connected) or ⚠️ (polling fallback)
- Console shows any connection errors
- Both frontend and backend on same domain/port

### Issue: TypeScript compilation errors

**Solution:**
```bash
# Check for errors
npm run build

# Fix issues:
# 1. Verify imports use correct paths
# 2. Check types are properly defined
# 3. Restart dev server
npm run dev
```

---

## Running Tests (Future)

Once Vitest is configured:

```bash
npm run test              # Run all tests
npm run test -- --watch   # Watch mode
npm run test -- --coverage # Coverage report
```

---

## Building for Production

```bash
npm run build
```

Creates optimized `dist/` directory (~100KB gzipped)

### Serving from Python Backend

```python
from flask import send_from_directory

app.static_folder = 'web/dist'

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')
```

### Deploy to Cloud

- **Netlify:** `npm run build` → drag `dist` folder
- **Vercel:** Connect GitHub → auto-builds on push
- **GitHub Pages:** Use `gh-pages` package
- **Azure/AWS:** Configure static hosting

---

## Best Practices

### Code Organization

✅ **DO:**
- Keep components small and focused
- Extract common logic into custom hooks
- Use TypeScript types for props
- Import from barrel files (`hooks/`, `components/`)

❌ **DON'T:**
- Put all logic in App.tsx
- Use `any` type (use proper types)
- Hard-code API URLs (use .env)
- Fetch data in render function

### Performance

✅ **DO:**
- Use React.memo for expensive components
- Implement lazy loading for routes
- Cache API responses when appropriate
- Minimize bundle size

❌ **DON'T:**
- Create new objects/functions in render
- Pass inline functions as props
- Subscribe multiple times to same event
- Load all data at app start

### Error Handling

✅ **DO:**
- Show user-friendly error messages
- Log errors for debugging
- Gracefully handle network failures
- Implement error boundaries

❌ **DON'T:**
- Show raw error stack traces to users
- Ignore errors silently
- Assume network always works
- Crash on validation errors

---

## Resources

📚 **Documentation**
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Vite Guide](https://vitejs.dev/guide)
- [Socket.io Client](https://socket.io/docs/v4/client-api/)

🎓 **Tutorials**
- React fundamentals
- TypeScript for React developers
- Building a complete app from scratch

🔗 **Tools**
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [React DevTools Extension](https://react-devtools-tutorial.vercel.app/)
- [VS Code Extensions](https://marketplace.visualstudio.com/)

---

## Questions & Support

**Common questions will be documented in the web/README.md file.**

For specific issues:
1. Check browser console for errors (F12)
2. Check Network tab for failed requests
3. Review the API integration code in `src/api/`
4. Check the backend logs for server-side errors

---

**Ready to build components!** 🚀

Next: Create the Login and Register components for Phase 3.2
