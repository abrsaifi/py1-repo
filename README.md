# DocPro - Document Processing & Conversion API

A Flask-based document conversion service with image, PDF, Excel, and advanced processing capabilities. **Recently refactored into a modular package structure** for better maintainability and scalability.

## 🎯 Features

- **Image Processing**: Convert between formats (JPG, PNG, WebP, TIFF), compress, resize, add watermarks
- **PDF Operations**: Preview, merge, split, add watermarks, OCR text extraction, redaction
- **Excel Conversion**: Convert Excel sheets to PDF with layout preservation
- **Office Documents**: Convert DOCX, PPTX to PDF
- **Advanced Features**: EasyOCR text extraction, intelligent table detection, scanned PDF handling
- **Chunked Uploads**: Support for large file uploads via chunked transfer
- **Rate Limiting**: Built-in per-IP rate limiting
- **History Tracking**: SQLite-based operation logging
- **Background Tasks**: Automatic cleanup of old uploads

---

## 📋 Quick Start

### Environment Setup

**Option 1: Local Python**
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m app.main
# Server runs on http://localhost:5000
```

**Option 2: Docker**
```bash
# Build and run
docker build -t docpro:latest .
docker run -p 5000:5000 docpro:latest
```

**Option 3: Docker Compose (includes database)**
```bash
docker-compose up
```

### Test Health
```bash
curl http://localhost:5000/api/health
# {"status":"ok"}
```

---

## 🏗️  Architecture

**Recently migrated from monolithic to modular structure:**

### Before (Deprecated)
```
server.py (4300+ lines)
├── Routes
├── Services
├── Utilities
└── Helpers
```

### After (Current)
```
app/
├── __init__.py             # Flask app factory
├── main.py                 # CLI entrypoint
├── config.py               # Centralized config
├── api/routes/
│   ├── health.py           # Health check
│   ├── image.py            # Image conversions
│   ├── pdf.py              # PDF operations
│   ├── excel.py            # Excel conversions
│   └── uploads.py          # Chunked upload API
├── services/
│   ├── conversions.py      # Image/PDF conversions
│   ├── history.py          # Operation logging
│   ├── advanced.py         # OCR, watermark, etc.
│   └── file_cleanup.py     # Upload cleanup
└── utils/
    ├── file_validator.py   # Validation
    └── logger.py           # Logging
```

**Benefits:**
- ✅ Modular & maintainable
- ✅ Easy to test
- ✅ Scalable
- ✅ Clear separation of concerns

For detailed migration info: see [MIGRATION_NOTES.md](MIGRATION_NOTES.md)

---

## 📚 API Endpoints

### Health Check
```
GET /api/health
→ {"status":"ok"}
```

### Image Processing
```
POST /api/image/convert
Form: file, target_format (jpg|png|webp|tiff), quality, lossless
→ Converted image file

POST /api/image/compress
Form: file, quality
→ Compressed image file
```

### PDF Operations
```
POST /api/pdf/preview
Form: file, operation, max_pages, dpi
→ {"success":true, "images":[...]}
```

### Excel to PDF
```
POST /api/excel/to-pdf
Form: file
→ PDF file
```

### Chunked Uploads
```
POST /api/upload-chunk
Form: upload_id, filename, index, total, chunk
→ {"success":true, "assembled":false|true}

POST /api/convert-uploaded
JSON: {uploads:[{upload_id, filename}], target_format, preset, quality}
→ Converted file(s)

GET /api/upload-status
Query: upload_id, filename
→ {"success":true, "chunks":[...], "total":N}

POST /api/admin/purge-uploads
JSON: {older_than: seconds}
→ {"success":true, "removed":N}
```

Full API documentation: See endpoint docstrings in `app/api/routes/`

---

## ⚙️  Configuration

### Environment Variables
```bash
# Server
FLASK_ENV=production              # or 'development'
SECRET_KEY=your-secret-key        # ⚠️  Change in production!

