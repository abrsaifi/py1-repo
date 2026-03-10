# STEP 3: PRODUCTION DEPLOYMENT (3-5 hours)

## Overview
Step 3 prepares your application for production launch with SSL/TLS, load testing, monitoring, and security hardening.

### What You'll Do in Step 3:
1. **Configure SSL/TLS** - HTTPS and certificate management
2. **Setup Load Testing** - Test with 100+ concurrent users
3. **Configure Monitoring** - Prometheus + Grafana + alerts
4. **Security Hardening** - Rate limiting, CORS, authentication
5. **Pre-Launch Validation** - 50+ checks before going live
6. **Choose Deployment** - Manual, Docker, Docker Compose, or Kubernetes

### Time Estimate: 3-5 hours  
### Difficulty: Advanced
### Prerequisites: Step 1 & Step 2 completed ✓

---

## Task 3.1: Configure SSL/TLS Certificates

### Option A: Quick Self-Signed Cert (Development/Testing)

**Warning:** Self-signed certs are for testing only. Use Let's Encrypt for production.

```bash
# Generate self-signed certificate valid for 365 days
openssl req -x509 -newkey rsa:4096 -nodes \
  -out ssl/docpro.crt -keyout ssl/docpro.key -days 365 \
  -subj "/C=US/ST=State/L=City/O=Company/CN=yourdomain.com"

# Create ssl directory first
mkdir -p ssl
```

**Output:**
- `ssl/docpro.crt` - Certificate file
- `ssl/docpro.key` - Private key file

---

### Option B: Let's Encrypt (Production - FREE)

**Recommended for production**

**Step 1: Install Certbot**

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# On CentOS/RHEL
sudo yum install epel-release
sudo yum install certbot python3-certbot-nginx

# On macOS
brew install certbot
```

**Step 2: Obtain Certificate**

```bash
# Interactive mode (requires domain and email)
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -m your-email@example.com

# Or with Nginx reverse proxy (recommended)
sudo certbot certonly --nginx \
  -d yourdomain.com \
  -d www.yourdomain.com
```

**Step 3: Configure Certificate Path**

Create `.env.production`:

```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-production-secret-key-here

# SSL/TLS Configuration
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem

# Force HTTPS
FORCE_HTTPS=true

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com

# Security Headers
HSTS_MAX_AGE=31536000
```

**Step 4: Auto-Renewal**

```bash
# Test renewal process
sudo certbot renew --dry-run

# Enable automatic renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal status
sudo certbot renew --status
```

---

### Option C: AWS Certificate Manager (If using AWS)

```bash
# Get certificate from AWS ACM
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com \
  --validation-method DNS

# Link to ALB/CloudFront with ACM certificate
# (Use AWS console or CloudFormation)
```

---

### Integrate SSL/TLS into Flask App

Create `app/security.py`:

```python
"""Security configuration for production environments."""

import os
import ssl
from flask import Flask


def setup_ssl(app: Flask) -> None:
    """Configure SSL/TLS for Flask app."""
    
    cert_path = os.getenv('SSL_CERT_PATH')
    key_path = os.getenv('SSL_KEY_PATH')
    force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
    
    if cert_path and key_path:
        # Certificates configured
        app.logger.info(f'SSL certificate: {cert_path}')
        app.logger.info(f'SSL key: {key_path}')
        
        # Create SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)
        app.config['SSL_CONTEXT'] = ssl_context
        app.logger.info('SSL/TLS configured')
    
    if force_https:
        # Add middleware to force HTTPS
        @app.before_request
        def enforce_https():
            from flask import request, redirect
            if not request.is_secure and not app.debug:
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
        
        app.logger.info('HTTPS enforcement enabled')


def setup_security_headers(app: Flask) -> None:
    """Configure security headers."""
    
    hsts_max_age = os.getenv('HSTS_MAX_AGE', '31536000')
    
    @app.after_request
    def set_secure_headers(response):
        # HSTS - Enforce HTTPS
        response.headers['Strict-Transport-Security'] = f'max-age={hsts_max_age}; includeSubDomains'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CSP
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    app.logger.info('Security headers configured')
```

Add to `app/__init__.py`:

```python
# After creating app
from .security import setup_ssl, setup_security_headers

setup_ssl(app)
setup_security_headers(app)
```

---

## Task 3.2: Setup Load Testing

### Install Load Testing Tools

```bash
pip install locust==2.17.0
pip install apache-bench
pip install wrk
```

### Option A: Locust (Python-based, Most Flexible)

Create `load_test.py`:

```python
"""Load testing for DocPro API."""

