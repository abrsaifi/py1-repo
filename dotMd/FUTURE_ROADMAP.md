# 🚀 Future Roadmap - Marked for Later Implementation

**Last Updated:** February 23, 2026  
**Status:** All Critical SPA fixes complete ✅

---

## 📋 Phase 1: Production Finalization
**Priority: HIGH** | **Effort: Medium** | **Timeline: 1-2 weeks**

- [x] Reduce rate limit back to 5/min (from current 20/min testing limit)
  - File: `server.py` line 228
  - Change: `_rate_limit_max_requests = 5` ✅ DONE
  
- [x] Implement job persistence (database storage)
  - Add SQLite database for job history ✅ DONE
  - Store completed jobs beyond memory ✅ DONE
  - Track conversion metrics ✅ DONE
  - New file: `services/database.py`
  
- [x] Security hardening
  - Add input sanitization enhancements ✅ (verified in utils.py)
  - Implement CORS & security headers ✅ DONE
  - Add UUID validation for job_id parameters ✅ DONE
  - ~~Rate limit by user authentication (not just IP)~~ SKIPPED (as requested)
  - Encrypt sensitive data in job registry ⏳ (optional)
  
- [x] Performance optimization
  - Job cleanup scheduler ✅ DONE
  - Database clean up old jobs (>7 days) ✅ DONE
  - Periodic cleanup triggered on status checks ✅ DONE

---

## 💡 Phase 2: Enhanced Features
**Priority: MEDIUM** | **Effort: High** | **Timeline: 2-3 weeks**

- [x] User accounts & authentication (✅ COMPLETE)
  - User registration/login ✅ DONE
  - Per-user rate limiting (deferred)
  - Conversion history per user ✅ DONE
  - Favorite tools/presets ✅ DONE
  - API keys for programmatic access ✅ DONE
  - File: `services/auth.py`, `AUTH_API_QUICK_START.md`
  
- [x] WebSockets instead of polling (✅ COMPLETE)
  - Reduce network bandwidth ✅ DONE
  - Real-time bidirectional updates ✅ DONE
  - Better for mobile connections ✅ DONE
  - Requires: `python-socketio`, `python-engineio`, `flask-socketio` ✅ INSTALLED
  - File: `services/websocket.py`, `WEBSOCKET_GUIDE.md`
  
- [x] Job resumption capability (✅ COMPLETE)
  - Save failed job state to database ✅ DONE
  - Allow users to resume/retry conversions ✅ DONE
  - Track conversion attempts ✅ DONE
  - Preserve original parameters ✅ DONE
  - File: `/api/convert/resume/{job_id}` endpoint
  - File: `JOB_RESUMPTION_GUIDE.md`
  
- [ ] Notification system
  - Email notifications on completion
  - Webhook support for external integrations
  - In-app notification center
  - SMS/push notifications (optional)

---

## ⚛️ Phase 3: React Migration
**Priority: HIGH** | **Effort: Very High** | **Timeline: 4-6 weeks** | **Status: Foundation (✅ Started)**

### Phase 3.1: Project Foundation (✅ Complete)

- [x] Project initialization
  - Created Vite + React + TypeScript project structure ✅
  - Configured TypeScript with strict mode ✅
  - Set up ESLint and code quality rules ✅
  - File: `web/` directory with full scaffolding
  
- [x] API integration layer
  - Created axios instance with interceptors ✅
  - Auth API module (`login`, `register`, `profile`, etc.) ✅
  - Conversion API module (`start`, `status`, `resume`, `download`) ✅
  - WebSocket client manager with event system ✅
  - Automatic token attachment to requests ✅
  - 401 error handling with logout ✅
  
- [x] Custom hooks
  - `useAuth` - Authentication state management ✅
  - `useJobStatus` - Job status polling with interval ✅
  - `useWebSocketJob` - Real-time job updates ✅
  - `useWebSocketEvents` - General WebSocket events ✅
  
- [x] Type definitions
  - TypeScript interfaces for all API responses ✅
  - Tool parameters and configuration types ✅
  - Job state and upload tracking types ✅
  - User and API response types ✅
  
- [x] Core application shell
  - App.tsx with routing structure ✅
  - Navigation bar with user info ✅
  - Footer and basic layout ✅
  - WebSocket initialization on app load ✅
  - Authentication state integration ✅
  
- [x] Configuration files
  - vite.config.ts with API proxy ✅
  - tsconfig.json with path aliases ✅
  - .eslintrc.cjs for code quality ✅
  - .env.example for configuration ✅
  - .gitignore for repository ✅

### Phase 3.2: Core Components (Next - In Progress)

- [ ] Authentication Components
  - [ ] Login form with validation
  - [ ] Register form with password confirmation
  - [ ] Protected route wrapper
  - [ ] Authentication context provider
  - Estimated: 2-3 hours