# Uploads
UPLOAD_MAX_FILE_SIZE=52428800     # 50 MB (bytes)
UPLOAD_CLEANUP_RETENTION=86400    # 24 hours (seconds)
UPLOAD_CLEANUP_INTERVAL=3600      # 1 hour (seconds)

# Rate limiting
RATE_LIMIT_WINDOW=60              # seconds
RATE_LIMIT_MAX=60                 # requests per window

# Optional API Key
UPLOAD_API_KEY=key                # If set, required for uploads
```

### Config Class
All defaults in `app/config.py::Config`. Override:
```python
from app import create_app
from app.config import Config

class ProdConfig(Config):
    SECRET_KEY = 'prod-secret'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

app = create_app(ProdConfig)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_image.py -v

# Watch mode
pytest-watch
```

Tests live in `tests/` directory. When adding features:
1. Write test first (TDD)
2. Implement feature in service
3. Add blueprint endpoint
4. Test end-to-end

---

## 🐳 Docker Deployment

### Build
```bash
docker build -t docpro:latest .
```

### Run (Standalone)
```bash
docker run -d \
  --name docpro \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-key \
  -e UPLOAD_MAX_FILE_SIZE=52428800 \
  -v /path/to/uploads:/tmp/docpro_uploads \
  docpro:latest
```

### Run with Compose (Dev + DB)
```bash
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

### Health Check
Container includes health check:
```bash
docker ps  # HEALTH column shows status
```

---

## 🚀 Production Checklist

- [ ] Use Gunicorn (4+ workers) instead of Flask dev server
- [ ] Change `SECRET_KEY` in config
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/TLS (use nginx or load balancer)
- [ ] Set `UPLOAD_API_KEY` for secure uploads
- [ ] Configure file size limits for your use case
- [ ] Set up database if using Docker Compose
- [ ] Configure log rotation
- [ ] Monitor disk space (uploads accumulate)
- [ ] Backup `conversion_history.db` regularly

**Production run:**
```bash
gunicorn --workers=8 --bind=0.0.0.0:5000 app.main:app
```

---

## 🔄 CI/CD Pipeline

GitHub Actions configured in `.github/workflows/python-tests.yml`:

- Tests on Python 3.8, 3.9, 3.10, 3.11
- Linting with flake8
- Coverage reporting to Codecov
- Runs on PR and push to main/develop

See `.github/workflows/python-tests.yml` for details.

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [MIGRATION_NOTES.md](MIGRATION_NOTES.md) | Detailed architecture migration guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment steps & troubleshooting |
| [README_API_KEY.md](README_API_KEY.md) | API key setup |

---

## 🔗 Dependencies

Core libraries:
- **flask** — Web framework
- **pillow** — Image processing
- **pymupdf** (fitz) — PDF operations
- **pdfplumber** — PDF text extraction
- **openpyxl** — Excel parsing
- **reportlab** — PDF generation
- **easyocr** — Text extraction from images
- **python-docx**, **python-pptx** — Office document handling
- **opencv-python** — Image processing
- **beautifulsoup4** — HTML parsing
- **weasyprint** — CSS-to-PDF rendering

See `requirements.txt` for full list.

---

## 📝 License

[Your License Here]

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Write tests first (TDD)
3. Implement feature using the modular structure
4. Run tests: `pytest`
5. Submit PR with description

---

## 📞 Support

For issues, questions, or feature requests:
1. Check [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for architecture
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
3. Review endpoint docstrings in `app/api/routes/`
4. Open an issue with details

---

## ✨ Recent Changes (February 2026)

**Major Refactor: Monolith → Modular Package**

- ✅ Refactored 4300+ line `server.py` into `app/` package
- ✅ Organized code: routes → blueprints, services, utils
- ✅ Added Docker & docker-compose support
- ✅ Added GitHub Actions CI/CD pipeline
- ✅ Created comprehensive migration documentation
- ✅ 100% backward compatible (all endpoints unchanged)

**See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for details.**

---

**Last Updated:** February 14, 2026  
**Status:** ✅ Actively Maintained  
**Python:** 3.8+  
**Framework:** Flask 2.x
