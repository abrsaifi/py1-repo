# User Service Implementation Guide

**Service**: User Service  
**Port**: 5002  
**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: Phase 3  

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [API Endpoints](#api-endpoints)
5. [Database Schema](#database-schema)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **User Service** is a microservice responsible for managing user profiles, preferences, activity tracking, and usage statistics. It provides a complete API for user account management and personalization.

### Key Features

✓ **User Profile Management** - Store and update user information  
✓ **Preferences & Settings** - Customizable user preferences  
✓ **Activity Logging** - Track all user actions  
✓ **Device Management** - Manage trusted devices  
✓ **Usage Statistics** - Monitor conversion and API usage  
✓ **Email Management** - Change email with verification  
✓ **Account Security** - Password changes and account deletion  

### Service Dependencies

- **PostgreSQL** - Primary data store
- **Redis** - Caching (optional)
- **Auth Service** - Token validation
- **API Gateway** - Request routing

---

## Architecture

### Database Schema

The User Service uses five main tables:

#### 1. User Profiles (`user_profiles`)

Extends the base User table with additional profile information.

```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- bio: String(500)
- company: String(255)
- job_title: String(255)
- location: String(255)
- website_url: String(500)
- phone_number: String(20)
- github_username: String(100)
- linkedin_username: String(100)
- twitter_handle: String(100)
- avatar_url: String(500)
- cover_image_url: String(500)
- industry: String(100)
- company_size: String(50)
- job_function: String(100)
- total_conversions: Integer
- total_files_processed: Integer
- total_files_size_gb: Float
- profile_complete_percentage: Integer (0-100)
- verified_email: Boolean
- verified_phone: Boolean
- created_at: DateTime
- updated_at: DateTime
```

#### 2. User Preferences (`user_preferences`)

Stores user-specific settings and preferences.

```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key, Unique)
- theme: String(20) -> 'light' | 'dark'
- language: String(10) -> 'en', 'es', 'fr', etc.
- timezone: String(50) -> 'UTC', 'America/New_York', etc.
- email_notifications: Boolean (default: true)
- conversion_complete_email: Boolean (default: true)
- newsletter: Boolean (default: true)
- marketing_emails: Boolean (default: false)
- profile_public: Boolean (default: false)
- show_conversion_history: Boolean (default: true)
- data_retention_days: Integer (default: 90)
- api_throttle_limit: Integer (default: 100)
- api_keys_limit: Integer (default: 5)
- default_output_format: String(50) -> 'pdf', 'png', etc.
- auto_delete_converted_files: Boolean (default: false)
- two_factor_enabled: Boolean (default: false)
- session_timeout_minutes: Integer (default: 60)
- custom_settings: JSON (Text)
- created_at: DateTime
- updated_at: DateTime
```

#### 3. Activity Logs (`activity_logs`)

Tracks all user activities for auditing and analytics.

```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- action_type: String(100) -> 'login', 'profile_update', 'conversion', etc.
- resource_type: String(50) -> 'profile', 'file', 'conversion', etc.
- resource_id: String(255)
- description: String(500)
- status: String(50) -> 'success', 'failed', 'partial'
- details: JSON (Text)
- ip_address: String(45)
- user_agent: String(500)
- location: String(255)
- created_at: DateTime (Indexed)
```

#### 4. User Devices (`user_devices`)

Manages trusted devices for multi-device support and security.

```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- device_name: String(255)
- device_type: String(50) -> 'mobile', 'tablet', 'desktop'
- device_os: String(100) -> 'iOS', 'Android', 'Windows', 'macOS', 'Linux'
- browser: String(100) -> 'Chrome', 'Firefox', 'Safari'
- device_token: String(255) (Unique)
- is_trusted: Boolean (default: false)
- last_verified_at: DateTime
- last_used_at: DateTime
- ip_address: String(45)
- location: String(255)
- created_at: DateTime
- updated_at: DateTime
```

#### 5. Usage Statistics (`user_usage_stats`)

Tracks usage metrics for billing and analytics.

```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- period_start: DateTime (Indexed)
- period_end: DateTime
- period_type: String(20) -> 'daily', 'weekly', 'monthly'
- conversion_count: Integer
- successful_conversions: Integer
- failed_conversions: Integer
- total_input_size_bytes: Integer
- total_output_size_bytes: Integer
- unique_file_formats: Integer
- total_processing_time_seconds: Integer
- average_processing_time_seconds: Float
- api_calls_count: Integer
- api_errors_count: Integer
- files_stored_count: Integer
- storage_used_bytes: Integer
- cost_estimated_cents: Integer
- cost_actual_cents: Integer
- reached_conversion_limit: Boolean
- reached_storage_limit: Boolean
- reached_api_limit: Boolean
- created_at: DateTime
- updated_at: DateTime
```

### Request/Response Flow

```
Client Request
    ↓
API Gateway (Port 5000)
    ├─ Authentication (JWT verification)
    ├─ Rate Limiting
    └─ Request Routing
    ↓
User Service (Port 5002)
    ├─ Route Handler
    ├─ Business Logic
    ├─ Database Query
    ├─ Activity Logging
    └─ Response Formatting
    ↓
PostgreSQL Database
    ├─ User Profiles
    ├─ Preferences
    ├─ Activity Logs
    ├─ Devices
    └─ Usage Stats
    ↓
Response to Client
```

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip or conda
- Virtual environment manager

### Step 1: Create Virtual Environment

```bash
cd c:\Users\dell\OneDrive\Documents\py1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

```bash
cd services/user-service
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/saas_db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Service
SERVICE_ENV=development
SERVICE_DEBUG=true
SERVICE_PORT=5002

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Logging
LOG_LEVEL=INFO
```

### Step 4: Initialize Database

```bash
python -c "
from packages.shared_models.postgres_manager import PostgresDatabase
import os

db = PostgresDatabase()
db.init(os.getenv('DATABASE_URL'), 'development')
db.create_all_tables()
print('✓ Database initialized')
"
```

### Step 5: Start Service

```bash
python services/user-service/main.py
```

Expected output:
```
Starting user-service v1.0.0 on port 5002
✓ Database connected: saas_db
✓ User Service initialized successfully
```

---

## API Endpoints

### Base URL

Via API Gateway: `http://localhost:5000/user`  
Direct: `http://localhost:5002/user`

### Authentication

All endpoints (except `/user/health`) require:

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### 1. User Profile Endpoints

#### GET /user/profile

Get current user's complete profile.

**Request:**
```http
GET /user/profile HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "subscription_tier": "pro",
    "is_verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-03-04T14:22:30Z"
  },
  "profile": {
    "company": "Acme Corp",
    "job_title": "Senior Engineer",
    "location": "San Francisco, CA",
    "bio": "Cloud engineer and open source contributor",
    "website_url": "https://johndoe.com",
    "github_username": "johndoe",
    "avatar_url": "https://cdn.example.com/avatars/550e8400.jpg",
    "profile_complete_percentage": 85,
    "total_conversions": 1432,
    "total_files_processed": 5847,
    "total_files_size_gb": 234.5
  }
}
```

#### PUT /user/profile

Update user's profile information.

**Request:**
```http
PUT /user/profile HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "company": "Acme Corp",
  "job_title": "Senior Engineer",
  "location": "San Francisco, CA",
  "bio": "Cloud engineer and open source contributor",
  "website_url": "https://johndoe.com",
  "github_username": "johndoe",
  "linkedin_username": "johndoe",
  "twitter_handle": "@johndoe",
  "avatar_url": "https://cdn.example.com/avatars/new.jpg"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "profile": { /* updated profile */ },
  "user": { /* updated user */ }
}
```

**Status Codes:**
- `200 OK` - Profile updated successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

---

### 2. Preferences Endpoints

#### GET /user/preferences

Get user's preferences and settings.

**Request:**
```http
GET /user/preferences HTTP/1.1
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "theme": "dark",
  "language": "en",
  "timezone": "America/Los_Angeles",
  "email_notifications": true,
  "conversion_complete_email": true,
  "newsletter": false,
  "marketing_emails": false,
  "profile_public": false,
  "show_conversion_history": true,
  "data_retention_days": 90,
  "api_throttle_limit": 100,
  "default_output_format": "pdf",
  "auto_delete_converted_files": false,
  "two_factor_enabled": false,
  "session_timeout_minutes": 60,
  "updated_at": "2024-03-04T12:00:00Z"
}
```

#### PUT /user/preferences

Update user's preferences.

**Request:**
```http
PUT /user/preferences HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "theme": "dark",
  "language": "en",
  "timezone": "America/Los_Angeles",
  "email_notifications": true,
  "conversion_complete_email": true,
  "newsletter": false,
  "marketing_emails": false,
  "profile_public": false,
  "show_conversion_history": true,
  "data_retention_days": 365,
  "default_output_format": "pdf",
  "auto_delete_converted_files": false,
  "two_factor_enabled": false,
  "session_timeout_minutes": 120
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "preferences": { /* updated preferences */ }
}
```

---

### 3. Activity History Endpoints

#### GET /user/activity

Get user's activity history with pagination and filtering.

**Query Parameters:**
- `limit` (optional, default: 50, max: 100) - Number of records to return
- `offset` (optional, default: 0) - Number of records to skip
- `action_type` (optional) - Filter by action type (login, profile_update, conversion, etc.)

**Request:**
```http
GET /user/activity?limit=50&offset=0&action_type=conversion HTTP/1.1
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "activities": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "action_type": "conversion_completed",
      "resource_type": "conversion_job",
      "resource_id": "job-12345",
      "description": "PDF conversion completed successfully",
      "status": "success",
      "ip_address": "192.168.1.100",
      "location": "San Francisco, CA",
      "created_at": "2024-03-04T14:30:00Z"
    }
  ],
  "total": 1432,
  "limit": 50,
  "offset": 0
}
```

---

### 4. Device Management Endpoints

#### GET /user/devices

Get list of trusted devices.

**Request:**
```http
GET /user/devices HTTP/1.1
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "devices": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "device_name": "MacBook Pro 14\"",
      "device_type": "desktop",
      "device_os": "macOS",
      "browser": "Chrome",
      "is_trusted": true,
      "last_used_at": "2024-03-04T14:30:00Z",
      "location": "San Francisco, CA",
      "created_at": "2024-02-15T10:00:00Z"
    }
  ],
  "count": 3
}
```

#### DELETE /user/devices/{device_id}

Remove a trusted device.

**Request:**
```http
DELETE /user/devices/550e8400-e29b-41d4-a716-446655440003 HTTP/1.1
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Device removed successfully"
}
```

---

### 5. Usage Statistics Endpoints

#### GET /user/usage/current

Get current month's usage statistics.

**Request:**
```http
GET /user/usage/current HTTP/1.1
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "period_type": "monthly",
  "period_start": "2024-03-01T00:00:00Z",
  "period_end": "2024-03-31T23:59:59Z",
  "conversion_count": 42,
  "successful_conversions": 40,
  "failed_conversions": 2,
  "total_input_size_bytes": 536870912,
  "total_output_size_bytes": 429496729,
  "total_processing_time_seconds": 3600,
  "api_calls_count": 125,
  "files_stored_count": 35,
  "storage_used_bytes": 10737418240,
  "reached_conversion_limit": false,
  "reached_storage_limit": false,
  "reached_api_limit": false
}
```

#### GET /user/usage/history

Get historical usage statistics.

**Query Parameters:**
- `months` (optional, default: 12, max: 36) - Number of months of history

**Request:**
```http
GET /user/usage/history?months=12 HTTP/1.1
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "history": [
    {
      "period_start": "2024-03-01T00:00:00Z",
      "period_end": "2024-03-31T23:59:59Z",
      "conversion_count": 42,
      "successful_conversions": 40,
      "failed_conversions": 2,
      "total_input_size_bytes": 536870912,
      "total_output_size_bytes": 429496729
    }
  ],
  "count": 12
}
```

---

### 6. Account Management Endpoints

#### PUT /user/email

Request to change email address.

**Request:**
```http
PUT /user/email HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "new_email": "newemail@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Email updated. Verification required.",
  "user": { /* updated user */ }
}
```

#### PUT /user/password

Change user's password.

**Request:**
```http
PUT /user/password HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "CurrentPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Status Codes:**
- `200 OK` - Password changed
- `400 Bad Request` - Password too short (min 8 chars)
- `401 Unauthorized` - Current password incorrect
- `404 Not Found` - User not found

#### POST /user/delete-account

Delete/deactivate user's account (requires password confirmation).

**Request:**
```http
POST /user/delete-account HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "UserPassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Account has been deactivated"
}
```

---

### 7. Health Check

#### GET /user/health

Service health check.

**Request:**
```http
GET /user/health HTTP/1.1
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "user-service",
  "version": "1.0.0",
  "database": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "service": "user-service",
  "database": "disconnected",
  "error": "Connection refused"
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `DATABASE_POOL_SIZE` | `5` | Connection pool size (dev) |
| `DATABASE_MAX_OVERFLOW` | `10` | Max pool overflow connections |
| `JWT_SECRET_KEY` | `your-secret-key` | JWT signing key |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRY_HOURS` | `24` | Token expiry in hours |
| `SERVICE_ENV` | `development` | Environment type |
| `SERVICE_DEBUG` | `true` | Debug mode |
| `SERVICE_PORT` | `5002` | Service port |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database |
| `LOG_LEVEL` | `INFO` | Logging level |

### Production Configuration

For production deployments:

```bash
# Security
JWT_SECRET_KEY=<generate-strong-key>
SERVICE_ENV=production
SERVICE_DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@db.example.com/saas_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_HOST=redis.example.com
REDIS_PASSWORD=<secure-password>

# Logging
LOG_LEVEL=WARNING
```

---

## Error Handling

### Standard Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "timestamp": "2024-03-04T14:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| `200` | OK | Request successful |
| `201` | Created | Resource created |
| `400` | Bad Request | Invalid input data |
| `401` | Unauthorized | Missing/invalid token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource already exists |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Server Error | Internal server error |
| `503` | Service Unavailable | Database connection failed |

### Common Errors

**Missing Authorization Header:**
```json
{
  "error": "Missing or invalid authorization header"
}
```

**Invalid Token:**
```json
{
  "error": "Invalid or expired token"
}
```

**User Not Found:**
```json
{
  "error": "User not found"
}
```

---

## Testing

### Run Test Suite

```bash
python ProjectTest/test_user_service_e2e.py
```

### Test Coverage

- ✓ Service health checks
- ✓ Profile CRUD operations
- ✓ Preferences management
- ✓ Activity history retrieval
- ✓ Device management
- ✓ Usage statistics
- ✓ Email change
- ✓ Account security (password change, deletion)
- ✓ Authentication and authorization
- ✓ Error handling

### Manual Testing with curl

```bash
# Get profile
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/user/profile

# Update profile
curl -X PUT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"company": "Acme Corp", "job_title": "Engineer"}' \
  http://localhost:5000/user/profile

