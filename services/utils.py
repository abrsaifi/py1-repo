"""
Shared utilities and constants for conversion services.
"""

import os
import tempfile
import shutil
import time
import uuid
import json
import sqlite3
from datetime import datetime, timezone
from collections import deque
from werkzeug.utils import secure_filename
from flask import request
    
# ============================================================================
# CONSTANTS
# ============================================================================

PDF_ALLOWED_EXTENSIONS = {'pdf'}
IMAGE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'}
DOCUMENT_ALLOWED_EXTENSIONS = {'docx', 'doc'}
EXCEL_ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Directory to store chunk uploads
UPLOAD_CHUNKS_DIR = os.path.join(tempfile.gettempdir(), 'docpro_uploads')
os.makedirs(UPLOAD_CHUNKS_DIR, exist_ok=True)

# Cleanup configuration via environment
UPLOAD_CLEANUP_RETENTION = int(os.environ.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600))
UPLOAD_CLEANUP_INTERVAL = int(os.environ.get('UPLOAD_CLEANUP_INTERVAL', 3600))

PRESETS = {
    'default': {'quality': 85, 'lossless': False},
    'high': {'quality': 95, 'lossless': False},
    'low': {'quality': 60, 'lossless': False},
    'lossless': {'quality': 100, 'lossless': True}
}

# Max allowed single upload file size (bytes)
UPLOAD_MAX_FILE_SIZE = int(os.environ.get('UPLOAD_MAX_FILE_SIZE', 50 * 1024 * 1024))

# Simple in-memory rate limiting (per-IP sliding window)
RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))  # seconds
RATE_LIMIT_MAX = int(os.environ.get('RATE_LIMIT_MAX', 60))      # requests per window
_rate_limit_store = {}

# Conversion history database 
HISTORY_DB = os.path.join(os.path.dirname(__file__), '..', 'conversion_history.db')

# Store for converted files (file_id -> {path, filename, expires})
_converted_files_store = {}
_FILES_EXPIRE_AFTER = 3600  # 1 hour

# EasyOCR reader (lazy-loaded)
_EASYOCR_READER = None

# Flask app reference (will be set by server.py)
_app = None

def set_app(app):
    """Set the Flask app instance for use in utilities."""
    global _app
    _app = app

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename, file_type=None):
    """Check if file extension is allowed for the given type."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'pdf':
        return ext in PDF_ALLOWED_EXTENSIONS
    elif file_type == 'image':
        return ext in IMAGE_ALLOWED_EXTENSIONS
    elif file_type == 'document':
        return ext in DOCUMENT_ALLOWED_EXTENSIONS
    elif file_type == 'excel':
        return ext in EXCEL_ALLOWED_EXTENSIONS
    # If no specific type requested, allow common extensions
    return ext in (PDF_ALLOWED_EXTENSIONS | IMAGE_ALLOWED_EXTENSIONS | DOCUMENT_ALLOWED_EXTENSIONS | EXCEL_ALLOWED_EXTENSIONS)


def sanitize_filename(name: str) -> str:
    """Sanitize and limit filename length for safe local storage."""
    try:
        if not name:
            return ''
        safe = secure_filename(name)
        if not safe:
            # Fallback: hex of uuid
            return uuid.uuid4().hex
        # Limit length to avoid very long filesystem names
        if len(safe) > 200:
            base, dot, ext = safe.rpartition('.')
            if dot and ext:
                safe = base[:180] + '.' + ext[:18]
            else:
                safe = safe[:200]
        return safe
    except Exception:
        return uuid.uuid4().hex


def validate_image_file(path):
    """Basic server-side validation: ensure file is a readable image and extension allowed."""
    from PIL import Image
    try:
        if not os.path.exists(path):
            return False, 'file_missing'
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext not in IMAGE_ALLOWED_EXTENSIONS:
            return False, 'bad_extension'
        # Try opening with Pillow
        with Image.open(path) as im:
            im.verify()
        return True, ''
    except Exception as e:
        return False, str(e)


def parse_page_numbers(pages_input):
    """Parse page numbers from user input string
    
    Accepts formats like: "1, 3, 5-8, 10-15" or "1 3 5-8 10-15"
    Returns a list of 0-indexed page numbers
    Returns None if input is empty or invalid
    """
    if not pages_input or not pages_input.strip():
        return None
    
    pages = set()
    
    # Split by comma or space
    import re
    tokens = re.split(r'[,\s]+', pages_input.strip())
    
    for token in tokens:
        if not token:
            continue
        
        if '-' in token:
            # Range like "5-8"
            try:
                parts = token.split('-')
                if len(parts) == 2:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    # Convert to 0-indexed
                    for page in range(start - 1, end):
                        if page >= 0:
                            pages.add(page)
            except:
                continue
        else:
            # Single page number
            try:
                page = int(token.strip())
                # Convert to 0-indexed
                if page > 0:
                    pages.add(page - 1)
            except:
                continue
    
    return sorted(list(pages)) if pages else None


def get_easyocr_reader():
    """Get lazy-loaded EasyOCR reader instance."""
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        try:
            import easyocr
            if easyocr is None:
                return None
            _EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
        except Exception:
            _EASYOCR_READER = None
    return _EASYOCR_READER


def is_rate_limited():
    """Return True if the current request should be rate-limited.

    Uses `request.remote_addr` or `X-Forwarded-For` header when present.
    """
    try:
        # Prefer X-Forwarded-For when behind a proxy
        addr = request.headers.get('X-Forwarded-For', '')
        if addr:
            ip = addr.split(',')[0].strip()
        else:
            ip = request.remote_addr or 'unknown'
        now = time.time()
        dq = _rate_limit_store.get(ip)
        if dq is None:
            dq = deque()
            _rate_limit_store[ip] = dq
        # pop old timestamps
        while dq and dq[0] <= now - RATE_LIMIT_WINDOW:
            dq.popleft()
        if len(dq) >= RATE_LIMIT_MAX:
            return True
        dq.append(now)
        return False
    except Exception:
        return False


def _check_api_key(app):
    """Optional API key check. Set `app.config['UPLOAD_API_KEY']` to enable."""
    key = app.config.get('UPLOAD_API_KEY')
    if not key:
        return True
    provided = request.headers.get('X-API-Key') or request.args.get('api_key')
    return provided == key


def cleanup_old_upload_dirs(retention_seconds=24 * 3600, interval_seconds=3600):
    """Background task to clean up old upload directories."""
    import time
    while True:
        try:
            now = time.time()
            for name in os.listdir(UPLOAD_CHUNKS_DIR):
                path = os.path.join(UPLOAD_CHUNKS_DIR, name)
                try:
                    mtime = os.path.getmtime(path)
                    if now - mtime > retention_seconds:
                        shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(interval_seconds)


def init_history_db():
    """Initialize conversion history database."""
    try:
        conn = sqlite3.connect(HISTORY_DB)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                operation TEXT,
                files TEXT,
                status TEXT,
                message TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception:
        pass


def log_history(operation, files, status='success', message=''):
    """Log conversion history to database."""
    try:
        conn = sqlite3.connect(HISTORY_DB)
        c = conn.cursor()
        c.execute('INSERT INTO history (timestamp, operation, files, status, message) VALUES (?, ?, ?, ?, ?)',
                  (datetime.now(timezone.utc).isoformat(), operation, json.dumps(files), status, message))
        conn.commit()
        conn.close()
    except Exception:
        # Don't let history logging break the main flow
        pass