- [ ] File Upload Components
  - [ ] Drag-and-drop upload area
  - [ ] File list with preview
  - [ ] Progress indicators per file
  - [ ] File size validation UI
  - Estimated: 2-3 hours

- [ ] Converter Components
  - [ ] Tool selector dropdown
  - [ ] Dynamic parameter form generator
  - [ ] Real-time progress bar with percentage
  - [ ] Result download button
  - [ ] Error display and retry button
  - Estimated: 3-4 hours

- [ ] History Components
  - [ ] Conversion history table
  - [ ] Status badges (processing, complete, failed)
  - [ ] Search and filter functionality
  - [ ] Retry failed conversion button
  - [ ] Download previous results
  - Estimated: 2-3 hours

### Phase 3.3: Complete Pages (Later)

- [ ] Pages
  - [ ] HomePage - Landing page
  - [ ] ConverterPage - Main conversion UI
  - [ ] HistoryPage - Conversion history
  - [ ] SettingsPage - User preferences
  - [ ] ProfilePage - Account management
  
- [ ] Navigation & Routing
  - [ ] React Router setup
  - [ ] Route guards for auth
  - [ ] Per-page layouts
  - [ ] Deep linking support

### Phase 3.4: Advanced Features (Later)

- [ ] Real-time metrics dashboard
  - [ ] Live conversion statistics
  - [ ] Performance charts
  - [ ] Tool usage analytics
  
- [ ] Favorites & Presets
  - [ ] Save favorite conversion parameters
  - [ ] Load saved presets
  - [ ] Manage presets interface
  
- [ ] API Key Management
  - [ ] View active API keys
  - [ ] Create new keys
  - [ ] Revoke keys
  - [ ] Copy/show secrets (once)
  
- [ ] Notifications & Alerts
  - [ ] Toast notifications for actions
  - [ ] Success/error alerts
  - [ ] Job completion notifications
  - [ ] Browser notifications (optional)

- [ ] Testing Framework
  - [ ] Unit tests with Vitest
  - [ ] Component tests with React Testing Library
  - [ ] E2E tests with Playwright
  - [ ] CI/CD pipeline

---

## 🧪 Phase 4: Testing & Documentation
**Priority: MEDIUM** | **Effort: High** | **Timeline: 2-3 weeks**

- [ ] Integration tests
  - Test async conversion workflow
  - Test rate limiting
  - Test file size validation
  - Test error handling paths
  - Test concurrent jobs
  
- [ ] Load testing
  - JMeter/Locust for stress testing
  - Benchmark async system
  - Find bottlenecks
  - Measure response times
  - Concurrent user capacity
  
- [ ] API documentation
  - OpenAPI/Swagger spec
  - Generate interactive docs
  - Add request/response examples
  - Document error codes
  - Auth flows
  
- [ ] User documentation
  - Getting started guide
  - Feature explanations
  - Troubleshooting section
  - FAQ
  - Video tutorials
  
- [ ] Developer documentation
  - Architecture diagrams
  - Database schema (when added)
  - Component structure (for React)
  - Contributing guidelines
  - Local setup instructions

---

## 📊 Current System Status

### ✅ Completed (Latest Session)
- Async job tracking with thread safety
- Rate limiting (per-IP, sliding window) - now set to 5/min production limit
- File size validation (100MB limit)
- Frontend polling mechanism (1-second intervals)
- Real-time progress bar (0-100%)
- Error handling (429, 413, timeouts)
- File I/O fixes (no more "closed file" errors)
- Server fully functional and tested
- **Phase 1:** Job persistence with SQLite database
- **Phase 1:** UUID validation for job parameters
- **Phase 1:** Security headers (CORS, X-Frame-Options, etc.)
- **Phase 1:** Automatic job cleanup scheduler (7-day retention)
- **Phase 1:** Job metrics and analytics database
- **NEW:** Metrics Dashboard Endpoint - `/api/metrics` and `/dashboard` routes
  - File: `server.py` lines 7202-7390
  - Features: Overview cards, tool analytics, hourly trends, detailed tables
  - Technology: Chart.js for visualizations, responsive design
  - Access: Visit http://localhost:5000/dashboard for visual dashboard
  - API: `/api/metrics` returns JSON for programmatic access
- **PHASE 2:** User Authentication System (✅ Complete)
  - New database module: `services/auth.py` (password hashing, JWT tokens)
  - Enhanced database schema: users, api_keys, user_favorites tables
  - Registration endpoint: `POST /api/auth/register` (username, email, password)
  - Login endpoint: `POST /api/auth/login` (returns JWT token)
  - API Keys system: `POST /api/auth/api-keys` (create programmatic access keys)
  - User profile endpoint: `GET /api/user/profile` (requires auth)
  - Conversion history: `GET /api/user/history` (per-user history, requires auth)
  - User favorites: `GET/POST /api/user/favorites` (save tool presets, requires auth)
  - Password hashing: PBKDF2-SHA256 with salt
  - Token validation: JWT-based with fallback token system
  - File: `services/auth.py` (authentication manager, password/token utilities)
  - File: `services/database.py` (extended with 3 new tables, 8 new methods)
