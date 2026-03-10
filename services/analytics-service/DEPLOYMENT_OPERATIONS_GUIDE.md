# Phase 10 Analytics Service - Deployment & Operations Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Service](#running-the-service)
6. [Database Setup](#database-setup)
7. [Health Checks](#health-checks)
8. [Monitoring](#monitoring)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)
11. [Security](#security)
12. [Backup & Recovery](#backup--recovery)


## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6.0+
- Docker (optional)

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd services/analytics-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with local configuration

# Initialize database
flask db upgrade

# Start service
python main.py
```

**Service available at:** http://localhost:5009


## System Requirements

### Minimum Specifications
- **CPU**: 2 cores (8 cores recommended for production)
- **Memory**: 2GB RAM (8GB recommended for production)
- **Storage**: 10GB disk space (larger for high-volume metrics)
- **Network**: 1 Gbps connection

### Database Requirements
- **PostgreSQL 12+**: For metric storage and indexes
- **Disk Space**: 100GB+ for production metrics
- **Backup**: Daily backups recommended

### Cache Requirements
- **Redis 6.0+**: For query caching and session storage
- **Memory**: 2GB+ for caching 100K+ queries


## Installation

### Using Docker

```bash
# Build image
docker build -t analytics-service:1.0.0 .

# Run container
docker run -d \
  -p 5009:5009 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/analytics \
  -e REDIS_URL=redis://cache:6379 \
  -e FLASK_ENV=production \
  --name analytics \
  analytics-service:1.0.0
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f analytics-service

# Stop services
docker-compose down
```


## Configuration

### Environment Variables

```bash
# Core Configuration
FLASK_ENV=production  # development, testing, production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-must-be-strong

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/analytics
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_ECHO=False

# Redis / Caching
REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TTL=600
CACHE_METRIC_TTL=3600

# JWT / Authentication
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_DEFAULT=100/hour
RATELIMIT_METRICS=500/hour
RATELIMIT_EXPORT=50/hour

# Data Retention (days)
METRIC_RETENTION_MINUTE=7
METRIC_RETENTION_HOUR=30
METRIC_RETENTION_DAY=365
METRIC_RETENTION_MONTH=2555
METRIC_RETENTION_YEAR=3650

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/analytics/service.log

# Monitoring
METRICS_ENABLED=True
STATSD_HOST=localhost
STATSD_PORT=8125
```

### Production Configuration File

Create `config/production.ini`:

```ini
[DATABASE]
url = postgresql://analytics:strong_password@db.example.com:5432/analytics
pool_size = 30
pool_recycle = 3600

[REDIS]
url = redis://cache.example.com:6379/0

[SECURITY]
secret_key = your-very-secure-key-here
jwt_algorithm = HS256

[MONITORING]
statsd_enabled = true
statsd_host = monitoring.example.com
statsd_port = 8125
```


## Running the Service

### Local Development

```bash
# Run with Flask development server
python main.py

# Or with hot-reload
flask run --reload
```

### Production with Gunicorn

```bash
# Start with 4 workers
gunicorn -w 4 -b 0.0.0.0:5009 main:app

# Start with configuration file
gunicorn --config gunicorn_config.py main:app
```

### Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing

bind = "0.0.0.0:5009"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 5
accesslog = "/var/log/analytics/access.log"
errorlog = "/var/log/analytics/error.log"
loglevel = "info"
```

### Systemd Service File

Create `/etc/systemd/system/analytics-service.service`:

```ini
[Unit]
Description=Analytics Service
After=network.target
Requires=postgresql.service redis.service

[Service]
Type=notify
User=analytics
Group=analytics
WorkingDirectory=/opt/analytics-service

Environment="PATH=/opt/analytics-service/venv/bin"
Environment="FLASK_ENV=production"
EnvironmentFile=/etc/analytics/analytics.env

ExecStart=/opt/analytics-service/venv/bin/gunicorn \
    --config gunicorn_config.py \
    main:app

ExecReload=/bin/kill -s HUP $MAINPID
KillSignal=SIGTERM
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable analytics-service
sudo systemctl start analytics-service
sudo systemctl status analytics-service
```


## Database Setup

### Initial Setup

```bash
# Create database
createdb -U postgres analytics

# Create user
createuser -U postgres analytics
psql -U postgres -c "ALTER USER analytics WITH PASSWORD 'secure_password';"

# Grant privileges
psql -U postgres -d analytics -c "GRANT ALL PRIVILEGES ON DATABASE analytics TO analytics;"

# Initialize tables
flask db upgrade
```

### Database Indexes

Ensure indexes exist for optimal performance:

```sql
-- Check existing indexes
SELECT * FROM pg_stat_user_indexes;

-- Key indexes (should be created automatically)
CREATE INDEX idx_system_metric_tenant_service 
    ON system_metric(tenant_id, service_name, timestamp);
CREATE INDEX idx_metrics_aggregation 
    ON system_metric(metric_name, aggregation_level);
CREATE INDEX idx_service_metric_service 
    ON service_metric(tenant_id, service_name);
CREATE INDEX idx_alert_active 
    ON alert(tenant_id, is_active);
```

### Backup Strategy

```bash
# Full backup (daily)
pg_dump -U analytics analytics | gzip > /backups/analytics-$(date +%Y%m%d).sql.gz

# Incremental backup with WAL archiving
# Enable in postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /backups/wal/%f'

# Backup script
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="analytics"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -U analytics $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```


## Health Checks

### Service Health Endpoint

```bash
# Check service health
curl http://localhost:5009/health

# Response (200 OK)
{
  "status": "healthy",
  "timestamp": "2024-03-04T15:30:00Z",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "disk": "available",
    "memory": "normal"
  }
}
```

### Database Health

```bash
# Check database connection
psql -U analytics -d analytics -c "SELECT 1 AS status;"

# Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Redis Health

```bash
# Check Redis connection
redis-cli ping
# Output: PONG

# Check memory usage
redis-cli info memory
```


## Monitoring

### Prometheus Metrics

Enable metric collection for Prometheus:

```python
# In main.py
from prometheus_client import Counter, Histogram
import time

# Define metrics
request_count = Counter('analytics_requests_total', 'Total requests')
request_duration = Histogram('analytics_request_duration_seconds', 'Request duration')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_count.inc()
    request_duration.observe(duration)
    return response
```

### Key Metrics to Monitor

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| API Response Time (p99) | > 1000ms | Investigate bottleneck |
| Error Rate | > 1% | Check logs and database |
| Database Connections | > 25/30 | Scale connection pool |
| Redis Memory | > 85% | Clear old data/scale |
| Disk Usage | > 90% | Archive old metrics |
| CPU Usage | > 80% | Scale horizontally |

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    file_handler = RotatingFileHandler(
        '/var/log/analytics/service.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```


## Scaling

### Horizontal Scaling

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-service
spec:
  replicas: 3  # Scale to 3 replicas
  selector:
    matchLabels:
      app: analytics-service
  template:
    metadata:
      labels:
        app: analytics-service
    spec:
      containers:
      - name: analytics
        image: analytics-service:1.0.0
        ports:
        - containerPort: 5009
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
```

### Database Scaling

```sql
-- Create read replica
SELECT * FROM pg_create_physical_replication_slot('replica_1', 'physical');

-- Monitor replication lag
SELECT slot_name, restart_lsn, confirmed_flush_lsn 
FROM pg_replication_slots;
```

### Redis Clustering

For high-availability Redis:

```
# redis.conf
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
```


## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: psycopg2.OperationalError: could not connect to server: Connection timed out

Solution:
- Check database is running: psql -U postgres -c "SELECT 1;"
- Verify DATABASE_URL is correct
- Check firewall rules allow port 5432
- Verify PostgreSQL user permissions
```

#### 2. Redis Connection Refused
```
Error: redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379

Solution:
- Restart Redis: redis-server or systemctl restart redis
- Check REDIS_URL is correct
- Verify Redis port (default 6379)
- Check firewall rules
```

#### 3. JWT Token Expired
```
Error: 401 Unauthorized - Token has expired

Solution:
- Refresh token using endpoint: POST /auth/refresh
- Check system time is synchronized
- Verify JWT_ACCESS_TOKEN_EXPIRES setting
```

#### 4. Rate Limiting Issues
```
Error: 429 Too Many Requests

Solution:
- Implement exponential backoff
- Check X-RateLimit-Reset header
- Contact admin to increase limit for your tenant
- Cache responses to reduce requests
```

### Debug Mode

```bash
# Enable debug logging
export FLASK_ENV=development
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG

# View detailed logs
tail -f /var/log/analytics/service.log
```

### Performance Issues

```bash
# Check slow queries
SELECT * FROM pg_stat_statements 
WHERE mean_exec_time > 1000  # > 1 second
ORDER BY mean_exec_time DESC;

# Check index usage
SELECT * FROM pg_stat_user_indexes
WHERE idx_scan < 100;

# Monitor database activity
SELECT * FROM pg_stat_activity;
```


## Security

### SSL/TLS Configuration

```python
# Enable HTTPS in gunicorn
gunicorn --certfile=/path/to/cert.pem \
         --keyfile=/path/to/key.pem \
         --ssl-version=TLSv1_2 \
         main:app
```

### Authentication Best Practices

```python
# Enforce JWT validation
@app.before_request
def check_auth():
    if request.path.startswith('/api/'):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or not validate_jwt(token):
            return {'error': 'Unauthorized'}, 401
```

### Input Validation

```python
from flask import request
from marshmallow import Schema, fields, ValidationError

class MetricQuerySchema(Schema):
    metric_name = fields.Str(required=True, validate=Length(min=1, max=100))
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)

@app.route('/api/metrics')
def get_metrics():
    schema = MetricQuerySchema()
    try:
        args = schema.load(request.args)
    except ValidationError as err:
        return {'errors': err.messages}, 400
```


## Backup & Recovery

### Backup Verification

```bash
# Test backup restoration
pg_restore -d test_analytics /backups/analytics-20240304.sql.gz

# Verify data integrity
psql -U analytics -d test_analytics -c \
  "SELECT COUNT(*) FROM system_metric; \
   SELECT COUNT(*) FROM alert; \
   SELECT COUNT(*) FROM dashboard;"
```

### Point-in-Time Recovery

```sql
-- Restore to specific timestamp
SELECT pg_start_backup('backup_label', false);
-- [Copy tablespace files to backup location]
SELECT pg_stop_backup();

-- Later, restore to point in time
pg_basebackup -D /var/lib/postgresql/backup \
              --recovery-target-timeline=latest \
              --recovery-target-xid=1000
```

### Disaster Recovery Plan

1. **Detection**: Monitor backup verification logs
2. **Assessment**: Check data integrity
3. **Recovery**: Use latest backup (< 1 hour old)
4. **Validation**: Compare record counts pre/post
5. **Notification**: Alert stakeholders
6. **Post-mortem**: Document root cause


## Support & Resources

- **Documentation**: https://docs.example.com/analytics
- **Slack Channel**: #analytics-team
- **On-call**: Pagerduty rotation
- **Issue Tracker**: Jira project ANALYTICS


---

**Last Updated**: 2024-03-04
**Version**: 1.0.0
**Maintained By**: Analytics Engineering Team