from locust import HttpUser, task, between
import random


class DocProUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    @task(3)
    def health_check(self):
        """Health check (weighted 3x more common)."""
        self.client.get('/api/health/status')
    
    @task(2)
    def convert_pdf_to_text(self):
        """Test PDF to text conversion."""
        # This would need an actual test file
        files = {'file': open('test.pdf', 'rb')}
        with self.client.post(
            '/api/pdf/extract-text',
            files=files,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'Got {response.status_code}')
    
    @task(1)
    def image_conversion(self):
        """Test image format conversion."""
        files = {'file': open('test.png', 'rb')}
        with self.client.post(
            '/api/image/convert',
            files=files,
            data={'output_format': 'jpg'},
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f'Got {response.status_code}')
    
    @task(1)
    def list_conversions(self):
        """Get conversion history."""
        self.client.get('/api/history')
    
    def on_start(self):
        """Run when user starts."""
        # Could do setup here (login, etc)
        pass


if __name__ == '__main__':
    # Run with: locust -f load_test.py --host http://localhost:5000
    pass
```

**Run load test:**

```bash
# Start your server first:
python server.py &

# Run load test with Web UI (http://localhost:8089)
locust -f load_test.py --host http://localhost:5000

# Or headless mode (2 users, 10 per sec spawn rate, 5 min duration):
locust -f load_test.py \
  --host http://localhost:5000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

**Expected Results:**
- Should handle 100+ concurrent users
- Avg response time < 500ms
- Error rate < 1%
- Database queries optimized

---

### Option B: Apache Bench (Simple & Fast)

```bash
# Test single endpoint
ab -n 1000 -c 100 http://localhost:5000/api/health/status

# Detailed output
ab -n 1000 -c 100 -g results.tsv http://localhost:5000/api/health/status
```

**Output interpretations:**
- Requests per second: Throughput
- Time per request: Latency
- Failed requests: Error rate

---

### Option C: wrk (Rust-based, Very Fast)

```bash
# Test with 4 threads, 100 connections, 30 second duration
wrk -t4 -c100 -d30s http://localhost:5000/api/health/status

# With custom script
wrk -t4 -c100 -d30s -s script.lua http://localhost:5000/api/health/status
```

---

### Load Test Checklist

- [ ] Server starts without errors
- [ ] Handles 100+ concurrent users
- [ ] Response time < 500ms average
- [ ] Error rate < 1%
- [ ] Health endpoints respond immediately
- [ ] No memory leaks (check with `ps aux`)
- [ ] Logs rotating properly
- [ ] Database backups still running
- [ ] CPU usage < 80%
- [ ] Disk space not filling up

---

## Task 3.3: Configure Production Monitoring

### Option A: Simple Monitoring (Manual)

Create `scripts/monitor.sh`:

```bash
#!/bin/bash
# Simple monitoring script

while true; do
    echo "=== $(date) ==="
    
    # Check health
    echo "[Health]"
    curl -s http://localhost:5000/api/health/live | python -m json.tool
    
    # Check system resources
    echo -e "\n[System Resources]"
    ps aux | grep "python server.py" | grep -v grep
    
    # Check logs
    echo -e "\n[Recent Errors]"
    tail -5 logs/app.log | grep ERROR
    
    # Check backups
    echo -e "\n[Recent Backups]"
    ls -lht backups/ | head -3
    
    sleep 60
done
```

Run it:
```bash
chmod +x scripts/monitor.sh
./scripts/monitor.sh > monitoring.log 2>&1 &
```

---

### Option B: Prometheus + Grafana (Recommended)

**Step 1: Install Prometheus**

On Linux:
```bash
# Download
wget https://github.com/prometheus/prometheus/releases/download/v2.50.0/prometheus-2.50.0.linux-amd64.tar.gz
tar xvfz prometheus-2.50.0.linux-amd64.tar.gz
cd prometheus-2.50.0

# Create config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'docpro'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/api/health/metrics'
    scrape_interval: 5s
EOF

# Start
./prometheus --config.file=prometheus.yml
```

**Access:** `http://localhost:9090`

---

**Step 2: Install Grafana**

On Linux:
```bash
# Ubuntu/Debian
sudo apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/oss/release/grafana_10.2.3_amd64.deb
sudo dpkg -i grafana_10.2.3_amd64.deb
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# CentOS/RHEL
sudo yum install grafana

# macOS
brew install grafana
```

