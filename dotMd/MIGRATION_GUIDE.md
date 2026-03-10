# Migration Guide: From Monolith to Microservices

This guide explains how to migrate your existing file converter code to the new enterprise SaaS architecture.

## What Changed?

### Before (Legacy Monolith)
```
app.py (everything here)
├── Routes
├── Conversion logic
├── User management
├── Auth
├── Database models
└── Workers
```

### After (Microservices)
```
services/
├── api-gateway/       # Routes only
├── auth-service/      # Auth only
├── conversion-service/# Job management only
├── user-service/      # User data only
└── billing-service/   # Payments only

workers/
├── conversion-workers/# Actual conversions
├── cleanup-worker/    # File cleanup
└── priority-worker/   # Premium users
```

## Key Architectural Changes

### 1. **Separation of Concerns**
- **Before**: One Flask app handling everything
- **After**: Each service has ONE responsibility

### 2. **Asynchronous Processing**
- **Before**: Conversions in request-response cycle (blocking)
- **After**: Jobs queued immediately, workers process asynchronously

### 3. **Shared Code**
- **Before**: Code duplication across services
- **After**: Centralized in `packages/` for reuse

### 4. **Configuration**
- **Before**: Environment variables scattered
- **After**: Centralized via `packages/shared-config/`

## Migration Steps

### Step 1: Authentication Routes
**Old Code** (`app.py`):
```python
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')
    # ... validation ...
    db.add_user(email, hash_password(password))
    return {'token': create_token()}
```

**New Code** (`services/auth-service/routes/register.py`):
```python
from packages.shared_utils import PasswordHelper, TokenHelper

def register():
    email = request.json.get('email')
    password = request.json.get('password')
    # ... validation ...
    hashed = PasswordHelper.hash_password(password)
    user_id = db.add_user(email, hashed)
    token = TokenHelper.generate_token()
    return {'user_id': user_id, 'token': token}
```

### Step 2: Conversion Logic
**Old Code** (`app.py`):
```python
@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    target_format = request.json.get('format')
    
    # Conversion happens here (BLOCKING!)
    output = convert_to_pdf(file.stream, target_format)
    
    return {'result': output_file}  # Takes 30 seconds!
```

**New Code** (`services/conversion-service/routes/convert.py`):
```python
def convert():
    file = request.files['file']
    target_format = request.json.get('format')
    user_id = get_user_from_jwt()
    
    # Validate (fast)
    if not FileValidator.validate_file_extension(file.filename):
        return {'error': 'Invalid format'}, 400
    
    # Store file (fast)
    file_id = storage.save(file.stream)
    
    # Create job record
    job = ConversionJob(
        user_id=user_id,
        input_file=file_id,
        target_format=target_format
    )
    job.save()
    
    # Queue job (very fast!)
    queue.enqueue(job)
    
    return {'job_id': job.id}  # Returns in < 100ms!
```

**Worker** (`workers/conversion-workers/pdf_worker.py`):
```python
def process_job(job):
    try:
        input_file = storage.get(job.input_file)
        
        # Actual conversion (happens here)
        output = convert_to_pdf(input_file)
        
        # Save output
        output_id = storage.save(output)
        
        # Update job
        job.output_file = output_id
        job.status = 'COMPLETED'
        job.save()
        
        # Notify user (WebSocket)
        notify_user(job.user_id, {'status': 'completed', 'job_id': job.id})
        
    except Exception as e:
        job.status = 'FAILED'
        job.error_message = str(e)
        job.save()
```

### Step 3: User Data Endpoints
**Old Code** (`app.py`):
```python
@app.route('/user/history')
def get_history():
    user_id = get_user_id_from_jwt()
    history = db.get_user_conversions(user_id)
    return {'history': history}
```

**New Code** (`services/user-service/routes/history.py`):
```python
# Uses same database, but dedicated service
def get_history():
    user_id = get_user_id_from_jwt()
    history = db.get_user_conversions(user_id)
    return {'history': history}
```

### Step 4: API Gateway Setup
**New Component** (`services/api-gateway/`):
```python
from flask import Flask

app = Flask(__name__)

# Each route forwards to appropriate service
@app.route('/register', methods=['POST'])
def register():
    response = requests.post('http://auth-service:5001/register', json=request.json)
    return response.json()

@app.route('/convert', methods=['POST'])
def convert():
    response = requests.post('http://conversion-service:5003/convert', 
                            files={'file': request.files['file']},
                            json=request.json)
    return response.json()
```

