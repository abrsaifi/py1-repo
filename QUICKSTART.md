# DocPro Enterprise Edition - Quick Reference

## 🎯 Quick Start Guide

### Initial Setup (First Time)
```bash
# 1. Ensure database is initialized
python -m app.maintenance --optimize

# 2. Start the application
python -m app.main

# 3. Open browser to http://localhost:5000
```

### Using Web UI

**Register New User:**
1. Click "📝 Register" button
2. Enter username, email, password
3. Click "Register"
4. Auto-redirected to dashboard

**Login:**
1. Click "🔐 Login" button
2. Enter credentials
3. Access dashboard with "📊 Dashboard" button

**Dashboard Features:**
- 📈 View API usage stats
- 🎯 Check operation success rates
- 🔑 Manage API keys (view, copy, reset)

### Using Python SDK

```python
from app.client_sdk import DocProClient

# Initialize client
client = DocProClient()

# 1. Register
result = client.register('john', 'john@example.com', 'pass123')
api_key = result['api_key']

# 2. Or login
result = client.login('john', 'pass123')
api_key = result['api_key']

# 3. Use API key
client = DocProClient(api_key=api_key)

# 4. Process files
cleaned = client.remove_duplicates('data.csv')
quality = client.validate_data('data.csv')
metrics = client.check_data_quality('data.csv')

# 5. View analytics
summary = client.get_analytics_summary()
print(summary)
```

### Using API Directly

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123"}'

# Use API key
curl http://localhost:5000/api/analytics/summary \
  -H "X-API-Key: dpk_your_key_here"

# Remove duplicates
curl -X POST http://localhost:5000/api/data/duplicate-remover \
  -H "X-API-Key: dpk_your_key_here" \
  -F "file=@data.csv"

# Check data quality
curl -X POST http://localhost:5000/api/features/quality-check \
  -H "X-API-Key: dpk_your_key_here" \
  -F "file=@data.csv"

# Bulk process
curl -X POST http://localhost:5000/api/features/bulk-process \
  -H "X-API-Key: dpk_your_key_here" \
  -F "files=@file1.csv" -F "files=@file2.csv" \
  -F "operation=duplicate-remover"
```

---

## 📊 Feature Overview

### Data Processing
- **Duplicate Remover** - Remove duplicate rows
- **Data Validator** - Quality checking
- **PDF Export** - Multiple format options
- **Report Generator** - Statistics & charts

### Advanced Features
- **Bulk Processing** - Handle multiple files
- **File Merging** - Combine CSV/Excel files
- **Quality Metrics** - Detailed data analysis
- **Multi-Format Export** - JSON, XML, Parquet, HTML

### User Management
- **Registration** - Create accounts
- **Authentication** - Login with credentials
- **API Keys** - Generate, reset, manage
- **Dashboard** - Analytics & metrics

### Webhooks
- **Event Subscriptions** - Listen for events
- **Automatic Delivery** - Webhook triggers
- **Signature Verification** - Security
- **Event Logging** - Track deliveries

### Administration
- **Database Optimization** - Indexes, vacuuming
- **Backup & Restore** - Data protection
- **Log Cleanup** - Maintenance
- **Health Checks** - Database integrity

---

## 🔧 Configuration

### Environment Variables (.env)

**Essential Settings:**
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this
MAX_FILE_SIZE_MB=100
DATABASE_PATH=./docpro_database.db
```

**Optional Settings:**
```bash
# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# S3 Storage
USE_S3=true
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=your-bucket

# Redis Caching
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_HOURS=24

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# Session
SESSION_TIMEOUT_MINUTES=60
```

See `.env.production.template` for complete configuration.

---

## 🚀 Deployment

### Development
```bash
python -m app.main
# Listens on http://localhost:5000
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Production (uWSGI)
```bash
uwsgi --http :8000 \
  --wsgi-file wsgi.py \
  --master --processes 4 \
  --workers 2
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
```

---

## 📈 Monitoring

### View Logs
```bash
# Real-time logs
tail -f logs/app.log

# Error logs only
tail -f logs/errors.log

# Last 50 lines
tail -50 logs/app.log
```

### Database Status
```bash
# Check health
python -m app.maintenance --check

# View database size
ls -lh docpro_database.db

