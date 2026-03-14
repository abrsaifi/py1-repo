# DocPro Developer Guide

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- 500 MB free disk space

### Installation

1. **Clone/Navigate to project**
```bash
cd py1
```

2. **Create virtual environment**
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Unix/Mac:
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database**
```bash
python -c "from app.services.database import init_db; init_db()"
```

5. **Start application**
```bash
python -m app.main
```

Application will be available at `http://localhost:5000`

### Database Migrations
Use the real Flask-Migrate / Alembic tree in `migrations/` for schema changes:

```bash
flask --app manage.py db heads
flask --app manage.py db current
flask --app manage.py db migrate -m "describe change"
flask --app manage.py db upgrade
```

`manage.py` runs with schema bootstrap and background tasks disabled so migration commands stay isolated from normal startup side effects.

### Seed Development Data
Use the SQLAlchemy-aware seed module to bootstrap a small local dataset:

```bash
python -c "from app import create_app; from app.models import db; from database.seed.seeds import seed_database; app=create_app({'ENABLE_BACKGROUND_TASKS': False}); ctx=app.app_context(); ctx.push(); print(seed_database(db)); ctx.pop()"
```

### Background Workers
The production async path is Celery-backed. The scripts under `workers/` are compatibility launchers that delegate to the queue topology defined in `app/celery_config.py`.

Common commands:

```bash
celery -A app.celery_config worker -Q conversions --loglevel=info
celery -A app.celery_config worker -Q critical --loglevel=info
celery -A app.celery_config worker -Q maintenance --loglevel=info
celery -A app.celery_config beat --loglevel=info
```

---

## Project Architecture

### Directory Structure
```
app/
├── api/
│   └── routes/           # API endpoints
│       ├── data.py       # Data processing endpoints
│       ├── analytics.py  # Analytics endpoints
│       ├── pdf.py        # PDF endpoints
│       ├── image.py      # Image endpoints
│       ├── excel.py      # Excel endpoints
│       └── health.py     # Health check
├── services/             # Business logic
│       ├── database.py   # Database operations
│       ├── auth.py       # Authentication
│       ├── advanced_features.py  # Advanced tools
│       ├── conversions.py
│       ├── history.py
│       └── file_cleanup.py
├── utils/                # Utilities
│       ├── file_validator.py  # File validation
│       ├── logger_enhanced.py  # Logging
│       └── logger.py
├── config.py             # Configuration
├── main.py              # Entry point
└── __init__.py          # App factory

templates/
└── Index.html           # Web interface

tests/
└── test_new_features.py # Test suite

logs/                    # Application logs
docpro_database.db       # SQLite database
```

### Key Modules

#### app/services/database.py
```python
from app.services.database import DatabaseManager, init_db

# Initialize database
init_db()

# Add conversion record
record_id = DatabaseManager.add_conversion_record(
    'operation_type', 'input_file', 'processing', user_id=1
)

# Update conversion record
DatabaseManager.update_conversion_record(
    record_id, 'success', 'output_file', file_size_output=1024
)

# Update analytics
DatabaseManager.update_analytics('duplicate-remover', success=True, file_size_mb=5.2)

# Get analytics
analytics = DatabaseManager.get_analytics()
```

#### app/services/auth.py
```python
from app.services.auth import AuthManager, require_auth

# Create user
success, user_id, api_key = AuthManager.create_user(
    'username', 'email@example.com', 'password'
)

# Authenticate
success, user_id = AuthManager.authenticate_user('username', 'password')

# Verify API key
user_id = AuthManager.verify_api_key('dpk_xxxxx')

# Use in endpoint
@bp.route('/protected')
@require_auth
def protected_endpoint(user_id=None):
    return {'user_id': user_id}
```

#### app/utils/file_validator.py
```python
from app.utils.file_validator import validate_file, get_file_size_mb

# Validate file
is_valid, error_msg = validate_file(file_obj, ['csv', 'xlsx'])
if not is_valid:
    return {'error': error_msg}, 400

# Get file size
size_mb = get_file_size_mb(file_path)
```

#### app/utils/logger_enhanced.py
```python
from app.utils.logger_enhanced import (
    OperationLogger, AuditLogger, get_logger, setup_logging
)

# Initialize logging
setup_logging()

# Log operation
op_logger = OperationLogger('my-operation')
op_logger.log_start(param1='value1')
op_logger.log_success(result_rows=100)
# or
op_logger.log_error('Something went wrong', operation_id='op_123')

# Audit logging
AuditLogger.log_action(user_id=1, action='upload', 
                      resource='file.csv', status='success')

# Get logger
logger = get_logger('mymodule')
logger.info('Information message')
logger.error('Error occurred', exc_info=True)
```

