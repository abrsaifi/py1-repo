# Demo Accounts - Quick Reference

## 🎯 Overview

Two demo accounts are ready to use for testing the admin dashboard and user dashboard.

---

## 👨‍💼 Admin Account

For testing **Admin Dashboard** features (users, settings, analytics, etc.)

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `demo123` |
| Email | `admin@example.com` |
| Role | Admin |
| Access Level | Full system access, user management, analytics |

**Where to Login:**
- Open: http://localhost:5173
- Click: **"Admin Login"** button
- OR direct URL: http://localhost:5173/admin-login

**What You Can Do:**
- ✅ View Admin Dashboard
- ✅ User Management (list, delete, view details)
- ✅ Settings & API Keys
- ✅ System Analytics & Reports
- ✅ Compliance & Security Logs
- ✅ Multi-region Configuration
- ✅ Auto-scaling Management

---

## 👤 Subscriber Account

For testing **User Dashboard** features (user profile, tools, conversions, etc.)

| Field | Value |
|-------|-------|
| Username | `subscriber` |
| Password | `demo123` |
| Email | `subscriber@example.com` |
| Role | Subscriber/User |
| Access Level | Limited to user features |

**Where to Login:**
- Open: http://localhost:5173
- Click: **"User Login"** button  
- OR direct URL: http://localhost:5173/login

**What You Can Do:**
- ✅ View User Dashboard
- ✅ Access Tools (file conversion, etc.)
- ✅ View Conversion History
- ✅ Manage Profile & Account
- ✅ View Personal Analytics
- ✅ API Key Management (personal)

---

## 🚀 How to Use

### 1. Start the Servers

**Terminal 1 - Flask API (Port 5000):**
```powershell
cd c:\Users\dell\OneDrive\Documents\py1
.venv\Scripts\python.exe -m flask run --port 5000
```

**Terminal 2 - Vite Dev (Port 5173):**
```powershell
cd c:\Users\dell\OneDrive\Documents\py1\frontend-analytics
npm run dev
```

### 2. Open the Dashboard

Navigate to: **http://localhost:5173**

### 3. Login

- **For Admin Dashboard:** Use `admin` / `demo123`
- **For User Dashboard:** Use `subscriber` / `demo123`

---

## 🔄 Fallback Authentication

Both demo accounts work in **two modes:**

1. **With Backend (Preferred):**
   - Credentials validated against Flask database
   - Token stored in localStorage
   - Full API integration

2. **Without Backend (Fallback):**
   - Frontend accepts hardcoded demo credentials
   - Works even if Flask server is down
   - Great for quick testing

---

## 🔐 Reset Credentials

To reset credentials to defaults, run:

```bash
# Reset admin account
python reset_admin_credentials.py

# Reset subscriber account  
python reset_subscriber_credentials.py
```

### Output Example:
```
======================================================================
✅ ADMIN ACCOUNT READY
======================================================================

📧 Email:    admin@example.com
👤 Username: admin
🔐 Password: demo123

🌐 Login at: http://localhost:5173
   • Click 'Admin Login'
   • Enter credentials above
   • Dashboard will load automatically
```

---

## 📊 Dashboard Components Accessible

### Admin Dashboard (`/admin`)
- Dashboard Overview
- User Management
- Analytics & Reports
- Settings & Configuration
- Security & Compliance
- Multi-Region Deployment
- Auto-scaling Management
- Disaster Recovery

### User Dashboard (`/dashboard`)
- Personal Dashboard
- Conversion Tools
- File Upload & Processing
- Conversion History
- Account Settings
- Profile Management
- Usage Analytics

---

## 💾 Database Location

Demo accounts are stored in:
```
c:\Users\dell\OneDrive\Documents\py1\docpro_database.db
```

To view accounts via SQLite:
```bash
sqlite3 docpro_database.db "SELECT id, username, email FROM users;"
```

---

## 🎨 Dark Mode & Preferences

- Dark mode toggle available in **Settings** tab (Admin)
- User preferences saved to localStorage
- Persists across sessions for same browser

---

## ⚡ Quick Test Checklist

- [ ] Admin login works
- [ ] Admin dashboard loads
- [ ] User management tab accessible
- [ ] Subscriber login works
- [ ] User dashboard loads
- [ ] Tools page accessible
- [ ] Both can toggle dark mode
- [ ] Logout function works

---

## 🐛 Troubleshooting

### "Invalid credentials" error
- Check spelling: `admin` and `subscriber` (lowercase)
- Password is: `demo123`
- Both are case-sensitive

### Dashboard doesn't load
- Flask server must be running on port 5000
- Vite must be running on port 5173
- Check browser console for CORS errors

### API endpoints return 404
- Ensure Flask is running
- Check that `/api/*` routes are registered
- CORS should allow requests from localhost:5173

---

## 📱 HTTP Headers

API requests automatically include:
```
Content-Type: application/json
Authorization: Bearer [token]
Access-Control-Allow-Origin: * (with CORS)
```

---

## 🔗 Related Files

- Admin credentials: [`reset_admin_credentials.py`](reset_admin_credentials.py)
- Subscriber credentials: [`reset_subscriber_credentials.py`](reset_subscriber_credentials.py)
- Auth service: [`app/services/auth.py`](app/services/auth.py)
- Auth routes: [`app/api/routes/auth.py`](app/api/routes/auth.py)
- Frontend auth: [`frontend-analytics/src/hooks/useAuth.js`](frontend-analytics/src/hooks/useAuth.js)

---

**Last Updated:** March 10, 2026  
**Status:** ✅ Both demo accounts ready