# Query stats
sqlite3 docpro_database.db "SELECT COUNT(*) FROM conversion_history;"
```

### Performance Testing
```bash
# Load test
python scripts/load_testing.py

# Custom load test
python scripts/load_testing.py --concurrent 20 --requests 500
```

---

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set strong DATABASE passwords
- [ ] Configure SSL/TLS for HTTPS
- [ ] Enable rate limiting
- [ ] Setup firewall rules
- [ ] Regular database backups
- [ ] Monitor API key usage
- [ ] Enable webhook signature verification
- [ ] Use environment variables for secrets
- [ ] Update dependencies regularly

---

## 📞 Common Tasks

### Reset Everything
```bash
# Remove database
rm docpro_database.db

# Reinitialize
python -m app.maintenance --optimize
```

### Backup Database
```bash
# Manual backup
python -m app.maintenance --backup

# Specific location
python -c "from app.maintenance import backup_database; backup_database('/backup/docpro.db')"
```

### Clean Old Data
```bash
# Remove logs older than 30 days
python -m app.maintenance --cleanup-logs

# Remove events older than 90 days
python -m app.maintenance --cleanup-events
```

### Rotate API Keys
```bash
# Via Python
from app.services.auth import AuthManager
new_key = AuthManager.reset_api_key(user_id=1)

# Via API
curl -X POST http://localhost:5000/api/auth/reset-api-key \
  -H "X-API-Key: old_key_here"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ImportError: No module | `pip install -r requirements.txt` |
| Database locked | Close other connections, restart app |
| Slow queries | `python -m app.maintenance --optimize` |
| Memory leak | Monitor processes, restart app periodically |
| Webhook not working | Verify URL reachable, check firewall |
| Login failing | Clear cookies, check SESSION_TIMEOUT |
| Large file upload | Increase MAX_FILE_SIZE_MB in config |

---

## 📚 Documentation Files

- `DEVELOPER_GUIDE.md` - For developers
- `FEATURES_DOCUMENTATION.md` - Feature details
- `IMPLEMENTATION_SUMMARY.md` - Architecture overview
- `ENTERPRISE_FEATURES.md` - Enterprise features (this implementation)
- `README.md` - General information

---

## 🎓 Example Workflows

### Workflow 1: Duplicate Cleanup
```python
from app.client_sdk import DocProClient

client = DocProClient(api_key='your_key')

# 1. Check quality
quality = client.validate_data('raw_data.csv')
print(f"Duplicates found: {quality['report']['duplicate_rows']}")

# 2. Remove duplicates
cleaned = client.remove_duplicates('raw_data.csv')
with open('cleaned.csv', 'wb') as f:
    f.write(cleaned)

# 3. Verify result
quality = client.validate_data('cleaned.csv')
print(f"Quality score: {quality['report']['quality_score']:.1f}%")
```

### Workflow 2: Data Aggregation
```python
from app.client_sdk import DocProClient

client = DocProClient(api_key='your_key')

# Merge multiple files
merged = client.merge_files(['jan.csv', 'feb.csv', 'mar.csv'], 'csv')
with open('q1_data.csv', 'wb') as f:
    f.write(merged)

# Generate report
report = client.get_report('q1_data.csv')
print(f"Total records: {report['report']['total_rows']}")
print(f"Columns: {report['report']['total_columns']}")
```

### Workflow 3: Webhook Integration
```python
from app.services.webhooks import WebhookManager

# Register webhook
webhook_id = WebhookManager.register_webhook(
    user_id=1,
    event_type='operation.completed',
    url='https://your-app.com/callbacks/operations',
    secret='my-secret-key'
)

# In your app, receive webhook:
@app.route('/callbacks/operations', methods=['POST'])
def handle_completion():
    payload = request.get_json()
    
    # Verify signature
    import hmac
    import hashlib
    
    signature = request.headers.get('X-DocPro-Signature')
    my_signature = hmac.new(
        'my-secret-key'.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if signature != my_signature:
        return {'error': 'Invalid signature'}, 401
    
    # Process event
    event = payload['event']
    data = payload['data']
    
    print(f"Operation {data['operation_id']} completed!")
    return {'ok': True}
```

---

**Version:** 3.0.0  
**Last Updated:** February 16, 2026  
**Status:** Production Ready ✅