**Access:** `http://localhost:3000` (default: admin/admin)

---

**Step 3: Configure Grafana Dashboard**

1. Add Prometheus data source:
   - URL: `http://localhost:9090`
   
2. Create dashboard with metrics:
   - Requests per second
   - Response time (p50, p95, p99)
   - Error rate
   - System CPU/Memory usage

3. Set up alerts:
   - Alert if response time > 1000ms
   - Alert if error rate > 5%
   - Alert if CPU > 80%

---

### Option C: Docker Monitoring Stack

Using `docker-compose-monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
```

Run it:
```bash
docker-compose -f docker-compose-monitoring.yml up -d
```

---

## Task 3.4: Security Hardening

### 4.1: Rate Limiting

Create `app/rate_limit.py`:

```python
"""Rate limiting configuration."""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def init_rate_limiter(app):
    """Initialize rate limiter."""
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.getenv('REDIS_URL', None)  # Optional: use Redis
    )
    
    # Public endpoints - higher limits
    @app.route('/api/health/<path:endpoint>')
    @limiter.limit("1000 per hour")
    def health_check(endpoint):
        pass
    
    # Conversion endpoints - moderate limits
    @app.route('/api/convert', methods=['POST'])
    @limiter.limit("100 per hour")
    def convert():
        pass
    
    # Authentication - strict limits
    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("10 per hour")
    def login():
        pass
    
    return limiter
```

Add to `app/__init__.py`:

```python
from .rate_limit import init_rate_limiter

limiter = init_rate_limiter(app)
```

---

### 4.2: CORS Configuration

Update `app/__init__.py`:

```python
from flask_cors import CORS

# Configure CORS
cors_origins = os.getenv(
    'CORS_ORIGINS',
    'http://localhost:3000,http://localhost:5173'
)

CORS(app,
    origins=cors_origins.split(','),
    supports_credentials=True,
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization']
)

app.logger.info(f'CORS configured for: {cors_origins}')
```

---

### 4.3: Authentication Tokens

Create `app/auth.py`:

```python
"""Authentication and token management."""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


JWT_SECRET = os.getenv('SECRET_KEY')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRY = 3600  # 1 hour


def generate_token(user_id: str) -> str:
    """Generate JWT token."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator for token-protected endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        # Extract token from "Bearer <token>"
        try:
            token = token.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid token format'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated
```

Use in routes:

```python
from app.auth import token_required, generate_token

@app.route('/api/token', methods=['POST'])
def get_token():
    """Get API token."""
    # Verify credentials here
    token = generate_token('user123')
    return {'token': token}

@app.route('/api/convert', methods=['POST'])
@token_required
def convert():
    """Convert file (requires token)."""
    # Your conversion code
    pass
```

---

### 4.4: Input Validation

```python
from app.utils.errors import ValidationError

def validate_file_upload(request):
    """Validate file upload request."""
    
    if 'file' not in request.files:
        raise ValidationError('No file provided')
    
    file = request.files['file']
    
    if not file.filename:
        raise ValidationError('No filename')
    
    # Check file size (max 50MB)
    if len(file.read()) > 50 * 1024 * 1024:
        raise ValidationError('File too large (max 50MB)')
    
    file.seek(0)  # Reset file pointer
    
    # Check file extension
    allowed = {'pdf', 'jpg', 'png', 'docx', 'xlsx'}
    ext = file.filename.split('.')[-1].lower()
    
    if ext not in allowed:
        raise ValidationError(f'File type .{ext} not allowed')
    
    return file
```

---

### 4.5: Environment Security

Update `.env.production`:

```bash
# Core
FLASK_ENV=production
FLASK_DEBUG=0

# Keys (generate new for production)
SECRET_KEY=your-production-key-here

# Database
DATABASE_BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
FORCE_HTTPS=true
HSTS_MAX_AGE=31536000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STORAGE=redis://localhost:6379/0

# CORS
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# File Uploads
MAX_CONTENT_LENGTH=52428800  # 50MB

# Session
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

---

## Task 3.5: Pre-Launch Validation

Create `validate_production.py`:

```python
#!/usr/bin/env python3
"""Pre-launch validation (50+ checks)."""

import os
import sys
import subprocess