#### app/services/advanced_features.py
```python
from app.services.advanced_features import (
    CacheManager, BulkProcessor, PerformanceOptimizer,
    DataAggregator, DataQualityMetrics, ScheduledTasks, DataExporter
)

# Cache results
key = CacheManager.get_cache_key('op', file_hash, params)
CacheManager.cache_result(key, data, ttl_hours=24)
cached = CacheManager.get_cached_result(key)

# Bulk processing
processor = BulkProcessor('duplicate-remover', files_list, callback)
results, errors = processor.process_sync()

# Performance estimation
chunk_size = PerformanceOptimizer.get_chunk_size(file_size_mb=50)
threads = PerformanceOptimizer.get_thread_count(file_count=10)
est_time = PerformanceOptimizer.estimate_processing_time('duplicate-remover', 50)

# Data quality metrics
quality = DataQualityMetrics.get_quality_details(df)
# Returns: completeness, uniqueness, consistency, row_count, etc.
```

---

## API Reference

### Duplicate Remover
```
POST /api/data/duplicate-remover
Content-Type: multipart/form-data

file: <CSV/Excel file>
X-API-Key: dpk_xxxxx (optional)

Response: CSV/Excel file (cleaned)
```

### Data Validator
```
POST /api/data/validate
Content-Type: multipart/form-data

file: <CSV/Excel file>
X-API-Key: dpk_xxxxx (optional)

Response: {
  "success": true,
  "report": {
    "total_rows": 100,
    "total_columns": 5,
    "quality_score": 95.5,
    ...
  }
}
```

### PDF Export
```
POST /api/data/export-pdf
Content-Type: multipart/form-data

file: <CSV/Excel file>
format: table|list|compact
X-API-Key: dpk_xxxxx (optional)

Response: PDF file
```

### Basic Reporting
```
POST /api/data/reporting
Content-Type: multipart/form-data

file: <CSV/Excel file>
X-API-Key: dpk_xxxxx (optional)

Response: {
  "success": true,
  "report": {
    "total_rows": 100,
    "summary_statistics": {...}
  }
}
```

### Database Integration
```
POST /api/data/database-connect
Content-Type: application/json

{
  "db_type": "postgresql|mysql|mongodb|sqlite|mssql",
  "host": "localhost",
  "port": "5432",
  "database": "dbname",
  "username": "user"
}
X-API-Key: dpk_xxxxx (optional)

Response: {
  "success": true,
  "connection": {...}
}
```

### Analytics
```
GET /api/analytics/operations
GET /api/analytics/operations/<type>
GET /api/analytics/summary

Response: Analytics data in JSON format
```

---

## Configuration

### Environment Variables
```bash
# Server
FLASK_ENV=development
FLASK_DEBUG=1

# Security
SECRET_KEY=your-secret-key-change-in-production
BILLING_PROVIDER_WEBHOOK_SECRET=dev-billing-provider-secret
UPLOAD_API_KEY=optional-api-key

# File Upload
MAX_FILE_SIZE_MB=100
UPLOAD_MAX_FILE_SIZE=104857600

# Database
DATABASE_PATH=./docpro_database.db
HISTORY_DB=./conversion_history.db

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs

# Authentication
SESSION_TIMEOUT_MINUTES=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

For local provider-event testing, sign the raw JSON payload with HMAC-SHA256 using `BILLING_PROVIDER_WEBHOOK_SECRET` and send the digest in `X-DocPro-Billing-Signature` to `/api/admin/billing/provider-events`.

### Config File (app/config.py)
```python
class Config:
    SECRET_KEY = 'change-me-in-production'
    MAX_FILE_SIZE_MB = 100
    LOG_LEVEL = 'INFO'
    # ... more settings
```

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Class
```bash
pytest tests/test_new_features.py::TestDuplicateRemover -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Tool Runtime Smoke Checks
```bash
# Browser-path smoke through the Vite proxy
python tool_runtime_smoke.py --transport frontend --frontend http://127.0.0.1:5173 --backend http://127.0.0.1:5060

# Backend-direct smoke to isolate Flask/API issues from proxy issues
python tool_runtime_smoke.py --transport backend --frontend http://127.0.0.1:5173 --backend http://127.0.0.1:5060
```

### Test Individual Function
```python
# In Python interpreter
from app import create_app
app = create_app({'TESTING': True})
client = app.test_client()

# Test duplicate remover
with open('test.csv', 'rb') as f:
    response = client.post('/api/data/duplicate-remover', 
                          data={'file': (f, 'test.csv')})
print(response.status_code)  # Should be 200
```

---

## Logging

### View Recent Logs
```bash
# Last 50 lines
tail -50 logs/app.log

# Follow live updates
tail -f logs/app.log

# Errors only
tail -50 logs/errors.log
```

### Parse JSON Logs
```bash
# Pretty print JSON
cat logs/app.log | python -m json.tool | head -50

# Filter by operation
grep "duplicate-remover" logs/app.log | python -m json.tool

# Get duration of operations
grep "duration_seconds" logs/app.log
```

