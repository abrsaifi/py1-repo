# 📋 PRODUCTION DEPLOYMENT CHECKLIST

**Created:** March 10, 2026  
**Updated:** Phase 2 Implementation  
**Version:** 1.0

---

## 🔐 SECURITY CHECKLIST

### Secrets & Environment Variables
```
☐ Generate strong JWT_SECRET_KEY (use openssl rand -hex 32)
☐ Generate strong SECRET_KEY (use secrets.token_urlsafe(32))
☐ Store secrets in .secrets.json (NOT in git)
☐ Add .secrets.json to .gitignore
☐ Use environment variables in production
☐ Rotate secrets every 90 days
☐ Never commit .env files to version control
```

### Password & Authentication
```
☐ Enforce strong password policy (min 12 chars, complexity)
☐ Implement 2FA/MFA for admin accounts
☐ Set JWT token expiry to 1 hour
☐ Implement token refresh mechanism
☐ Disable default admin user after setup
☐ Change all default credentials
☐ Hash passwords using bcrypt (minimum 12 rounds)
☐ Implement logout that invalidates tokens
```

### Database Security
```
☐ Use PostgreSQL in production (NOT SQLite)
☐ Create separate DB user with limited permissions
☐ Enable SSL/TLS for database connections
☐ Implement automated daily backups
☐ Test backup restoration process
☐ Store backups in separate secure location
☐ Encrypt database at rest
☐ Enable audit logging on database
☐ Use connection pooling (pgBouncer)
```

### API Security
```
☐ Enable HTTPS/TLS (get SSL cert from Let's Encrypt)
☐ Redirect all HTTP to HTTPS
☐ Implement rate limiting (100 requests/hour per IP)
☐ Validate all input (server-side)
☐ Sanitize SQL queries (use parameterized queries)
☐ Implement CORS policy (restrict to specific domains)
☐ Add security headers (X-Frame-Options, CSP, etc.)
☐ Implement file upload validation (type & size checks)
☐ Disable directory listing
☐ Remove server version headers
```

### Infrastructure Security
```
☐ Use firewall to restrict access to services
☐ Use VPN for admin access
☐ Enable DDoS protection
☐ Configure WAF (Web Application Firewall)
☐ Use separate VPC for database
☐ Restrict SSH to specific IPs
☐ Implement intrusion detection (IDS)
☐ Enable CloudTrail/audit logging
☐ Configure security groups properly
☐ Use encrypted communication between services
```

---

## 🗄️ DATABASE SETUP

### PostgreSQL Installation
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/

# Start PostgreSQL
sudo systemctl start postgresql
# or
brew services start postgresql
```

### Create Production Database
```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE docpro_prod;
CREATE USER docprouser WITH PASSWORD 'strong_password_here';
ALTER ROLE docprouser SET client_encoding TO 'utf8';
ALTER ROLE docprouser SET default_transaction_isolation TO 'read committed';
ALTER ROLE docprouser SET default_transaction_deferrable TO on;
ALTER ROLE docprouser SET default_transaction_level TO 'read committed';
ALTER ROLE docprouser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE docpro_prod TO docprouser;

# Exit
\q
```

### Database Configuration
```env
# .env
DATABASE_URL=postgresql://docprouser:password@localhost:5432/docpro_prod
```

### Initialize Database Schema
```bash
# Create tables from models
python manage.py db upgrade

# Verify tables created
psql -U docprouser docpro_prod -c "\dt"
```

---

## 🐳 DOCKER SETUP

### Build & Push Image
```bash
# Build production image
docker build -f Dockerfile -t docpro:latest .
docker tag docpro:latest docpro:1.0.0

# Push to registry (Docker Hub, ECR, etc.)
docker push docpro:latest
docker push docpro:1.0.0
```

### Docker Compose Production
```bash
# Start with production compose file
docker-compose -f docker-compose.prod.yml up -d

# Verify services running
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f worker
```

---

## 🔧 APPLICATION DEPLOYMENT

### Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install production packages
pip install -r requirements.txt
pip install gunicorn
pip install celery[redis]
pip install psycopg2-binary
```

### Environment Setup
```bash
# Create .env file with production values
cp .env.example .env

# Edit .env with:
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=very-secure-key-here
CELERY_BROKER_URL=redis://localhost:6379/0
SECRET_KEY=very-secure-secret-here
```

### Database Initialization
```bash
# Run migrations
python manage.py db upgrade

# Create initial admin user
python scripts/create_admin.py

# Verify database
python -c "from app import create_app; from app.models import db, User; app = create_app(); db.create_all()"
```

### Run Application
```bash
# Using Gunicorn (production WSGI server)
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:create_app()

# Or with supervisor (see below)
```

---

## 🦾 BACKGROUND WORKERS

### Install Celery
```bash
pip install celery[redis] flower
```