# Get preferences
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/user/preferences

# Health check
curl http://localhost:5002/user/health
```

---

## Deployment

### Docker Setup

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY services/user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["python", "services/user-service/main.py"]
```

### Docker Compose

```yaml
services:
  user-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5002:5002"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/saas_db
      REDIS_HOST: redis
      SERVICE_ENV: production
    depends_on:
      - db
      - redis
    volumes:
      - ./services/user-service:/app/services/user-service
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: saas/user-service:1.0.0
        ports:
        - containerPort: 5002
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_HOST
          value: redis-service
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /user/health
            port: 5002
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## Troubleshooting

### Database Connection Issues

**Error:** `connection refused at 5432`

**Solution:**
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Verify DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql "postgresql://user:password@localhost:5432/saas_db" -c "SELECT 1"
```

### Token Validation Errors

**Error:** `Invalid or expired token`

**Solution:**
```bash
# Check JWT_SECRET_KEY matches auth-service
echo $JWT_SECRET_KEY

# Verify token expiry
# Tokens expire after JWT_EXPIRY_HOURS (default: 24)

# Get new token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'
```

### Rate Limiting Issues

**Error:** `429 Too Many Requests`

**Solution:**
```bash
# Check rate limit config
# Default: 100 requests/minute per IP

# Wait 60 seconds or change IP

# For API clients, add retry logic:
if response.status_code == 429:
    time.sleep(60)
    retry_request()
```

