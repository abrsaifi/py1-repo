# STEP 2: SHORT-TERM SETUP (1-2 days)

## Overview
Step 2 focuses on integrating robustness features into your Flask application and setting up monitoring infrastructure.

### What You'll Do in Step 2:
1. **Integrate Error Handlers** - Add custom error handling to Flask app
2. **Setup Logging** - Configure structured logging throughout the app
3. **Enable Health Checks** - Register health check endpoints
4. **Configure Backups** - Setup automatic database backups
5. **Enable Monitoring** - Setup monitoring and alerting
6. **Test Everything** - Verify all features work

### Time Estimate: 1-2 days
### Difficulty: Intermediate

---

## Task 2.1: Integrate Error Handlers into Flask App

### Current State
- Error handling classes exist: `app/utils/errors.py` ✓
- Health check endpoint exists: `app/api/routes/health.py` ✓
- But: Not yet integrated into `server.py`

### What to Do

**Option A: Update server.py (if still using it)**

Add this to your `server.py` after Flask app creation:

```python
# Near the top with other imports
from app.utils.errors import register_error_handlers
from app.utils.logger_setup import get_logger

# After creating the Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key')

# INTEGRATION POINT 1: Register error handlers
register_error_handlers(app)

# INTEGRATION POINT 2: Setup logging
logger = get_logger('docpro')
```

**Option B: Update app/__init__.py (Recommended)**

Better approach - integrate in the Flask app factory:

```python
from flask import Flask
from .config import Config
from .utils.errors import register_error_handlers
from .utils.logger_setup import get_logger

def create_app(config=None):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    
    # INTEGRATION: Register error handlers
    register_error_handlers(app)
    
    # INTEGRATION: Setup logging
    logger = get_logger('docpro')
    app.logger = logger
    
    # Register blueprints (existing code)
    try:
        from .api.routes.health import bp as health_bp
        app.register_blueprint(health_bp, url_prefix='/api')
    except Exception:
        pass
    
    return app
```

### Verification

Test error handling by creating a test route:

```bash
# In Python or via curl:
curl -X POST http://localhost:5000/api/test-error

# Should return consistent error JSON:
# {
#     "success": false,
#     "error": {
#         "code": "CONVERSION_ERROR",
#         "message": "Test error message"
#     }
# }
```

---

## Task 2.2: Setup Structured Logging

### Current State
- Logger setup exists: `app/utils/logger_setup.py` ✓
- Log files not yet created

### What to Do

**Step 1: Create log directory**
```bash
mkdir -p logs
chmod 755 logs
```

**Step 2: Initialize logging in your app**

Add to `server.py` or `app/__init__.py`:

```python
from app.utils.logger_setup import get_logger
import logging

# Get logger
logger = get_logger('docpro')

# Now use throughout your app:
@app.route('/convert', methods=['POST'])
def convert():
    logger.info('Conversion requested', extra={'user': 'username'})
    try:
        # Do conversion
        logger.info('Conversion completed', extra={'duration_ms': 1500})
    except Exception as e:
        logger.error('Conversion failed', exc_info=True, extra={'error': str(e)})
```

**Step 3: Add logging to conversion functions**

Example in `server.py` or your conversion functions:

```python
def convert_pdf_to_images(input_pdf):
    logger.debug(f'Converting {input_pdf} to images')
    try:
        # Conversion logic
        logger.info(f'PDF converted: {output_file}', extra={
            'input': input_pdf,
            'output': output_file,
            'pages': page_count
        })
        return output_file
    except Exception as e:
        logger.error(f'PDF conversion failed', exc_info=True, extra={
            'input': input_pdf,
            'error': str(e)
        })
        raise
```

### Verification

```bash
# Check that logs are being created
ls -lh logs/app.log

# View recent logs
tail -20 logs/app.log

# Search for specific events
grep "CONVERSION" logs/app.log
grep "ERROR" logs/app.log
```

---

## Task 2.3: Enable Health Check Endpoints

### Current State
- Health check code exists: `app/api/routes/health.py` ✓
- Already integrated in `app/__init__.py` blueprint registration

### What to Do

**Step 1: Verify endpoints are registered**

Check that this code is in `app/__init__.py`:

```python
try:
    from .api.routes.health import bp as health_bp
    app.register_blueprint(health_bp, url_prefix='/api')
except Exception:
    pass
```

**Step 2: Test endpoints**

Start your server and test:

```bash
# Liveness probe (is app running?)
curl http://localhost:5000/api/health/live
# Expected: {"status": "alive"}

# Readiness probe (is app ready?)
curl http://localhost:5000/api/health/ready
# Expected: {"status": "ready"} or 503 if not ready

# Detailed status
curl http://localhost:5000/api/health/status | python -m json.tool
# Expected: Full health report with components

# Metrics for monitoring
curl http://localhost:5000/api/health/metrics | python -m json.tool
# Expected: Performance metrics
```

**Step 3: Setup monitoring checks (optional)**

Create a cron job to monitor health (Linux/Mac):

```bash
# Monitor health every 5 minutes
*/5 * * * * curl -f http://localhost:5000/api/health/live || \
  mail -s "DocPro Health Check Failed" admin@company.com

# Or use in Windows Task Scheduler
powershell -Command "Invoke-WebRequest http://localhost:5000/api/health/live"
```

---

## Task 2.4: Configure Automated Database Backups

### Current State
- Database utilities exist: `app/services/database.py` ✓
- Background task manager exists: `app/services/background_tasks.py` ✓
- Not yet integrated into app startup

### What to Do

**Step 1: Create backup initialization script**

Create `app/startup.py`:

```python
"""Application startup tasks and initialization."""

import os
import logging
from app.services.database import DatabaseManager
from app.services.background_tasks import (
    get_background_manager,
    MaintenanceTaskFactory
)

logger = logging.getLogger(__name__)


def init_background_tasks():
    """Initialize background tasks for maintenance."""
    
    try:
        manager = get_background_manager()
        
        # Database file paths
        history_db = 'conversion_history.db'
        
        if not os.path.exists(history_db):
            logger.warning(f'Database not found: {history_db}')
            return
        
        # Create database manager
        db = DatabaseManager(history_db)
        
        # Register backup task (every 24 hours)
        manager.register_task(
            'daily_backup',
            MaintenanceTaskFactory.backup_database(db),
            interval_hours=24
        )
        logger.info('Registered: Daily database backup')
        
        # Register cleanup task (every 7 days)
        manager.register_task(
            'weekly_backup_cleanup',
            MaintenanceTaskFactory.cleanup_old_backups(db, max_age_days=30),
            interval_hours=24*7
        )
        logger.info('Registered: Weekly backup cleanup')
        
        # Register optimization task (every 7 days)
        manager.register_task(
            'weekly_optimization',
            MaintenanceTaskFactory.optimize_database(db),
            interval_hours=24*7
        )
        logger.info('Registered: Weekly database optimization')
        
        # Register temp cleanup task (every hour)
        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        manager.register_task(
            'hourly_temp_cleanup',
            MaintenanceTaskFactory.cleanup_temp_files(
                temp_dir=temp_dir,
                max_age_hours=24
            ),
            interval_hours=1
        )
        logger.info('Registered: Hourly temp file cleanup')
        
        # Start the manager
        manager.start()
        logger.info('Background task manager started')
        
    except Exception as e:
        logger.error(f'Failed to initialize background tasks: {str(e)}', exc_info=True)


def init_app(app):
    """Initialize application (called after app creation)."""
    
    # Setup background tasks
    init_background_tasks()
    
    logger.info('Application initialization complete')
```

**Step 2: Call init_app in your Flask app**

Update `app/__init__.py` or `server.py`:

```python
from flask import Flask
from app.startup import init_app

def create_app(config=None):
    app = Flask(__name__)
    
    # ... existing code ...
    
    # Register blueprints
    # ... existing code ...
    
    # Initialize background tasks
    init_app(app)
    
    return app


# Or in server.py after app creation:
if __name__ == '__main__':
    init_app(app)
    app.run(host='0.0.0.0', port=5000)
```

**Step 3: Verify backups are working**

```bash
# Check backup directory created
ls -la backups/

# Manually trigger a backup (for testing)
python -c "from app.services.database import DatabaseManager; \
           db = DatabaseManager('conversion_history.db'); \
           backup = db.backup(); \
           print(f'Backup created: {backup}')"

# Check backup files
ls -lh backups/
```

