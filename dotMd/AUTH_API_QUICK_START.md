# User Authentication API - Quick Start Guide

## Overview
Complete user authentication system with registration, login, API keys, and user account features.

---

## 1. User Registration

**Endpoint:** `POST /api/auth/register`

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 2. User Login

**Endpoint:** `POST /api/auth/login`

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 3. Create API Key (for programmatic access)

**Endpoint:** `POST /api/auth/api-keys`  
**Requires:** Bearer token from login

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USERNAME_TOKEN" \
  -d '{
    "name": "Mobile App"
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "key_id": "api_key_123456",
  "secret": "your_api_secret_key_here",
  "name": "Mobile App",
  "message": "Save your secret in a secure location - it will not be shown again"
}
```

⚠️ **Save the secret immediately** - it won't be shown again!

---

## 4. Protected Endpoints (Require Authentication)

All protected endpoints require the `Authorization: Bearer TOKEN` header.

### Get User Profile

**Endpoint:** `GET /api/user/profile`

```bash
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "550e8400...",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2026-02-24T10:30:00",
    "last_login": "2026-02-24T15:45:00",
    "is_active": 1
  }
}
```

---

### Get Conversion History

**Endpoint:** `GET /api/user/history?limit=50`

```bash
curl -X GET http://localhost:5000/api/user/history?limit=30 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "job_id": "abc-123-def",
      "tool_name": "To PDF",
      "status": "complete",
      "file_count": 3,
      "created_at": "2026-02-24T15:20:00",
      "completed_at": "2026-02-24T15:21:45",
      "elapsed_seconds": 105.5
    }
  ],
  "count": 1
}
```

---

### Get User Favorites

**Endpoint:** `GET /api/user/favorites`

```bash
curl -X GET http://localhost:5000/api/user/favorites \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "favorites": [
    {
      "favorite_id": 1,
      "tool_name": "To PDF",
      "preset_name": "High Quality PDF",
      "settings": "{\"quality\": \"95\"}",
      "created_at": "2026-02-24T10:30:00"
    }
  ],
  "count": 1
}
```

---

### Save Favorite Tool Preset

**Endpoint:** `POST /api/user/favorites`

```bash
curl -X POST http://localhost:5000/api/user/favorites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tool_name": "To PDF",
    "preset_name": "High Quality PDF",
    "settings": {
      "quality": "95",
      "page_size": "A4",
      "margin": "1cm"
    }
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Favorite saved successfully"
}
```

---

## 5. Starting Conversions with User Account

When a user is authenticated, you can attach their account to conversion jobs:

**Endpoint:** `POST /api/convert` (with auth header)

```bash
# Upload files and start conversion with user tracking
curl -X POST http://localhost:5000/api/convert \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.docx" \
  -F "tool_name=To PDF"
```

The job will be automatically linked to the user's account and appear in their history!

---

## 6. Frontend Integration Example

### Vue.js / JavaScript Example

```javascript
// 1. Register
async function register(username, email, password) {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user_id', data.user_id);
  }
  return data;
}

// 2. Login
async function login(username, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user_id', data.user_id);
  }
  return data;
}

// 3. Make authenticated request
async function getProfile() {
  const token = localStorage.getItem('token');
  const response = await fetch('/api/user/profile', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 4. Start conversion with auth
async function startConversion(files, toolName) {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  formData.append('tool_name', toolName);
  
  const token = localStorage.getItem('token');
  const response = await fetch('/api/convert', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return await response.json();
}
```

---

## 7. Security Notes

✅ **Implemented:**
- Passwords hashed with PBKDF2-SHA256 + salt (100,000 iterations)
- JWT tokens with configurable expiry (default: 24 hours)
- API secrets hashed before storage
- Bearer token authentication on all protected endpoints
- Input validation on all registration/login
- Account activation status check

🔒 **Best Practices:**
- Always use HTTPS in production (not just HTTP)
- Store tokens in HTTPOnly cookies (not localStorage)
- Implement token refresh endpoints
- Add rate limiting to auth endpoints (prevent brute force)
- Add optional 2FA / email verification
- Implement password reset flow

---

## 8. Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common status codes:
- `400` - Bad request (missing/invalid fields)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (account disabled)
- `404` - Not found
- `500` - Server error

---

## 9. Next Steps (Phase 2 Features)

After authentication is solid, implement:

1. **Per-user rate limiting** - Currently 5/min global, upgrade to per-user limits
2. **WebSockets** - Replace HTTP polling with real-time updates
3. **Job Resumption** - Allow retrying failed conversions with saved state
4. **Email Verification** - Confirm email before account activation
5. **Password Reset** - Secure password recovery flow
6. **API Key Permissions** - Granular access control for API keys

---

Last Updated: February 24, 2026