## Database Changes

### Query Distribution
- **Auth Service** accesses: `users`, `auth_tokens`
- **Conversion Service** accesses: `conversion_jobs`, `files`
- **User Service** accesses: `users`, `conversion_jobs`, `usage_logs`
- **Billing Service** accesses: `subscriptions`, `invoices`

All read same database, but **services own their data** (logical separation).

### Connection Pooling
```python
# Old (monolith)
ONE connection pool for everything

# New (microservices)
Each service has its own connection pool
→ Better resource management
→ Easier to scale different services differently
```

## Configuration Migration

### Before (scattered .env)
```bash
DB_HOST=localhost
FLASK_PORT=5000
UPLOAD_LIMIT=100MB
JWT_SECRET=xxx
S3_KEY=yyy
```

### After (centralized)
```python
# packages/shared-config/config.py
class ProductionConfig(BaseConfig):
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    # ... etc
```

## Testing Migration

### Before (monolith test)
```python
def test_convert():
    client = app.test_client()
    response = client.post('/convert', data={'file': ...})
    # Wait 30 seconds
    assert 'result' in response.json
```

### After (service tests)
```python
# Test conversion service
def test_convert_job_creation():
    response = post('/convert', data={'file': ...})
    assert response.status_code == 202  # Accepted
    assert 'job_id' in response.json
    
# Test worker separately
def test_pdf_worker():
    job = create_test_job()
    worker = PDFConversionWorker()
    assert worker.process_job(job) == True
    assert job.status == 'COMPLETED'
```

## Deployment Changes

### Before (single server)
```bash
python app.py  # Everything runs here
```

### After (microservices)
```bash
# Terminal 1
python -m services.api_gateway.main      # :5000

# Terminal 2
python -m services.auth_service.main     # :5001

# Terminal 3
python -m services.conversion_service.main  # :5003

# Terminal 4
python -m workers.conversion_workers.pdf_worker

# Terminal 5
python -m workers.cleanup_worker.delete_expired_files

# Or with Docker
docker-compose -f infra/docker-compose.dev.yml up
```

## Performance Impact

### Before
- User request blocks for 30 seconds during file conversion
- Server can handle ~10 concurrent conversions
- CPU maxed out

### After
- User request responds in < 100ms with job_id
- Server can handle 1000 concurrent "users"
- Actual conversions happen in background
- Workers scale independently

## Common Pitfalls

### ❌ **Mistake 1**: Keeping conversion logic in API service
```python
# WRONG - don't do this
@app.route('/convert')
def convert():
    output = heavy_conversion(file)  # DON'T
    return output
```

### ✅ **Fix**: Move to workers
```python
# RIGHT - queue the job
@app.route('/convert')
def convert():
    queue.enqueue(job)  # Then worker processes
    return {'job_id': job_id}
```

### ❌ **Mistake 2**: Services calling databases directly
```python
# WRONG
auth_service.user = get_user_from_db()  # Direct access

# RIGHT
user_service.get_user(user_id)  # Through API
```

### ❌ **Mistake 3**: Shared state between services
```python
# WRONG
_cache = {}  # Global state

# RIGHT - use Redis
redis.set(key, value, ex=3600)
```

## Timeline

- **Week 1**: Auth service migration
- **Week 2**: Conversion service + workers
- **Week 3**: User & Billing services
- **Week 4**: Testing & optimization
- **Week 5**: Deployment & monitoring setup

## Rollback Plan

If issues arise:
1. Run old monolith alongside new services
2. Use API Gateway to route traffic
3. Gradually migrate users
4. Rollback any service if needed

```python
# API Gateway can do gradual rollout
if user.is_beta_tester:
    service_url = 'http://new-conversion-service:5003'
else:
    service_url = 'http://old-app:5000'
```

## Support & Questions

1. Check `SERVICE_ARCHITECTURE.md` for detailed service docs
2. Each service has its own `README.md`
3. Review code examples in corresponding service dirs

---

**This migration enables 10-100x scalability while improving code maintainability.**