---

## Task 2.5: Enable Monitoring and Alerting

### Current State
- Health check endpoints ready ✓
- Metrics endpoint ready ✓
- Logging configured ✓

### What to Do

**Option A: Simple Monitoring (Free)**

**1. Setup log file monitoring:**

```bash
# Watch for errors in real-time
tail -f logs/app.log | grep ERROR

# Count errors per hour
grep ERROR logs/app.log | awk '{print $1}' | sort | uniq -c
```

**2. Setup health check monitoring:**

Create `scripts/monitor_health.py`:

```python
#!/usr/bin/env python3
"""Simple health monitoring script."""

import requests
import sys
from datetime import datetime

def check_health(url='http://localhost:5000/api/health/status'):
    """Check application health."""
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        status = data.get('status', 'unknown')
        timestamp = datetime.now().isoformat()
        
        if status == 'healthy':
            print(f"[{timestamp}] STATUS: HEALTHY")
            return 0
        elif status == 'degraded':
            print(f"[{timestamp}] STATUS: DEGRADED - {data}")
            return 1
        else:
            print(f"[{timestamp}] STATUS: UNHEALTHY - {data}")
            return 2
            
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ERROR: {str(e)}")
        return 3

if __name__ == '__main__':
    sys.exit(check_health())
```

Run it:
```bash
# Every 5 minutes via cron
*/5 * * * * /path/to/monitor_health.py

# Or directly
python scripts/monitor_health.py
```

**Option B: Production Monitoring (Recommended)**

**1. Setup Prometheus scraping:**

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'docpro'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/api/health/metrics'
```

**2. Setup Grafana Dashboard:**

Add data source:
- URL: `http://localhost:9090` (Prometheus)
- Create dashboard querying `/api/health/metrics`

**3. Setup Alerting:**

Create alert rules for:
- High CPU usage (> 80%)
- High memory usage (> 85%)
- Database unavailable
- Disk space low (< 10%)

---

## Task 2.6: Test Everything

### Comprehensive Testing

**Test 1: Error Handling**

```bash
# Create test error
curl -X POST http://localhost:5000/api/test-error

# Check logs for error entry
grep "test-error" logs/app.log
```

**Test 2: Logging**

```bash
# Perform a conversion
curl -X POST -F "file=@test.pdf" http://localhost:5000/api/convert

# Check conversion logged
grep "CONVERSION" logs/app.log
```

**Test 3: Health Checks**

```bash
# All endpoints
curl http://localhost:5000/api/health/live
curl http://localhost:5000/api/health/ready
curl http://localhost:5000/api/health/status
curl http://localhost:5000/api/health/metrics

# Should all return 200 OK
```

**Test 4: Database Backup**

```bash
# Verify backups directory
ls -la backups/

# Check backup policy
python -c "from app.services.database import DatabaseManager; \
           db = DatabaseManager('conversion_history.db'); \
           print(db.get_info())"
```

**Test 5: Background Tasks**

```bash
# Monitor task manager
python -c "from app.services.background_tasks import get_background_manager; \
           m = get_background_manager(); \
           for name, task in m.tasks.items(): \
               print(f'{name}: {task}')"
```

---

## Implementation Checklist

### Phase 1: Error Handling & Logging (Day 1)
- [ ] Read error handling code in `app/utils/errors.py`
- [ ] Read logging code in `app/utils/logger_setup.py`
- [ ] Create `logs/` directory
- [ ] Integrate error handlers into Flask app
- [ ] Integrate logging into Flask app
- [ ] Add logging to conversion functions
- [ ] Test error handling with a test route
- [ ] Verify logs are being written
- [ ] Test log rotation

### Phase 2: Health Checks & Monitoring (Day 1)
- [ ] Verify health endpoints are registered
- [ ] Test all health check endpoints
- [ ] Setup health check monitoring script
- [ ] Test monitoring script
- [ ] Setup log file monitoring
- [ ] Create health check alerts

