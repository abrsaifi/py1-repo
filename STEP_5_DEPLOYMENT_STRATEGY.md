# STEP 5: Deployment Strategy & Checklist 🚀

**Date:** February 19, 2026  
**Status:** Deployment plan ready  
**Environment:** Windows Server / Linux / Docker  
**Estimated Setup Time:** 2-4 hours  

---

## Deployment Overview

This guide covers deploying the Sheet Management system from development to production.

### Deployment Options

| Option | Complexity | Cost | Scaling | Best For |
|--------|-----------|------|---------|----------|
| **Windows Server** | Low | $0 (existing) | Limited | Small teams, enterprise Windows shops |
| **Linux + Gunicorn** | Medium | $10-50/month | Good | Startups, medium apps |
| **Docker Container** | Medium | $10-50/month | Excellent | Cloud-native, DevOps |
| **Kubernetes** | High | $50-200/month | Unlimited | Enterprise, high-volume |

**Recommended:** Docker on Linux (best balance of simplicity and scalability)

---

## Pre-Deployment Checklist

### Environment Assessment

- [ ] **Hosting Infrastructure**
  - [ ] Server specs identified (RAM, CPU, disk)
  - [ ] OS selected and ready
  - [ ] Network connectivity verified
  - [ ] SSL certificate obtained
  - [ ] DNS records configured

- [ ] **Python Environment**
  - [ ] Python 3.8+ installed
  - [ ] pip and virtualenv available
  - [ ] All dependencies compatible
  - [ ] No version conflicts

- [ ] **System Dependencies**
  - [ ] LibreOffice installed and tested
  - [ ] soffice command available
  - [ ] Temp directory writable
  - [ ] Disk space available (minimum 1GB free)

- [ ] **Security & Config**
  - [ ] API key generated and stored securely
  - [ ] HTTPS certificate installed
  - [ ] Firewall rules configured
  - [ ] Environment variables set
  - [ ] Secret management in place

- [ ] **Testing**
  - [ ] All unit tests passing
  - [ ] Manual endpoint tests completed
  - [ ] Security audit completed
  - [ ] Performance benchmarks recorded

---

## Option 1: Windows Server Deployment

### Step 1: Install Dependencies

#### 1.1 Install LibreOffice (if not present)
```bash
# Download from https://www.libreoffice.org/download/
# Or use winget
winget install libreoffice

# Verify installation
soffice --version
# Output: LibreOffice x.x.x
```

#### 1.2 Install Python Packages
```bash
# Navigate to project
cd c:\path\to\project

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Verify
pip list | findstr flask openpyxl
```

### Step 2: Configure Application

#### 2.1 Set Environment Variables
```powershell
# Create .env file
@"
FLASK_ENV=production
FLASK_DEBUG=0
UPLOAD_API_KEY=your-secure-key-here-minimum-32-chars
LOG_LEVEL=INFO
LOG_FILE=c:\logs\app.log
MAX_CONTENT_LENGTH=16777216
"@ | Out-File -Encoding UTF8 .env
```

#### 2.2 Create Startup Script
```powershell
# run_production.ps1
# Add to task scheduler or startup folder

$env:FLASK_ENV = "production"
$env:UPLOAD_API_KEY = (Get-Content "C:\secure\api_key.txt" | ConvertTo-SecureString -AsPlainText -Force)

cd C:\path\to\project
.\venv\Scripts\activate
python app.py
```

### Step 3: Run as Service

#### 3.1 Using NSSM (Non-Sucking Service Manager)
```powershell
# Download NSSM from https://nssm.cc/download
# Extract to C:\Tools\nssm

# Install service
C:\Tools\nssm\nssm.exe install DocumentPro python.exe c:\path\to\project\app.py

# Start service
C:\Tools\nssm\nssm.exe start DocumentPro

# Verify running
Get-Service DocumentPro | Select Status
```

#### 3.2 Using Windows Task Scheduler
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction `
  -Execute "C:\path\to\project\venv\Scripts\python.exe" `
  -Argument "app.py"

$trigger = New-ScheduledTaskTrigger -AtStartup

Register-ScheduledTask `
  -TaskName "DocumentPro" `
  -Action $action `
  -Trigger $trigger `
  -RunLevel Highest
