# Backend Setup & Testing Guide - Historical Auth Service Split

This document describes the older target auth-service plus api-gateway setup.
In the current workspace, the active backend runtime is the modular Flask application under `app/`, and async work is routed through `app/celery_config.py` plus `app/tasks.py`.
Use the service-split commands below as reference material rather than the primary way to boot this repository today.

**Complete Setup in 5 Minutes**

## Step 1: Start Infrastructure (2 min)

### Using Docker (Recommended)

```bash
# PostgreSQL
docker run -d \
  --name postgres_fileconv \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=file_converter \
  -p 5432:5432 \
  postgres:15

# Redis
docker run -d \
  --name redis_fileconv \
  -p 6379:6379 \
  redis:7
```

### Verify Running
```bash
docker ps
# Both postgres_fileconv and redis_fileconv should be listed
```

## Step 2: Install Python Dependencies (Historical Split Setup)

```bash
# From project root
cd services/auth-service && pip install -r requirements.txt
cd ../api-gateway && pip install -r requirements.txt
cd ../../packages/shared-models && pip install sqlalchemy psycopg2-binary pyjwt
cd ../shared-utils && pip install requests redis pyjwt
cd ../..
```

## Step 3: Start Services (Historical Split Setup)

**Open 2 separate terminal windows:**

### Terminal 1: Auth Service
```bash
cd services/auth-service
python main.py
```

**Expected output:**
```
✓ PostgreSQL connection successful
✓ All database tables created/verified
============================================================
  AUTH SERVICE STARTED
  Service: auth-service
  Version: 1.0.0
  Environment: development
  Port: 5001
  Routes:
    - POST /auth/register
    - POST /auth/login
    - POST /auth/verify
    - POST /auth/logout
    - GET  /auth/me
    - GET  /auth/health
============================================================
```

### Terminal 2: API Gateway
```bash
cd services/api-gateway
python main.py
```

**Expected output:**
```
✓ Redis connection successful  
✓ PostgreSQL connection initialized
============================================================
  API GATEWAY STARTED
  Service: api-gateway
  Version: 1.0.0
  Environment: development
  Port: 5000
  Proxies to:
    - /auth -> http://localhost:5001
    - /user -> http://localhost:5002
    - /convert -> http://localhost:5003
    - /billing -> http://localhost:5004
    - /analytics -> http://localhost:5005
    - /admin -> http://localhost:5006
  Rate Limit: 100 requests/minute
============================================================
```

## Step 4: Test the Historical Split Setup (Optional)

### Option A: Automated Tests (Recommended)

```bash
# Terminal 3
cd ProjectTest
python test_auth_service_e2e.py
```

**Expected output:**
```
============================================================
        AUTH SERVICE END-TO-END TEST SUITE
============================================================

✓ AUTH_SERVICE_HEALTH: PASSED
✓ GATEWAY_HEALTH: PASSED
✓ REGISTRATION: PASSED
✓ LOGIN: PASSED
✓ TOKEN_VERIFY: PASSED
✓ GET_USER: PASSED
✓ LOGOUT: PASSED
✓ INVALID_TOKEN: PASSED
✓ MISSING_HEADER: PASSED
✓ INVALID_CREDS: PASSED

============================================================
✓ ALL TESTS PASSED (10/10)
============================================================
```

### Option B: Manual Testing with curl

```bash
# 1. Check health
curl http://localhost:5000/health | python -m json.tool

# 2. Register user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "DemoPass123!",
    "full_name": "Demo User"
  }' | python -m json.tool

# Save the `access_token` from response

# 3. Get user info (replace TOKEN with actual token)
TOKEN="eyJhbGciOiJIUzI1NiIs..."
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# 4. Logout
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

## Step 5: Verify the Historical Split Setup

✅ **If you follow the historical split setup, you should now have:**
- PostgreSQL database with user accounts
- Auth service running on port 5001
- API Gateway running on port 5000
- All tests passing (10/10)
- Working JWT authentication

## Common Issues & Fixes

### Error: "Connection refused on port 5432"
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running, start it:
docker run -d --name postgres_fileconv \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=file_converter \
  -p 5432:5432 postgres:15

# Wait 10 seconds for startup
sleep 10
```