### Phase 3: Backups & Automation (Day 2)
- [ ] Read database utilities code
- [ ] Read background task manager code
- [ ] Create `app/startup.py`
- [ ] Create `backups/` directory
- [ ] Integrate background tasks into app
- [ ] Test manual backup
- [ ] Verify automatic backup runs
- [ ] Setup backup rotation
- [ ] Test backup restoration

### Phase 4: Integration & Testing (Day 2)
- [ ] Run full application test
- [ ] Perform stress test
- [ ] Verify all logs are written
- [ ] Check database backups created
- [ ] Verify health checks working
- [ ] Test error handling
- [ ] Monitor resource usage
- [ ] Create documentation of setup

---

## Common Issues & Solutions

### Issue 1: Logs not being written
**Cause:** `logs/` directory doesn't exist
**Solution:**
```bash
mkdir -p logs
chmod 755 logs
```

### Issue 2: Background tasks not running
**Cause:** Not initialized in app startup
**Solution:** Call `init_background_tasks()` from `app/__init__.py`

### Issue 3: Health endpoints return 500
**Cause:** Missing dependencies (psutil)
**Solution:**
```bash
pip install psutil==5.10.0
```

### Issue 4: Database backups not created
**Cause:** Backup directory doesn't exist
**Solution:**
```bash
mkdir -p backups
chmod 755 backups
```

### Issue 5: LOG_FORMAT=json issues
**Cause:** python-json-logger not installed
**Solution:**
```bash
pip install python-json-logger==2.0.7
```

---

## Verification Commands

After completing Step 2, run these commands:

```bash
# 1. Check all directories exist
ls -la logs/ backups/

# 2. Run test conversion
curl -X POST -F "file=@test.pdf" http://localhost:5000/api/convert

# 3. Check logs
tail -20 logs/app.log

# 4. Test health
curl http://localhost:5000/api/health/status | python -m json.tool

# 5. Check backups
ls -la backups/

# 6. Verify error handling
curl -X POST http://localhost:5000/api/test-error

# All should work without errors
```

---

## Success Criteria for Step 2

By the end of Step 2, you should have:

- [ ] Error handlers integrated into Flask app
- [ ] Structured logging throughout application
- [ ] Logs being written to `logs/app.log` with rotation
- [ ] Health check endpoints responding
- [ ] Automatic database backups configured
- [ ] Background task manager running
- [ ] Monitoring alerts setup
- [ ] All tests passing
- [ ] No errors in application logs

---

## Files to Review/Update

| File | Action | Status |
|------|--------|--------|
| `app/__init__.py` | Update: Add error handlers & logging | ⏳ Do now |
| `server.py` | Update: Add logging and init_app | ⏳ Do now |
| `app/startup.py` | Create: Background task initialization | ⏳ Create |
| `logs/` | Create: Log directory | ⏳ Create |
| `backups/` | Create: Backup directory | ⏳ Create |
| `app/utils/errors.py` | Review: Error handling | ✓ Ready |
| `app/utils/logger_setup.py` | Review: Logging setup | ✓ Ready |
| `app/services/database.py` | Review: Database utilities | ✓ Ready |
| `app/services/background_tasks.py` | Review: Task manager | ✓ Ready |

---

## Next Steps

After Step 2 is complete:

**Step 3: Production Deployment (Before Launch)**
- Change SECRET_KEY again with production machine
- Setup HTTPS/TLS certificates
- Configure reverse proxy (Nginx)
- Setup monitoring (Prometheus/Grafana)
- Run load testing
- Create disaster recovery plan

---

## Time Estimate Breakdown

| Task | Time |
|------|------|
| Error handling integration | 30 min |
| Logging setup | 30 min |
| Health endpoint verification | 15 min |
| Backup configuration | 45 min |
| Monitoring setup | 30 min |
| Testing and verification | 60 min |
| **Total** | **~3.5 hours** |

**Recommended:** Spread over 1-2 days for thorough testing

---

## Resources

- `ROBUSTNESS_IMPROVEMENTS.md` - Feature documentation
- `app/utils/errors.py` - Error handling code
- `app/utils/logger_setup.py` - Logging setup code
- `app/services/database.py` - Database utilities
- `app/services/background_tasks.py` - Task manager code
- `DEPLOYMENT_GUIDE.md` - Full deployment guide

---

**Ready to start Step 2?** Follow the implementation checklist above! 🚀