```

### Step 4: Configure IIS (Optional)

```xml
<!-- web.config -->
<configuration>
  <appSettings>
    <add key="PYTHONPATH" value="C:\path\to\project" />
  </appSettings>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" 
           scriptProcessor="C:\path\to\project\venv\Scripts\python.exe|app.py" />
    </handlers>
    <security>
      <requestFiltering>
        <requestLimits maxAllowedContentLength="16777216" />
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
```

---

## Option 2: Linux + Gunicorn Deployment

### Step 1: Install System Dependencies

```bash
# Update package manager
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3.10 python3-pip python3-venv
sudo apt-get install -y libreoffice-calc libreoffice-writer
sudo apt-get install -y nginx
sudo apt-get install -y supervisor

# Verify installations
python3 --version
soffice --version
```

### Step 2: Setup Application

```bash
# Create project directory
sudo mkdir -p /var/www/documentpro
cd /var/www/documentpro

# Clone or copy application
git clone <repo> . # or copy files

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directory for logs
mkdir -p /var/log/documentpro
sudo chown -R www-data:www-data /var/log/documentpro
```

### Step 3: Configure Environment

```bash
# Create .env file
sudo tee /var/www/documentpro/.env > /dev/null << EOF
FLASK_ENV=production
FLASK_DEBUG=0
UPLOAD_API_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
LOG_LEVEL=INFO
LOG_FILE=/var/log/documentpro/app.log
EOF

# Secure file permissions
chmod 600 /var/www/documentpro/.env
sudo chown www-data:www-data /var/www/documentpro/.env
```

### Step 4: Setup Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Create gunicorn config
sudo tee /var/www/documentpro/gunicorn_config.py > /dev/null << 'EOF'
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
bind = "127.0.0.1:5000"
timeout = 60
accesslog = "/var/log/documentpro/access.log"
errorlog = "/var/log/documentpro/error.log"
loglevel = "info"
EOF

# Test Gunicorn
gunicorn --config /var/www/documentpro/gunicorn_config.py wsgi:app
```

### Step 5: Setup Supervisor

```bash
# Create supervisor config
sudo tee /etc/supervisor/conf.d/documentpro.conf > /dev/null << 'EOF'
[program:documentpro]
directory=/var/www/documentpro
command=/var/www/documentpro/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/documentpro/supervisor.log
EOF

# Start supervisor program
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start documentpro
```

### Step 6: Configure Nginx

```nginx
# /etc/nginx/sites-available/documentpro
upstream documentpro {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # File upload limit
    client_max_body_size 16M;
    
    # Logging
    access_log /var/log/documentpro/nginx_access.log;
    error_log /var/log/documentpro/nginx_error.log;
    
    # Compression
    gzip on;
    gzip_types application/json text/plain application/pdf;
    gzip_min_length 500;
    
    location / {
        proxy_pass http://documentpro;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }
    
    location /static/ {
        alias /var/www/documentpro/static/;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/documentpro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate (interactive)
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Option 3: Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="Sheet Management API"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice-calc \
    libreoffice-writer \
    libreoffice-base \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "app:app"]
```

### Step 2: Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  documentpro:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - UPLOAD_API_KEY=${UPLOAD_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - /tmp:/tmp  # For temporary files
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - documentpro-network
  
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - documentpro
    restart: unless-stopped
    networks:
      - documentpro-network

networks:
  documentpro-network:
    driver: bridge
```

### Step 3: Build and Run

```bash
# Create .env file
echo "UPLOAD_API_KEY=$(openssl rand -hex 32)" > .env

# Build image
docker-compose build

# Run containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f documentpro

# Stop containers
docker-compose down
```

### Step 4: Deploy to Cloud

#### AWS ECS
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag documentpro:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/documentpro:latest

docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/documentpro:latest
```

#### Google Cloud Run
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/documentpro

# Deploy
gcloud run deploy documentpro \
  --image gcr.io/PROJECT_ID/documentpro \
  --platform managed \
  --memory 512Mi \
  --timeout 60s \
  --set-env-vars UPLOAD_API_KEY=$API_KEY
```

---

## Post-Deployment Verification

### Verification Checklist

- [ ] **Application Health**
  - [ ] API is responding to requests
  - [ ] Health check endpoint works
  - [ ] All three endpoints functional
  - [ ] Error handling works correctly

- [ ] **Security**
  - [ ] HTTPS working
  - [ ] API key validation active
  - [ ] Temporary files being cleaned
  - [ ] Logs not exposing secrets

- [ ] **Performance**
  - [ ] Response times acceptable
  - [ ] No memory leaks
  - [ ] CPU usage normal
  - [ ] File operations working

- [ ] **Monitoring**
  - [ ] Logs being collected
  - [ ] Alerts configured
  - [ ] Metrics being captured
  - [ ] Dashboard accessible

### Quick Verification Script

```bash
#!/bin/bash