### Error: "Connection refused on port 6379"
```bash
# Check if Redis is running
docker ps | grep redis

# If not running, start it:
docker run -d --name redis_fileconv -p 6379:6379 redis:7
```

### Error: "Port 5000 already in use"
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 PID

# Or use different port by setting in config
```

### Error: "Username already taken"
```bash
# Use a different username in tests
# Or reset database:
docker exec postgres_fileconv psql -U postgres -d file_converter \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Then restart services
```

## Quick API Reference

### Public Endpoints (no auth required)

**1. Register User**
```
POST /auth/register
Body: {
  "username": "john",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
Response: 201 Created
{
  "user_id": "uuid",
  "access_token": "jwt_token",
  "subscription_tier": "free"
}
```

**2. Login**
```
POST /auth/login
Body: {
  "username": "john",
  "password": "SecurePass123!"
}
Response: 200 OK
{
  "access_token": "jwt_token",
  "subscription_tier": "free"
}
```

**3. Verify Token**
```
POST /auth/verify
Header: Authorization: Bearer <token>
Response: 200 OK
{
  "valid": true,
  "user_id": "uuid",
  "username": "john",
  "role": "free"
}
```

### Protected Endpoints (require auth token)

**4. Get Current User**
```
GET /auth/me
Header: Authorization: Bearer <token>
Response: 200 OK
{
  "user_id": "uuid",
  "username": "john",
  "email": "john@example.com",
  "subscription_tier": "free",
  "created_at": "2026-03-04T12:34:56"
}
```

**5. Logout**
```
POST /auth/logout
Header: Authorization: Bearer <token>
Response: 200 OK
{
  "success": true,
  "message": "Logged out successfully"
}
```

**6. Service Health**
```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "services": {
    "auth": "healthy",
    "user": "unreachable",
    "convert": "unreachable"
  }
}
```

## Database Info

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: file_converter
- User: postgres
- Password: password

**Tables Created:**
```
- users (user accounts)
- auth_tokens (JWT tokens)
- conversion_jobs (file conversions)
- api_keys (programmatic access)
```

## Performance Notes

| Operation | Time |
|-----------|------|
| Register | 50-100ms |
| Login | 100-150ms |
| Token Verify | 10-20ms |
| Get User | 20-50ms |
| Rate Limit Check | 5-10ms |

## Next Steps

1. ✅ **Auth Service is setup** - Users can register and login
2. 🔄 **User Service** - Create user profiles & history
3. 🔄 **Conversion Service** - Handle file conversions
4. 🔄 **Billing Service** - Payment processing
5. 🔄 **Frontend** - React/Vue dashboard

## Security Notes

✅ Passwords are hashed with PBKDF2-SHA256  
✅ Tokens expire after 24 hours  
✅ Rate limited to 100 requests/minute  
✅ All secrets in environment variables  
✅ SQL injection prevented with ORM  
✅ CORS enabled for frontend  

## Troubleshooting

### Test script says "service unreachable"
This is normal if only running 2 services. Other services (user, convert, etc.) are not yet running. Auth service is the one that matters for this test.

### Token keeps expiring
Default expiry is 24 hours. To change:
- Edit `packages/shared-config/config.py`
- Change `JWT_EXPIRY_HOURS = 24` to desired value
- Restart services

### Database keeps resetting
This is normal in development. Each service startup creates tables if they don't exist. To preserve data:
- Use persistent Docker volumes
- Or keep services running continuously

---

**✅ Setup Complete!** You can now test the full auth flow.

For detailed documentation, see:
- `DATABASE_AND_AUTH_IMPLEMENTATION.md` - Full implementation details
- `SERVICE_ARCHITECTURE.md` - Architecture overview
- `REST_API_REFERENCE.md` - Complete API documentation