### Performance Issues

**Slow Profile Queries:**
```sql
-- Ensure indexes exist
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_id ON activity_logs(user_id);
CREATE INDEX idx_created_at ON activity_logs(created_at);
```

**Memory Issues:**
```bash
# Increase pool size for production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Monitor memory usage
python -m memory_profiler services/user-service/main.py
```

---

## Performance Metrics

### Expected Response Times

| Endpoint | Method | Avg Time |
|----------|--------|----------|
| GET /profile | 50-100ms |
| PUT /profile | 100-150ms |
| GET /preferences | 50-80ms |
| PUT /preferences | 100-120ms |
| GET /activity | 150-300ms |
| GET /usage/current | 100-150ms |
| GET /health | 10-20ms |

### Database Query Performance

- Profile retrieval: 2-5ms
- Preferences update: 3-7ms
- Activity history (50 records): 50-100ms
- Usage stats: 10-20ms

---

## Next Steps

1. **Integration Testing** - Test with Auth Service and API Gateway
2. **Load Testing** - Verify performance under high load
3. **Security Audit** - Review authentication and authorization
4. **Documentation** - Create API documentation for frontend
5. **Monitoring** - Set up APM and error tracking
6. **Conversion Service** - Implement Phase 4 service

---

## Support

For issues, questions, or contributions:

- **Documentation**: See [PHASE_3_IMPLEMENTATION_SUMMARY.md](./dotmd/PHASE_3_IMPLEMENTATION_SUMMARY.md)
- **Issues**: Create an issue in the project repository
- **Slack**: #backend-services channel

---

**Version**: 1.0.0  
**Last Updated**: March 4, 2026  
**Status**: Production Ready