---

## Database

### View Database Schema
```bash
sqlite3 docpro_database.db ".schema"
```

### Query Database
```bash
sqlite3 docpro_database.db "SELECT * FROM conversion_history LIMIT 10;"
sqlite3 docpro_database.db "SELECT * FROM analytics;"
sqlite3 docpro_database.db "SELECT * FROM users;"
```

### Backup Database
```bash
cp docpro_database.db docpro_database.db.backup.$(date +%s)
```

### Reset Database
```bash
rm docpro_database.db
python -c "from app.services.database import init_db; init_db()"
```

---

## Development Workflow

### 1. Create New Feature
```python
# app/api/routes/newfeature.py
from flask import Blueprint, request, jsonify
from app.utils.logger_enhanced import OperationLogger
from app.services.database import DatabaseManager

bp = Blueprint('newfeature', __name__)

@bp.route('/newfeature/process', methods=['POST'])
def process():
    op_logger = OperationLogger('newfeature')
    try:
        # Validate input
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file'}), 400
        
        # Process
        op_logger.log_start(filename=file.filename)
        result = do_something(file)
        
        # Log success
        op_logger.log_success(result_size=len(result))
        DatabaseManager.update_analytics('newfeature', True)
        
        return jsonify({'success': True, 'data': result})
    
    except Exception as e:
        op_logger.log_error(str(e))
        DatabaseManager.update_analytics('newfeature', False)
        return jsonify({'error': str(e)}), 500
```

### 2. Register Feature in app/__init__.py
```python
try:
    from .api.routes.newfeature import bp as newfeature_bp
    app.register_blueprint(newfeature_bp, url_prefix='/api')
except Exception:
    pass
```

### 3. Add Tests
```python
class TestNewFeature:
    def test_success(self, client):
        with open('test.csv', 'rb') as f:
            response = client.post('/api/newfeature/process',
                                  data={'file': (f, 'test.csv')})
        assert response.status_code == 200
```

### 4. Update Documentation
- Add section to FEATURES_DOCUMENTATION.md
- Include API examples
- Document response formats

---

## Performance Optimization Tips

1. **Use Caching** for repeated operations
   ```python
   CacheManager.cache_result(key, data, ttl_hours=24)
   ```

2. **Monitor Log Size** - Logs grow ~50-100 MB/month
   ```bash
   du -sh logs/
   ```

3. **Optimize Database Queries**
   ```python
   # Add indexes for frequently queried columns
   CREATE INDEX idx_operation ON conversion_history(operation_type);
   ```

4. **Use Bulk Processing** for multiple files
   ```python
   processor = BulkProcessor('op', files, callback)
   results, errors = processor.process_sync()
   ```

5. **Cache Large DataFrames**
   ```python
   df = load_and_cache(file_path)
   ```

---

## Troubleshooting

### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies
pip list | grep -E "Flask|pandas|openpyxl"

# Check for port conflict
netstat -an | grep 5000
```

### Database Errors
```bash
# Verify database exists
ls -la docpro_database.db

# Check integrity
sqlite3 docpro_database.db "PRAGMA integrity_check;"

# Reset if corrupted
rm docpro_database.db
python -c "from app.services.database import init_db; init_db()"
```

### File Upload Issues
```bash
# Check upload directory
ls -la /tmp/docpro_uploads/  # or configured UPLOAD_CHUNKS_DIR

# Clear old uploads
rm -rf /tmp/docpro_uploads/*

# Check file permissions
chmod 777 /tmp/docpro_uploads/
```

### Logging Issues
```bash
# Ensure logs directory exists
mkdir -p logs
chmod 777 logs

# Check log file size
ls -lh logs/

# Rotate if too large
mv logs/app.log logs/app.log.1
```

---

## Contributing Guidelines

1. **Code Style**
   - Follow PEP 8
   - Use type hints where possible
   - Add docstrings to all functions

2. **Testing**
   - Write tests for new features
   - Ensure all tests pass: `pytest tests/`
   - Aim for >80% coverage

3. **Documentation**
   - Update FEATURES_DOCUMENTATION.md
   - Add API examples
   - Document any new configuration

4. **Commits**
   - Use clear commit messages
   - Reference issue numbers
   - Keep commits atomic

5. **Code Review**
   - Request review before merge
   - Address feedback
   - Ensure CI passes

---

## Support

For issues or questions:
1. Check logs: `tail -50 logs/errors.log`
2. Review documentation: [FEATURES_DOCUMENTATION.md](FEATURES_DOCUMENTATION.md)
3. Check analytics: `curl http://localhost:5000/api/analytics/summary`
4. Run tests: `pytest tests/`

---

**Last Updated**: February 16, 2026
**Version**: 2.0.0
**Created By**: Development Team
