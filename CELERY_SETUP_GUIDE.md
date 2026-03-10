# 🚀 CELERY SETUP GUIDE - BACKGROUND TASK PROCESSING

**Created:** March 10, 2026  
**Status:** Phase 2 Implementation

---

## 🎯 WHAT IS CELERY?

Celery is a distributed task queue library that allows you to:

✅ **Process large file conversions** without blocking the API  
✅ **Send emails asynchronously**  
✅ **Run scheduled tasks** (daily reports, cleanup, etc.)  
✅ **Scale processing** across multiple workers  
✅ **Retry failed tasks automatically**  

---

## 📦 INSTALLATION

```bash
# Install Celery and Redis (message broker)
pip install celery[redis]
pip install redis

# Or use RabbitMQ instead
pip install celery[amqp]
pip install amqp
```

Add to `requirements.txt`:
```
celery[redis]>=5.3.0
redis>=4.5.0
```

---

## 🔧 ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask API Server                         │
│                                                              │
│  POST /api/convert → Creates Conversion record             │
│                   → Queues task in Redis                   │
│                   → Returns task_id immediately            │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ (enqueue)
                          ↓
       ┌──────────────────────────────────────┐
       │      Redis Message Broker            │
       │  (Queue: conversions, emails, etc)   │
       └──────────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ↓              ↓              ↓
    ┌─────────────┐ ┌────────────┐ ┌─────────────┐
    │  Worker 1   │ │  Worker 2  │ │  Worker N   │
    │  (process)  │ │ (process)  │ │ (process)   │
    │  tasks      │ │ tasks      │ │ tasks       │
    └─────────────┘ └────────────┘ └─────────────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
                          ↓
                  Store results in Redis
```

---

## ⚙️ CONFIGURATION

### 1. Redis Setup

**Option A: Local Redis (Development)**
```bash
# Install Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Linux: sudo apt-get install redis-server

# Start Redis
redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

**Option B: Docker Redis**
```bash
docker run -d -p 6379:6379 redis:latest
```

### 2. Environment Variables

Create `.env`:
```env
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_TIMEOUT=1800  # 30 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER=4
```

### 3. Celery Configuration File

Already created at `app/celery_config.py` with:
- ✅ Task routing (conversions, emails, maintenance in separate queues)
- ✅ Automatic retries (up to 3 attempts)
- ✅ Scheduled tasks (Beat schedule)
- ✅ Task time limits
- ✅ Worker settings

---

## 🎯 AVAILABLE TASKS

### File Conversion Tasks

```python
# Convert any file type
@celery_app.task(name='app.tasks.convert_file')
def convert_file(conversion_id):
    """Convert file in background"""
    # Returns: {'status': 'completed', 'conversion_id': ..., 'processing_time': ...}

# Process images
@celery_app.task(name='app.tasks.process_image')
def process_image(image_id):
    """Process image in background"""

# Process PDFs
@celery_app.task(name='app.tasks.process_pdf')
def process_pdf(pdf_id):
    """Process PDF in background"""
```

### Email Tasks

```python
# Send email asynchronously
@celery_app.task(name='app.tasks.send_email')
def send_email(to_email, subject, template, context=None):
    """Send email in background"""
    # Returns: {'status': 'sent', 'to': ...}
```

### Scheduled Tasks (Runs automatically)

```python
# Runs every hour - clean old files
'cleanup-old-uploads': {
    'task': 'app.tasks.cleanup_old_uploads',
    'schedule': timedelta(hours=1),
}

# Runs every 5 minutes - update stats
'update-conversion-stats': {
    'task': 'app.tasks.update_conversion_stats',
    'schedule': timedelta(minutes=5),
}

# Runs every day - send daily reports
'send-daily-reports': {
    'task': 'app.tasks.send_daily_reports',
    'schedule': timedelta(days=1),
}
```

---

## 🚀 RUNNING WORKERS

### Start a Single Worker

```bash
# Process all tasks
celery -A app.celery_config worker --loglevel=info

# Process only conversion tasks
celery -A app.celery_config worker -Q conversions --loglevel=info

# Process only email tasks
celery -A app.celery_config worker -Q emails --loglevel=info

# Process multiple queues
celery -A app.celery_config worker -Q conversions,emails --loglevel=info
```

### Start Multiple Workers (Production)

```bash
# Worker 1: Handle conversions (CPU intensive)
celery -A app.celery_config worker \
  -Q conversions \
  --concurrency=4 \
  --loglevel=info \
  -n worker1@%h

# Worker 2: Handle emails (I/O intensive)
celery -A app.celery_config worker \
  -Q emails \
  --concurrency=10 \
  --loglevel=info \
  -n worker2@%h

# Worker 3: Handle maintenance
celery -A app.celery_config worker \
  -Q maintenance \
  --concurrency=2 \
  --loglevel=info \
  -n worker3@%h
```

### Start Celery Beat (Scheduler)

```bash
# Required to run scheduled tasks
celery -A app.celery_config beat --loglevel=info
```

### Using Supervisor (Production)

Create `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery_conversions]
command=celery -A app.celery_config worker -Q conversions --concurrency=4
directory=/var/www/docpro
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/conversions.log

[program:celery_emails]
command=celery -A app.celery_config worker -Q emails --concurrency=10
directory=/var/www/docpro
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/emails.log

[program:celery_beat]
command=celery -A app.celery_config beat
directory=/var/www/docpro
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

Start supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_conversions celery_emails celery_beat
```

