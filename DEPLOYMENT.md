# Deployment Guide

## Quick Start

### Local Development
```bash
# 1. Clone and install
git clone <repo>
cd py1
pip install -r requirements.txt

# 2. Run Flask dev server
python -m app.main

# Server runs on http://localhost:5000
```

### Docker (Recommended)
```bash
# 1. Build image
docker build -t docpro:latest .

# 2. Run container
docker run -d \
  --name docpro \
  -p 5000:5000 \
  -e UPLOAD_MAX_FILE_SIZE=52428800 \
  docpro:latest

# 3. Check health
curl http://localhost:5000/api/health
```

### Docker Compose (Dev + DB)
```bash
# Start all services (app + postgres)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

---

## Environment Variables

Set these before running:

```bash
# Server
FLASK_ENV=production              # or 'development'
SECRET_KEY=your-secret-key        # Change in production!
BILLING_PROVIDER_WEBHOOK_SECRET=shared-provider-signing-secret

# Uploads
UPLOAD_MAX_FILE_SIZE=52428800     # 50 MB (bytes)
UPLOAD_CLEANUP_RETENTION=86400    # 24 hours (seconds)
UPLOAD_CLEANUP_INTERVAL=3600      # 1 hour (seconds)

# Rate limiting
RATE_LIMIT_WINDOW=60              # seconds
RATE_LIMIT_MAX=60                 # requests per window

# API Key (optional)
UPLOAD_API_KEY=your-api-key       # If set, required for upload endpoints
```

`BILLING_PROVIDER_WEBHOOK_SECRET` must match the shared secret used by the upstream billing provider to sign requests for `/api/admin/billing/provider-events`.

---

## Production Checklist

- [ ] Change `SECRET_KEY` in config
- [ ] Set `FLASK_ENV=production`
- [ ] Use Gunicorn (4+ workers)
- [ ] Enable HTTPS/TLS
- [ ] Set `UPLOAD_API_KEY` for secure uploads
- [ ] Configure file size limits appropriate for use case
- [ ] Set up database (if using postgres in docker-compose)
- [ ] Configure log rotation
- [ ] Monitor disk space (uploads accumulate)
- [ ] Set up backup of `conversion_history.db`

---

## Scaling

### Multi-Worker Setup
Use Gunicorn with multiple workers:
```bash
gunicorn --workers=8 --worker-class=sync --bind=0.0.0.0:5000 app.main:app
```

### Load Balancing
Place nginx in front for load balancing across Gunicorn instances.

### Background Tasks
OCR and cleanup run in background threads (see `app/services/file_cleanup.py`, `app/services/advanced.py`).

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill it
kill -9 <PID>
```

### Upload Directory Issues
```bash
# Ensure write permissions
mkdir -p /tmp/docpro_uploads
chmod 755 /tmp/docpro_uploads
```

### Memory Issues with EasyOCR
EasyOCR loads large models (~100 MB). For constrained environments:
- Adjust `get_easyocr_reader()` in `app/services/advanced.py`
- Use `gpu=False` (already default)
- Monitor memory during first OCR call (model loads then)

---

## Logs

### Flask Dev
```
WARNING in app.run_server [app.py:XXXX]: Running on http://localhost:5000
```

### Gunicorn (Production)
Logs to stdout/stderr. Configure with `--access-logfile` and `--error-logfile`.

### Docker
```bash
docker logs -f docpro
# or with docker-compose
docker-compose logs -f app
```

---

## Health Check
```bash
curl http://localhost:5000/api/health

# Response:
# {"status":"ok"}
```

---

## Next Steps

- Review MIGRATION_NOTES.md for architecture overview
- Run tests: `pytest`
- Configure environment for your deployment
- Set up CI/CD pipeline (see .github/workflows/)
