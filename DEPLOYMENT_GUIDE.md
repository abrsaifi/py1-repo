# Production Deployment Guide

## Environment Setup

### 1. Initial Setup on New Server
```bash
# Clone repository
git clone <your-repo> docpro
cd docpro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment configuration
cp .env.example .env
nano .env  # Edit with production values
```

### 2. Security Configuration
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env:
SECRET_KEY=<generated-key>
BILLING_PROVIDER_WEBHOOK_SECRET=<shared-provider-signing-secret>
FLASK_ENV=production
DEBUG=0
```

Use the same `BILLING_PROVIDER_WEBHOOK_SECRET` value in your billing provider integration when generating the HMAC-SHA256 signature sent in `X-DocPro-Billing-Signature` to `/api/admin/billing/provider-events`.

### 3. Database Setup
```bash
# Initialize databases
mkdir -p data
python -c "from app.services.database import DatabaseManager; \
           db = DatabaseManager('data/docpro.db'); \
           print('Database initialized')"
```

### 4. Log Directory
```bash
# Create and setup log directory
mkdir -p logs
chmod 755 logs

# Configure log rotation
```

---

## Deployment Options

### Option A: Manual with Gunicorn

**Install production server:**
```bash
pip install gunicorn
```

**Create systemd service file** `/etc/systemd/system/docpro.service`:
```ini
[Unit]
Description=DocPro Document Conversion Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/docpro
EnvironmentFile=/var/www/docpro/.env
ExecStart=/var/www/docpro/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    server:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable docpro
sudo systemctl start docpro

# Monitor
sudo systemctl status docpro
sudo journalctl -u docpro -f
```

---

### Option B: Docker Deployment

**Dockerfile** (already exists - verify contents):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1-gdm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data backups

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health/live || exit 1

# Run with gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "server:app"]
```

**Build and run:**
```bash
# Build image
docker build -t docpro:latest .

# Run container
docker run -d \
  --name docpro \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/backups:/app/backups \
  --env-file .env \
  docpro:latest

# View logs
docker logs -f docpro

# Stop/restart
docker stop docpro
docker start docpro
```

**Docker Compose** (already exists - verify/enhance):
```yaml
version: '3.8'

services:
  docpro:
    build: .
    container_name: docpro
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
    environment:
      - FLASK_ENV=production
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Redis for caching/tasks
  redis:
    image: redis:7-alpine
    container_name: docpro-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

**Deploy with Docker Compose:**
```bash
# Start services
docker-compose up -d

# Monitor
docker-compose logs -f docpro

# Stop
docker-compose down
```

---

### Option C: Kubernetes Deployment

**Deployment manifest** (`k8s-deploy.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docpro
spec:
  replicas: 3
  selector:
    matchLabels:
      app: docpro
  template:
    metadata:
      labels:
        app: docpro
    spec:
      containers:
      - name: docpro
        image: docpro:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: production
        - name: LOG_LEVEL
          value: INFO
        livenessProbe:
          httpGet:
            path: /api/health/live
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health/ready
            port: 5000
          initialDelaySeconds: 20
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: docpro-service
spec:
  selector:
    app: docpro
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f k8s-deploy.yaml
kubectl get pods
kubectl logs -f deployment/docpro
```

---

## Reverse Proxy Setup (Nginx)

**Nginx configuration** (`/etc/nginx/sites-available/docpro`):
```nginx
upstream docpro {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Proxy configuration
    location / {
        proxy_pass http://docpro;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Health check
    location /healthz {
        access_log off;
        proxy_pass http://docpro/api/health/live;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/docpro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL Certificate Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (installed by default)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Manual renewal
sudo certbot renew --dry-run  # Test
sudo certbot renew            # Actual
```

---

## Monitoring & Logging

### Log Aggregation Setup
```bash
# Install ELK Stack or use centralized logging service

# View application logs
journalctl -u docpro -f

# Nginx access/error logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Application health
curl https://yourdomain.com/api/health/status
```

### Monitoring with Prometheus
```bash
# Install Prometheus and Grafana
# Configure scrape target:
# - targets: ['localhost:5000/api/health/metrics']
```

---

## Backup Strategy

### Automated Backups
```bash
# Daily backup cron job
0 2 * * * /var/www/docpro/backup.sh

# Backup script:
#!/bin/bash
DB_PATH="/var/www/docpro/data/docpro.db"
BACKUP_DIR="/var/backups/docpro"

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/docpro_$(date +%Y%m%d_%H%M%S).db

# Keep last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

### Off-site Backup
```bash
# Sync to S3
aws s3 sync /var/backups/docpro s3://your-bucket/docpro-backups/

# Or rsync to remote server
rsync -avz /var/backups/docpro user@backup.server:/backups/
```

---

## Health Checks & Alarms

### Setup Monitoring Alerts
```bash
# Check system health every 5 minutes
*/5 * * * * curl -f https://yourdomain.com/api/health/status || \
            mail -s "DocPro Health Check Failed" admin@company.com

# Monitor disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d% -f1)
if [ $DISK_USAGE -gt 80 ]; then
    mail -s "Disk Usage Alert: ${DISK_USAGE}%" admin@company.com
fi
```

---

## Maintenance Windows

### Zero-downtime Deployment
```bash
# Load balancer health checks will handle seamless transition
# 1. Update code in blue environment
# 2. Run tests
# 3. Switch traffic gradually
# 4. Keep green environment for rollback
```

### Database Maintenance
```bash
# During low-traffic hours:
# 1. Backup database
# 2. Optimize (vacuum)
# 3. Verify backups
# 4. Remove old temp files

# Automated nightly maintenance
0 3 * * * /var/www/docpro/maintenance.sh
```

---

## Performance Tuning

### Application Level
```env
WORKERS=4  # Number of worker processes
CONVERSION_TIMEOUT_SECONDS=300  # Reasonable timeout
UPLOAD_CHUNKING_ENABLED=true  # For large files
```

### Database Level
```python
# Connection pooling
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_MAX_OVERFLOW = 40
```

### System Level
```bash
# Increase file descriptors
ulimit -n 65535

# Network tuning
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
```

---

## Troubleshooting Production

### Service Won't Start
```bash
# Check logs
journalctl -u docpro -n 50

# Verify environment
source /var/www/docpro/.env
echo $FLASK_ENV

# Test manually
cd /var/www/docpro
source venv/bin/activate
python -c "from server import app; print('App loads OK')"
```

### High CPU/Memory
```bash
# Find resource-heavy processes
ps aux --sort=-%cpu | head -5
ps aux --sort=-%mem | head -5

# Check for conversion bottlenecks
tail -100 logs/app.log | grep CONVERSION
```

### Database Corruption
```bash
# Restore from backup
python -c "from app.services.database import DatabaseManager; \
           db = DatabaseManager('data/docpro.db'); \
           db.restore('backups/docpro_backup.db.20240101_000000')"
```

---

## Rollback Procedure

```bash
# Keep previous version in separate directory
/var/www/docpro-v1  # Current
/var/www/docpro-v0  # Previous

# Switch back quickly
sudo systemctl stop docpro
# Update symlink or env variable
sudo systemctl start docpro
sudo systemctl status docpro
```

---

## Security Checklist

- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Only necessary ports open (80, 443)
- [ ] SSH key-based auth
- [ ] Secret key properly set
- [ ] Database password strong
- [ ] Regular backups verified
- [ ] Log monitoring active
- [ ] Dependency updates planned
- [ ] API rate limiting enabled

---

**Deployment Status: Production-Ready** ✅