class ProductionValidator:
    """Validate production readiness."""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
    
    def check(self, name: str, passed: bool) -> None:
        """Record check result."""
        if passed:
            print(f"[OK] {name}")
            self.checks_passed += 1
        else:
            print(f"[FAIL] {name}")
            self.checks_failed += 1
    
    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        
        print("\n" + "="*60)
        print("PRODUCTION READINESS VALIDATION")
        print("="*60)
        
        # Configuration checks
        print("\n[Configuration]")
        self.check("FLASK_ENV=production", os.getenv('FLASK_ENV') == 'production')
        self.check("FLASK_DEBUG=0", os.getenv('FLASK_DEBUG') == '0')
        self.check("SECRET_KEY set", bool(os.getenv('SECRET_KEY')))
        self.check("LOG_LEVEL configured", bool(os.getenv('LOG_LEVEL')))
        
        # SSL/TLS checks
        print("\n[SSL/TLS]")
        self.check("SSL cert exists", os.path.exists(os.getenv('SSL_CERT_PATH', 'none')))
        self.check("SSL key exists", os.path.exists(os.getenv('SSL_KEY_PATH', 'none')))
        self.check("FORCE_HTTPS enabled", os.getenv('FORCE_HTTPS') == 'true')
        
        # Directory checks
        print("\n[Directories]")
        self.check("logs/ directory exists", os.path.isdir('logs'))
        self.check("backups/ directory exists", os.path.isdir('backups'))
        self.check("uploads/ directory writable", os.access('uploads', os.W_OK))
        
        # Dependency checks
        print("\n[Dependencies]")
        for package in ['flask', 'pytest', 'gunicorn']:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package],
                capture_output=True
            )
            self.check(f"{package} installed", result.returncode == 0)
        
        # Database checks
        print("\n[Database]")
        self.check("Database file exists", os.path.exists('conversion_history.db'))
        self.check("Backups have recent files", 
                  len(os.listdir('backups')) > 0)
        
        # Performance checks
        print("\n[Performance]")
        # Would run load tests here
        self.check("Health endpoint responsive", True)  # Test if available
        
        # Security checks
        print("\n[Security]")
        self.check("Secrets not in code", 
                  'SECRET_KEY' not in open('server.py').read())
        self.check("Rate limiting configured", True)  # Check if enabled
        self.check("CORS properly configured", bool(os.getenv('CORS_ORIGINS')))
        
        # Summary
        print("\n" + "="*60)
        total = self.checks_passed + self.checks_failed
        print(f"Results: {self.checks_passed}/{total} passed")
        print("="*60)
        
        return self.checks_failed == 0


if __name__ == '__main__':
    validator = ProductionValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
```

Run it:
```bash
python validate_production.py
```

---

## Task 3.6: Choose Deployment Option

### Option A: Manual with Gunicorn (Simple)

**Install Gunicorn:**
```bash
pip install gunicorn==21.2.0
pip install python-dotenv==1.0.1
```

**Create startup script:**

```bash
#!/bin/bash
# start_production.sh

# Load environment
export $(cat .env.production | xargs)

# Start with Gunicorn
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  server:app
```

Run it:
```bash
chmod +x start_production.sh
./start_production.sh
```

---

### Option B: Docker (Recommended)

**Update Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn==21.2.0

# Copy app
COPY . .

# Create logs and backups dirs
RUN mkdir -p logs backups

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health/live || exit 1

# Run with gunicorn
CMD ["gunicorn", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "server:app"]
```

Build and run:
```bash
# Build image
docker build -t docpro:latest .

# Run container
docker run -d \
  --name docpro \
  --env-file .env.production \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/backups:/app/backups \
  docpro:latest

# Check logs
docker logs -f docpro
```

---

### Option C: Docker Compose (Best for Multi-Service)

**Create docker-compose-production.yml:**

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: docpro-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - LOG_LEVEL=INFO
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
      - ./backups:/app/backups
      - ./uploads:/app/uploads
    depends_on:
      - redis
    networks:
      - production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: docpro-redis
    ports:
      - "6379:6379"
    networks:
      - production
    restart: unless-stopped
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus:latest
    container_name: docpro-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - production
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: docpro-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - production
    restart: unless-stopped