API_KEY="your-api-key"
BASE_URL="https://your-domain.com"

echo "=== API Health Check ==="

# Check 1: API availability
echo "1. Checking API availability..."
http_code=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
if [ $http_code -eq 200 ]; then
    echo "✓ API is responding"
else
    echo "✗ API not responding (HTTP $http_code)"
fi

# Check 2: API key validation
echo "2. Checking API key validation..."
# Missing key should fail
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/list-sheets)
if [ $http_code -eq 401 ]; then
    echo "✓ API key validation working"
else
    echo "✗ API key validation not working (HTTP $http_code)"
fi

# Check 3: Health endpoint
echo "3. Checking health endpoint..."
health=$(curl -s -H "X-API-Key: $API_KEY" $BASE_URL/health | jq .status)
if [ "$health" = "\"ok\"" ]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
fi

echo "=== Verification Complete ==="
```

---

## Troubleshooting Guide

### Issue: LibreOffice not found
**Error:** `soffice: command not found`
**Solution:**
```bash
# Linux
sudo apt-get install libreoffice

# Windows
# Download from libreoffice.org or use winget
```

### Issue: API key not being validated
**Error:** Requests without API key still work
**Solution:**
Check environment variable:
```bash
echo $UPLOAD_API_KEY  # Should return key
# If empty, set it:
export UPLOAD_API_KEY="your-secure-key"
```

### Issue: File uploads failing
**Error:** `413 Payload Too Large`
**Solution:**
Increase max file size in nginx/server config:
```nginx
client_max_body_size 30M;  # Change from 16M
```

### Issue: Memory usage increasing
**Error:** Memory grows over time, eventual OOM
**Solution:**
1. Enable monitoring to identify leaks
2. Check temp file cleanup
3. Restart application daily
4. Implement worker queue for large files

### Issue: Slow PDF conversions
**Error:** PDF generation takes 10+ seconds
**Solution:**
1. Upgrade server (more CPU cores)
2. Implement LibreOffice daemon mode
3. Use worker queue to parallelize
4. Cache conversions

---

## Rollback Plan

### If deployment fails:

```bash
# Step 1: Stop new version
docker-compose down
# or
sudo systemctl stop documentpro

# Step 2: Restore previous version
git checkout v1.0.0
docker-compose up -d
# or
sudo systemctl start documentpro

# Step 3: Verify working
curl https://yourdomain.com/health

# Step 4: Investigate issue
tail -f /var/log/documentpro/app.log
docker-compose logs -f
```

---

## Deployment Timeline

### Pre-Deployment (1 hour)
- [ ] System setup and dependencies
- [ ] Environment configuration
- [ ] SSL certificate installation
- [ ] DNS configuration

### Deployment (30-60 minutes)
- [ ] Application installation
- [ ] Service configuration
- [ ] Database and caches initialization
- [ ] Monitoring setup

### Post-Deployment (30 minutes)
- [ ] Verification testing
- [ ] Load testing
- [ ] Monitor for errors
- [ ] Documentation update

**Total: 2-3 hours for first deployment**

---

## Maintenance Schedule

### Daily
- Check logs for errors
- Verify API is responding
- Monitor resource usage

### Weekly
- Review monitoring dashboards
- Check for dependency updates
- Verify backups

### Monthly
- Security scan
- Performance analysis
- Capacity planning
- Update dependencies

---

## Deployment Success Criteria

✅ **The deployment is successful when:**
1. All three endpoints return HTTP 200 for valid requests
2. API key validation rejects unauthorized requests
3. Response times are consistent (< 3 seconds)
4. No errors in logs (or normal error rate < 0.1%)
5. Temperature file cleanup working (no accumulation)
6. Monitoring dashboard showing healthy status
7. SSL certificate valid and trusted

---

## Next Steps

1. Choose deployment option (Windows/Linux/Docker)
2. Follow setup steps for chosen option
3. Run verification checklist
4. Configure monitoring
5. Document any customizations
6. Setup tracking for improvements

---

**Estimated Effort:** 2-4 hours  
**Difficulty:** 🟡 Medium (well-documented, straightforward)  
**Risk:** 🟢 Low (verified system, good error handling)  
**Impact:** 🚀 High (system live and serving users)