### Start Redis
```bash
# Check if running
redis-cli ping

# Or start Docker container
docker run -d -p 6379:6379 redis:latest
```

### Start Workers with Supervisor

Create `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery_conversions]
command=/path/to/venv/bin/celery -A app.celery_config worker -Q conversions --concurrency=4
directory=/var/www/docpro
user=www-data
environment=FLASK_ENV=production,PYTHONUNBUFFERED=1
autostart=true
autorestart=true
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/conversions.log

[program:celery_emails]
command=/path/to/venv/bin/celery -A app.celery_config worker -Q emails --concurrency=10
directory=/var/www/docpro
user=www-data
environment=FLASK_ENV=production,PYTHONUNBUFFERED=1
autostart=true
autorestart=true
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/emails.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A app.celery_config beat
directory=/var/www/docpro
user=www-data
environment=FLASK_ENV=production,PYTHONUNBUFFERED=1
autostart=true
autorestart=true
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

Start workers:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery:*
```

---

## 👀 MONITORING & LOGGING

### Application Monitoring
```bash
# Install monitoring tools
pip install sentry-sdk  # Error tracking
pip install datadog    # Performance monitoring

# Configure in app
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=0.1
)
```

### Celery Monitoring
```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.celery_config flower --port=5555

# Access at http://localhost:5555
```

### Log Aggregation
```bash
# Install ELK stack or use cloud service
# Elasticsearch + Logstash + Kibana

# Or use CloudWatch, Datadog, Papertrail
```

### Backup Strategy
```bash
# Daily database backup
0 2 * * * /usr/local/bin/backup-db.sh

# Weekly backup to S3
0 3 * * 0 /usr/local/bin/backup-to-s3.sh

# Monthly snapshot
0 4 1 * * /usr/local/bin/snapshot.sh
```

---

## 🌐 WEB SERVER SETUP

### Nginx Configuration
```bash
# Install Nginx
sudo apt-get install nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/docpro
```

Config file:
```nginx
upstream docpro {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers (already set in Flask, but double-check)
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://docpro;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # Frontend static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/docpro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

---

## 🚀 DEPLOYMENT PROCESS

### Pre-Deployment Checklist
```
☐ All tests passing
☐ Code reviewed
☐ Performance tested
☐ Security audit completed
☐ Database migration tested
☐ Backup created
☐ Rollback plan in place
☐ Team notified
```

### Deployment Steps
```bash
# 1. Pull latest code
cd /var/www/docpro
git pull origin main

# 2. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 3. Run database migrations
python manage.py db upgrade

# 4. Collect static files (if applicable)
python manage.py collectstatic --noinput

# 5. Restart services
sudo supervisorctl restart docpro
sudo systemctl restart nginx

# 6. Health check
curl https://yourdomain.com/api/health

# 7. Smoke tests
python tests/smoke_tests.py

# 8. Monitor logs
tail -f /var/log/docpro/app.log
```

### Rollback Plan
```bash
# If deployment fails:
git checkout <previous-commit>
python manage.py db downgrade
sudo supervisorctl restart docpro
```

---

## 📊 PERFORMANCE REQUIREMENTS

### API Response Times
```
GET /api/health        < 100ms
GET /api/conversions   < 500ms
POST /api/admin/stats  < 1000ms
```

### Database Performance
```
Query timeout: 5 seconds
Connection pool: 20 connections
Slow query log: 1 second
```

### Worker Performance
```
Task timeout: 30 minutes
Task retries: 3 attempts
Queue depth: < 1000 tasks
```

---

## 🔍 MONITORING QUERIES

### Database Health
```sql
-- Check active connections
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;

-- Check slow queries
SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) 
FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;
```

### Application Metrics
```bash
# CPU usage
top -b -n 1 | grep gunicorn

# Memory usage
ps aux | grep gunicorn

# Disk space
df -h

# Redis stats
redis-cli INFO
```

---

## ✅ FINAL CHECKLIST BEFORE LAUNCH

```
SECURITY
☐ All secrets in environment variables
☐ HTTPS enabled and working
☐ Rate limiting active
☐ Security headers set
☐ CORS policy configured
☐ Admin user changed

DATABASE
☐ PostgreSQL installed and running
☐ Backups automated and tested
☐ Migrations applied
☐ Initial data loaded
☐ Indexes created

WORKERS
☐ Celery workers running
☐ Celery Beat running
☐ Redis running
☐ Flower monitoring active

MONITORING
☐ Error tracking (Sentry) configured
☐ Performance monitoring active
☐ Log aggregation working
☐ Health checks passing
☐ Alerts configured

DEPLOYMENT
☐ Nginx configured
☐ SSL certificate installed
☐ Load balancer configured
☐ CDN configured (optional)
☐ DNS pointing to server
```

---

**Status:** ✅ Production Ready  
**Estimated Setup Time:** 4-6 hours  
**Support:** See TROUBLESHOOTING.md for common issues