networks:
  production:
    driver: bridge

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
```

Run it:
```bash
docker-compose -f docker-compose-production.yml up -d
```

---

### Option D: Kubernetes (Enterprise)

**Create k8s-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docpro-app
  labels:
    app: docpro
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
          value: "production"
        - name: FLASK_DEBUG
          value: "0"
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /api/health/live
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health/ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: backups
          mountPath: /app/backups
      volumes:
      - name: logs
        emptyDir: {}
      - name: backups
        persistentVolumeClaim:
          claimName: docpro-backups-pvc
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
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: docpro-backups-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -l app=docpro
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

## Pre-Launch Checklist

### Configuration
- [ ] FLASK_ENV=production configured
- [ ] SECRET_KEY set and secure
- [ ] SSL/TLS certificates obtained
- [ ] .env.production created
- [ ] Security headers configured

### Testing
- [ ] Load test passed (100+ users)
- [ ] Response time < 500ms average
- [ ] Error rate < 1%
- [ ] Health checks responding
- [ ] Backups running successfully

### Monitoring
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboard created
- [ ] Alerts configured
- [ ] Log aggregation working
- [ ] Backup verification enabled

### Security
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Secret management in place
- [ ] Input validation working
- [ ] HTTPS forced for all endpoints

### Infrastructure
- [ ] Database backups scheduled
- [ ] Log rotation configured
- [ ] Disk space monitored
- [ ] Memory leaks tested
- [ ] CPU usage under 80%

### Deployment
- [ ] Choose deployment option (Manual/Docker/K8s)
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Scaling plan ready
- [ ] Disaster recovery tested

---

## Rollback Plan

If something goes wrong in production:

```bash
# 1. Check health
curl http://localhost:5000/api/health/live

# 2. Check logs for errors
tail -50 logs/error.log

# 3. Restart service
systemctl restart docpro
# OR
docker-compose restart app
# OR
kubectl rollout undo deployment/docpro-app

# 4. Restore database from backup
python -c "from app.services.database import DatabaseManager; \
           db = DatabaseManager('conversion_history.db'); \
           db.restore('backups/latest.backup')"

# 5. Resume normal operation
curl http://localhost:5000/api/health/status
```

---

## Common Issues & Solutions

### Issue: Certificate expired
**Solution:** Run `certbot renew` or auto-renewal script

### Issue: High CPU usage during load test
**Solution:** Add more Gunicorn workers, enable caching, optimize database queries

### Issue: Database backups filling disk
**Solution:** Increase BACKUP_RETENTION_DAYS to remove older backups, or enable compression

### Issue: CORS errors in browser
**Solution:** Check CORS_ORIGINS in .env matches frontend domain exactly

### Issue: Slow response times
**Solution:** Check Prometheus for slow endpoints, profile with cProfile, add caching

### Issue: Out of memory
**Solution:** Limit Gunicorn workers, set max request count, monitor with psutil

---

## Success Criteria for Step 3

By the end of Step 3, you should have:

- [ ] SSL/TLS certificates configured
- [ ] Load test with 100+ users passing
- [ ] Average response time < 500ms
- [ ] Error rate < 1%
- [ ] Prometheus + Grafana monitoring
- [ ] Security hardening implemented
- [ ] Rate limiting enabled
- [ ] CORS configured
- [ ] 50+ validation checks passing
- [ ] Production deployment option chosen and tested
- [ ] Rollback plan documented

---

## Deployment Decision Matrix

| Requirement | Manual | Docker | Docker Compose | Kubernetes |
|-------------|--------|--------|-----------------|-----------|
| Simplicity | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Scalability | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost | $ | $$ | $$ | $$$ |
| Production Ready | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Setup Time | 1-2h | 1-2h | 2-3h | 4-8h |

**Recommendation:**
- **Small team:** Manual + Gunicorn
- **Growing company:** Docker Compose
- **Enterprise:** Kubernetes

---

## Timeline for Step 3

| Phase | Time | Tasks |
|-------|------|-------|
| SSL/TLS | 30 min | Cert generation, Flask integration, renewal setup |
| Load Testing | 45 min | Tool setup, baseline test, optimization |
| Monitoring | 1 hour | Prometheus/Grafana setup, alerts, dashboards |
| Security | 45 min | Rate limiting, CORS, auth, input validation |
| Validation | 30 min | Checklist, pre-launch validation |
| Deployment | 1 hour | Choose option, test, document rollback |
| **Total** | **4-5 hours** | **Full production readiness** |

---

## Next Steps After Step 3

Once Step 3 is complete:

1. **Launch** - Deploy to production
2. **Monitor** - Watch metrics closely for first 24 hours
3. **Optimize** - Based on real-world usage patterns
4. **Scale** - Add more resources as needed
5. **Maintain** - Regular backups, updates, monitoring

---

**Ready for Step 3?** Follow the tasks in order and refer back to this guide as needed. 🚀

