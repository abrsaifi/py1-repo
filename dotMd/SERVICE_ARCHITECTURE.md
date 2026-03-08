# File Converter SaaS - Service Architecture Guide

## Overview

This document describes the enterprise-ready microservices architecture for the file converter SaaS application.

## Core Principles

### 1. **Separation of Concerns**
Each microservice has a single, well-defined responsibility:
- **Auth Service**: Only handles authentication
- **Conversion Service**: Only manages jobs (doesn't do conversions)
- **User Service**: Only manages user data
- **Workers**: Only perform conversions (off the main thread)

### 2. **Stateless Services**
- Each service instance can be scaled independently
- No sticky sessions or instance affinity needed
- Easy horizontal scaling

### 3. **API-First Communication**
- Services communicate via HTTP/REST APIs
- Clear, documented interfaces
- Version support for backward compatibility

### 4. **Asynchronous Processing**
- Long-running conversions happen in background workers
- Users get immediate feedback via job IDs
- Results available when ready

## Service Details

### API Gateway
**Responsibility**: Traffic routing, validation, rate limiting

**Key Routes**:
- `POST /auth/*` → Auth Service
- `POST /convert/*` → Conversion Service
- `GET /user/*` → User Service
- `GET /billing/*` → Billing Service

**Middleware**:
- Authentication (JWT validation)
- Rate Limiting (100 requests/minute per IP)
- CORS Handling
- Request Logging

### Auth Service
**Responsibility**: User authentication and token management

**Endpoints**:
- `POST /register` - Create new account
- `POST /login` - Get JWT token
- `POST /refresh` - Refresh expired token
- `POST /logout` - Invalidate token
- `GET /verify` - Verify token validity

**Database Tables**:
- `users` - User accounts
- `auth_tokens` - Active tokens

### Conversion Service
**Responsibility**: Job orchestration (NOT actual conversion)

**Endpoints**:
- `POST /convert` - Create conversion job
- `GET /jobs/{id}` - Get job status
- `DELETE /jobs/{id}` - Cancel job

**Flow**:
1. Receive file upload
2. Validate file (type, size)
3. Create job record
4. Push to queue
5. Return job ID

**Queue System**:
- Redis-based job queue
- Priority queues (free/pro/enterprise)
- Automatic retries with exponential backoff

### User Service
**Responsibility**: User data and dashboard

**Endpoints**:
- `GET /profile` - User profile
- `GET /history` - Conversion history
- `GET /usage` - Current usage stats
- `PUT /profile` - Update profile

**WebSocket**:
- Real-time job status updates
- Live conversion progress

### Billing Service
**Responsibility**: Subscriptions and payments

**Endpoints**:
- `GET /subscription` - Current subscription
- `POST /upgrade` - Upgrade subscription
- `GET /invoices` - Billing history

**Integration Points**:
- Stripe/PayPal for payments
- Quota enforcement
- Usage analytics

### Analytics Service
**Responsibility**: Metrics collection and reporting

**Endpoints**:
- `GET /metrics` - System metrics
- `GET /user-stats` - User statistics
- `GET /reports` - Generated reports

## Worker Architecture

### Job Queue
```
┌─────────────────────────────────────────┐
│  Conversion Service (Job Enqueuer)      │
│  Creates job and pushes to Redis queue  │
└──────────────┬──────────────────────────┘
               │
               ├─── Standard Queue ──────→ Conversion Workers (4 instances)
               │
               └─── Priority Queue ──────→ Priority Worker (2 instances)
```

### Job Lifecycle
```
NEW
  ↓
QUEUED
  ↓
PROCESSING (worker picks up)
  ↓
COMPLETED or FAILED
  ↓
USER NOTIFIED
  ↓
FILE STORED (until retention period)
  ↓
DELETED (by cleanup worker)
```

### Scaling Strategy
- **Standard Queue**: Scale up to 10 instances during peak load
- **Priority Queue**: Always at 2 instances minimum (SLA compliance)
- **Cleanup Worker**: Single instance, runs hourly
- **Load Balancer**: Distributes jobs to workers based on capacity

## Data Flow Example: File Conversion

```
User uploads file
    ↓
[API Gateway] validates request
    ↓
[Conversion Service] receives file
    - Validates file (type, size, virus scan)
    - Creates ConversionJob record
    - Stores file in S3/local storage
    - Pushes job to queue
    - Returns job_id to user
    ↓
[User receives immediate response]
    ↓
[Worker] picks up job from queue
    - Retrieves input file
    - Performs conversion
    - Stores output file
    - Updates job status
    ↓
[WebSocket] notifies user (if connected)
    ↓
[User Service] updates history
    ↓
User downloads result via presigned URL
```

## Database Schema (High Level)

### Core Tables
```sql
-- Users
users (id, email, password_hash, created_at, ...)

-- Conversion Jobs
conversion_jobs (id, user_id, input_file, output_file, status, ...)

-- Usage Tracking
usage_logs (id, user_id, action, timestamp, ...)

-- Subscriptions
subscriptions (user_id, tier, monthly_limit, used, expires_at, ...)
```

## Deployment

### Docker Containers Per Service
```
api-gateway:5000
auth-service:5001
user-service:5002
conversion-service:5003
billing-service:5004
analytics-service:5005
pdf-worker:workers
image-worker:workers
doc-worker:workers
cleanup-worker:workers
```

### Environment Variables

```bash
# Service Communication
CONVERSION_SERVICE_URL=http://conversion-service:5003
AUTH_SERVICE_URL=http://auth-service:5001
USER_SERVICE_URL=http://user-service:5002

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/fileconverter

# Cache & Queue
REDIS_URL=redis://redis:6379/0

# Storage
STORAGE_TYPE=s3  # or 'local'
AWS_S3_BUCKET=fileconverter-prod

# Security
JWT_SECRET_KEY=<random-32-char-key>
JWT_EXPIRY_HOURS=24
```

## Monitoring & Health Checks

### Health Check Endpoints
Every service exposes `/health`:
```json
{
  "status": "ok",
  "service": "conversion-service",
  "version": "1.0.0",
  "dependencies": {
    "database": "ok",
    "redis": "ok",
    "storage": "ok"
  }
}
```

### Metrics (Prometheus)
- Request count per endpoint
- Request duration (p50, p95, p99)
- Error rate per service
- Queue depth
- Worker CPU/Memory usage
- Database connection pool utilization

## Scaling Examples

### Scenario 1: Traffic Spike
1. Load balancer detects increased requests to conversion service
2. Auto-scaler adds 3 more PDF worker instances
3. Queue depth stabilizes
4. Most jobs complete within SLA

### Scenario 2: Image Processing Queue Grows
1. Prometheus alert triggers (queue_depth > 100)
2. Auto-scaler adds 2 more image worker instances
3. Alert resolves after 5 minutes

### Scenario 3: Premium User Traffic
1. Priority queue depth increases
2. Auto-scaler ensures minimum 2 instances running
3. Pro/Enterprise jobs get 95th percentile processing time < 10 minutes

## Failure Handling

### Scenario: PDF Worker Crashes
1. Job marked as PROCESSING (still in queue)
2. Heartbeat timeout triggers (30 seconds)
3. Job automatically reassigned to another worker
4. Original worker instance recovers or removed

### Scenario: Database Connection Lost
1. All services exponential backoff retry
2. User gets 503 error with retry-after header
3. Monitoring alerts triggered
4. Ops team informed

## API Contracts Example

### Create Conversion Job
**Request**:
```json
POST /convert
{
  "target_format": "pdf",
  "options": {
    "quality": "high",
    "pages": "1-5"
  }
}
```

**Response**:
```json
{
  "job_id": "conv_abc123xyz",
  "status": "queued",
  "progress": 0,
  "estimated_completion": "2026-03-04T12:30:00Z"
}
```

## Security Considerations

1. **Service-to-Service**: mTLS or shared API keys
2. **Data at Rest**: Encrypted storage buckets
3. **Data in Transit**: TLS for all communications
4. **Secrets**: Never in code, always via environment
5. **Access Control**: IAM roles per service
6. **Audit Logging**: All user actions logged

---

This architecture is designed to scale from 10 users to 10 million users with appropriate infrastructure investment.