- **PHASE 2:** WebSocket Real-Time Updates (✅ Complete)
  - New module: `services/websocket.py` (WebSocket manager)
  - Flask-SocketIO integration for bidirectional communication
  - Event handlers: watch_job, unwatch_job, job_started, job_completed, job_error
  - Job rooms: clients join room `job_{job_id}` to receive updates
  - Server broadcasts: job_started, job_completed, job_error events
  - Fallback: HTTP polling if WebSocket unavailable
  - Client libraries: Vanilla JS, Vue.js, React examples
  - Documentation: Complete implementation guide with examples
  - File: `WEBSOCKET_GUIDE.md` (client implementation examples)
  - Packages installed: python-socketio, python-engineio, flask-socketio
- **PHASE 2:** Job Resumption Capability (✅ Complete)
  - Resume failed conversions with new files
  - Preserve original conversion parameters
  - Track retry history and retry counts
  - Automatic linking of original and resumed jobs
  - New endpoint: `POST /api/convert/resume/{job_id}`
  - Database methods: `mark_job_as_retried()`, `update_job_metadata()`
  - Metadata storage for form_data and retry tracking
  - Documentation: Complete guide with code examples for all frameworks
  - File: `JOB_RESUMPTION_GUIDE.md`
  - Supports both WebSocket and HTTP polling for job status
- **PHASE 3:** React Migration Foundation (✅ Complete)
  - Project setup with Vite + React + TypeScript
  - API integration layer with axios and interceptors
  - Authentication API module with login/register/profile
  - Conversion API module with start/status/resume/download
  - WebSocket client manager with event subscription system
  - Custom hooks: useAuth, useJobStatus, useWebSocketJob, useWebSocketEvents
  - Type definitions for all data structures
  - Core App component with navigation and routing structure
  - Configuration files: vite.config.ts, tsconfig.json, eslint, env
  - Comprehensive documentation in web/README.md
  - Ready for component implementation
  - Files: Complete `web/` directory structure

### 🔄 In Progress
- **Phase 3: React Migration (Foundation Complete, Components Next)**
  - ✅ Project setup with Vite + TypeScript
  - ✅ API integration layer fully configured
  - ✅ Custom hooks for auth and WebSocket
  - ✅ App shell and navigation structure
  - 🔄 Components: File upload, converter, history
  - 🔄 Pages: Login, converter, history, settings

### ⏳ Backlog (Priority Order)
1. ~~Rate limit to 5/min~~ ✅ DONE
2. ~~Database persistence~~ ✅ DONE
3. ~~User Authentication~~ ✅ DONE
4. ~~WebSocket real-time updates~~ ✅ DONE
5. ~~Job resumption capability~~ ✅ DONE
6. ✅ Phase 3 Foundation (project setup, API integration, hooks)
7. Phase 3 Components (file upload, converter, history) - IN PROGRESS
8. Per-user rate limiting (adapt from IP-based system)
9. Notification system
10. Batch processing mode

---

## 📌 Technical Debt

- [ ] Remove test rate limit comments from code
- [ ] Add comprehensive error logging
- [ ] Refactor large functions in server.py (>200 lines)
- [ ] Add type hints to Python functions
- [ ] Clean up HTML comments (200+ lines of comments)
- [ ] Optimize CSS (currently inline, move to stylesheet)
- [ ] Add request validation schemas
- [ ] Implement job cleanup scheduler

---

## 🎯 Key Metrics to Track

When implementing future phases, measure:
- Conversion completion time (baseline: current)
- Network bandwidth usage (polling vs WebSockets)
- Server memory usage (job registry growth)
- API response times (before/after optimizations)
- User satisfaction (conversion success rate)
- Error rates (by error type)

---

## 🔗 Related Documents

- [SPA_READINESS_ASSESSMENT.md](SPA_READINESS_ASSESSMENT.md) - Initial assessment (4.5/10 readiness before fixes)
- [TEST_ASYNC_CONVERSION.md](TEST_ASYNC_CONVERSION.md) - Testing guide for current system
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment steps (update when DB added)

---

## 📝 Notes

### Production Checklist
- [ ] Change `_rate_limit_max_requests` from 20 to 5
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring/alerting
- [ ] Configure backup strategy (when DB added)
- [ ] Update security headers
- [ ] Set up CDN for static assets
- [ ] Configure log rotation

### Testing Before Merge
- [ ] Load test with 50+ concurrent users
- [ ] Test with 10GB+ total file uploads
- [ ] Verify rate limiting under load
- [ ] Test timeout scenarios (30 min limit)
- [ ] Check memory leaks in long-running conversions
- [ ] Test browser compatibility (all major + mobile)

---

**Last Review:** 23 Feb 2026  
**Next Review:** After features complete or quarterly