---

## 📝 USING TASKS IN YOUR CODE

### Enqueue a file conversion task

```python
from app.tasks import convert_file

# In your conversion API route
conversion = Conversion(
    user_id=user_id,
    input_path='/path/to/file.pdf',
    output_format='docx',
    input_filename='document.pdf'
)
db.session.add(conversion)
db.session.commit()

# Enqueue the task
task = convert_file.apply_async(
    args=[conversion.id],
    queue='conversions',
    timeout=1800  # 30 min timeout
)

# Return task id to client
return {
    'task_id': task.id,
    'conversion_id': conversion.id,
    'status': 'queued'
}
```

### Check task status

```python
from celery.result import AsyncResult

def get_conversion_status(task_id):
    task = AsyncResult(task_id)
    
    return {
        'status': task.state,
        'result': task.result if task.successful() else None,
        'error': str(task.info) if task.failed() else None
    }
```

### Send email asynchronously

```python
from app.tasks import send_email

# Enqueue email task
send_email.apply_async(
    args=['user@example.com', 'Your conversion is ready', 'conversion_complete', {
        'conversion_id': 123,
        'filename': 'document.docx'
    }],
    queue='emails'
)
```

---

## 🧪 TESTING TASKS

```python
from app import create_app
from app.tasks import convert_file
from app.models import db, Conversion

app = create_app()

with app.app_context():
    # Create test conversion
    conversion = Conversion(
        user_id=1,
        input_filename='test.pdf',
        input_format='pdf',
        output_format='docx',
        input_path='./test.pdf'
    )
    db.session.add(conversion)
    db.session.commit()
    
    # Execute task synchronously (for testing)
    result = convert_file(conversion.id)
    print(f"Result: {result}")
```

Or in production mode (async):

```bash
# Terminal 1: Start worker
celery -A app.celery_config worker --loglevel=info

# Terminal 2: Run test script
python -c "
from app import create_app
from app.tasks import convert_file
from app.models import db, Conversion

app = create_app()
with app.app_context():
    conversion = Conversion.query.first()
    task = convert_file.apply_async(args=[conversion.id])
    print(f'Task ID: {task.id}')
"

# Terminal 1 will show: Task received and processing...
```

---

## 📊 MONITORING CELERY

### Flower (Web UI for Celery)

```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.celery_config flower

# Access at http://localhost:5555
```

Features:
- ✅ View all workers
- ✅ Monitor task progress
- ✅ See failed tasks
- ✅ Inspect queues
- ✅ Task history
- ✅ Worker statistics

### CLI Commands

```bash
# View active tasks
celery -A app.celery_config inspect active

# View registered tasks
celery -A app.celery_config inspect registered

# View worker stats
celery -A app.celery_config inspect stats

# Purge a queue
celery -A app.celery_config purge

# Restart a worker
celery -A app.celery_config control shutdown
```

---

## 🔧 TROUBLESHOOTING

### Issue: "Connection refused" to Redis
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

### Issue: Tasks not executing
```bash
# Check if worker is running
ps aux | grep celery

# Start worker in foreground to see errors
celery -A app.celery_config worker --loglevel=debug
```

### Issue: Tasks timing out
```python
# Increase timeout in celery_config.py
task_time_limit=30 * 60  # Increase from 30 to 60 minutes
```

### Issue: Memory usage growing
```bash
# Set max tasks per child (worker will restart after N tasks)
celery -A app.celery_config worker --max-tasks-per-child=1000
```

---

## 🎯 PRODUCTION SETUP CHECKLIST

```
✅ Redis installed and running
✅ Celery installed (pip install celery[redis])
✅ app/celery_config.py created
✅ app/tasks.py created
✅ app/__init__.py updated with Celery init
✅ .env configured with CELERY_BROKER_URL
✅ Multiple workers running (conversions, emails, etc.)
✅ Celery Beat running for scheduled tasks
✅ Flower installed for monitoring
✅ Supervisor config created for worker management
✅ Log files configured at /var/log/celery/
✅ Error handling and retries configured
```

---

## 📈 SCALING STRATEGY

### Stage 1: Single Server (Dev/Small)
```
1 API Server → 1 Redis → 1 Celery Worker
```

### Stage 2: Growth (Medium)
```
Multiple API Servers
         ↓
    1 Redis Instance
         ↓
3+ Celery Workers (conversions, emails, maintenance)
+ Celery Beat for scheduling
```

### Stage 3: Enterprise (Large)
```
Load Balancer → Multiple API Servers
         ↓
    Redis Cluster (HA)
         ↓
Worker Pool (10+ workers)
- Scale conversions up/down based on queue depth
- Separate worker nodes for CPU vs I/O tasks
- Redis Sentinel for failover
```

---

## ✨ FEATURES NOW AVAILABLE

✅ Async file conversions (no more blocking)  
✅ Email notifications (send & forget)  
✅ Automatic retries on failure  
✅ Task scheduling (daily reports, cleanup)  
✅ Task routing (separate queues)  
✅ Worker monitoring (Flower)  
✅ Graceful error handling  
✅ Scalable worker pools  

---

**Next:** Production deployment and monitoring setup  
**Status:** ✅ Phase 2 - Background Tasks Complete
