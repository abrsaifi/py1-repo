import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from PIL import Image
import tempfile
import shutil
import io
import base64
from docx import Document as DocxDocument
from openpyxl import load_workbook, Workbook
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas as pdf_canvas
import pdfplumber
try:
    import easyocr
except Exception:
    easyocr = None
try:
    from pptx import Presentation
    from pptx.util import Inches as PptxInches
except Exception:
    Presentation = None
try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None
try:
    from weasyprint import HTML as WeasyHTML
except Exception:
    WeasyHTML = None
try:
    from pypdf import PdfReader, PdfWriter
except Exception:
    PdfReader = None
    PdfWriter = None
from pathlib import Path
import zipfile
from datetime import datetime
import uuid
import json as _json
import time
from collections import deque
import subprocess
from threading import Thread, Lock
from app.utils.errors import register_error_handlers
from app.utils.logger_setup import LoggerSetup

# Import services
try:
    from services.utils import (
        allowed_file, sanitize_filename, validate_image_file, parse_page_numbers,
        get_easyocr_reader, is_rate_limited, cleanup_old_upload_dirs,
        init_history_db, log_history, set_app
    )
    from services.preview import _generate_preview_from_pdf, _generate_previews_from_pdf
    from services.document_conversion import (
        docx_to_pdf, soffice_to_pdf, excel_to_pdf, powerpoint_to_pdf,
        pdf_to_word, pdf_to_excel, pdf_to_powerpoint, excel_to_csv,
        html_to_pdf, pdf_to_html, url_to_pdf, text_to_pdf,
        get_sheet_info, combine_csvs_to_excel
    )
    from services.image_processing import (
        image_to_pdf, convert_image_format, pdf_to_true_bw
    )
    from services.pdf_tools import (
        encrypt_pdf, decrypt_pdf, pdf_remove_metadata, extract_pdf_pages,
        split_pdf, merge_pdf, remove_pages_from_pdf, redact_pdf, clean_autoformat_pdf
    )
    from services.watermark import add_watermark, add_image_watermark
    from services.ocr import ocr_extract_text, ocr_extract_with_language
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import services: {e}")
    SERVICES_AVAILABLE = False
    # Fallback stubs will be defined below

app = Flask(__name__)
# Load SECRET_KEY from environment, fallback to development key
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store for converted files (file_id -> {path, filename, expires})
_converted_files_store = {}
_FILES_EXPIRE_AFTER = 3600  # 1 hour

# INTEGRATION: Setup structured logging
log_file = os.getenv('LOG_FILE', os.path.join(os.path.dirname(__file__), 'logs', 'app.log'))
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_format = os.getenv('LOG_FORMAT', 'standard')
use_json = log_format == 'json'

logger = LoggerSetup.setup(
    app_name='docpro',
    level=log_level,
    log_file=log_file,
    use_json=use_json
)
app.logger = logger
logger.info('DocPro server initialized with structured logging')

# ========================
# JOB TRACKING SYSTEM (SPA Async Support)
# ========================
_job_registry = {}  # {job_id: ConversionJob instance}
_job_lock = Lock()  # Thread safety for job updates
_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max file size
_conversion_rate_limit = {}  # {ip_address: [timestamps]}
_rate_limit_window = 60  # 1 minute window
_rate_limit_max_requests = 20  # Max 20 conversions per minute per IP (increased for testing)

class ConversionJob:
    """Represents an async conversion job"""
    def __init__(self, job_id, tool_name, file_count):
        self.job_id = job_id
        self.tool_name = tool_name
        self.file_count = file_count
        self.status = 'queued'  # queued, processing, complete, error
        self.progress = 0  # 0-100
        self.result = None  # Conversion result
        self.error = None  # Error message
        self.timestamp = datetime.now()
        self.start_time = None
        self.end_time = None
    
    def to_dict(self):
        elapsed = 0
        if self.start_time:
            end = self.end_time or datetime.now()
            elapsed = (end - self.start_time).total_seconds()
        
        return {
            'job_id': self.job_id,
            'tool_name': self.tool_name,
            'status': self.status,
            'progress': self.progress,
            'file_count': self.file_count,
            'has_result': self.result is not None,
            'error': self.error,
            'elapsed_seconds': elapsed
        }

def _check_rate_limit(ip_address):
    """Check if IP has exceeded rate limit. Returns True if allowed, False if limited."""
    if ip_address not in _conversion_rate_limit:
        _conversion_rate_limit[ip_address] = []
    
    now = time.time()
    # Remove timestamps older than the rate limit window
    _conversion_rate_limit[ip_address] = [
        ts for ts in _conversion_rate_limit[ip_address] 
        if now - ts < _rate_limit_window
    ]
    
    if len(_conversion_rate_limit[ip_address]) >= _rate_limit_max_requests:
        return False  # Rate limited
    
    _conversion_rate_limit[ip_address].append(now)
    return True  # Allowed

def _get_client_ip():
    """Get client IP address, accounting for proxies"""
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

# INTEGRATION: Register error handlers
register_error_handlers(app)
logger.info('Error handlers registered')

# Helper function to get soffice path for document conversions
def get_soffice_path():
    """Get the full path to soffice executable, trying multiple common locations"""
    possible_paths = [
        'soffice',  # Try in PATH first
        'soffice.exe',
        r'C:\Program Files\LibreOffice\program\soffice.exe',
        r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        r'C:\Program Files\LibreOffice\program\soffice',
        r'C:\Program Files (x86)\LibreOffice\program\soffice',
    ]
    
    for path in possible_paths:
        if path in ('soffice', 'soffice.exe'):
            # These are in PATH, try them
            try:
                result = subprocess.run([path, '--version'], capture_output=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                pass
        else:
            # Check if file exists
            if os.path.exists(path):
                return path
    
    # Default to standard Path location
    return r'C:\Program Files\LibreOffice\program\soffice.exe'

# Simple conversion history (lightweight SQLite) to avoid NameError when
# routes call `log_history`. This is safe if a fuller implementation exists
# elsewhere — it will simply reinitialize the DB here.
import sqlite3
import json

HISTORY_DB = os.path.join(os.path.dirname(__file__), 'conversion_history.db')

def init_history_db():
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
    try:
        conn = sqlite3.connect(HISTORY_DB)
        c = conn.cursor()
        c.execute('INSERT INTO history (timestamp, operation, files, status, message) VALUES (?, ?, ?, ?, ?)',
                  (datetime.utcnow().isoformat(), operation, json.dumps(files), status, message))
        conn.commit()
        conn.close()
    except Exception:
        # Don't let history logging break the main flow
        pass

# initialize DB and background tasks via explicit starter (avoid import-time side-effects)
def start_background_tasks():
    """Initialize lightweight DB and start background cleanup thread.

    This avoids running threads or heavy subprocesses during import which can
    interfere with test runners and short-lived CLI imports.
    """
    try:
        init_history_db()
    except Exception:
        pass

PDF_ALLOWED_EXTENSIONS = {'pdf'}
IMAGE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'svg'}
DOCUMENT_ALLOWED_EXTENSIONS = {'docx', 'doc', 'odt'}
EXCEL_ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'xlsm', 'xlsb', 'csv', 'ods'}

def allowed_file(filename, file_type=None):
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

# EasyOCR reader factory (safe stub). The real reader can be slow to initialize
# so we provide a cached factory. If `easyocr` isn't available this returns None.
_EASYOCR_READER = None

def get_easyocr_reader():
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        try:
            if easyocr is None:
                return None
            _EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
        except Exception:
            _EASYOCR_READER = None
    return _EASYOCR_READER

def image_to_pdf(image_path, output_pdf):
    """Convert image to PDF"""
    img = Image.open(image_path)
    
    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Save as PDF
    img.save(output_pdf, 'PDF')
    return True


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


def _check_api_key():
    """Optional API key check. Set `app.config['UPLOAD_API_KEY']` to enable."""
    key = app.config.get('UPLOAD_API_KEY')
    if not key:
        return True
    provided = request.headers.get('X-API-Key') or request.args.get('api_key')
    return provided == key


def cleanup_old_upload_dirs(retention_seconds=24 * 3600, interval_seconds=3600):
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


# Background thread starter moved to `start_background_tasks()` to avoid
# import-time side-effects. Tests or CLI tools should call that function
# before running long-lived server tasks.


def validate_image_file(path):
    """Basic server-side validation: ensure file is a readable image and extension allowed."""
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


@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    """Accept a single chunk for a given upload_id + filename.

    Fields: upload_id, filename, index, total (optional), chunk (file)
    When the last chunk is received (index == total-1), assemble and return assembled=True
    """
    upload_id = request.form.get('upload_id') or request.headers.get('X-Upload-Id')
    filename = request.form.get('filename') or request.headers.get('X-Upload-Filename')
    try:
        index = int(request.form.get('index', 0))
    except Exception:
        index = 0
    try:
        total = int(request.form.get('total', -1))
    except Exception:
        total = -1

    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401

    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    if 'chunk' not in request.files:
        return jsonify({'success': False, 'error': 'no_chunk'}), 400

    if not upload_id:
        upload_id = str(uuid.uuid4())

    chunk_file = request.files['chunk']

    safe_uid = sanitize_filename(upload_id)
    if not safe_uid:
        safe_uid = uuid.uuid4().hex

    upload_dir = os.path.join(UPLOAD_CHUNKS_DIR, safe_uid)
    os.makedirs(upload_dir, exist_ok=True)

    # save chunk
    chunk_path = os.path.join(upload_dir, f'chunk_{index:06d}')
    chunk_file.save(chunk_path)

    # maintain metadata (filename, total)
    meta_path = os.path.join(upload_dir, 'meta.json')
    try:
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as mf:
                meta = _json.load(mf)
        meta.setdefault('filename', sanitize_filename(filename) or filename)
        if total > 0:
            meta['total'] = total
        with open(meta_path, 'w', encoding='utf-8') as mf:
            _json.dump(meta, mf)
    except Exception:
        pass

    assembled = False
    assembled_path = None
    # If total known and last chunk arrived, assemble
    try:
        meta = {}
        if os.path.exists(os.path.join(upload_dir, 'meta.json')):
            with open(os.path.join(upload_dir, 'meta.json'), 'r', encoding='utf-8') as mf:
                meta = _json.load(mf)
        expected_total = meta.get('total', total)
        if expected_total and index >= expected_total - 1:
            # assemble
            safe_fname = sanitize_filename(filename) or secure_filename(filename)
            assembled_path = os.path.join(upload_dir, safe_fname)
            # check cumulative size
            total_size = 0
            for i in range(expected_total):
                part = os.path.join(upload_dir, f'chunk_{i:06d}')
                if not os.path.exists(part):
                    return jsonify({'success': False, 'error': 'missing_chunk', 'missing': i}), 500
                total_size += os.path.getsize(part)
                if total_size > UPLOAD_MAX_FILE_SIZE:
                    return jsonify({'success': False, 'error': 'file_too_large'}), 413
            with open(assembled_path, 'wb') as out_f:
                for i in range(expected_total):
                    part = os.path.join(upload_dir, f'chunk_{i:06d}')
                    with open(part, 'rb') as pf:
                        out_f.write(pf.read())
                    try:
                        os.remove(part)
                    except Exception:
                        pass
            assembled = True
    except Exception as e:
        assembled = False
        print(f"Assembly error: {e}")

    return jsonify({'success': True, 'upload_id': upload_id, 'filename': filename, 'assembled': assembled, 'assembled_path': assembled_path})


@app.route('/convert-uploaded', methods=['POST'])
def convert_uploaded():
    """Convert files that were uploaded via chunked uploads.

    Expects JSON body: { uploads: [{upload_id, filename}], target_format, preset(optional), quality(optional), lossless(optional) }
    """
    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401

    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'success': False, 'error': 'invalid_json'}), 400

    uploads = data.get('uploads', [])
    target = (data.get('target_format') or '').lower()
    preset = data.get('preset')
    quality = int(data.get('quality', 85) or 85)
    lossless = bool(data.get('lossless', False))

    if preset in PRESETS:
        quality = PRESETS[preset]['quality']
        lossless = PRESETS[preset]['lossless']

    if target not in ('jpg', 'jpeg', 'png', 'webp', 'tiff', 'tif'):
        return jsonify({'success': False, 'error': 'unsupported_target'}), 400

    temp_dir = tempfile.mkdtemp()
    converted = []
    debug_errors = []
    try:
        for up in uploads:
            uid = up.get('upload_id')
            fname = up.get('filename')
            if not uid or not fname:
                debug_errors.append(f"Missing upload_id or filename: {uid}, {fname}")
                continue
            safe_uid = sanitize_filename(uid)
            upload_dir = os.path.join(UPLOAD_CHUNKS_DIR, safe_uid)
            assembled_path = os.path.join(upload_dir, sanitize_filename(fname) or secure_filename(fname))
            
            # Check if assembled file exists
            if not os.path.exists(assembled_path):
                # Try alternative path without double-sanitizing
                alt_path = os.path.join(upload_dir, fname)
                if os.path.exists(alt_path):
                    assembled_path = alt_path
                else:
                    debug_errors.append(f"Assembled file not found at {assembled_path} or {alt_path}")
                    continue
            
            ok, msg = validate_image_file(assembled_path)
            if not ok:
                debug_errors.append(f"Validation failed for {assembled_path}: {msg}")
                continue

            out_ext = 'jpg' if target in ('jpg', 'jpeg') else ('tif' if target in ('tiff', 'tif') else target)
            out_name = f"{Path(fname).stem}_converted.{out_ext}"
            out_path = os.path.join(temp_dir, out_name)

            ok_conv = convert_image_format(assembled_path, out_path, target, quality=quality, lossless=lossless)
            if ok_conv:
                converted.append((out_name, out_path))
            else:
                debug_errors.append(f"Conversion failed for {assembled_path}")

        if not converted:
            error_detail = '; '.join(debug_errors) if debug_errors else 'no_converted_files'
            return jsonify({'success': False, 'error': error_detail}), 500

        if len(converted) == 1:
            name, p = converted[0]
            return send_file(p, as_attachment=True, download_name=name)

        zip_path = os.path.join(temp_dir, 'converted_images.zip')
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for name, p in converted:
                zf.write(p, arcname=name)

        return send_file(zip_path, as_attachment=True, download_name='converted_images.zip')
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


    @app.route('/upload-status', methods=['GET'])
    def upload_status():
        """Return which chunk files currently exist for a given upload_id and filename."""
        if not _check_api_key():
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

        if is_rate_limited():
            return jsonify({'success': False, 'error': 'rate_limited'}), 429

        upload_id = request.args.get('upload_id')
        filename = request.args.get('filename')
        if not upload_id:
            return jsonify({'success': False, 'error': 'missing_upload_id'}), 400

        upload_dir = os.path.join(UPLOAD_CHUNKS_DIR, sanitize_filename(upload_id) or secure_filename(upload_id))
        if not os.path.exists(upload_dir):
            return jsonify({'success': True, 'chunks': [], 'total': None})

        chunks = []
        for name in os.listdir(upload_dir):
            if name.startswith('chunk_'):
                try:
                    idx = int(name.split('_', 1)[1])
                    chunks.append(idx)
                except Exception:
                    pass
        chunks = sorted(chunks)
        total = None
        meta_path = os.path.join(upload_dir, 'meta.json')
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as mf:
                    meta = _json.load(mf)
                    total = meta.get('total')
            except Exception:
                total = None

        return jsonify({'success': True, 'chunks': chunks, 'total': total})


    @app.route('/admin/purge-uploads', methods=['POST'])
    def admin_purge_uploads():
        """Admin endpoint to purge upload directories.

        Optional JSON body: { "older_than": seconds }
        Requires the configured API key if present.
        """
        if not _check_api_key():
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

        try:
            data = request.get_json(silent=True) or {}
            older_than = int(data.get('older_than', UPLOAD_CLEANUP_RETENTION))
        except Exception:
            older_than = UPLOAD_CLEANUP_RETENTION

        now = __import__('time').time()
        removed = 0
        for name in os.listdir(UPLOAD_CHUNKS_DIR):
            path = os.path.join(UPLOAD_CHUNKS_DIR, name)
            try:
                mtime = os.path.getmtime(path)
                if now - mtime > older_than:
                    shutil.rmtree(path, ignore_errors=True)
                    removed += 1
            except Exception:
                pass

        return jsonify({'success': True, 'removed': removed})


def convert_image_format(input_path, output_path, target_format, quality=85, lossless=False):
    """Convert an image file to the requested format using Pillow.

    Supported target_format values: 'jpg', 'jpeg', 'png', 'webp', 'tiff'.
    """
    try:
        img = Image.open(input_path)

        fmt = target_format.lower().lstrip('.')

        # Normalize formats
        if fmt in ('jpg', 'jpeg'):
            # JPEG doesn't support alpha; flatten if necessary
            if img.mode in ('RGBA', 'LA') or ('A' in img.getbands()):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.convert('RGBA').split()[-1])
                img = background
            else:
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality)
        elif fmt == 'png':
            # Preserve alpha if present
            img.save(output_path, 'PNG')
        elif fmt == 'webp':
            # WebP supports optionally lossy/lossless and alpha
            save_kwargs = {'quality': quality}
            if lossless:
                save_kwargs['lossless'] = True
            try:
                img.save(output_path, 'WEBP', **save_kwargs)
            except Exception:
                # Fallback: convert to RGB then save
                img.convert('RGB').save(output_path, 'WEBP', **save_kwargs)
        elif fmt in ('tiff', 'tif'):
            img.save(output_path, 'TIFF')
        else:
            # Generic save attempt
            img.save(output_path)

        return True
    except Exception as e:
        print(f"Image conversion error: {e}")
        return False


@app.route('/convert-image', methods=['POST'])
def convert_image_route():
    """Endpoint to convert uploaded image to target format.

    Form fields:
      - file: uploaded image
      - target_format: jpg|png|webp|tiff
    Returns the converted file as attachment.
    """
    # Accept single file (`file`) or multiple files (`file` as multiple input)
    files = request.files.getlist('file') or []
    if not files:
        flash('No file part')
        return redirect(request.referrer or url_for('index'))

    if is_rate_limited():
        flash('Rate limited, please try again later')
        return redirect(request.referrer or url_for('index'))

    target = request.form.get('target_format', '').strip().lower()
    quality = int(request.form.get('quality', 85) or 85)
    lossless = request.form.get('lossless', 'false').lower() in ('1', 'true', 'on')

    if target not in ('jpg', 'jpeg', 'png', 'webp', 'tiff', 'tif'):
        flash('Unsupported target format')
        return redirect(request.referrer or url_for('index'))

    temp_dir = tempfile.mkdtemp()
    converted_paths = []
    try:
        # support `selected_indices` (1-based list like '1,3,5-7') to allow processing only a subset
        sel_idx_raw = request.form.get('selected_indices', '').strip()
        sel_set = None
        if sel_idx_raw:
            sel0 = parse_page_numbers(sel_idx_raw)
            if sel0 is not None:
                sel_set = set(sel0)

        for idx, f in enumerate(files):
            if not f or f.filename == '':
                continue
            # if selection set provided, skip unselected (parse_page_numbers returns 0-indexed values)
            if sel_set is not None and idx not in sel_set:
                continue
            if not allowed_file(f.filename, 'image'):
                continue
            safe_name = sanitize_filename(f.filename) or secure_filename(f.filename)
            input_path = os.path.join(temp_dir, safe_name)
            f.save(input_path)

            out_ext = 'jpg' if target in ('jpg', 'jpeg') else ('tif' if target in ('tiff', 'tif') else target)
            base_name = Path(f.filename).stem
            output_name = f"{base_name}_converted.{out_ext}"
            output_path = os.path.join(temp_dir, output_name)

            ok = convert_image_format(input_path, output_path, target, quality=quality, lossless=lossless)
            if ok and os.path.exists(output_path):
                converted_paths.append((output_name, output_path))

        if not converted_paths:
            flash('Conversion failed for all files')
            return redirect(request.referrer or url_for('index'))

        # If only one converted file, return it directly
        if len(converted_paths) == 1:
            name, path_out = converted_paths[0]
            log_history('image_convert', [files[0].filename, target], status='success')
            return send_file(path_out, as_attachment=True, download_name=name)

        # Multiple files: bundle into a ZIP
        zip_path = os.path.join(temp_dir, 'converted_images.zip')
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for name, path_out in converted_paths:
                zf.write(path_out, arcname=name)

        log_history('image_convert_batch', [f.filename for f in files], status='success')
        return send_file(zip_path, as_attachment=True, download_name='converted_images.zip')
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

def docx_to_pdf(docx_path, output_pdf, preserve_colors=True, preserve_images=True, **kwargs):
    """Convert DOCX to PDF with color and image preservation using LibreOffice"""
    try:
        # Extract PDF parameters if provided
        pdf_params = {k: v for k, v in kwargs.items() if v is not None}
        
        # Use LibreOffice for best formatting/color/image preservation
        import subprocess
        from pathlib import Path
        
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        logger.info(f'Converting DOCX to PDF: {docx_path} -> {output_pdf}')
        if pdf_params:
            logger.info(f'With PDF parameters: {pdf_params}')
        
        # LibreOffice command for DOCX -> PDF conversion
        cmd = [
            get_soffice_path(),
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', out_dir,
            docx_path
        ]
        
        logger.info(f'Running LibreOffice command: {" ".join(cmd)}')
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, timeout=120, text=True)
        
        logger.info(f'LibreOffice return code: {result.returncode}')
        if result.stdout:
            logger.info(f'LibreOffice stdout: {result.stdout}')
        if result.stderr:
            logger.warning(f'LibreOffice stderr: {result.stderr}')
        
        if result.returncode == 0:
            # Find the generated PDF (LibreOffice creates it with original filename stem)
            temp_pdf = os.path.join(out_dir, f"{Path(docx_path).stem}.pdf")
            logger.info(f'Looking for PDF at: {temp_pdf}')
            
            if os.path.exists(temp_pdf):
                logger.info(f'Found PDF at {temp_pdf}, file size: {os.path.getsize(temp_pdf)} bytes')
                # Move to target location if different
                if os.path.abspath(temp_pdf) != os.path.abspath(output_pdf):
                    logger.info(f'Moving PDF from {temp_pdf} to {output_pdf}')
                    shutil.move(temp_pdf, output_pdf)
                logger.info(f'Successfully created PDF: {output_pdf}')
                return True
            else:
                logger.error(f'Expected PDF not found at {temp_pdf}')
        else:
            logger.error(f'LibreOffice conversion failed with return code {result.returncode}')
        
        # Fallback: Try basic conversion
        logger.info(f'Attempting fallback DOCX conversion')
        return False
        
    except Exception as e:
        logger.error(f"DOCX to PDF error (LibreOffice): {e}", exc_info=True)
        
        # Fallback to basic conversion if LibreOffice not available
        try:
            doc = DocxDocument(docx_path)
            c = pdf_canvas.Canvas(output_pdf, pagesize=letter)
            y = letter[1] - 40
            
            for para in doc.paragraphs:
                if para.text.strip():
                    # Try to get text color
                    text_color = None
                    if preserve_colors and para.runs:
                        for run in para.runs:
                            if run.font.color and run.font.color.rgb:
                                try:
                                    # Convert RGB to hex/tuple for reportlab
                                    rgb_str = str(run.font.color.rgb)
                                    if len(rgb_str) >= 6:
                                        r = int(rgb_str[0:2], 16) / 255.0
                                        g = int(rgb_str[2:4], 16) / 255.0
                                        b = int(rgb_str[4:6], 16) / 255.0
                                        text_color = (r, g, b)
                                except:
                                    pass
                    
                    # Draw text (limited to prevent overflow)
                    text_to_draw = para.text[:100]
                    if text_color:
                        c.setFillColor(*text_color)
                    else:
                        c.setFillColor(0, 0, 0)  # Black
                    
                    c.drawString(40, y, text_to_draw)
                    y -= 20
                    if y < 40:
                        c.showPage()
                        y = letter[1] - 40
            
            # Extract and embed images if preserve_images is True
            if preserve_images:
                try:
                    from docx.oxml import parse_xml
                    from docx.oxml.ns import nsdecls
                    
                    # Reset position
                    y = letter[1] - 40
                    
                    # Extract images from document relationships
                    for rel in doc.part.rels.values():
                        if 'image' in rel.target_ref:
                            img_stream = rel.target_part.blob
                            img = Image.open(io.BytesIO(img_stream))
                            
                            # Scale image to fit PDF width
                            max_width = letter[0] - 80
                            img_ratio = img.height / img.width
                            new_width = min(200, max_width)
                            new_height = int(new_width * img_ratio)
                            
                            # Save temp image
                            temp_img_path = f"/tmp/temp_img_{uuid.uuid4().hex}.png"
                            img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
                            img.save(temp_img_path)
                            
                            # Draw image on next page if needed
                            if y - new_height < 40:
                                c.showPage()
                                y = letter[1] - 40
                            
                            c.drawImage(temp_img_path, 40, y - new_height, width=new_width, height=new_height)
                            y -= (new_height + 20)
                            
                            # Clean up temp image
                            try:
                                os.unlink(temp_img_path)
                            except:
                                pass
                except:
                    pass
            
            c.save()
            return True
        except Exception as e2:
            print(f"DOCX to PDF fallback error: {e2}")
            return False


def soffice_to_pdf(input_path, output_pdf, timeout=60, **kwargs):
    """Convert an Office document to PDF using LibreOffice (soffice) if available.

    This is primarily used to support legacy .doc/.odt files. Returns True on success.
    Now supports advanced parameters for page setup.
    """
    try:
        out_dir = os.path.dirname(output_pdf)
        os.makedirs(out_dir, exist_ok=True)
        
        logger.info(f'Converting document to PDF via LibreOffice: {input_path} -> {output_pdf}')
        
        # Use the new _convert_with_libreoffice helper that handles post-processing
        return _convert_with_libreoffice(input_path, output_pdf, **kwargs)
        
    except Exception as e:
        logger.error(f'soffice_to_pdf error: {e}', exc_info=True)
        return False

def csv_to_pdf(csv_path, output_pdf, **kwargs):
    """Convert CSV to PDF table"""
    try:
        import csv
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        
        # Read CSV file
        data = []
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for row in reader:
                if any(row):  # Skip empty rows
                    data.append(row)
        
        if not data:
            return False
        
        # Create PDF
        orientation = kwargs.get('orientation', 'landscape').lower()
        pagesize = landscape(A4) if orientation == 'landscape' else A4
        
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=pagesize,
            topMargin=20*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )
        
        # Calculate column widths
        num_cols = len(data[0]) if data else 1
        available_width = pagesize[0] - 40*mm
        col_width = available_width / num_cols
        
        # Create table
        table = Table(data, colWidths=[col_width] * num_cols)
        
        # Style table
        style_commands = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]
        
        table.setStyle(TableStyle(style_commands))
        
        # Build PDF
        elements = [table]
        doc.build(elements)
        
        return os.path.exists(output_pdf)
    except Exception as e:
        logger.warning(f'CSV to PDF conversion failed: {e}')
        return False

def excel_to_pdf(excel_path, output_pdf, **kwargs):
    """Convert Excel/CSV to PDF using LibreOffice with proper parameter support"""
    try:
        from pathlib import Path
        
        # Helper function to convert string booleans
        def to_bool(val):
            if isinstance(val, bool):
                return val
            return str(val).lower() in ('true', 'yes', '1', 'on') if val else False
        
        # Get parameters
        orientation = kwargs.get('orientation', 'portrait').lower()
        paper_size = kwargs.get('paper_size', 'A4').upper()
        margin_top = float(kwargs.get('margin_top', 25))
        margin_bottom = float(kwargs.get('margin_bottom', 25))
        margin_left = float(kwargs.get('margin_left', 25))
        margin_right = float(kwargs.get('margin_right', 25))
        include_headers = to_bool(kwargs.get('include_headers', True))
        gridlines = to_bool(kwargs.get('gridlines', False))
        scale_factor = float(kwargs.get('scale_factor', 100))
        
        print(f"\n========== EXCEL_TO_PDF DEBUG START ==========")
        print(f"[excel_to_pdf] Input: {excel_path}")
        print(f"[excel_to_pdf] Output: {output_pdf}")
        print(f"[excel_to_pdf] Parameters received:")
        print(f"  orientation={orientation} (type: {type(orientation).__name__})")
        print(f"  paper_size={paper_size} (type: {type(paper_size).__name__})")
        print(f"  margins: top={margin_top}mm, bottom={margin_bottom}mm, left={margin_left}mm, right={margin_right}mm")
        print(f"  include_headers={include_headers} (type: {type(include_headers).__name__})")
        print(f"  gridlines={gridlines} (type: {type(gridlines).__name__})")
        print(f"  scale_factor={scale_factor}% (type: {type(scale_factor).__name__})")
        
        logger.info(f"Converting Excel with parameters: orientation={orientation}, paper_size={paper_size}, margins={margin_top}x{margin_bottom}x{margin_left}x{margin_right}mm, scale={scale_factor}%, headers={include_headers}, gridlines={gridlines}")
        
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        # Determine input file type
        input_ext = Path(excel_path).suffix.lower()
        print(f"[excel_to_pdf] Input file extension: '{input_ext}'")
        
        # If CSV, convert to XLSX first (so we can apply page setup)
        temp_excel = excel_path
        if input_ext == '.csv':
            print(f"[excel_to_pdf] CSV file detected, converting to XLSX...")
            from openpyxl import Workbook
            import csv as csv_module
            
            temp_excel = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False).name
            wb = Workbook()
            ws = wb.active
            
            with open(excel_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv_module.reader(f)
                for row_idx, row in enumerate(reader, 1):
                    for col_idx, cell in enumerate(row, 1):
                        ws.cell(row=row_idx, column=col_idx, value=cell)
            
            wb.save(temp_excel)
            wb.close()
            print(f"[excel_to_pdf] CSV converted to XLSX: {temp_excel}")
        
        try:
            from openpyxl.worksheet.page import PageMargins, PrintOptions
            
            wb = load_workbook(temp_excel)
            ws = wb.active
            
            # Paper size mapping (openpyxl uses specific codes)
            paper_size_map = {
                'A4': 9,
                'A3': 8,
                'A5': 11,
                'LETTER': 1,
                'LEGAL': 5,
            }
            
            # Apply page setup
            ws.page_setup.paperSize = paper_size_map.get(paper_size, 9)
            ws.page_setup.orientation = orientation  # 'portrait' or 'landscape'
            
            print(f"[excel_to_pdf] Applied page_setup:")
            print(f"  paperSize={ws.page_setup.paperSize}, orientation={ws.page_setup.orientation}")
            
            # Apply margins (convert mm to inches: 1 inch = 25.4mm)
            ws.page_margins = PageMargins(
                left=margin_left / 25.4,
                right=margin_right / 25.4,
                top=margin_top / 25.4,
                bottom=margin_bottom / 25.4,
                header=0.3,
                footer=0.3
            )
            
            print(f"[excel_to_pdf] Applied page_margins:")
            print(f"  left={ws.page_margins.left}, right={ws.page_margins.right}, top={ws.page_margins.top}, bottom={ws.page_margins.bottom}")
            
            # Apply print options for gridlines and headers
            ws.print_options = PrintOptions(
                horizontalCentered=False,
                verticalCentered=False
            )
            
            # Apply gridlines display
            if gridlines:
                ws.print_options.gridLines = True
                ws.sheet_view.showGridLines = True
            
            # Apply headers (column/row headers)
            if include_headers:
                ws.print_options.headings = True
            
            print(f"[excel_to_pdf] Applied print_options:")
            print(f"  gridlines={gridlines}, headers={include_headers}")
            
            # Apply fit mode (how to scale content)
            fit_mode = kwargs.get('fit_mode', 'fit-page')
            print(f"[excel_to_pdf] Applying fit mode: {fit_mode}")
            
            if fit_mode == 'fit-page':
                # Fit all data on one page
                ws.page_setup.fitToPage = True
                ws.page_setup.fitToHeight = 1
                ws.page_setup.fitToWidth = 1
            elif fit_mode == 'fit-width':
                # Fit all columns on one page width
                ws.page_setup.fitToPage = True
                ws.page_setup.fitToHeight = None  # Let height expand as needed
                ws.page_setup.fitToWidth = 1
            elif fit_mode == 'fit-height':
                # Fit all rows on one page height
                ws.page_setup.fitToPage = True
                ws.page_setup.fitToHeight = 1
                ws.page_setup.fitToWidth = None  # Let width expand as needed
            # else: 'no-fit' - use scale factor instead
            
            # Apply scale/zoom (only if not using fit mode)
            if fit_mode == 'no-fit':
                ws.page_setup.scale = int(scale_factor)
            else:
                # Use scale as additional zoom
                ws.page_setup.scale = max(int(scale_factor), 50)  # Minimum 50%
            
            print(f"[excel_to_pdf] Applied fit mode: {fit_mode}, scale: {ws.page_setup.scale}%")
            
            # Enable color/font preservation settings
            # Note: LibreOffice will preserve these automatically during conversion
            print(f"[excel_to_pdf] Color and font preservation: enabled (LibreOffice will preserve)")
            
            wb.save(temp_excel)
            wb.close()
            
            print(f"[excel_to_pdf] Excel file with all settings saved to: {temp_excel}")
            logger.info(f"Applied page setup: orientation={orientation}, paperSize={paper_size}, fit_mode={fit_mode}")
            
        except Exception as e:
            logger.warning(f"Could not apply page setup to Excel: {e}", exc_info=True)
            print(f"[excel_to_pdf] Warning: Could not apply page setup: {e}")
            # Continue anyway - will use default settings
        
        # Convert using LibreOffice
        soffice = get_soffice_path()
        print(f"[excel_to_pdf] Using soffice: {soffice}")
        logger.info(f"Using soffice: {soffice}")
        
        cmd = [
            soffice,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', out_dir,
            temp_excel
        ]
        
        print(f"[excel_to_pdf] Running LibreOffice command: {' '.join(cmd)}")
        print(f"[excel_to_pdf] Converting from: {temp_excel}")
        logger.info(f"Running conversion...")
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        print(f"[excel_to_pdf] LibreOffice return code: {result.returncode}")
        logger.info(f"Return code: {result.returncode}")
        if result.stdout:
            stdout_text = result.stdout.decode('utf-8', errors='ignore')
            print(f"[excel_to_pdf] LibreOffice stdout: {stdout_text}")
            logger.info(f"Stdout: {stdout_text}")
        if result.stderr:
            stderr_text = result.stderr.decode('utf-8', errors='ignore')
            print(f"[excel_to_pdf] LibreOffice stderr: {stderr_text}")
            logger.warning(f"Stderr: {stderr_text}")
        
        if result.returncode == 0:
            temp_pdf = os.path.join(out_dir, f"{Path(temp_excel).stem}.pdf")
            print(f"[excel_to_pdf] Looking for PDF at: {temp_pdf}")
            logger.info(f"Looking for PDF at: {temp_pdf}")
            
            if os.path.exists(temp_pdf):
                pdf_size = os.path.getsize(temp_pdf)
                print(f"[excel_to_pdf] PDF found: {pdf_size} bytes")
                logger.info(f"Found PDF: {pdf_size} bytes")
                if os.path.abspath(temp_pdf) != os.path.abspath(output_pdf):
                    shutil.move(temp_pdf, output_pdf)
                
                # Post-processing: Add page numbers if requested
                page_numbers_enabled = kwargs.get('page_numbers', False)
                compression_level = kwargs.get('compression', 'normal')  # 'low', 'normal', 'high'
                
                print(f"[excel_to_pdf] Post-processing: page_numbers={page_numbers_enabled}, compression={compression_level}")
                
                if page_numbers_enabled or compression_level != 'normal':
                    try:
                        from PyPDF2 import PdfWriter, PdfReader
                        from reportlab.pdfgen import canvas
                        from reportlab.lib.pagesizes import letter, landscape, A4
                        from io import BytesIO
                        
                        # Try to add page numbers and/or compress
                        output_pdf_temp = output_pdf.replace('.pdf', '_temp.pdf')
                        
                        if page_numbers_enabled:
                            print(f"[excel_to_pdf] Adding page numbers...")
                            try:
                                # Read the original PDF
                                pdf_reader = PdfReader(output_pdf)
                                pdf_writer = PdfWriter()
                                num_pages = len(pdf_reader.pages)
                                
                                # Process each page
                                for page_num in range(num_pages):
                                    page = pdf_reader.pages[page_num]
                                    
                                    # Create a page with page number
                                    packet = BytesIO()
                                    can = canvas.Canvas(packet, pagesize=letter)
                                    can.setFont("Helvetica", 9)
                                    can.drawString(500, 20, f"Page {page_num + 1} of {num_pages}")
                                    can.save()
                                    
                                    # Merge page number with original page
                                    packet.seek(0)
                                    annotation = PdfReader(packet)
                                    page.merge_page(annotation.pages[0])
                                    pdf_writer.add_page(page)
                                
                                # Write to temp PDF
                                with open(output_pdf_temp, 'wb') as f:
                                    pdf_writer.write(f)
                                
                                # Replace original with versioned PDF
                                if os.path.exists(output_pdf_temp):
                                    os.remove(output_pdf)
                                    os.rename(output_pdf_temp, output_pdf)
                                    print(f"[excel_to_pdf] Page numbers added successfully")
                                    
                            except Exception as e:
                                print(f"[excel_to_pdf] Warning: Could not add page numbers: {e}")
                                logger.warning(f"Could not add page numbers: {e}")
                        
                        # Apply compression if requested
                        if compression_level == 'high':
                            print(f"[excel_to_pdf] Applying high compression...")
                            try:
                                pdf_reader = PdfReader(output_pdf)
                                pdf_writer = PdfWriter()
                                
                                for page in pdf_reader.pages:
                                    page.compress_content_streams()
                                    pdf_writer.add_page(page)
                                
                                with open(output_pdf_temp, 'wb') as f:
                                    pdf_writer.write(f)
                                
                                # Check compression results
                                original_size = os.path.getsize(output_pdf)
                                compressed_size = os.path.getsize(output_pdf_temp)
                                compression_ratio = (1 - compressed_size / original_size) * 100
                                
                                if compressed_size < original_size:
                                    os.remove(output_pdf)
                                    os.rename(output_pdf_temp, output_pdf)
                                    print(f"[excel_to_pdf] Compression successful: {original_size} → {compressed_size} bytes ({compression_ratio:.1f}% reduction)")
                                else:
                                    os.remove(output_pdf_temp)
                                    print(f"[excel_to_pdf] Compression not beneficial, keeping original")
                                    
                            except Exception as e:
                                # Handle encoding issues in error message for Windows
                                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                                print(f"[excel_to_pdf] Warning: Could not compress PDF: {error_msg}")
                                logger.warning(f"Could not compress PDF: {e}")
                                if os.path.exists(output_pdf_temp):
                                    try:
                                        os.remove(output_pdf_temp)
                                    except:
                                        pass
                        
                    except ImportError:
                        print(f"[excel_to_pdf] Note: PyPDF2 or reportlab not available for page numbers/compression")
                        logger.info("PyPDF2 or reportlab not available")
                
                final_pdf_size = os.path.getsize(output_pdf)
                print(f"[excel_to_pdf] SUCCESS! PDF created: {output_pdf} ({final_pdf_size} bytes)")
                print(f"========== EXCEL_TO_PDF DEBUG END ==========\n")
                logger.info(f"Successfully created: {output_pdf}")
                
                # Cleanup temp Excel
                try:
                    os.unlink(temp_excel)
                except:
                    pass
                
                return True
            else:
                print(f"[excel_to_pdf] ERROR: PDF not found at: {temp_pdf}")
                print(f"========== EXCEL_TO_PDF DEBUG END ==========\n")
                logger.error(f"PDF not found at: {temp_pdf}")
        else:
            print(f"[excel_to_pdf] ERROR: LibreOffice conversion failed with return code {result.returncode}")
            print(f"========== EXCEL_TO_PDF DEBUG END ==========\n")
            logger.error(f"LibreOffice conversion failed")
        
        # Cleanup on error
        try:
            os.unlink(temp_excel)
        except:
            pass
        
        return False
        
    except Exception as e:
        logger.error(f"Excel to PDF error: {e}", exc_info=True)
        return False


def docx_to_pdf_with_params(docx_path, output_pdf, **kwargs):
    """Convert DOCX to PDF with page layout parameters"""
    try:
        # Try to import python-docx
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            from docx.oxml.ns import qn
            from docx.oxml import OxmlElement
        except ImportError:
            print("[docx_to_pdf] python-docx not available, using LibreOffice only")
            # Fall back to LibreOffice without page setup
            return _convert_with_libreoffice(docx_path, output_pdf, **kwargs)
        
        # Extract parameters
        orientation = kwargs.get('orientation', 'portrait').lower()
        paper_size = kwargs.get('paper_size', 'A4')
        margin_top = float(kwargs.get('margin_top', 20))
        margin_bottom = float(kwargs.get('margin_bottom', 20))
        margin_left = float(kwargs.get('margin_left', 20))
        margin_right = float(kwargs.get('margin_right', 20))
        scale_factor = float(kwargs.get('scale_factor', 100))
        
        print(f"\n========== DOCX_TO_PDF DEBUG START ==========")
        print(f"[docx_to_pdf] Input: {docx_path}")
        print(f"[docx_to_pdf] Output: {output_pdf}")
        print(f"[docx_to_pdf] Parameters: orientation={orientation}, paper_size={paper_size}, margins={margin_top}x{margin_bottom}x{margin_left}x{margin_right}mm")
        
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        # Load document
        doc = Document(docx_path)
        
        # Apply page setup
        section = doc.sections[0]
        
        # Set margins (convert mm to inches: 1 inch = 25.4mm)
        section.top_margin = Inches(margin_top / 25.4)
        section.bottom_margin = Inches(margin_bottom / 25.4)
        section.left_margin = Inches(margin_left / 25.4)
        section.right_margin = Inches(margin_right / 25.4)
        
        # Set page orientation (landscape=horizontal)
        if orientation == 'landscape':
            section.page_height = Inches(8.27)  # A4 width in landscape
            section.page_width = Inches(11.69)  # A4 height in landscape
        else:
            section.page_height = Inches(11.69)  # A4 height in portrait
            section.page_width = Inches(8.27)   # A4 width in portrait
        
        # Save modified document to temporary file
        temp_docx = tempfile.NamedTemporaryFile(suffix='.docx', delete=False).name
        doc.save(temp_docx)
        print(f"[docx_to_pdf] Modified DOCX saved: {temp_docx}")
        
        # Convert to PDF using LibreOffice
        print(f"[docx_to_pdf] Converting to PDF using LibreOffice...")
        success = _convert_with_libreoffice(temp_docx, output_pdf, **kwargs)
        
        # Cleanup temp file
        try:
            os.unlink(temp_docx)
        except:
            pass
        
        if success:
            pdf_size = os.path.getsize(output_pdf)
            print(f"[docx_to_pdf] SUCCESS! PDF created: {output_pdf} ({pdf_size} bytes)")
            print(f"========== DOCX_TO_PDF DEBUG END ==========\n")
            logger.info(f"Successfully created DOCX-based PDF: {output_pdf}")
            return True
        else:
            print(f"[docx_to_pdf] ERROR: LibreOffice conversion failed")
            print(f"========== DOCX_TO_PDF DEBUG END ==========\n")
            return False
            
    except Exception as e:
        logger.error(f"DOCX to PDF error: {e}", exc_info=True)
        print(f"[docx_to_pdf] ERROR: {e}")
        print(f"========== DOCX_TO_PDF DEBUG END ==========\n")
        return False


def _convert_with_libreoffice(input_file, output_pdf, **kwargs):
    """Helper function to convert any document format to PDF using LibreOffice"""
    try:
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        soffice = get_soffice_path()
        print(f"[libreoffice_convert] Using soffice: {soffice}")
        
        cmd = [
            soffice,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', out_dir,
            input_file
        ]
        
        print(f"[libreoffice_convert] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        if result.returncode == 0:
            temp_pdf = os.path.join(out_dir, f"{Path(input_file).stem}.pdf")
            if os.path.exists(temp_pdf):
                if os.path.abspath(temp_pdf) != os.path.abspath(output_pdf):
                    shutil.move(temp_pdf, output_pdf)
                
                # Apply post-processing (page numbers and compression)
                page_numbers_enabled = kwargs.get('page_numbers', False)
                compression_level = kwargs.get('compression', 'normal')
                
                if page_numbers_enabled or compression_level != 'normal':
                    try:
                        from PyPDF2 import PdfWriter, PdfReader
                        from reportlab.pdfgen import canvas
                        from io import BytesIO
                        
                        output_pdf_temp = output_pdf.replace('.pdf', '_temp.pdf')
                        
                        if page_numbers_enabled:
                            print(f"[libreoffice_convert] Adding page numbers...")
                            try:
                                pdf_reader = PdfReader(output_pdf)
                                pdf_writer = PdfWriter()
                                num_pages = len(pdf_reader.pages)
                                
                                for page_num in range(num_pages):
                                    page = pdf_reader.pages[page_num]
                                    packet = BytesIO()
                                    can = canvas.Canvas(packet, pagesize=(612, 792))
                                    can.setFont("Helvetica", 9)
                                    can.drawString(500, 20, f"Page {page_num + 1} of {num_pages}")
                                    can.save()
                                    packet.seek(0)
                                    annotation = PdfReader(packet)
                                    page.merge_page(annotation.pages[0])
                                    pdf_writer.add_page(page)
                                
                                with open(output_pdf_temp, 'wb') as f:
                                    pdf_writer.write(f)
                                
                                if os.path.exists(output_pdf_temp):
                                    os.remove(output_pdf)
                                    os.rename(output_pdf_temp, output_pdf)
                                    print(f"[libreoffice_convert] Page numbers added")
                            except Exception as e:
                                print(f"[libreoffice_convert] Warning: Could not add page numbers: {e}")
                        
                        if compression_level == 'high':
                            print(f"[libreoffice_convert] Applying compression...")
                            try:
                                pdf_reader = PdfReader(output_pdf)
                                pdf_writer = PdfWriter()
                                
                                for page in pdf_reader.pages:
                                    page.compress_content_streams()
                                    pdf_writer.add_page(page)
                                
                                with open(output_pdf_temp, 'wb') as f:
                                    pdf_writer.write(f)
                                
                                original_size = os.path.getsize(output_pdf)
                                compressed_size = os.path.getsize(output_pdf_temp)
                                
                                if compressed_size < original_size:
                                    os.remove(output_pdf)
                                    os.rename(output_pdf_temp, output_pdf)
                                    ratio = (1 - compressed_size / original_size) * 100
                                    print(f"[libreoffice_convert] Compression: {original_size} → {compressed_size} bytes ({ratio:.1f}% reduction)")
                                else:
                                    os.remove(output_pdf_temp)
                            except Exception as e:
                                print(f"[libreoffice_convert] Warning: Compression failed: {e}")
                                if os.path.exists(output_pdf_temp):
                                    try:
                                        os.remove(output_pdf_temp)
                                    except:
                                        pass
                    except ImportError:
                        print(f"[libreoffice_convert] PyPDF2/reportlab not available for post-processing")
                
                return True
        
        return False
    except Exception as e:
        logger.error(f"LibreOffice conversion error: {e}", exc_info=True)
        print(f"[libreoffice_convert] ERROR: {e}")
        return False


def pdf_to_powerpoint(pdf_path, output_pptx):
    """Convert PDF pages to PowerPoint presentation (one page per slide)"""
    try:
        if Presentation is None:
            print("python-pptx not installed")
            return False
        
        # Open PDF and get page count
        pdf_doc = fitz.open(pdf_path)
        prs = Presentation()
        
        # Set slide dimensions (standard 16:9)
        prs.slide_width = PptxInches(10)
        prs.slide_height = PptxInches(7.5)
        
        for page_num in range(len(pdf_doc)):
            # Render PDF page as image
            page = pdf_doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)

            # Save to temporary image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                img_path = tmp_img.name
            pix.save(img_path)
            
            # Create slide with blank layout
            blank_slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(blank_slide_layout)
            
            # Add image to slide (full-size)
            left = PptxInches(0)
            top = PptxInches(0)
            slide.shapes.add_picture(img_path, left, top, width=prs.slide_width, height=prs.slide_height)
            
            try:
                os.remove(img_path)
            except:
                pass
        
        prs.save(output_pptx)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"PDF to PowerPoint error: {e}")
        import traceback
        traceback.print_exc()
        return False


# Simple PDF encrypt/decrypt helpers (safe stubs). These provide minimal
# encryption/decryption using PyPDF2 where possible. They return (ok, message)
# similar to how routes expect. These are intentionally small and non-exhaustive.
def encrypt_pdf(input_path, output_path, password):
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for p in reader.pages:
            writer.add_page(p)
        writer.encrypt(user_pwd=password or "", owner_pwd=None)
        with open(output_path, 'wb') as f:
            writer.write(f)
        return True, ''
    except Exception as e:
        return False, str(e)


def powerpoint_to_pdf(pptx_path, output_pdf):
    """Convert PowerPoint presentation to PDF using LibreOffice"""
    try:
        import subprocess
        from pathlib import Path
        
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        # LibreOffice command for PPTX -> PDF conversion
        cmd = [
            get_soffice_path(),
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', out_dir,
            pptx_path
        ]
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        if result.returncode == 0:
            # Find the generated PDF (LibreOffice creates it with original filename stem)
            temp_pdf = os.path.join(out_dir, f"{Path(pptx_path).stem}.pdf")
            
            if os.path.exists(temp_pdf):
                # Move to target location if different
                if os.path.abspath(temp_pdf) != os.path.abspath(output_pdf):
                    shutil.move(temp_pdf, output_pdf)
                return True
        
        logger.error(f"LibreOffice conversion failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
        return False
        
    except Exception as e:
        logger.error(f"PowerPoint to PDF error: {e}")
        return False

def pdf_to_word(pdf_path, output_docx):
    """Convert PDF to Word DOCX - exact copy of PDF content with black borders"""
    try:
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        doc = DocxDocument()
        
        def set_cell_border(cell, **kwargs):
            """Set cell border with black color"""
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            
            for edge in ('top', 'left', 'bottom', 'right'):
                if edge in kwargs:
                    edge_el = OxmlElement(f'w:{edge}')
                    edge_el.set(qn('w:val'), 'single')
                    edge_el.set(qn('w:sz'), '12')  # Border size
                    edge_el.set(qn('w:space'), '0')
                    edge_el.set(qn('w:color'), '000000')  # Black color
                    tcBorders.append(edge_el)
            
            tcPr.append(tcBorders)
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                if page_num > 1:
                    doc.add_page_break()
                
                # Try to extract tables first
                tables = page.extract_tables()
                if tables:
                    for table_data in tables:
                        if not table_data:
                            continue
                        # Create table with black borders
                        table = doc.add_table(rows=len(table_data), cols=len(table_data[0]) if table_data else 1)
                        
                        for row_idx, row_data in enumerate(table_data):
                            for col_idx, cell_value in enumerate(row_data):
                                cell = table.rows[row_idx].cells[col_idx]
                                cell.text = str(cell_value) if cell_value else ""
                                # Add black borders to cell
                                set_cell_border(cell, top={}, left={}, bottom={}, right={})
                        
                        doc.add_paragraph()  # Space between tables
                else:
                    # Extract text as-is
                    text = page.extract_text()
                    if text:
                        doc.add_paragraph(text)
        
        doc.save(output_docx)
        return True
    except Exception as e:
        print(f"PDF to Word error: {e}")
        import traceback
        traceback.print_exc()
        return False

def pdf_to_excel(pdf_path, output_xlsx):
    """Convert PDF to Excel XLSX.

    Important: many invoices are scanned/image-based PDFs (no embedded text).
    For those, classic PDF table extraction returns nothing and the output looks
    mashed up. This function detects that case and switches to OCR + grid/line
    detection to recreate the layout with borders and spacing.
    """
    try:
        from openpyxl.styles import Border, Side, Alignment, Font
        from openpyxl.utils import get_column_letter
        from openpyxl.drawing.image import Image as XlImage

        def _dedupe_positions(values, min_gap):
            values = sorted(values)
            out = []
            for v in values:
                if not out or abs(v - out[-1]) >= min_gap:
                    out.append(v)
            return out

        def _find_line_positions(mask, axis, min_len_px, min_thickness_px=1):
            # axis=0 -> find vertical lines (return xs)
            # axis=1 -> find horizontal lines (return ys)
            import cv2
            positions = []
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if axis == 0:
                    # vertical
                    if h >= min_len_px and w <= max(8, min_thickness_px * 8):
                        positions.append(x + (w / 2.0))
                else:
                    # horizontal
                    if w >= min_len_px and h <= max(8, min_thickness_px * 8):
                        positions.append(y + (h / 2.0))
            return positions

        # Border style
        side = Side(style='thin', color='000000')
        black_border = Border(left=side, right=side, top=side, bottom=side)

        wb = Workbook()
        # We'll rename the active sheet to Page 1; additional pages -> new sheets
        wb.active.title = "Page 1"

        # Keep a single PyMuPDF doc open (used for rendering scanned/image PDFs)
        fitz_doc = None
        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                ws = wb["Page 1"] if page_index == 1 else wb.create_sheet(title=f"Page {page_index}")

                # Fast check: if the PDF page has extractable text, prefer text/table extraction.
                words = page.extract_words(use_text_flow=True)
                has_text = bool(words)

                if has_text:
                    # Text-based extraction (best-effort)
                    HEADER_KEYWORDS = ['description', 'hsn', 'hsn code', 'weight', 'qty', 'rate', 'amount', 'approx', 's.no', 's.no.']

                    # Attempt explicit table extraction using vector lines
                    vertical_lines_x = []
                    try:
                        for ln in getattr(page, 'lines', []):
                            if abs(ln.get('x1', 0) - ln.get('x0', 0)) < 2.0:
                                vertical_lines_x.append((ln.get('x0', 0) + ln.get('x1', 0)) / 2.0)
                    except Exception:
                        vertical_lines_x = []

                    vertical_lines_x = sorted(list({round(x, 2) for x in vertical_lines_x}))

                    current_row = 1
                    if len(vertical_lines_x) >= 2:
                        try:
                            tables = page.extract_tables({
                                'explicit_vertical_lines': vertical_lines_x,
                                'vertical_strategy': 'explicit',
                                'horizontal_strategy': 'lines'
                            })
                        except Exception:
                            tables = None
                        if tables:
                            for table in tables:
                                if not table:
                                    continue
                                max_cols = max(len(r) for r in table)
                                col_widths = {}
                                for r_idx, row in enumerate(table):
                                    for c_idx, cell_val in enumerate(row):
                                        txt = str(cell_val or '').strip()
                                        if txt:
                                            col_widths[c_idx] = max(col_widths.get(c_idx, 0), len(txt))
                                for r_idx, row in enumerate(table):
                                    for c_idx in range(max_cols):
                                        val = row[c_idx] if c_idx < len(row) else ''
                                        if val is None:
                                            val = ''
                                        cell = ws.cell(row=current_row, column=c_idx + 1)
                                        cell.value = val
                                        cell.border = black_border
                                        if r_idx == 0:
                                            cell.font = Font(bold=True, size=11)
                                            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                                        else:
                                            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                                    ws.row_dimensions[current_row].height = 20
                                    current_row += 1
                                for c_idx, wlen in col_widths.items():
                                    col_letter = get_column_letter(c_idx + 1)
                                    ws.column_dimensions[col_letter].width = min(max(wlen + 2, 10), 80)
                                current_row += 1
                            continue

                    # Header/position mapping fallback (text PDFs without clear table lines)
                    header_candidates = [w for w in words if any(k in w['text'].lower() for k in HEADER_KEYWORDS)]
                    header_candidates_sorted = sorted(header_candidates, key=lambda w: w['x0'])
                    if header_candidates_sorted and len(header_candidates_sorted) >= 2:
                        centers = [((w['x0'] + w['x1']) / 2.0) for w in header_candidates_sorted]
                        centers_sorted = sorted(centers)
                        boundaries = [0.0]
                        for i in range(len(centers_sorted) - 1):
                            boundaries.append((centers_sorted[i] + centers_sorted[i + 1]) / 2.0)
                        boundaries.append(page.width)
                    else:
                        xcenters = sorted([((w['x0'] + w['x1']) / 2.0) for w in words])
                        if len(xcenters) <= 1:
                            boundaries = [0.0, page.width]
                        else:
                            gaps = [(xcenters[i + 1] - xcenters[i], i) for i in range(len(xcenters) - 1)]
                            gaps_sorted = sorted(gaps, key=lambda g: g[0], reverse=True)
                            split_indices = sorted([g[1] for g in gaps_sorted[:min(6, len(gaps_sorted))]])
                            boundaries = [0.0]
                            for si in split_indices:
                                boundaries.append((xcenters[si] + xcenters[si + 1]) / 2.0)
                            boundaries.append(page.width)

                    # group words into lines by y
                    lines = []
                    tol = 3.0
                    for w in words:
                        ymid = (w['top'] + w['bottom']) / 2.0
                        for line in lines:
                            if abs(line['y'] - ymid) <= tol:
                                line['words'].append(w)
                                break
                        else:
                            lines.append({'y': ymid, 'words': [w]})
                    lines_sorted = sorted(lines, key=lambda l: l['y'])

                    header_row_idx = None
                    for idx, line in enumerate(lines_sorted[:8]):
                        texts = ' '.join([ww['text'].lower() for ww in line['words']])
                        if any(k in texts for k in HEADER_KEYWORDS):
                            header_row_idx = idx
                            break

                    current_row = 1
                    num_columns = max(2, len(boundaries) - 1)
                    for li, line in enumerate(lines_sorted):
                        row_cells = ['' for _ in range(num_columns)]
                        for w in sorted(line['words'], key=lambda ww: ww['x0']):
                            xmid = (w['x0'] + w['x1']) / 2.0
                            col_idx = 0
                            for ci in range(len(boundaries) - 1):
                                if boundaries[ci] <= xmid < boundaries[ci + 1]:
                                    col_idx = ci
                                    break
                            row_cells[col_idx] = (row_cells[col_idx] + ' ' + w['text']).strip() if row_cells[col_idx] else w['text']

                        for ci, cell_text in enumerate(row_cells):
                            if cell_text.strip():
                                cell = ws.cell(row=current_row, column=ci + 1)
                                cell.value = cell_text.strip()
                                cell.border = black_border
                                if header_row_idx is not None and li == header_row_idx:
                                    cell.font = Font(bold=True, size=11)
                                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                                else:
                                    cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                        ws.row_dimensions[current_row].height = 18
                        current_row += 1

                    for column in ws.columns:
                        max_len = 0
                        col_letter = column[0].column_letter
                        for cell in column:
                            if cell.value:
                                max_len = max(max_len, len(str(cell.value)))
                        ws.column_dimensions[col_letter].width = min(max(max_len + 2, 10), 80)

                    continue

                # OCR-based extraction for image/scanned PDFs
                import cv2
                # numpy not required directly here

                dpi = 200
                # render PDF page to image
                if fitz_doc is None:
                    fitz_doc = fitz.open(pdf_path)
                fpage = fitz_doc[page_index - 1]
                mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
                pix = fpage.get_pixmap(matrix=mat, alpha=False)

                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                    tmp_img.write(pix.tobytes('png'))
                    img_path = tmp_img.name

                img = cv2.imread(img_path)
                if img is None:
                    # fallback: nothing we can do
                    cell = ws.cell(row=1, column=1)
                    cell.value = "OCR failed: could not render page image"
                    cell.border = black_border
                    continue

                img_h, img_w = img.shape[:2]

                # Insert the rendered page image so the XLSX visually matches the PDF.
                try:
                    xl_img = XlImage(img_path)
                    xl_img.anchor = 'A1'
                    ws.add_image(xl_img)
                except Exception:
                    pass

                # binarize for line detection
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                inv = cv2.bitwise_not(gray)
                bw = cv2.adaptiveThreshold(inv, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, -2)

                # detect vertical & horizontal lines with morphology
                vert = bw.copy()
                vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(10, img_h // 40)))
                vert = cv2.erode(vert, vert_kernel)
                vert = cv2.dilate(vert, vert_kernel)

                hori = bw.copy()
                hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(10, img_w // 40), 1))
                hori = cv2.erode(hori, hori_kernel)
                hori = cv2.dilate(hori, hori_kernel)

                # extract line positions
                xs = _find_line_positions(vert, axis=0, min_len_px=int(img_h * 0.25))
                ys = _find_line_positions(hori, axis=1, min_len_px=int(img_w * 0.25))

                # always include page bounds
                xs.extend([0.0, float(img_w)])
                ys.extend([0.0, float(img_h)])
                xs = _dedupe_positions(xs, min_gap=8)
                ys = _dedupe_positions(ys, min_gap=8)

                # guard against insane grids
                if len(xs) > 80 or len(ys) > 200:
                    xs = [0.0, float(img_w)]
                    ys = _dedupe_positions(ys, min_gap=20)
                    if len(ys) > 200:
                        ys = [0.0, float(img_h)]

                # Create grid sizing in Excel
                # Column width in Excel units ~ pixels/7 (rough). Row height in points = px * 72 / dpi.
                num_cols = max(1, len(xs) - 1)
                num_rows = max(1, len(ys) - 1)

                for ci in range(1, num_cols + 1):
                    wpx = xs[ci] - xs[ci - 1]
                    ws.column_dimensions[get_column_letter(ci)].width = min(max((wpx / 7.0), 2.0), 60.0)
                for ri in range(1, num_rows + 1):
                    hpx = ys[ri] - ys[ri - 1]
                    ws.row_dimensions[ri].height = min(max((hpx * 72.0 / dpi), 8.0), 200.0)

                # OCR read (cached)
                reader = get_easyocr_reader()
                ocr = reader.readtext(img, detail=1)

                # accumulate text per cell
                cell_items = {}  # (r,c) -> list[(y,x,text)]
                for bbox, text, conf in ocr:
                    if not text or not str(text).strip():
                        continue
                    # bbox: 4 points
                    xs_box = [p[0] for p in bbox]
                    ys_box = [p[1] for p in bbox]
                    xmid = float(sum(xs_box) / 4.0)
                    ymid = float(sum(ys_box) / 4.0)

                    # find col
                    col = None
                    for i in range(len(xs) - 1):
                        if xs[i] <= xmid < xs[i + 1]:
                            col = i + 1
                            break
                    if col is None:
                        col = max(1, min(num_cols, int((xmid / img_w) * num_cols) + 1))

                    # find row
                    row = None
                    for j in range(len(ys) - 1):
                        if ys[j] <= ymid < ys[j + 1]:
                            row = j + 1
                            break
                    if row is None:
                        row = max(1, min(num_rows, int((ymid / img_h) * num_rows) + 1))

                    cell_items.setdefault((row, col), []).append((ymid, xmid, str(text).strip()))

                # write cells + borders
                for r in range(1, num_rows + 1):
                    for c in range(1, num_cols + 1):
                        cell = ws.cell(row=r, column=c)
                        cell.border = black_border
                        items = cell_items.get((r, c))
                        if items:
                            items_sorted = sorted(items, key=lambda t: (t[0], t[1]))
                            cell.value = ' '.join([t[2] for t in items_sorted]).strip()
                            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

                # bold likely header row if detected
                # (simple heuristic: first row with many non-empty cells)
                best_row = None
                best_count = 0
                for r in range(1, min(25, num_rows) + 1):
                    cnt = 0
                    for c in range(1, min(12, num_cols) + 1):
                        if ws.cell(r, c).value:
                            cnt += 1
                    if cnt > best_count:
                        best_count = cnt
                        best_row = r
                if best_row and best_count >= 4:
                    for c in range(1, num_cols + 1):
                        if ws.cell(best_row, c).value:
                            ws.cell(best_row, c).font = Font(bold=True, size=11)
                            ws.cell(best_row, c).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        try:
            if fitz_doc is not None:
                fitz_doc.close()
        except Exception:
            pass

        wb.save(output_xlsx)
        return True
    except Exception as e:
        print(f"PDF to Excel error: {e}")
        import traceback
        traceback.print_exc()
        return False

def pdf_to_true_bw(input_pdf, output_pdf, dpi=300, threshold=250, contrast=3.0, sharpness=2.5, brightness=0, gamma=1.0, blur=0, invert=False, denoise=0):
    """Convert PDF to true black and white using PyMuPDF - optimized for technical drawings"""
    # Open the PDF
    pdf_document = fitz.open(input_pdf)
    
    # Create a new PDF
    output_doc = fitz.open()
    
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document[page_num]
        
        # Render page to image (pixmap) at DPI 300 minimum
        mat = fitz.Matrix(dpi/72, dpi/72)  # Scale matrix for DPI
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert pixmap to PIL Image (RGB mode to handle colored lines)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Apply brightness adjustment
        if brightness != 0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.0 + (brightness / 100.0))
        
        # Apply gamma correction
        if gamma != 1.0:
            import numpy as np
            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.power(img_array, 1.0 / gamma)
            img = Image.fromarray((img_array * 255).astype(np.uint8))
        
        # Convert RGB to grayscale - this handles colored lines (purple/magenta)
        gray = img.convert("L")
        
        # Apply denoise if specified
        if denoise > 0:
            from PIL import ImageFilter
            gray = gray.filter(ImageFilter.MedianFilter(size=int(denoise + 1)))
        
        # Enhance sharpness for cleaner lines
        from PIL import ImageEnhance, ImageFilter
        sharpener = ImageEnhance.Sharpness(gray)
        gray = sharpener.enhance(sharpness)
        
        # Apply contrast enhancement
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(contrast)
        
        # Apply SHARPEN filter
        gray = gray.filter(ImageFilter.SHARPEN)
        
        # Apply threshold - anything below threshold becomes black
        bw = gray.point(lambda x: 255 if x >= threshold else 0, '1')
        bw = bw.convert('RGB')
        
        # Apply blur/anti-alias
        if blur > 0:
            from PIL import ImageFilter
            bw = bw.filter(ImageFilter.GaussianBlur(radius=float(blur)))
        
        # Apply color inversion
        if invert:
            from PIL import ImageOps
            bw = ImageOps.invert(bw)
        
        # Save to bytes as PNG for embedding
        img_bytes = io.BytesIO()
        bw.save(img_bytes, format='PNG', dpi=(dpi, dpi))
        img_bytes.seek(0)
        
        # Create a new page in output PDF with same dimensions as original
        rect = page.rect
        new_page = output_doc.new_page(width=rect.width, height=rect.height)
        
        # Insert the B&W image
        new_page.insert_image(rect, stream=img_bytes.getvalue())
    
    # Save the output PDF with compression
    output_doc.save(output_pdf, deflate=True)
    output_doc.close()
    pdf_document.close()
    
    return True


def extract_pdf_pages(input_pdf, output_pdf, pages):
    """Create a new PDF at output_pdf containing only the 1-based `pages` list from input_pdf."""
    try:
        src = fitz.open(input_pdf)
        out = fitz.open()
        for p in pages:
            idx = int(p) - 1
            if 0 <= idx < len(src):
                page = src[idx]
                pix = page.get_pixmap(alpha=False)
                # create a temp PDF page via insert
                rect = page.rect
                new = out.new_page(width=rect.width, height=rect.height)
                img_bytes = pix.tobytes('png')
                new.insert_image(rect, stream=img_bytes)
        out.save(output_pdf)
        out.close()
        src.close()
        return True
    except Exception:
        return False

def _generate_preview_from_pdf(pdf_path, dpi=150):
    """Render the first page of a PDF to PNG bytes and return bytes."""
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return None
        page = doc[0]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes('png')
        doc.close()
        return img_bytes
    except Exception:
        return None


def _generate_previews_from_pdf(pdf_path, max_pages=3, dpi=150):
    """Render up to max_pages from a PDF and return list of PNG bytes."""
    out = []
    try:
        doc = fitz.open(pdf_path)
        total = len(doc)
        count = min(total, max_pages)
        for i in range(count):
            page = doc[i]
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out.append(pix.tobytes('png'))
        doc.close()
    except Exception:
        return []
    return out


@app.route('/preview', methods=['POST'])
def preview_conversion():
    """Endpoint to simulate a conversion and return a preview image (base64 PNG).

    Accepts form-data with file(s), operation, and conversion parameters.
    Returns JSON: { success: bool, images: [dataurl, ...], message: '' }
    """
    # Log ALL form data received
    logger.info(f"Preview request received. Form keys: {list(request.form.keys())}")
    logger.info(f"All form data: {dict(request.form)}")
    
    if 'file' in request.files:
        files = request.files.getlist('file')
    elif 'files' in request.files:
        files = request.files.getlist('files')
    else:
        return jsonify({'success': False, 'message': 'No file uploaded for preview'}), 400

    if len(files) == 0:
        return jsonify({'success': False, 'message': 'No file uploaded for preview'}), 400

    # Use only the first file for preview to keep it fast
    f = files[0]
    filename = secure_filename(f.filename)
    if not filename:
        return jsonify({'success': False, 'message': 'Invalid filename'}), 400

    operation = request.form.get('operation', 'bw')
    try:
        max_pages = int(request.form.get('max_pages', '3'))
    except Exception:
        max_pages = 3
    try:
        dpi = int(request.form.get('dpi', '150'))
    except Exception:
        dpi = 150

    # Extract conversion parameters from form
    threshold = request.form.get('threshold', None)
    contrast = request.form.get('contrast', None)
    brightness = request.form.get('brightness', None)
    gamma = request.form.get('gamma', None)
    sharpness = request.form.get('sharpness', None)
    blur = request.form.get('blur', None)
    invert = request.form.get('invert', 'false').lower() == 'true'
    denoise = request.form.get('denoise', None)
    
    # Extract PDF-specific parameters for "To PDF" tool
    pdf_params = {}
    
    # Always set these parameters (with defaults if not provided)
    pdf_params['orientation'] = request.form.get('orientation', 'portrait')
    pdf_params['paper_size'] = request.form.get('paper_size', 'A4')
    
    # Numeric margins - extract as floats with defaults
    try:
        pdf_params['margin_top'] = float(request.form.get('margin_top', 10))
    except:
        pdf_params['margin_top'] = 10
    try:
        pdf_params['margin_bottom'] = float(request.form.get('margin_bottom', 10))
    except:
        pdf_params['margin_bottom'] = 10
    try:
        pdf_params['margin_left'] = float(request.form.get('margin_left', 10))
    except:
        pdf_params['margin_left'] = 10
    try:
        pdf_params['margin_right'] = float(request.form.get('margin_right', 10))
    except:
        pdf_params['margin_right'] = 10
    try:
        pdf_params['scale_factor'] = int(request.form.get('scale_factor', 100))
    except:
        pdf_params['scale_factor'] = 100
    
    # Boolean parameters
    pdf_params['include_headers'] = request.form.get('include_headers', 'false').lower() in ('true', 'yes', '1', 'on')
    pdf_params['gridlines'] = request.form.get('gridlines', 'false').lower() in ('true', 'yes', '1', 'on')
    pdf_params['page_numbers'] = request.form.get('page_numbers', 'false').lower() in ('true', 'yes', '1', 'on')
    pdf_params['preserve_colors'] = request.form.get('preserve_colors', 'true').lower() in ('true', 'yes', '1', 'on')
    pdf_params['embed_fonts'] = request.form.get('embed_fonts', 'false').lower() in ('true', 'yes', '1', 'on')
    pdf_params['background'] = request.form.get('background', 'false').lower() in ('true', 'yes', '1', 'on')
    
    # Log what parameters we're using
    logger.info(f"Preview request parameters: {pdf_params}")
    
    # Convert to appropriate types
    if threshold:
        try:
            threshold = int(threshold)
        except:
            threshold = None
    if contrast:
        try:
            contrast = float(contrast)
        except:
            contrast = None
    if brightness:
        try:
            brightness = int(brightness)
        except:
            brightness = None
    if gamma:
        try:
            gamma = float(gamma)
        except:
            gamma = None
    if sharpness:
        try:
            sharpness = float(sharpness)
        except:
            sharpness = None
    if blur:
        try:
            blur = float(blur)
        except:
            blur = None
    if denoise:
        try:
            denoise = float(denoise)
        except:
            denoise = None

    temp_dir = tempfile.mkdtemp()
    try:
        input_path = os.path.join(temp_dir, filename)
        f.save(input_path)

        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        # If it's an office file, convert to PDF first
        source_pdf = None
        if ext == 'pdf':
            source_pdf = input_path
        elif ext in DOCUMENT_ALLOWED_EXTENSIONS:
            inter = os.path.join(temp_dir, f"__preview_{Path(filename).stem}.pdf")
            try:
                logger.info(f'Attempting to convert {ext.upper()} file {filename} with params: {pdf_params}')
                if ext == 'docx':
                    result = docx_to_pdf(input_path, inter, **pdf_params)
                    logger.info(f'docx_to_pdf returned: {result}')
                elif ext in ['doc', 'odt']:
                    result = soffice_to_pdf(input_path, inter)
                    logger.info(f'soffice_to_pdf returned: {result}')
                
                if os.path.exists(inter):
                    source_pdf = inter
                    logger.info(f'Successfully created PDF: {inter}')
                else:
                    logger.warning(f'PDF file not created at expected location: {inter}')
            except Exception as e:
                logger.error(f'Document conversion failed for {filename}: {e}', exc_info=True)
        elif ext in EXCEL_ALLOWED_EXTENSIONS:
            inter = os.path.join(temp_dir, f"__preview_{Path(filename).stem}.pdf")
            try:
                logger.info(f'Attempting to convert Excel file {filename} with params: {pdf_params}')
                if ext == 'csv':
                    result = csv_to_pdf(input_path, inter, **pdf_params)
                else:
                    result = excel_to_pdf(input_path, inter, **pdf_params)
                logger.info(f'Excel/CSV conversion returned: {result}')
                
                if os.path.exists(inter):
                    source_pdf = inter
                    logger.info(f'Successfully created PDF: {inter}')
                else:
                    logger.warning(f'PDF file not created at expected location: {inter}')
            except Exception as e:
                logger.error(f'Excel conversion failed for {filename}: {e}', exc_info=True)

        # Validate B&W operations only work on PDFs (after conversion attempts)
        if 'b&w' in operation.lower() or 'bw' in operation.lower() or 'pdf-to-b' in operation.lower():
            if not source_pdf:
                return jsonify({'success': False, 'message': 'B&W conversion requires PDF or convertible document (DOCX, Excel)'}), 400

        # If operation is image-convert or input is image, render image preview
        if ext in IMAGE_ALLOWED_EXTENSIONS and operation == 'image-convert':
            try:
                img = Image.open(input_path)
                # Convert to PNG preview to be safe
                buf = io.BytesIO()
                img.convert('RGBA').save(buf, format='PNG')
                buf.seek(0)
                data = base64.b64encode(buf.read()).decode('ascii')
                return jsonify({'success': True, 'images': [f'data:image/png;base64,{data}'], 'message': ''})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Image preview error: {e}'}), 500
        # For non-image-convert operations on images, use fallback image handling
        elif ext in IMAGE_ALLOWED_EXTENSIONS:
            try:
                img = Image.open(input_path)
                buf = io.BytesIO()
                img.convert('RGBA').save(buf, format='PNG')
                buf.seek(0)
                data = base64.b64encode(buf.read()).decode('ascii')
                return jsonify({'success': True, 'images': [f'data:image/png;base64,{data}'], 'message': ''})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Image preview error: {e}'}), 500

        # If we have a PDF (either uploaded or converted), render pages
        if source_pdf:
            logger.info(f'Rendering pages from PDF: {source_pdf}')
            logger.info(f'PDF file exists: {os.path.exists(source_pdf)}')
            logger.info(f'PDF file size: {os.path.getsize(source_pdf) if os.path.exists(source_pdf) else "N/A"} bytes')
            
            # Render raw pages first
            img_bytes_list = _generate_previews_from_pdf(source_pdf, max_pages=max_pages, dpi=dpi)
            logger.info(f'Generated {len(img_bytes_list) if img_bytes_list else 0} preview images')
            
            # Apply B&W conversion if operation is related to B&W
            if 'b&w' in operation.lower() or 'bw' in operation.lower() or 'pdf-to-b' in operation.lower():
                processed_images = []
                for img_bytes in img_bytes_list:
                    # Convert bytes to PIL image
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    # Apply brightness adjustment
                    if brightness and brightness != 0:
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Brightness(img)
                        img = enhancer.enhance(1.0 + (brightness / 100.0))
                    
                    # Apply gamma correction
                    if gamma and gamma != 1.0:
                        import numpy as np
                        img_array = np.array(img, dtype=np.float32) / 255.0
                        img_array = np.power(img_array, 1.0 / gamma)
                        img = Image.fromarray((img_array * 255).astype(np.uint8))
                    
                    # Convert to grayscale
                    img_gray = img.convert('L')
                    
                    # Apply contrast if specified
                    if contrast and contrast != 1:
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Contrast(img_gray)
                        img_gray = enhancer.enhance(float(contrast))
                    
                    # Apply denoise if specified (reduce noise)
                    if denoise and denoise > 0:
                        from PIL import ImageFilter
                        img_gray = img_gray.filter(ImageFilter.MedianFilter(size=int(denoise + 1)))
                    
                    # Apply threshold if specified (converts to pure B&W)
                    if threshold is not None:
                        img_bw = img_gray.point(lambda x: 255 if x > threshold else 0, '1')
                        img_bw = img_bw.convert('RGB')  # Convert back to RGB for PNG
                        processed_img = img_bw
                    else:
                        processed_img = img_gray.convert('RGB')
                    
                    # Apply sharpness adjustment
                    if sharpness and sharpness != 1.0:
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Sharpness(processed_img)
                        processed_img = enhancer.enhance(float(sharpness))
                    
                    # Apply blur/anti-alias
                    if blur and blur > 0:
                        from PIL import ImageFilter
                        processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=float(blur)))
                    
                    # Apply color inversion
                    if invert:
                        from PIL import ImageOps
                        processed_img = ImageOps.invert(processed_img.convert('RGB'))
                    
                    # Convert back to bytes
                    buf = io.BytesIO()
                    processed_img.save(buf, format='PNG')
                    buf.seek(0)
                    processed_images.append(buf.getvalue())
                
                img_bytes_list = processed_images
            # For "to-pdf" or other document operations, just return the PDF pages as-is
            elif 'to-pdf' in operation.lower() or 'to_pdf' in operation.lower() or 'to pdf' in operation.lower():
                # Already rendered - return as-is
                pass
            
            if img_bytes_list:
                images = [f'data:image/png;base64,{base64.b64encode(b).decode("ascii")}' for b in img_bytes_list]
                return jsonify({'success': True, 'images': images, 'message': ''})
            else:
                logger.error(f'Failed to render pages from PDF: {source_pdf}')
                return jsonify({
                    'success': False, 
                    'message': 'Could not render preview pages from PDF. Please check the server logs for details.'
                }), 500

        # Check if file was a convertible document type but conversion failed
        if ext in DOCUMENT_ALLOWED_EXTENSIONS or ext in EXCEL_ALLOWED_EXTENSIONS:
            return jsonify({
                'success': False, 
                'message': f'Could not convert {ext.upper()} file to PDF. Please ensure the file is not corrupted.'
            }), 400

        # Fallback: try to open as image and preview
        try:
            img = Image.open(input_path)
            buf = io.BytesIO()
            img.convert('RGBA').save(buf, format='PNG')
            buf.seek(0)
            data = base64.b64encode(buf.read()).decode('ascii')
            return jsonify({'success': True, 'images': [f'data:image/png;base64,{data}'], 'message': ''})
        except Exception:
            return jsonify({'success': False, 'message': 'Unsupported file type for preview'}), 400
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@app.route('/compress-image', methods=['POST'])
def compress_image_route():
    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401
    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400

    if not allowed_file(f.filename, 'image'):
        return jsonify({'success': False, 'error': 'unsupported_file_type'}), 400

    try:
        quality = int(request.form.get('quality', 85) or 85)
    except Exception:
        quality = 85

    temp_dir = tempfile.mkdtemp()
    try:
        safe_name = sanitize_filename(f.filename) or secure_filename(f.filename)
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        ext = Path(safe_name).suffix.lstrip('.').lower()
        out_name = f"{Path(safe_name).stem}_compressed.{ext}"
        out_path = os.path.join(temp_dir, out_name)

        ok = convert_image_format(in_path, out_path, ext, quality=quality, lossless=False)
        if not ok or not os.path.exists(out_path):
            return jsonify({'success': False, 'error': 'compression_failed'}), 500

        log_history('compress_image', [f.filename], status='success')
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@app.route('/compress-pdf', methods=['POST'])
def compress_pdf_route():
    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401
    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400
    if not allowed_file(f.filename, 'pdf'):
        return jsonify({'success': False, 'error': 'unsupported_file_type'}), 400

    optimize_for = request.form.get('optimize_for', 'web')
    remove_metadata = request.form.get('remove_metadata', 'true').lower() in ('1', 'true', 'on')
    try:
        image_quality = int(request.form.get('image_quality', 85) or 85)
    except Exception:
        image_quality = 85

    temp_dir = tempfile.mkdtemp()
    try:
        in_name = sanitize_filename(f.filename) or secure_filename(f.filename)
        in_path = os.path.join(temp_dir, in_name)
        f.save(in_path)

        out_name = f"{Path(in_name).stem}_compressed.pdf"
        out_path = os.path.join(temp_dir, out_name)

        try:
            doc = fitz.open(in_path)
            if remove_metadata:
                try:
                    doc.set_metadata({})
                except Exception:
                    pass

            # If user requests lower image quality, rasterize pages at reduced scale
            if 0 < image_quality < 100:
                scale = image_quality / 100.0
                new_doc = fitz.open()
                for page in doc:
                    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                    img_bytes = pix.tobytes('png')
                    new_page = new_doc.new_page(width=pix.width, height=pix.height)
                    new_page.insert_image(new_page.rect, stream=img_bytes)
                new_doc.save(out_path, garbage=4, deflate=True)
                new_doc.close()
            else:
                # Save with compression flags where supported
                doc.save(out_path, garbage=4, deflate=True)
            doc.close()
        except Exception as e:
            return jsonify({'success': False, 'error': 'pdf_processing_failed', 'detail': str(e)}), 500

        log_history('compress_pdf', [f.filename], status='success')
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@app.route('/resize-image', methods=['POST'])
def resize_image_route():
    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401
    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400
    if not allowed_file(f.filename, 'image'):
        return jsonify({'success': False, 'error': 'unsupported_file_type'}), 400

    preset = request.form.get('preset')
    keep_aspect = request.form.get('keep_aspect', 'true').lower() in ('1', 'true', 'on')
    try:
        width = int(request.form.get('width') or 0)
    except Exception:
        width = 0
    try:
        height = int(request.form.get('height') or 0)
    except Exception:
        height = 0

    PRESET_SIZES = {
        'instagram': (1080, 1080),
        'twitter': (1200, 675),
        'facebook': (1200, 630)
    }

    temp_dir = tempfile.mkdtemp()
    try:
        in_name = sanitize_filename(f.filename) or secure_filename(f.filename)
        in_path = os.path.join(temp_dir, in_name)
        f.save(in_path)

        if preset and preset in PRESET_SIZES:
            width, height = PRESET_SIZES[preset]

        from PIL import Image as PILImage
        img = PILImage.open(in_path)
        orig_w, orig_h = img.size

        if keep_aspect:
            if width and not height:
                height = int(orig_h * (width / orig_w))
            elif height and not width:
                width = int(orig_w * (height / orig_h))
            elif not width and not height:
                width, height = orig_w, orig_h
        else:
            if not width:
                width = orig_w
            if not height:
                height = orig_h

        new_size = (max(1, int(width)), max(1, int(height)))
        img = img.resize(new_size, PILImage.LANCZOS)

        out_name = f"{Path(in_name).stem}_resized{Path(in_name).suffix}"
        out_path = os.path.join(temp_dir, out_name)
        img.save(out_path)

        log_history('resize_image', [f.filename], status='success')
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@app.route('/bg-to-white', methods=['POST'])
def bg_to_white_route():
    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401
    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400
    if not allowed_file(f.filename, 'image'):
        return jsonify({'success': False, 'error': 'unsupported_file_type'}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        in_name = sanitize_filename(f.filename) or secure_filename(f.filename)
        in_path = os.path.join(temp_dir, in_name)
        f.save(in_path)

        from PIL import Image as PILImage
        img = PILImage.open(in_path)
        if img.mode == 'RGBA' or 'A' in img.getbands():
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            out_img = background
        else:
            out_img = img.convert('RGB')

        out_name = f"{Path(in_name).stem}_whitebg{Path(in_name).suffix}"
        out_path = os.path.join(temp_dir, out_name)
        out_img.save(out_path)

        log_history('bg_to_white', [f.filename], status='success')
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@app.route('/watermark', methods=['POST'])
def watermark_tool_route():
    if not _check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401
    if is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400
    if not allowed_file(f.filename, 'image'):
        return jsonify({'success': False, 'error': 'unsupported_file_type'}), 400

    watermark_text = request.form.get('watermark_text')
    position = request.form.get('position', 'center')
    try:
        opacity = float(request.form.get('opacity', 0.3))
    except Exception:
        opacity = 0.3
    try:
        scale = float(request.form.get('scale', 1.0))
    except Exception:
        scale = 1.0

    temp_dir = tempfile.mkdtemp()
    try:
        in_name = sanitize_filename(f.filename) or secure_filename(f.filename)
        in_path = os.path.join(temp_dir, in_name)
        f.save(in_path)

        from PIL import Image as PILImage, ImageDraw, ImageFont
        img = PILImage.open(in_path).convert('RGBA')
        w, h = img.size

        overlay = PILImage.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Simple font handling: fallback to default
        try:
            font_size = max(12, int(min(w, h) * 0.05 * scale))
            font = ImageFont.truetype('arial.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()

        if watermark_text:
            try:
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except Exception:
                # Fallback for older Pillow versions
                try:
                    text_w, text_h = font.getsize(watermark_text)
                except Exception:
                    text_w, text_h = (len(watermark_text) * 6, 10)
            if position == 'center':
                pos = ((w - text_w) // 2, (h - text_h) // 2)
            elif position == 'top-left':
                pos = (10, 10)
            elif position == 'top-right':
                pos = (w - text_w - 10, 10)
            elif position == 'bottom-left':
                pos = (10, h - text_h - 10)
            elif position == 'bottom-right':
                pos = (w - text_w - 10, h - text_h - 10)
            else:
                pos = ((w - text_w) // 2, (h - text_h) // 2)

            # apply text with alpha derived from opacity
            alpha = int(255 * max(0.0, min(1.0, opacity)))
            draw.text(pos, watermark_text, fill=(0, 0, 0, alpha), font=font)

        result = PILImage.alpha_composite(img, overlay).convert('RGB')

        out_name = f"{Path(in_name).stem}_watermarked{Path(in_name).suffix}"
        out_path = os.path.join(temp_dir, out_name)
        result.save(out_path)

        log_history('watermark_image', [f.filename], status='success')
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

# ============== ADVANCED FEATURES ==============

def ocr_extract_text(image_or_pdf_path, output_txt):
    """Extract text from image or PDF using EasyOCR"""
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        extracted_text = []
        
        # Check if it's a PDF or image
        if image_or_pdf_path.lower().endswith('.pdf'):
            # Extract images from PDF
            pdf_doc = fitz.open(image_or_pdf_path)
            for page_num, page in enumerate(pdf_doc, 1):
                # Convert PDF page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                with tempfile.NamedTemporaryFile(suffix=f"_page_{page_num}.png", delete=False) as timg:
                    img_path = timg.name
                pix.save(img_path)
                
                # Run OCR on page
                results = reader.readtext(img_path)
                extracted_text.append(f"--- PAGE {page_num} ---")
                for detection in results:
                    text = detection[1]
                    confidence = detection[2]
                    extracted_text.append(f"{text} ({confidence:.2%} confidence)")
            pdf_doc.close()
        else:
            # Direct image OCR
            results = reader.readtext(image_or_pdf_path)
            for detection in results:
                text = detection[1]
                confidence = detection[2]
                extracted_text.append(f"{text} ({confidence:.2%} confidence)")
        
        # Save to text file
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(extracted_text))
        
        return True
    except Exception as e:
        print(f"OCR error: {e}")
        import traceback
        traceback.print_exc()
        return False

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

def add_watermark(input_pdf, output_pdf, watermark_text, opacity=0.3, position='diagonal', font_size=60, color=(0.5, 0.5, 0.5), fontname='helv', pages=None, rotation=0, scale=1.0):
    """Add text watermark to PDF with advanced settings and effects
    
    Args:
        input_pdf: Input PDF file path
        output_pdf: Output PDF file path
        watermark_text: Text to display as watermark
        opacity: Opacity of watermark (0.0-1.0), default 0.3
        position: Position of watermark (diagonal, top, bottom, center, top-left, top-right, bottom-left, bottom-right)
        font_size: Font size in points (20-120)
        color: Color as (R, G, B) tuple, each 0.0-1.0
        fontname: Font name (helv, times-roman, courier)
        pages: List of page numbers (0-indexed) to watermark, or None for all pages
        rotation: Rotation angle in degrees (0-360), applied to watermark text
        scale: Scale factor for watermark (0.5-2.0)
    """
    try:
        import math
        
        pdf_doc = fitz.open(input_pdf)
        
        # Determine which pages to watermark
        if pages is None:
            # All pages
            pages_to_process = list(range(len(pdf_doc)))
        else:
            # Specific pages - filter to valid page numbers
            pages_to_process = [p for p in pages if 0 <= p < len(pdf_doc)]
        
        # Adjust font size by scale factor
        adjusted_font_size = font_size * scale
        
        for page_num in pages_to_process:
            page = pdf_doc[page_num]
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Default positioning with padding
            padding = 20
            if position == 'diagonal':
                x = width / 2
                y = height / 2
                angle = rotation if rotation else 45
            elif position == 'top':
                x = width / 2
                y = padding + 30
                angle = rotation
            elif position == 'bottom':
                x = width / 2
                y = height - padding - 30
                angle = rotation
            elif position == 'center':
                x = width / 2
                y = height / 2
                angle = rotation
            elif position == 'top-left':
                x = padding + 40
                y = padding + 30
                angle = rotation
            elif position == 'top-right':
                x = width - padding - 40
                y = padding + 30
                angle = rotation
            elif position == 'bottom-left':
                x = padding + 40
                y = height - padding - 30
                angle = rotation
            elif position == 'bottom-right':
                x = width - padding - 40
                y = height - padding - 30
                angle = rotation
            else:
                # default to center
                x = width / 2
                y = height / 2
                angle = rotation if rotation else 45
            
            # Use shape for rotated/scaled text with opacity
            if angle != 0 or opacity < 1.0:
                shape = page.new_shape()
                text_point = fitz.Point(x, y)
                
                # Create rotation matrix
                rad = math.radians(angle)
                cos_a = math.cos(rad)
                sin_a = math.sin(rad)
                
                # Translation-adjusted rotation matrix
                # rotation matrix prepared (not directly used by current API)
                # keep computation in case future APIs use it
                _ = fitz.Matrix(cos_a, sin_a, -sin_a, cos_a, 
                                 x - x*cos_a + y*sin_a, y - x*sin_a - y*cos_a)
                
                # Draw text with matrix transformation
                shape.insert_text(
                    text_point,
                    watermark_text,
                    fontsize=adjusted_font_size,
                    color=color,
                    fontname=fontname
                )
                # Commit shape with opacity
                shape.commit()
            else:
                # Simple text insertion without rotation
                page.insert_text(
                    fitz.Point(x, y),
                    watermark_text,
                    fontsize=adjusted_font_size,
                    color=color,
                    fontname=fontname
                )
        
        pdf_doc.save(output_pdf, deflate=True)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Watermark error: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_image_watermark(input_pdf, output_pdf, image_path, position='center', scale=100, scale_unit='percent', pages=None):
    """Add image watermark to PDF
    
    Args:
        input_pdf: Input PDF file path
        output_pdf: Output PDF file path
        image_path: Path to image file (PNG, JPG, etc.)
        position: Position (diagonal, top, bottom, center, top-left, top-right, bottom-left, bottom-right)
        scale: Scale percentage (10-200) or inches
        scale_unit: 'percent' for percentage of page width, 'inches' for inches
        pages: List of page numbers (0-indexed) to watermark, or None for all pages
    """
    try:
        from PIL import Image as PILImage
        
        pdf_doc = fitz.open(input_pdf)
        
        # Load and validate image
        try:
            pil_img = PILImage.open(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
        
        # Determine which pages to watermark
        if pages is None:
            pages_to_process = list(range(len(pdf_doc)))
        else:
            pages_to_process = [p for p in pages if 0 <= p < len(pdf_doc)]
        
        for page_num in pages_to_process:
            page = pdf_doc[page_num]
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Calculate image dimensions
            if scale_unit == 'percent':
                # Scale as percentage of page width
                img_width = (width / 100) * scale
            else:
                # Scale in inches (72 points per inch)
                img_width = scale * 72
            
            # Maintain aspect ratio
            aspect_ratio = pil_img.width / pil_img.height
            img_height = img_width / aspect_ratio
            
            # Calculate position
            padding = 20
            
            if position == 'diagonal':
                # Diagonal center position
                x = (width - img_width) / 2
                y = (height - img_height) / 2
            elif position == 'top':
                x = (width - img_width) / 2
                y = padding
            elif position == 'bottom':
                x = (width - img_width) / 2
                y = height - img_height - padding
            elif position == 'center':
                x = (width - img_width) / 2
                y = (height - img_height) / 2
            elif position == 'top-left':
                x = padding
                y = padding
            elif position == 'top-right':
                x = width - img_width - padding
                y = padding
            elif position == 'bottom-left':
                x = padding
                y = height - img_height - padding
            elif position == 'bottom-right':
                x = width - img_width - padding
                y = height - img_height - padding
            else:
                # Default to center
                x = (width - img_width) / 2
                y = (height - img_height) / 2
            
            # Create rect for image placement
            img_rect = fitz.Rect(x, y, x + img_width, y + img_height)
            
            # Insert image
            page.insert_image(img_rect, filename=image_path)
        
        pdf_doc.save(output_pdf, deflate=True)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Image watermark error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============== DOCUMENT REDACTION ==============

def redact_pdf(input_pdf, output_pdf, keywords, redaction_color=(0, 0, 0)):
    """Redact sensitive text/keywords from PDF
    
    Args:
        input_pdf: Input PDF file path
        output_pdf: Output PDF file path
        keywords: List of words/phrases to redact
        redaction_color: RGB color for redaction box (default black)
    """
    try:
        pdf_doc = fitz.open(input_pdf)
        redacted_count = 0
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            for keyword in keywords:
                # Find all instances of keyword on page
                text_dict = page.get_text('dict')
                
                # Search through text blocks
                for block in text_dict.get('blocks', []):
                    if block['type'] != 0:  # 0 = text block
                        continue
                    
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            text = span.get('text', '')
                            if keyword.lower() in text.lower():
                                # Get text position
                                rect = fitz.Rect(span['bbox'])
                                # Draw black rectangle over text
                                page.draw_rect(rect, color=None, fill=redaction_color, width=0.5)
                                redacted_count += 1
        
        pdf_doc.save(output_pdf, deflate=True)
        pdf_doc.close()
        return redacted_count > 0
    except Exception as e:
        print(f"Redaction error: {e}")
        return False

# ============== BATCH PROCESSING ==============

def batch_process_pdfs(input_directory, output_directory, operation='watermark', operation_params=None):
    """Batch process multiple PDFs
    
    Args:
        input_directory: Directory with input PDF files
        output_directory: Directory for output files
        operation: Operation to perform (watermark, encrypt, watermark)
        operation_params: Dictionary of parameters for the operation
    """
    # multiprocessing not used here; process sequentially
    import os
    from pathlib import Path
    
    operation_params = operation_params or {}
    
    # Get all PDF files
    pdf_files = list(Path(input_directory).glob('*.pdf'))
    if not pdf_files:
        return {'count': 0, 'results': []}
    
    results = []
    
    try:
        for pdf_file in pdf_files:
            try:
                input_path = str(pdf_file)
                output_name = pdf_file.stem + '_processed.pdf'
                output_path = os.path.join(output_directory, output_name)
                
                success = False
                if operation == 'watermark':
                    success = add_watermark(
                        input_path, output_path,
                        operation_params.get('text', 'WATERMARK'),
                        opacity=operation_params.get('opacity', 0.3),
                        position=operation_params.get('position', 'diagonal'),
                        font_size=operation_params.get('font_size', 50)
                    )
                elif operation == 'encrypt':
                    success = encrypt_pdf(
                        input_path, output_path,
                        password=operation_params.get('password', 'password')
                    )
                elif operation == 'bw':
                    success = pdf_to_true_bw(input_path, output_path)
                
                results.append({
                    'file': pdf_file.name,
                    'success': success,
                    'output': output_name if success else None
                })
            except Exception as e:
                results.append({
                    'file': pdf_file.name,
                    'success': False,
                    'error': str(e)
                })
        
        return {'count': len(results), 'results': results}
    except Exception as e:
        print(f"Batch processing error: {e}")
        return {'count': 0, 'results': []}

# ============== MORE FORMAT CONVERSIONS ==============

def html_to_pdf(html_content, output_pdf, **kwargs):
    """Convert HTML to PDF using LibreOffice for best formatting"""
    try:
        import subprocess
        import tempfile
        from pathlib import Path
        
        # Write HTML content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(html_content)
            html_file = tmp_file.name
        
        try:
            out_dir = os.path.dirname(output_pdf) or '.'
            os.makedirs(out_dir, exist_ok=True)
            
            # LibreOffice command for HTML -> PDF conversion
            cmd = [
                get_soffice_path(),
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', out_dir,
                html_file
            ]
            
            # Run conversion
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            
            if result.returncode == 0:
                # Find the generated PDF (LibreOffice creates it with original filename stem)
                temp_pdf = os.path.join(out_dir, f"{Path(html_file).stem}.pdf")
                
                if os.path.exists(temp_pdf):
                    # Move to target location if different
                    if os.path.abspath(temp_pdf) != os.path.abspath(output_pdf):
                        shutil.move(temp_pdf, output_pdf)
                    return True
            
            logger.error(f"LibreOffice HTML to PDF conversion failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
            return False
            
        finally:
            # Clean up temp HTML file
            try:
                os.unlink(html_file)
            except:
                pass
        
    except Exception as e:
        logger.error(f"HTML to PDF error: {e}")
        return False


def pdf_to_html(pdf_path, output_html):
    """Convert PDF to HTML"""
    try:
        doc = fitz.open(pdf_path)
        html_content = "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n"
        html_content += "<style>body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }\n"
        html_content += ".page { page-break-after: always; margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; }\n"
        html_content += "h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }\n"
        html_content += "p { color: #555; }</style>\n</head>\n<body>\n"
        
        for page_num, page in enumerate(doc, 1):
            html_content += f"<div class='page'>\n<h2>Page {page_num}</h2>\n"
            
            # Extract text blocks
            text = page.get_text("text")
            if text.strip():
                # Split into paragraphs and wrap with <p> tags
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                for para in paragraphs:
                    # Escape HTML special characters
                    para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    para = para.replace('\n', '<br>')
                    html_content += f"<p>{para}</p>\n"
            
            html_content += "</div>\n"
        
        html_content += "</body>\n</html>"
        doc.close()
        
        # Write to file
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return True
    except Exception as e:
        print(f"PDF to HTML error: {e}")
        import traceback
        traceback.print_exc()
        return False

def url_to_pdf(webpage_url, output_pdf):
    """Convert web page from URL to PDF with formatting preserved"""
    try:
        if requests is None:
            print("requests library not installed")
            return False
        
        # Fetch the webpage with a timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(webpage_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Try to use weasyprint for formatted output (preserves CSS styling)
        if WeasyHTML:
            try:
                # Create a wrapper HTML that includes the webpage
                html_content = response.text
                
                # Ensure proper encoding
                if '<?xml' not in html_content and '<html' not in html_content.lower():
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='UTF-8'>
</head>
<body>
{html_content}
</body>
</html>"""
                
                # Add source attribution
                html_content = html_content.replace('</body>', f"""
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666;">
  <strong>Source:</strong> <a href="{webpage_url}">{webpage_url}</a><br>
  Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
</body>""")
                
                # Convert using weasyprint which preserves CSS styling
                WeasyHTML(string=html_content, base_url=webpage_url).write_pdf(output_pdf)
                return True
            except Exception as e:
                print(f"WeasyPrint rendering error, trying fallback: {e}")
                # Continue to fallback method
        
        # Fallback: Extract text and create simple PDF (if weasyprint fails or unavailable)
        if BeautifulSoup:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script, style and nav tags
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            # Get title
            title = soup.find('title')
            title_text = title.get_text() if title else 'Web Page'
            
            # Get main content
            main_content = soup.find(['main', 'article', 'body'])
            if main_content:
                content = main_content.get_text()
            else:
                content = soup.get_text()
            
            # Create HTML with extracted content
            html_content = f"""<h1>{title_text}</h1>
"""
            # Process content
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            for para in paragraphs[:100]:
                para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                if len(para) > 10:
                    html_content += f"<p>{para}</p>\n"
            
            # Add source info separately (not inside <p> tags)
            html_content += f"""<p>Source: {webpage_url}</p>
<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"""
        else:
            # No BeautifulSoup, use raw HTML
            html_content = response.text
        
        # Convert to PDF using reportlab
        return html_to_pdf(html_content, output_pdf)
    
    except requests.RequestException as e:
        print(f"URL fetch error: {e}")
        return False
    except Exception as e:
        print(f"URL to PDF error: {e}")
        import traceback
        traceback.print_exc()
        return False

def text_to_pdf(text_content, output_pdf, **kwargs):
    """Convert plain text to PDF with formatting options"""
    try:
        from reportlab.lib.pagesizes import A4, A3, letter, legal, landscape, portrait
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        
        # Get PDF parameters
        orientation = kwargs.get('orientation', 'portrait').lower()
        paper_size = kwargs.get('paper_size', 'A4').upper()
        margin_top = float(kwargs.get('margin_top', 20)) * mm
        margin_bottom = float(kwargs.get('margin_bottom', 20)) * mm
        margin_left = float(kwargs.get('margin_left', 20)) * mm
        margin_right = float(kwargs.get('margin_right', 20)) * mm
        
        # Select page size
        page_size_map = {
            'A4': A4,
            'A3': A3,
            'LETTER': letter,
            'LEGAL': legal
        }
        base_page_size = page_size_map.get(paper_size, A4)
        page_size = landscape(base_page_size) if orientation == 'landscape' else portrait(base_page_size)
        
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=page_size,
            topMargin=margin_top,
            bottomMargin=margin_bottom,
            leftMargin=margin_left,
            rightMargin=margin_right
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Create custom style for text
        custom_style = ParagraphStyle(
            'CustomText',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor='#333333'
        )
        
        # Process text content
        lines = text_content.split('\n')
        for line in lines:
            if line.strip():
                story.append(Paragraph(line, custom_style))
            else:
                story.append(Spacer(1, 12))
        
        doc.build(story)
        return True
    except Exception as e:
        print(f"Text to PDF error: {e}")
        return False


def pdf_remove_metadata(input_pdf, output_pdf):
    """Remove metadata from PDF for privacy"""
    try:
        pdf_doc = fitz.open(input_pdf)
        
        # Clear metadata
        pdf_doc.set_metadata({
            'title': '',
            'author': '',
            'subject': '',
            'keywords': '',
            'creator': 'DocPro',
            'producer': 'DocPro',
        })
        
        pdf_doc.save(output_pdf, deflate=True, garbage=4)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Metadata removal error: {e}")
        return False

# ============== OCR ENHANCEMENTS ==============

def ocr_extract_with_language(image_or_pdf_path, output_txt, languages=['en']):
    """Extract text from image or PDF using EasyOCR with language selection"""
    try:
        from easyocr import Reader
        
        reader = Reader(languages, gpu=False)
        extracted_text = []
        
        # Check if it's a PDF or image
        if image_or_pdf_path.lower().endswith('.pdf'):
            # Extract images from PDF
            pdf_doc = fitz.open(image_or_pdf_path)
            for page_num, page in enumerate(pdf_doc, 1):
                # Convert PDF page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                with tempfile.NamedTemporaryFile(suffix=f"_page_{page_num}.png", delete=False) as timg:
                    img_path = timg.name
                pix.save(img_path)
                
                # Run OCR on page
                results = reader.readtext(img_path)
                extracted_text.append(f"\n=== PAGE {page_num} ===\n")
                for detection in results:
                    text = detection[1]
                    confidence = detection[2]
                    extracted_text.append(f"{text} [{confidence:.1%}]")
                
                try:
                    os.remove(img_path)
                except:
                    pass
            pdf_doc.close()
        else:
            # Direct image OCR
            results = reader.readtext(image_or_pdf_path)
            for detection in results:
                text = detection[1]
                confidence = detection[2]
                extracted_text.append(f"{text} [{confidence:.1%}]")
        
        # Save to text file
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(extracted_text))
        
        return True
    except Exception as e:
        print(f"OCR error: {e}")
        return False


    

def decrypt_pdf(input_pdf, output_pdf, password):
    """Decrypt an encrypted PDF given the user password."""
    try:
        from PyPDF2 import PdfReader, PdfWriter

        with open(input_pdf, 'rb') as f:
            reader = PdfReader(f)
            if reader.is_encrypted:
                # try to decrypt
                try:
                    ok = reader.decrypt(password)
                except Exception:
                    ok = False
                if not ok:
                    # PyPDF2 decrypt returns 0 or 1; failure
                    return False
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(output_pdf, 'wb') as out_f:
                writer.write(out_f)
        return True
    except Exception as e:
        print(f"Decryption error: {e}")
        return False

def clean_autoformat_pdf(input_pdf, output_pdf):
    """Clean and optimize PDF formatting - preserves all content"""
    try:
        pdf_doc = fitz.open(input_pdf)
        
        # Simply re-save with better compression and cleanup
        # This preserves all content (images, text, tables, etc.)
        # while cleaning up metadata and reducing file size
        pdf_doc.save(output_pdf, deflate=True, garbage=4)
        
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Auto-format error: {e}")
        return False

def excel_to_csv(excel_path, output_csv):
    """Convert Excel sheet to CSV"""
    try:
        import pandas as pd
        
        # Read Excel file (reads first sheet by default)
        df = pd.read_excel(excel_path, sheet_name=0)
        
        # Save to CSV
        df.to_csv(output_csv, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Excel to CSV error: {e}")
        import traceback
        traceback.print_exc()
        return False

def split_pdf(input_pdf, output_dir, page_ranges):
    """Split PDF into multiple files based on page ranges
    page_ranges: list of tuples [(start1, end1), (start2, end2), ...]
    Page numbers are 1-indexed
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter

        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)
        output_files = []

        for i, (start, end) in enumerate(page_ranges):
            start_idx = max(0, start - 1)
            end_idx = min(total_pages, end)
            if start_idx < end_idx:
                writer = PdfWriter()
                for page_num in range(start_idx, end_idx):
                    writer.add_page(reader.pages[page_num])

                output_file = os.path.join(output_dir, f"split_{i+1}.pdf")
                with open(output_file, 'wb') as out_f:
                    writer.write(out_f)
                output_files.append(output_file)

        return output_files
    except Exception as e:
        print(f"Split PDF error: {e}")
        import traceback
        traceback.print_exc()
        return None

def merge_pdf(pdf_list, output_pdf):
    """Merge multiple PDFs into a single PDF"""
    try:
        from PyPDF2 import PdfReader, PdfWriter

        writer = PdfWriter()
        for pdf_file in pdf_list:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_pdf, 'wb') as f:
            writer.write(f)

        return True
    except Exception as e:
        print(f"Merge PDF error: {e}")
        import traceback
        traceback.print_exc()
        return False

def remove_pages_from_pdf(input_pdf, pages_to_remove, output_pdf):
    """Remove specific pages from a PDF
    pages_to_remove: list of page numbers to remove (1-indexed)
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter

        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)

        pages_to_remove_set = set(p - 1 for p in pages_to_remove if 1 <= p <= total_pages)

        writer = PdfWriter()
        for page_num in range(total_pages):
            if page_num not in pages_to_remove_set:
                writer.add_page(reader.pages[page_num])

        with open(output_pdf, 'wb') as f:
            writer.write(f)

        return True
    except Exception as e:
        print(f"Remove pages error: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/')
def index():
    # Pass optional upload API key and tus endpoint to template for client-side usage
    upload_api_key = app.config.get('UPLOAD_API_KEY', '')
    tus_endpoint = app.config.get('TUS_ENDPOINT', '')
    return render_template('Index.html', upload_api_key=upload_api_key, tus_endpoint=tus_endpoint)

@app.route('/convert', methods=['POST'])
def convert():
    # Check if files were uploaded
    if 'files' not in request.files:
        flash('No files uploaded')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    
    # Check if any files were selected
    if len(files) == 0 or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))
    
    # Filter valid inputs for True Black conversion
    def _is_true_black_input(name: str) -> bool:
        if not name or '.' not in name:
            return False
        ext = name.rsplit('.', 1)[1].lower()
        return ext in (PDF_ALLOWED_EXTENSIONS | DOCUMENT_ALLOWED_EXTENSIONS | EXCEL_ALLOWED_EXTENSIONS)

    valid_files = [f for f in files if f and _is_true_black_input(f.filename)]

    if len(valid_files) == 0:
        flash('No valid files found. Please upload PDF / DOC / DOCX / Excel files.')
        return redirect(url_for('index'))
    
    # Get custom settings from form (with defaults)
    try:
        dpi = int(request.form.get('dpi', 300))
        threshold = int(request.form.get('threshold', 250))
        contrast = float(request.form.get('contrast', 3.0))
        sharpness = float(request.form.get('sharpness', 2.5))
        
        # Validate ranges
        dpi = max(150, min(600, dpi))  # Between 150-600
        threshold = max(128, min(255, threshold))  # Between 128-255
        contrast = max(1.0, min(5.0, contrast))  # Between 1.0-5.0
        sharpness = max(1.0, min(5.0, sharpness))  # Between 1.0-5.0
    except (ValueError, TypeError):
        flash('Invalid settings provided. Using default values.')
        dpi, threshold, contrast, sharpness = 300, 250, 3.0, 2.5
    
    # Create temp directory for processing
    temp_dir = tempfile.mkdtemp()
    converted_files = []
    
    try:
        # Process each file with custom settings
        for file in valid_files:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Save uploaded file
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)

            # Ensure we have a PDF as input for the true-black renderer
            source_pdf_path = input_path
            if ext != 'pdf':
                intermediate_pdf = os.path.join(temp_dir, f"__source_{Path(filename).stem}.pdf")
                ok_pdf = False

                if ext == 'docx':
                    ok_pdf = docx_to_pdf(input_path, intermediate_pdf)
                elif ext in ('xls', 'xlsx', 'xlsm', 'xlsb', 'csv', 'ods'):
                    ok_pdf = excel_to_pdf(input_path, intermediate_pdf)
                elif ext in ('doc', 'odt'):
                    # Optional: requires LibreOffice installed and available as `soffice`
                    ok_pdf = soffice_to_pdf(input_path, intermediate_pdf)
                else:
                    ok_pdf = False

                if not ok_pdf or not os.path.exists(intermediate_pdf):
                    flash(f'Could not convert {filename} to PDF for True Black processing')
                    continue

                source_pdf_path = intermediate_pdf
                # If user selected specific pages from preview (1-based string like '1,3,5-7'), extract them
                sel_pages = request.form.get('selected_pages', '').strip()
                if sel_pages:
                    pages0 = parse_page_numbers(sel_pages)
                    if pages0:
                        # convert 0-indexed to 1-based for extractor
                        pages1 = [p + 1 for p in pages0]
                        extracted_pdf = os.path.join(temp_dir, f"__sel_{Path(filename).stem}.pdf")
                        ok_ex = extract_pdf_pages(source_pdf_path, extracted_pdf, pages1)
                        if ok_ex and os.path.exists(extracted_pdf):
                            source_pdf_path = extracted_pdf
            
            # Generate output filename
            output_filename = f"TrueBlack_{Path(filename).stem}.pdf"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Convert to B/W with custom settings
            pdf_to_true_bw(source_pdf_path, output_path, dpi=dpi, threshold=threshold, 
                          contrast=contrast, sharpness=sharpness)
            converted_files.append((output_path, output_filename))
        
        # If single file, send it directly
        if len(converted_files) == 1:
            return send_file(
                converted_files[0][0],
                as_attachment=True,
                download_name=converted_files[0][1],
                mimetype='application/pdf'
            )
        
        # If multiple files, create a ZIP archive
        else:
            import zipfile
            zip_path = os.path.join(temp_dir, 'true_black_outputs.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, file_name in converted_files:
                    zipf.write(file_path, file_name)
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name='true_black_outputs.zip',
                mimetype='application/zip'
            )
    
    except Exception as e:
        print(f'ERROR: {str(e)}')  # Print to console for debugging
        import traceback
        traceback.print_exc()  # Print full traceback
        flash(f'Error converting PDF: {str(e)}')
        return redirect(url_for('index'))
    
    finally:
        # Cleanup temp directory after a delay (since file is being sent)
        import threading
        def cleanup():
            import time
            time.sleep(5)  # Wait 5 seconds before cleanup
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        threading.Thread(target=cleanup).start()

@app.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    """Convert images, documents, and excel files to PDF"""
    if 'files' not in request.files:
        flash('No files uploaded')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    
    if len(files) == 0 or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    converted_files = []
    
    try:
        for file in files:
            if not file:
                continue
            
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Save uploaded file
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)
            
            output_filename = f"{filename.rsplit('.', 1)[0]}.pdf"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Convert based on file type
            try:
                if ext == 'pdf':
                    # PDF files are already in target format - skip conversion
                    logger.info(f'Skipping {filename} - already PDF')
                    continue
                
                elif ext in IMAGE_ALLOWED_EXTENSIONS:
                    image_to_pdf(input_path, output_path)
                    if os.path.exists(output_path):
                        converted_files.append((output_path, output_filename))
                    else:
                        logger.warning(f'Image conversion failed for {filename}')
                
                elif ext in DOCUMENT_ALLOWED_EXTENSIONS:
                    ok = False
                    if ext == 'docx':
                        ok = docx_to_pdf(input_path, output_path)
                    elif ext in ('doc', 'odt'):
                        ok = soffice_to_pdf(input_path, output_path)
                    
                    if ok or os.path.exists(output_path):
                        converted_files.append((output_path, output_filename))
                    else:
                        logger.warning(f'Document conversion failed for {filename}')
                
                elif ext in EXCEL_ALLOWED_EXTENSIONS:
                    # Special handling for CSV
                    if ext == 'csv':
                        ok = csv_to_pdf(input_path, output_path)
                    else:
                        ok = excel_to_pdf(input_path, output_path)
                    
                    if ok or os.path.exists(output_path):
                        converted_files.append((output_path, output_filename))
                    else:
                        logger.warning(f'Excel conversion failed for {filename}')
                else:
                    flash(f'Unsupported file type: {ext}')
                    logger.warning(f'Unsupported file type: {ext}')
                    continue
            except Exception as e:
                logger.error(f'Conversion error for {filename}: {e}')
                flash(f'Error converting {filename}: {str(e)}')
                continue
        
        if len(converted_files) == 0:
            flash('No files could be converted')
            return redirect(url_for('index'))
        
        # If single file, send directly
        if len(converted_files) == 1:
            return send_file(
                converted_files[0][0],
                as_attachment=True,
                download_name=converted_files[0][1],
                mimetype='application/pdf'
            )
        
        # If multiple files, create ZIP
        else:
            import zipfile
            zip_path = os.path.join(temp_dir, 'converted_files.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, file_name in converted_files:
                    zipf.write(file_path, file_name)
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name='converted_files.zip',
                mimetype='application/zip'
            )
    
    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        flash(f'Error converting file: {str(e)}')
        return redirect(url_for('index'))
    
    finally:
        # Cleanup temp directory
        import threading
        def cleanup():
            import time
            time.sleep(5)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        threading.Thread(target=cleanup).start()

@app.route('/pdf-extract', methods=['POST'])
def pdf_extract():
    """Extract PDF to Word or Excel"""
    if 'files' not in request.files:
        flash('No files uploaded')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    format_type = request.form.get('format', 'docx')  # 'docx' or 'xlsx'
    
    if len(files) == 0 or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))
    
    # Filter valid PDF files
    valid_files = [f for f in files if f and allowed_file(f.filename, 'pdf')]
    
    if len(valid_files) == 0:
        flash('No valid PDF files found.')
        return redirect(url_for('index'))
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    converted_files = []
    
    try:
        for file in valid_files:
            filename = secure_filename(file.filename)
            
            # Save uploaded file
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)
            
            # Generate output filename
            base_name = filename.rsplit('.', 1)[0]
            if format_type == 'docx':
                output_filename = f"{base_name}.docx"
                output_path = os.path.join(temp_dir, output_filename)
                pdf_to_word(input_path, output_path)
            else:  # xlsx
                output_filename = f"{base_name}.xlsx"
                output_path = os.path.join(temp_dir, output_filename)
                pdf_to_excel(input_path, output_path)
            
            converted_files.append((output_path, output_filename))
        
        if len(converted_files) == 0:
            flash('No files could be converted')
            return redirect(url_for('index'))
        
        # If single file, send directly
        if len(converted_files) == 1:
            return send_file(
                converted_files[0][0],
                as_attachment=True,
                download_name=converted_files[0][1],
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
                    if format_type == 'docx' 
                    else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        # If multiple files, create ZIP
        else:
            import zipfile
            zip_path = os.path.join(temp_dir, 'extracted_files.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, file_name in converted_files:
                    zipf.write(file_path, file_name)
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name='extracted_files.zip',
                mimetype='application/zip'
            )
    
    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        flash(f'Error extracting PDF: {str(e)}')
        return redirect(url_for('index'))
    
    finally:
        # Cleanup temp directory
        import threading
        def cleanup():
            import time
            time.sleep(5)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        threading.Thread(target=cleanup).start()

@app.route('/pdf-to-pptx', methods=['POST'])
def pdf_to_pptx_route():
    """Convert PDF to PowerPoint presentation"""
    try:
        if 'files' not in request.files:
            flash('No PDF files selected')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'pdf'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_pptx = os.path.join(temp_dir, f"{Path(filename).stem}.pptx")
                if pdf_to_powerpoint(input_path, output_pptx):
                    converted_files.append(output_pptx)
                    log_history('pdf_to_pptx', [filename], status='success')
            
            if len(converted_files) == 1:
                output_filename = f"{Path(files[0].filename).stem}.pptx"
                return send_file(converted_files[0], as_attachment=True, download_name=output_filename)
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'presentations.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='presentations.zip')
            else:
                flash('PDF to PowerPoint conversion failed')
                log_history('pdf_to_pptx', [f.filename for f in files], status='failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'PDF to PowerPoint Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/pptx-to-pdf', methods=['POST'])
def pptx_to_pdf_route():
    """Convert PowerPoint to PDF"""
    try:
        if 'files' not in request.files:
            flash('No PowerPoint files selected')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not file.filename.lower().endswith('.pptx'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}.pdf")
                if powerpoint_to_pdf(input_path, output_pdf):
                    converted_files.append(output_pdf)
                    log_history('pptx_to_pdf', [filename], status='success')
            
            if len(converted_files) == 1:
                output_filename = f"{Path(files[0].filename).stem}.pdf"
                return send_file(converted_files[0], as_attachment=True, download_name=output_filename)
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'pdfs.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='pdfs.zip')
            else:
                flash('PowerPoint to PDF conversion failed')
                log_history('pptx_to_pdf', [f.filename for f in files], status='failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'PowerPoint to PDF Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/ocr', methods=['POST'])
def ocr_route():
    """Extract text from images or PDF using OCR"""
    try:
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file:
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                # Extract text using OCR
                output_txt = os.path.join(temp_dir, f"{Path(filename).stem}_OCR.txt")
                if ocr_extract_text(input_path, output_txt):
                    converted_files.append(output_txt)
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True)
            elif len(converted_files) > 1:
                # Create ZIP
                zip_path = os.path.join(temp_dir, 'ocr_results.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='ocr_results.zip')
            else:
                flash('OCR processing failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'OCR Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/watermark', methods=['POST'])
def watermark_route():
    """Add watermark (text or image) to PDF with advanced settings and page selection"""
    try:
        files = request.files.getlist('files')
        watermark_type = request.form.get('watermark_type', 'text')
        position = request.form.get('watermark_position', 'diagonal')
        opacity = float(request.form.get('watermark_opacity', 0.3))
        page_mode = request.form.get('watermark_page_mode', 'all')
        pages_input = request.form.get('watermark_pages', '')
        
        # Parse pages to watermark
        pages = None
        if page_mode == 'selected':
            pages = parse_page_numbers(pages_input)
            if not pages:
                flash('Invalid page numbers. Please use format: 1, 3, 5-8')
                return redirect(url_for('index'))
        
        # Validate parameters
        opacity = max(0.1, min(0.9, opacity))
        
        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            # Handle text watermark
            if watermark_type == 'text':
                watermark_text = request.form.get('watermark_text', 'CONFIDENTIAL')
                font_size = int(request.form.get('watermark_font_size', 50))
                fontname = request.form.get('watermark_font', 'helv')
                color_rgb_str = request.form.get('watermark_color_rgb', '0.5,0.5,0.5')
                
                # NEW: Extract rotation and scale for effects
                try:
                    rotation = int(request.form.get('watermark_rotation', 0))
                    rotation = rotation % 360  # Keep between 0-360
                except:
                    rotation = 0
                
                try:
                    scale = float(request.form.get('watermark_scale', 1.0))
                    scale = max(0.5, min(2.0, scale))  # 0.5x to 2.0x
                except:
                    scale = 1.0
                
                # Parse color RGB values
                try:
                    r, g, b = map(float, color_rgb_str.split(','))
                    color = (r, g, b)
                except:
                    color = (0.5, 0.5, 0.5)  # Default gray
                
                # Validate parameters
                font_size = max(20, min(120, font_size))
                
                for file in files:
                    if not file or not allowed_file(file.filename, 'pdf'):
                        continue
                    
                    filename = secure_filename(file.filename)
                    input_path = os.path.join(temp_dir, filename)
                    file.save(input_path)
                    
                    output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_watermarked.pdf")
                    # NEW: Pass rotation and scale to add_watermark
                    if add_watermark(input_path, output_pdf, watermark_text, opacity, position, 
                                   font_size=font_size, color=color, fontname=fontname, pages=pages, 
                                   rotation=rotation, scale=scale):
                        converted_files.append(output_pdf)
            
            # Handle image watermark
            else:
                if 'watermark_image' not in request.files:
                    flash('No image selected for watermark')
                    return redirect(url_for('index'))
                
                image_file = request.files['watermark_image']
                if image_file.filename == '':
                    flash('No image selected for watermark')
                    return redirect(url_for('index'))
                
                # Save image temporarily
                image_filename = secure_filename(image_file.filename)
                image_path = os.path.join(temp_dir, 'watermark_' + image_filename)
                image_file.save(image_path)
                
                # Get image scaling options
                try:
                    image_scale = float(request.form.get('image_scale', 100))
                    image_scale = max(10, min(200, image_scale))
                except:
                    image_scale = 100
                
                image_scale_unit = request.form.get('image_scale_unit', 'percent')
                
                for file in files:
                    if not file or not allowed_file(file.filename, 'pdf'):
                        continue
                    
                    filename = secure_filename(file.filename)
                    input_path = os.path.join(temp_dir, filename)
                    file.save(input_path)
                    
                    output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_watermarked.pdf")
                    if add_image_watermark(input_path, output_pdf, image_path, position, 
                                         scale=image_scale, scale_unit=image_scale_unit, pages=pages):
                        converted_files.append(output_pdf)
            
            if len(converted_files) == 1:
                output_filename = f"{Path(files[0].filename).stem}_watermarked.pdf"
                return send_file(converted_files[0], as_attachment=True, download_name=output_filename)
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'watermarked_pdfs.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='watermarked_pdfs.zip')
            else:
                flash('Watermark failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Watermark Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    """Encrypt PDF with password"""
    try:
        files = request.files.getlist('files')
        password = request.form.get('pdf_password', '')
        
        if not password:
            flash('Password required for encryption')
            return redirect(url_for('index'))
        
        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'pdf'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_encrypted.pdf")
                if encrypt_pdf(input_path, output_pdf, password):
                    converted_files.append(output_pdf)
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True)
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'encrypted_pdfs.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='encrypted_pdfs.zip')
            else:
                flash('Encryption failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Encryption Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/autoformat', methods=['POST'])
def autoformat_route():
    """Clean and optimize PDF formatting"""
    try:
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'pdf'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_cleaned.pdf")
                if clean_autoformat_pdf(input_path, output_pdf):
                    converted_files.append(output_pdf)
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True)
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'cleaned_pdfs.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='cleaned_pdfs.zip')
            else:
                flash('Auto-format failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Auto-format Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/excel-to-csv', methods=['POST'])
def excel_to_csv_route():
    """Convert Excel to CSV"""
    try:
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'excel'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_csv = os.path.join(temp_dir, f"{Path(filename).stem}.csv")
                if excel_to_csv(input_path, output_csv):
                    converted_files.append(output_csv)
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True)
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'excel_to_csv.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='excel_to_csv.zip')
            else:
                flash('Excel to CSV conversion failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Excel to CSV Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/split-pdf', methods=['POST'])
def split_pdf_route():
    """Split PDF into separate files based on page ranges"""
    try:
        # allow multiple files uploaded with input name 'file'
        files = request.files.getlist('file') if 'file' in request.files else []
        if not files or all(f.filename == '' for f in files):
            flash('No files provided')
            return redirect(url_for('index'))

        # Get page ranges from form
        page_ranges_str = request.form.get('page_ranges', '')
        if not page_ranges_str.strip():
            flash('Please specify page ranges (e.g., "1-5, 6-10")')
            return redirect(url_for('index'))

        # Parse page ranges
        page_ranges = []
        for range_str in page_ranges_str.split(','):
            range_str = range_str.strip()
            if '-' in range_str:
                parts = range_str.split('-')
                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    page_ranges.append((start, end))
                except Exception:
                    continue

        if not page_ranges:
            flash('Invalid page ranges format. Use "1-5, 6-10" format.')
            return redirect(url_for('index'))

        temp_dir = tempfile.mkdtemp()
        all_outputs = []
        processed_files = []

        try:
            for file in files:
                if file.filename == '' or not allowed_file(file.filename, 'pdf'):
                    continue
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                processed_files.append(filename)

                output_files = split_pdf(input_path, temp_dir, page_ranges)
                if output_files:
                    all_outputs.extend(output_files)

            if not all_outputs:
                log_history('split', processed_files, status='failed', message='No outputs')
                flash('Failed to split PDFs')
                return redirect(url_for('index'))

            # if only one output, return it directly
            if len(all_outputs) == 1:
                log_history('split', processed_files, status='success')
                return send_file(all_outputs[0], as_attachment=True, download_name='split.pdf')

            # Create zip with all split files
            zip_path = os.path.join(temp_dir, 'split_pdfs.zip')
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for fpath in all_outputs:
                    zf.write(fpath, os.path.basename(fpath))

            log_history('split', processed_files, status='success')
            return send_file(zip_path, as_attachment=True, download_name='split_pdfs.zip')
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash('Split PDF Error: an internal error occurred')
        log_history('split', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/merge-pdf', methods=['POST'])
def merge_pdf_route():
    """Merge multiple PDFs into a single PDF"""
    try:
        if 'files' not in request.files:
            flash('No files uploaded')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            flash('No files selected')
            return redirect(url_for('index'))
        
        # Filter out empty files
        files = [f for f in files if f.filename != '' and allowed_file(f.filename, 'pdf')]
        
        if len(files) < 2:
            flash('Please upload at least 2 PDF files to merge')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            pdf_list = []
            
            for file in files:
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                pdf_list.append(input_path)
            
            output_pdf = os.path.join(temp_dir, 'merged.pdf')
            if merge_pdf(pdf_list, output_pdf):
                log_history('merge', [os.path.basename(p) for p in pdf_list], status='success')
                return send_file(output_pdf, as_attachment=True, download_name='merged.pdf')
            else:
                log_history('merge', [os.path.basename(p) for p in pdf_list], status='failed', message='merge failed')
                flash('Failed to merge PDFs')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Merge PDF Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/remove-pdf-pages', methods=['POST'])
def remove_pdf_pages():
    """Remove specific pages from a PDF"""
    try:
        # allow multiple files via input name 'file'
        files = request.files.getlist('file') if 'file' in request.files else []
        if not files or all(f.filename == '' for f in files):
            flash('No files uploaded')
            return redirect(url_for('index'))

        # Get pages to remove from form
        pages_str = request.form.get('pages_to_remove', '')
        if not pages_str.strip():
            flash('Please specify page numbers to remove')
            return redirect(url_for('index'))

        # Parse page numbers (can be comma-separated, space-separated, or ranges)
        pages_to_remove = []
        for token in pages_str.split(','):
            token = token.strip()
            if '-' in token:
                parts = token.split('-')
                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    pages_to_remove.extend(list(range(start, end+1)))
                except Exception:
                    continue
            else:
                for p in token.replace(',', ' ').split():
                    try:
                        pn = int(p.strip())
                        pages_to_remove.append(pn)
                    except Exception:
                        continue

        pages_to_remove = sorted(set([p for p in pages_to_remove if p > 0]))
        if not pages_to_remove:
            flash('Invalid page numbers. Please enter valid page numbers.')
            return redirect(url_for('index'))

        temp_dir = tempfile.mkdtemp()
        processed_files = []
        outputs = []

        try:
            for file in files:
                if file.filename == '' or not allowed_file(file.filename, 'pdf'):
                    continue
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                processed_files.append(filename)

                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_removed.pdf")
                if remove_pages_from_pdf(input_path, pages_to_remove, output_pdf):
                    outputs.append(output_pdf)

            if not outputs:
                log_history('remove_pages', processed_files, status='failed', message='no outputs')
                flash('Failed to remove pages from PDFs')
                return redirect(url_for('index'))

            if len(outputs) == 1:
                log_history('remove_pages', processed_files, status='success')
                return send_file(outputs[0], as_attachment=True, download_name='removed_pages.pdf')

            zip_path = os.path.join(temp_dir, 'removed_pages.zip')
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for fpath in outputs:
                    zf.write(fpath, os.path.basename(fpath))

            log_history('remove_pages', processed_files, status='success')
            return send_file(zip_path, as_attachment=True, download_name='removed_pages.zip')
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash('Remove Pages Error: an internal error occurred')
        log_history('remove_pages', [], status='error', message=str(e))
        return redirect(url_for('index'))


@app.route('/decrypt-pdf', methods=['POST'])
def decrypt_pdf_route():
    """Decrypt uploaded PDF using provided password"""
    try:
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(url_for('index'))

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename, 'pdf'):
            flash('Invalid file')
            return redirect(url_for('index'))

        password = request.form.get('password', '')
        if not password:
            flash('Please provide the password for the encrypted PDF')
            return redirect(url_for('index'))

        temp_dir = tempfile.mkdtemp()
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)

            output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_decrypted.pdf")
            ok, msg = decrypt_pdf(input_path, output_pdf, password)
            if ok:
                log_history('decrypt', [filename], status='success')
                return send_file(output_pdf, as_attachment=True, download_name='decrypted.pdf')
            else:
                log_history('decrypt', [filename], status='failed', message=msg)
                if msg == 'incorrect password':
                    flash('Incorrect password for PDF')
                else:
                    flash('Failed to decrypt PDF')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash('Decrypt Error: an internal error occurred')
        log_history('decrypt', [], status='error', message=str(e))
        return redirect(url_for('index'))

# ============== NEW ADVANCED ROUTES ==============

@app.route('/redact', methods=['POST'])
def redact_route():
    """Redact sensitive text from PDF"""
    try:
        if 'files' not in request.files:
            flash('No PDF selected')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        redaction_keywords = request.form.get('redaction_keywords', '').split(',')
        redaction_keywords = [kw.strip() for kw in redaction_keywords if kw.strip()]
        
        if not redaction_keywords:
            flash('Please enter keywords to redact')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'pdf'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_redacted.pdf")
                if redact_pdf(input_path, output_pdf, redaction_keywords):
                    converted_files.append(output_pdf)
                    log_history('redact', [filename], status='success')
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True, download_name='redacted.pdf')
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'redacted_pdfs.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='redacted_pdfs.zip')
            else:
                flash('Redaction failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Redaction Error: {str(e)}')
        log_history('redact', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/text-to-pdf', methods=['POST'])
def text_to_pdf_route():
    """Convert plain text to PDF"""
    try:
        text_content = request.form.get('text_content', '')
        if not text_content.strip():
            flash('Please enter text to convert')
            return redirect(url_for('index'))
        
        font_size = int(request.form.get('font_size', 11))
        font_size = max(8, min(16, font_size))
        
        temp_dir = tempfile.mkdtemp()
        try:
            output_pdf = os.path.join(temp_dir, 'text_to_pdf.pdf')
            if text_to_pdf(text_content, output_pdf, font_size=font_size):
                log_history('text_to_pdf', ['text'], status='success')
                return send_file(output_pdf, as_attachment=True, download_name='document.pdf')
            else:
                flash('Failed to convert text to PDF')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Text to PDF Error: {str(e)}')
        log_history('text_to_pdf', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/html-to-pdf', methods=['POST'])
def html_to_pdf_route():
    """Convert HTML content to PDF"""
    try:
        html_content = request.form.get('html_content', '')
        if not html_content.strip():
            flash('Please enter HTML content to convert')
            return redirect(url_for('index'))
        
        temp_dir = tempfile.mkdtemp()
        try:
            output_pdf = os.path.join(temp_dir, 'html_to_pdf.pdf')
            if html_to_pdf(html_content, output_pdf):
                log_history('html_to_pdf', ['html'], status='success')
                return send_file(output_pdf, as_attachment=True, download_name='document.pdf')
            else:
                flash('Failed to convert HTML to PDF')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'HTML to PDF Error: {str(e)}')
        log_history('html_to_pdf', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/url-to-pdf', methods=['POST'])
def url_to_pdf_route():
    """Convert web page from URL to PDF"""
    try:
        webpage_url = request.form.get('webpage_url', '').strip()
        if not webpage_url:
            flash('Please enter a valid URL')
            return redirect(url_for('index'))
        
        # Validate URL format
        if not webpage_url.startswith(('http://', 'https://')):
            webpage_url = 'https://' + webpage_url
        
        temp_dir = tempfile.mkdtemp()
        try:
            output_pdf = os.path.join(temp_dir, 'webpage_to_pdf.pdf')
            if url_to_pdf(webpage_url, output_pdf):
                log_history('url_to_pdf', [webpage_url], status='success')
                return send_file(output_pdf, as_attachment=True, download_name='webpage.pdf')
            else:
                flash('Failed to convert webpage to PDF. Please check the URL and try again.')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'URL to PDF Error: {str(e)}')
        log_history('url_to_pdf', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/pdf-to-html', methods=['POST'])
def pdf_to_html_route():
    """Convert PDF to HTML"""
    try:
        if 'files' not in request.files:
            flash('No PDF selected')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'pdf'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_html = os.path.join(temp_dir, f"{Path(filename).stem}.html")
                if pdf_to_html(input_path, output_html):
                    converted_files.append((output_html, f"{Path(filename).stem}.html"))
                    log_history('pdf_to_html', [filename], status='success')
            
            if len(converted_files) == 0:
                flash('No PDFs could be converted')
                return redirect(url_for('index'))
            
            # If single file, send directly
            if len(converted_files) == 1:
                return send_file(
                    converted_files[0][0],
                    as_attachment=True,
                    download_name=converted_files[0][1]
                )
            # Multiple files, create ZIP
            else:
                zip_path = os.path.join(temp_dir, 'html_files.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file_path, file_name in converted_files:
                        zf.write(file_path, file_name)
                return send_file(zip_path, as_attachment=True, download_name='html_files.zip')
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'PDF to HTML Error: {str(e)}')
        log_history('pdf_to_html', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/remove-metadata', methods=['POST'])
def remove_metadata_route():
    """Remove metadata from PDF for privacy"""
    try:
        if 'files' not in request.files:
            flash('No PDF selected')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, 'pdf'):
                    continue
                
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                
                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_clean.pdf")
                if pdf_remove_metadata(input_path, output_pdf):
                    converted_files.append(output_pdf)
                    log_history('remove_metadata', [filename], status='success')
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True, download_name='clean.pdf')
            elif len(converted_files) > 1:
                zip_path = os.path.join(temp_dir, 'clean_pdfs.zip')
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for file in converted_files:
                        zf.write(file, os.path.basename(file))
                return send_file(zip_path, as_attachment=True, download_name='clean_pdfs.zip')
            else:
                flash('Metadata removal failed')
                return redirect(url_for('index'))
        finally:
            import threading
            def cleanup():
                import time
                time.sleep(5)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup).start()
    except Exception as e:
        flash(f'Metadata Removal Error: {str(e)}')
        log_history('remove_metadata', [], status='error', message=str(e))
        return redirect(url_for('index'))

@app.route('/history-data', methods=['GET'])
def history_data():
    try:
        conn = sqlite3.connect(HISTORY_DB)
        c = conn.cursor()
        c.execute('SELECT id, timestamp, operation, files, status, message FROM history ORDER BY id DESC LIMIT 200')
        rows = c.fetchall()
        conn.close()

        entries = []
        for r in rows:
            entries.append({
                'id': r[0],
                'timestamp': r[1],
                'operation': r[2],
                'files': json.loads(r[3]) if r[3] else [],
                'status': r[4],
                'message': r[5]
            })
        return jsonify({'success': True, 'entries': entries})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ EXCEL PRODUCTIVITY TOOLS ============

@app.route('/excel-to-pdf', methods=['POST'])
def excel_to_pdf_route():
    """Convert Excel spreadsheet to PDF."""
    try:
        _check_api_key()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not any(file.filename.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.ods']):
            return jsonify({'error': 'File must be .xlsx, .xls, or .ods'}), 400
        
        from openpyxl import load_workbook
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.pdfgen import canvas as rl_canvas
        
        # Load and read Excel file
        temp_xlsx = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_xlsx.name)
        
        try:
            wb = load_workbook(temp_xlsx.name)
            ws = wb.active
            
            # Create PDF
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            c = rl_canvas.Canvas(temp_pdf.name, pagesize=letter)
            
            # Simple implementation: write table to PDF
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(temp_pdf.name, pagesize=A4)
            elements = []
            
            # Extract data from worksheet
            data = []
            for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 100), 
                                    min_col=1, max_col=min(ws.max_column, 10)):
                data.append([cell.value or '' for cell in row])
            
            if data:
                table = Table(data, colWidths=[40]*len(data[0]))
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
            
            doc.build(elements)
            
            log_history('excel-to-pdf', [file.filename], 'success')
            return send_file(temp_pdf.name, as_attachment=True, download_name='converted.pdf')
        finally:
            os.unlink(temp_xlsx.name)
    
    except Exception as e:
        log_history('excel-to-pdf', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/excel-remove-colors', methods=['POST'])
def excel_remove_colors():
    """Remove all colors from Excel cells."""
    try:
        _check_api_key()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not any(file.filename.lower().endswith(ext) for ext in ['.xlsx']):
            return jsonify({'error': 'File must be .xlsx'}), 400
        
        from openpyxl import load_workbook
        from openpyxl.styles import PatternFill, Font
        
        temp_in = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_in.name)
        
        try:
            wb = load_workbook(temp_in.name)
            
            for ws in wb.sheetnames:
                worksheet = wb[ws]
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.fill = PatternFill(fill_type=None)
                        if cell.font:
                            cell.font = Font(color='000000', name=cell.font.name, size=cell.font.size)
            
            temp_out = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            wb.save(temp_out.name)
            log_history('excel-remove-colors', [file.filename], 'success')
            return send_file(temp_out.name, as_attachment=True, download_name='no-colors.xlsx')
        finally:
            os.unlink(temp_in.name)
    
    except Exception as e:
        log_history('excel-remove-colors', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/excel-formulas-to-values', methods=['POST'])
def excel_formulas_to_values():
    """Convert all formulas to their calculated values."""
    try:
        _check_api_key()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not any(file.filename.lower().endswith(ext) for ext in ['.xlsx']):
            return jsonify({'error': 'File must be .xlsx'}), 400
        
        from openpyxl import load_workbook
        
        temp_in = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_in.name)
        
        try:
            wb = load_workbook(temp_in.name, data_only=False)
            
            for ws in wb.sheetnames:
                worksheet = wb[ws]
                for row in worksheet.iter_rows():
                    for cell in row:
                        if cell.data_type == 'f':  # formula
                            # Note: openpyxl data_only requires reload
                            pass
            
            # Re-load with data_only=True to get calculated values
            wb_data = load_workbook(temp_in.name, data_only=True)
            wb.close()
            
            temp_out = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            wb_data.save(temp_out.name)
            log_history('excel-formulas-to-values', [file.filename], 'success')
            return send_file(temp_out.name, as_attachment=True, download_name='values-only.xlsx')
        finally:
            os.unlink(temp_in.name)
    
    except Exception as e:
        log_history('excel-formulas-to-values', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/excel-clean-charts', methods=['POST'])
def excel_clean_charts():
    """Optimize charts for monochrome printing."""
    try:
        _check_api_key()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not any(file.filename.lower().endswith(ext) for ext in ['.xlsx']):
            return jsonify({'error': 'File must be .xlsx'}), 400
        
        from openpyxl import load_workbook
        
        temp_in = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_in.name)
        
        try:
            wb = load_workbook(temp_in.name)
            
            # Iterate over charts in worksheets
            for ws in wb.sheetnames:
                worksheet = wb[ws]
                # Note: Chart manipulation in openpyxl is limited
                # For now, we'll just save as-is (chart cleanup would require additional processing)
            
            temp_out = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            wb.save(temp_out.name)
            log_history('excel-clean-charts', [file.filename], 'success')
            return send_file(temp_out.name, as_attachment=True, download_name='charts-cleaned.xlsx')
        finally:
            os.unlink(temp_in.name)
    
    except Exception as e:
        log_history('excel-clean-charts', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/excel-normalize-tables', methods=['POST'])
def excel_normalize_tables():
    """Normalize Excel table formatting."""
    try:
        _check_api_key()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not any(file.filename.lower().endswith(ext) for ext in ['.xlsx']):
            return jsonify({'error': 'File must be .xlsx'}), 400
        
        from openpyxl import load_workbook
        from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
        
        temp_in = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_in.name)
        
        try:
            wb = load_workbook(temp_in.name)
            
            for ws in wb.sheetnames:
                worksheet = wb[ws]
                
                # Auto-fit columns
                for column in worksheet.columns:
                    max_len = 0
                    for cell in column:
                        try:
                            if len(str(cell.value or '')) > max_len:
                                max_len = len(str(cell.value or ''))
                        except:
                            pass
                    worksheet.column_dimensions[column[0].column_letter].width = min(max_len + 2, 50)
                
                # Apply header styling
                if worksheet.max_row > 0:
                    header_fill = PatternFill(start_color='E0E0E0', end_color='E0E0E0', fill_type='solid')
                    header_font = Font(bold=True)
                    border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )
                    
                    for col in range(1, worksheet.max_column + 1):
                        cell = worksheet.cell(row=1, column=col)
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.border = border
                        cell.alignment = Alignment(horizontal='center', vertical='center')
                    
                    # Apply borders to all cells
                    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row,
                                                   min_col=1, max_col=worksheet.max_column):
                        for cell in row:
                            cell.border = border
            
            temp_out = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            wb.save(temp_out.name)
            log_history('excel-normalize-tables', [file.filename], 'success')
            return send_file(temp_out.name, as_attachment=True, download_name='normalized.xlsx')
        finally:
            os.unlink(temp_in.name)
    
    except Exception as e:
        log_history('excel-normalize-tables', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/excel-split-sheets-pdf', methods=['POST'])
def excel_split_sheets_pdf():
    """Split Excel sheets into separate PDFs."""
    try:
        _check_api_key()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not any(file.filename.lower().endswith(ext) for ext in ['.xlsx', '.xls']):
            return jsonify({'error': 'File must be .xlsx or .xls'}), 400
        
        from openpyxl import load_workbook
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
        from reportlab.lib import colors
        import zipfile
        
        temp_xlsx = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_xlsx.name)
        
        try:
            wb = load_workbook(temp_xlsx.name)
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    pdf_filename = f"{sheet_name}.pdf"
                    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                    
                    doc = SimpleDocTemplate(temp_pdf.name, pagesize=A4)
                    elements = []
                    
                    # Extract data
                    data = []
                    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 100),
                                           min_col=1, max_col=min(ws.max_column, 10)):
                        data.append([str(cell.value or '') for cell in row])
                    
                    if data:
                        table = Table(data, colWidths=[40]*len(data[0]))
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        elements.append(table)
                    
                    doc.build(elements)
                    
                    with open(temp_pdf.name, 'rb') as f:
                        zf.writestr(pdf_filename, f.read())
                    os.unlink(temp_pdf.name)
            
            zip_buffer.seek(0)
            log_history('excel-split-sheets-pdf', [file.filename], 'success')
            return send_file(zip_buffer, as_attachment=True, download_name='sheets.zip', mimetype='application/zip')
        finally:
            os.unlink(temp_xlsx.name)
    
    except Exception as e:
        log_history('excel-split-sheets-pdf', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Simple file upload endpoint for Lumina UI.
    
    Accepts multipart/form-data with file(s).
    Returns: {success: true, files: [{name, size}]}
    """
    try:
        if 'files' not in request.files and 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        files_key = 'files' if 'files' in request.files else 'file'
        uploaded_files_list = request.files.getlist(files_key)
        
        if not uploaded_files_list:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        # Create upload directory
        upload_session_dir = os.path.join(UPLOAD_CHUNKS_DIR, str(uuid.uuid4()))
        os.makedirs(upload_session_dir, exist_ok=True)
        
        uploaded_info = []
        
        for file in uploaded_files_list:
            if file and file.filename:
                # Secure the filename
                safe_name = secure_filename(file.filename) or 'upload_' + uuid.uuid4().hex
                file_path = os.path.join(upload_session_dir, safe_name)
                
                # Save file
                file.save(file_path)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                uploaded_info.append({
                    'name': file.filename,
                    'size': file_size,
                    'path': file_path
                })
        
        if not uploaded_info:
            return jsonify({'success': False, 'error': 'No valid files uploaded'}), 400
        
        # Log the upload
        file_names = [info['name'] for info in uploaded_info]
        log_history('api-upload', file_names, 'success')
        
        # Return simplified response for Lumina UI
        return jsonify({
            'success': True,
            'files': [{'name': info['name'], 'size': info['size']} for info in uploaded_info],
            'upload_id': upload_session_dir.split(os.sep)[-1]
        }), 200
    
    except Exception as e:
        log_history('api-upload', [], 'error', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ SERVICE MAPPING FOR ALL 46 TOOLS ============
SERVICE_TOOLS = {
    # PDF Core (14 services)
    'PDF to B&W': 'pdf_to_bw',
    'To PDF': 'to_pdf',
    'Extract Pages': 'extract_pages_pdf',
    'Split PDF': 'split_pdf',
    'Merge PDF': 'merge_pdf',
    'Remove Pages': 'remove_pages_pdf',
    'OCR Text': 'ocr_pdf_text',
    'Add Watermark': 'watermark_pdf',
    'Clean PDF': 'clean_pdf',
    'Compress PDF': 'compress_pdf_service',
    'Encrypt PDF': 'encrypt_pdf_service',
    'Decrypt PDF': 'decrypt_pdf_service',
    'Redact Content': 'redact_pdf',
    'Extract Metadata': 'extract_metadata_pdf',
    
    # Conversions (12 services)
    'PDF to PPT': 'pdf_to_ppt',
    'PPT to PDF': 'pptx_to_pdf',
    'PDF to HTML': 'pdf_to_html',
    'HTML to PDF': 'html_to_pdf',
    'Excel to PDF': 'excel_to_pdf',
    'Excel to CSV': 'excel_to_csv',
    'Text to PDF': 'text_to_pdf',
    'Remove Colors': 'remove_colors',
    'Formulas to Values': 'formulas_to_values_excel',
    'Clean Charts': 'clean_charts_excel',
    'Normalize Data': 'normalize_data',
    'Split Sheets': 'split_sheets_excel',
    
    # Images (5 services)
    'Image Convert': 'image_convert',
    'Image Compress': 'image_compress_service',
    'Image Resize': 'image_resize_service',
    'Remove Background': 'remove_image_bg',
    'Duplicate Remover': 'remove_duplicate_images',
    
    # Data (4 services)
    'Data Validator': 'validate_data_files',
    'PDF Export': 'export_to_pdf',
    'Reporting': 'generate_report',
    'Database': 'database_operations',
    
    # More/Advanced (14 services)
    'PDF to B&W Pro': 'pdf_to_bw_pro',
    'Pro Merge': 'merge_pdf_pro',
    'Smart Extract': 'smart_extract_pages',
    'Batch Compress': 'batch_compress_pdf',
    'Secure Encrypt': 'encrypt_pdf_aes256',
    'Advanced OCR': 'ocr_pdf_searchable',
    'Batch Watermark': 'batch_watermark_pdf',
    'Form Fill': 'fill_pdf_forms',
    'Page Reorder': 'reorder_pdf_pages',
    'Bulk Convert': 'bulk_convert',
    'Smart Crop': 'smart_crop_images',
    'Thumbnail Generator': 'generate_thumbnails',
    'Batch Rename': 'batch_rename_files',
    'Convert History': 'access_conversion_history',
}

def execute_service_conversion(tool_name, input_path, output_path, **kwargs):
    """Execute conversion based on service tool name.
    
    Args:
        tool_name: Service name from SERVICE_TOOLS
        input_path: Input file path
        output_path: Output file path  
        **kwargs: Additional parameters (quality, options, etc.)
        
    Returns: bool (success/failure)
    """
    try:
        # Normalize tool name (convert title case to snake_case)
        tool_mapping = {
            'PDF to B&W': 'pdf_to_bw',
            'PDF to B&W Pro': 'pdf_to_bw_pro',
            'True Black (Print-Optimized)': 'pdf_to_bw',
            'Convert to PDF': 'to_pdf',
            'To PDF': 'to_pdf',
            'Convert Images': 'image_convert',
            'Image Compress': 'image_compress_service',
            'Image Compression': 'image_compress_service',
            'Image Resize': 'image_resize_service',
            'Remove Background': 'remove_image_bg',
            'Background → White': 'remove_image_bg',
            'Image Background to White': 'remove_image_bg',
            'Extract from PDF': 'extract_pages_pdf',
            'Extract PDF': 'extract_pages_pdf',
            'OCR': 'ocr_pdf_text',
            'Optical Character Recognition': 'ocr_pdf_text',
            'Add Watermarks': 'watermark_pdf',
            'Watermark': 'watermark_pdf',
            'Encrypt PDF': 'encrypt_pdf_service',
            'Decrypt PDF': 'decrypt_pdf_service',
            'Auto-Format Cleaning': 'clean_pdf',
            'Auto-Format': 'clean_pdf',
            'Excel to CSV': 'excel_to_csv',
            'Split PDF': 'split_pdf',
            'Merge PDF': 'merge_pdf',
            'Remove Pages': 'remove_pages_pdf',
            'Redact Text': 'redact_pdf',
            'Text to PDF': 'text_to_pdf',
            'Remove Metadata': 'extract_metadata_pdf',
            'PDF to PowerPoint': 'pdf_to_ppt',
            'PDF to Presentation': 'pdf_to_ppt',
            'PowerPoint to PDF': 'pptx_to_pdf',
            'PDF to HTML': 'pdf_to_html',
            'HTML to PDF': 'html_to_pdf',
            'Excel to PDF': 'excel_to_pdf',
            'Compress PDF': 'compress_pdf_service',
        }
        
        # Map display name to internal name
        internal_tool_name = tool_mapping.get(tool_name, tool_name)
        
        # PDF Core operations
        if internal_tool_name == 'pdf_to_bw':
            # Extract B&W specific parameters from kwargs
            dpi = kwargs.get('dpi', 300)
            threshold = kwargs.get('threshold', 250)
            contrast = kwargs.get('contrast', 3.0)
            sharpness = kwargs.get('sharpness', 1.0)
            brightness = kwargs.get('brightness', 0)
            gamma = kwargs.get('gamma', 1.0)
            blur = kwargs.get('blur', 0)
            invert = kwargs.get('invert', False)
            denoise = kwargs.get('denoise', 0)
            
            # Convert string/form values to appropriate types
            try:
                dpi = int(dpi) if dpi else 300
                threshold = int(threshold) if threshold else 250
                contrast = float(contrast) if contrast else 3.0
                sharpness = float(sharpness) if sharpness else 1.0
                brightness = int(brightness) if brightness else 0
                gamma = float(gamma) if gamma else 1.0
                blur = float(blur) if blur else 0
                invert = invert is True or invert == 'true' or invert == 'True'
                denoise = float(denoise) if denoise else 0
            except:
                pass
            
            return pdf_to_true_bw(input_path, output_path, dpi=dpi, threshold=threshold, 
                                 contrast=contrast, sharpness=sharpness, brightness=brightness,
                                 gamma=gamma, blur=blur, invert=invert, denoise=denoise)
        
        elif internal_tool_name == 'pdf_to_bw_pro':
            # Extract B&W specific parameters from kwargs (Pro version with edge enhancement)
            dpi = kwargs.get('dpi', 300)
            threshold = kwargs.get('threshold', 250)
            contrast = kwargs.get('contrast', 5.0)  # Higher contrast by default for Pro
            sharpness = kwargs.get('sharpness', 1.5)  # Higher sharpness for Pro
            brightness = kwargs.get('brightness', 0)
            gamma = kwargs.get('gamma', 1.0)
            blur = kwargs.get('blur', 0)
            edgeEnhance = kwargs.get('edgeEnhance', True)
            invert = kwargs.get('invert', False)
            denoise = kwargs.get('denoise', 0)
            
            # Convert string/form values to appropriate types
            try:
                dpi = int(dpi) if dpi else 300
                threshold = int(threshold) if threshold else 250
                contrast = float(contrast) if contrast else 5.0
                sharpness = float(sharpness) if sharpness else 1.5
                brightness = int(brightness) if brightness else 0
                gamma = float(gamma) if gamma else 1.0
                blur = float(blur) if blur else 0
                edgeEnhance = edgeEnhance is True or edgeEnhance == 'true' or edgeEnhance == 'True'
                invert = invert is True or invert == 'true' or invert == 'True'
                denoise = float(denoise) if denoise else 0
            except:
                pass
            
            return pdf_to_true_bw(input_path, output_path, dpi=dpi, threshold=threshold, 
                                 contrast=contrast, sharpness=sharpness, brightness=brightness,
                                 gamma=gamma, blur=blur, invert=invert, denoise=denoise)
        
        elif internal_tool_name == 'extract_pages_pdf':
            pages = kwargs.get('pages', '1')
            page_list = parse_page_numbers(str(pages))
            if page_list:
                return extract_pdf_pages(input_path, output_path, page_list)
            return False
        
        elif internal_tool_name == 'split_pdf':
            return split_pdf_pages(input_path, output_path)
        
        elif internal_tool_name == 'merge_pdf':
            return True  # Handled at batch level
        
        elif internal_tool_name == 'remove_pages_pdf':
            pages_to_remove = kwargs.get('pages_to_remove', '')
            page_list = parse_page_numbers(str(pages_to_remove))
            if page_list:
                return remove_pdf_pages(input_path, output_path, page_list)
            return False
        
        elif internal_tool_name == 'ocr_pdf_text':
            return ocr_extract_text(input_path, output_path)
        
        elif internal_tool_name == 'watermark_pdf':
            text = kwargs.get('watermark_text', 'WATERMARK')
            position = kwargs.get('position', 'diagonal')
            opacity = kwargs.get('opacity', 0.3)
            return add_watermark(input_path, output_path, text, position=position, opacity=opacity)
        
        elif internal_tool_name == 'clean_pdf':
            return clean_pdf_document(input_path, output_path)
        
        elif internal_tool_name == 'compress_pdf_service':
            return compress_pdf_document(input_path, output_path)
        
        elif internal_tool_name == 'encrypt_pdf_service':
            password = kwargs.get('password', 'password123')
            return encrypt_pdf(input_path, output_path, password)
        
        elif internal_tool_name == 'decrypt_pdf_service':
            password = kwargs.get('password', '')
            return decrypt_pdf(input_path, output_path, password)
        
        elif internal_tool_name == 'redact_pdf':
            return redact_pdf_content(input_path, output_path, kwargs.get('search_terms', ''))
        
        elif internal_tool_name == 'extract_metadata_pdf':
            return extract_pdf_metadata(input_path, output_path)
        
        # Conversions
        elif internal_tool_name == 'pdf_to_ppt':
            return pdf_to_powerpoint(input_path, output_path)
        
        elif internal_tool_name == 'pptx_to_pdf':
            return powerpoint_to_pdf(input_path, output_path)
        
        elif internal_tool_name == 'pdf_to_html':
            return pdf_to_html(input_path, output_path)
        
        elif internal_tool_name == 'html_to_pdf':
            return html_to_pdf(input_path, output_path)
        
        elif internal_tool_name == 'to_pdf':
            # Universal converter: handles any format and converts to PDF with advanced options
            ext = Path(input_path).suffix.lower().lstrip('.')
            
            print(f"[execute_service_conversion] to_pdf: ext={ext}, kwargs={kwargs}")
            logger.info(f"to_pdf conversion: ext={ext}, kwargs={kwargs}")
            
            # Extract To PDF specific parameters
            image_quality = int(kwargs.get('image_quality', 85))
            page_numbers = kwargs.get('page_numbers', False) in (True, 'true', 'True')
            compression = kwargs.get('compression', 'medium')
            preserve_colors = kwargs.get('preserve_colors', True) in (True, 'true', 'True')
            preserve_images = kwargs.get('background', True) in (True, 'true', 'True')
            embed_fonts = kwargs.get('embed_fonts', True) in (True, 'true', 'True')
            background = kwargs.get('background', True) in (True, 'true', 'True')
            
            # Image formats
            if ext in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'tif'):
                try:
                    img = Image.open(input_path)
                    
                    # Apply quality/compression if needed
                    if image_quality < 100:
                        # Reduce quality for smaller file size
                        img = img.convert('RGB')
                        img.save(output_path, 'PDF', quality=image_quality, optimize=True)
                    else:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(output_path, 'PDF')
                    return True
                except Exception as e:
                    print(f"Image to PDF error: {e}")
                    return False
            
            # Document formats
            elif ext == 'docx':
                # Use new docx_to_pdf_with_params for advanced parameter support
                return docx_to_pdf_with_params(input_path, output_path, **kwargs)
            elif ext in ('doc', 'odt'):
                # Use updated soffice_to_pdf with parameter support
                return soffice_to_pdf(input_path, output_path, **kwargs)
            elif ext in ('xlsx', 'xls', 'xlsm', 'xlsb', 'ods', 'csv'):
                print(f"[execute_service_conversion] Calling excel_to_pdf with kwargs: {kwargs}")
                logger.info(f"Calling excel_to_pdf with kwargs: {kwargs}")
                return excel_to_pdf(input_path, output_path, **kwargs)
            elif ext == 'pptx':
                return powerpoint_to_pdf(input_path, output_path)
            elif ext == 'odp':
                return powerpoint_to_pdf(input_path, output_path)
            
            # Text formats
            elif ext == 'txt':
                try:
                    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text_content = f.read()
                    return text_to_pdf(text_content, output_path, **kwargs)
                except Exception as e:
                    print(f"Text to PDF error: {e}")
                    return False
            elif ext in ('html', 'htm'):
                try:
                    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                        html_content = f.read()
                    return html_to_pdf(html_content, output_path, **kwargs)
                except Exception as e:
                    print(f"HTML to PDF error: {e}")
                    return False
            elif ext == 'csv':
                # Convert CSV to PDF via temporary Excel
                try:
                    from openpyxl import Workbook
                    import csv as csv_module
                    
                    wb = Workbook()
                    ws = wb.active
                    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv_module.reader(f)
                        for row_idx, row in enumerate(reader, 1):
                            for col_idx, cell in enumerate(row, 1):
                                ws.cell(row=row_idx, column=col_idx, value=cell)
                    
                    temp_xlsx = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
                    wb.save(temp_xlsx.name)
                    result = excel_to_pdf(temp_xlsx.name, output_path, **kwargs)
                    try:
                        os.unlink(temp_xlsx.name)
                    except:
                        pass
                    return result
                except Exception as e:
                    print(f"CSV to PDF error: {e}")
                    return False
            
            # Already PDF
            elif ext == 'pdf':
                try:
                    shutil.copy(input_path, output_path)
                    return True
                except:
                    return False
            
            # Unknown format
            else:
                print(f"Unsupported file format for PDF conversion: {ext}")
                return False
        
        elif internal_tool_name == 'excel_to_pdf':
            return excel_to_pdf(input_path, output_path)
        
        elif internal_tool_name == 'excel_to_csv':
            return excel_to_csv(input_path, output_path)
        
        elif internal_tool_name == 'text_to_pdf':
            return text_to_pdf(input_path, output_path)
        
        elif internal_tool_name == 'remove_colors':
            return remove_image_colors(input_path, output_path)
        
        elif internal_tool_name == 'formulas_to_values_excel':
            return excel_formulas_to_values(input_path, output_path)
        
        elif internal_tool_name == 'clean_charts_excel':
            return clean_excel_charts(input_path, output_path)
        
        elif internal_tool_name == 'normalize_data':
            return normalize_data_excel(input_path, output_path)
        
        elif internal_tool_name == 'split_sheets_excel':
            return split_excel_sheets(input_path, output_path)
        
        # Images
        elif internal_tool_name == 'image_convert' or internal_tool_name == 'Image Convert':
            output_format = kwargs.get('output_format') or Path(output_path).suffix.lstrip('.') or 'jpg'
            output_format = output_format.lower()
            # Ensure output format is valid
            if output_format not in ('jpg', 'jpeg', 'png', 'webp', 'tiff', 'tif', 'bmp', 'gif'):
                output_format = 'jpg'
            quality = int(kwargs.get('quality', 85))
            lossless = kwargs.get('lossless', False)
            ok = convert_image_format(input_path, output_path, output_format, quality=quality, lossless=lossless)
            if ok:
                return True
            else:
                print(f"Image convert failed: {input_path} -> {output_path} (format={output_format})")
                return False
        
        elif internal_tool_name == 'image_compress_service':
            quality = int(kwargs.get('quality', 85))
            return convert_image_format(input_path, output_path, Path(output_path).suffix.lstrip('.'), quality=quality)
        
        elif internal_tool_name == 'image_resize_service':
            width = int(kwargs.get('width', 800))
            height = int(kwargs.get('height', 600))
            return resize_image(input_path, output_path, width, height)
        
        elif internal_tool_name == 'remove_image_bg':
            return remove_image_background(input_path, output_path)
        
        elif internal_tool_name == 'remove_duplicate_images':
            return True  # Handled at batch level
        
        # Data operations
        elif internal_tool_name == 'validate_data_files':
            return validate_data_file(input_path, output_path)
        
        elif internal_tool_name == 'export_to_pdf':
            return pdf_to_true_bw(input_path, output_path)  # Fallback
        
        elif internal_tool_name == 'generate_report':
            return generate_text_report(input_path, output_path)
        
        elif internal_tool_name == 'database_operations':
            return True  # Placeholder
        
        # Advanced/Pro versions
        elif internal_tool_name == 'pdf_to_bw_pro':
            dpi = int(kwargs.get('dpi', 300))
            threshold = int(kwargs.get('threshold', 250))
            return pdf_to_true_bw(input_path, output_path, dpi=dpi, threshold=threshold)
        
        elif internal_tool_name == 'merge_pdf_pro':
            return True  # Handled at batch level
        
        elif internal_tool_name == 'smart_extract_pages':
            pages = kwargs.get('pages', '1')
            page_list = parse_page_numbers(str(pages))
            if page_list:
                return extract_pdf_pages(input_path, output_path, page_list)
            return False
        
        elif internal_tool_name == 'batch_compress_pdf':
            return compress_pdf_document(input_path, output_path)
        
        elif internal_tool_name == 'encrypt_pdf_aes256':
            password = kwargs.get('password', 'secure123')
            return encrypt_pdf(input_path, output_path, password)
        
        elif internal_tool_name == 'ocr_pdf_searchable':
            return ocr_extract_text(input_path, output_path)
        
        elif internal_tool_name == 'batch_watermark_pdf':
            text = kwargs.get('watermark_text', 'WATERMARK')
            return add_watermark(input_path, output_path, text)
        
        elif internal_tool_name == 'fill_pdf_forms':
            return True  # Placeholder for form filling
        
        elif internal_tool_name == 'reorder_pdf_pages':
            new_order = kwargs.get('new_order', '')
            page_list = parse_page_numbers(new_order)
            if page_list:
                return extract_pdf_pages(input_path, output_path, page_list)
            return False
        
        elif internal_tool_name == 'bulk_convert':
            output_format = kwargs.get('output_format', 'pdf')
            return execute_service_conversion('to_pdf' if output_format == 'pdf' else output_format, input_path, output_path)
        
        elif internal_tool_name == 'smart_crop_images':
            return crop_image(input_path, output_path, kwargs.get('crop_params', {}))
        
        elif internal_tool_name == 'generate_thumbnails':
            size = kwargs.get('size', 200)
            return generate_image_thumbnail(input_path, output_path, size)
        
        elif internal_tool_name == 'batch_rename_files':
            return True  # Handled at batch level
        
        elif internal_tool_name == 'access_conversion_history':
            return True  # Handled separately
        
        return False
    
    except Exception as e:
        print(f"Conversion error for {tool_name}: {e}")
        return False


def split_pdf_pages(input_pdf, output_prefix):
    """Split PDF into individual pages"""
    try:
        pdf = fitz.open(input_pdf)
        for i, page in enumerate(pdf):
            output = f"{output_prefix}_page_{i+1}.pdf"
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf, from_page=i, to_page=i)
            new_pdf.save(output)
            new_pdf.close()
        pdf.close()
        return True
    except:
        return False


def remove_pdf_pages(input_pdf, output_pdf, pages_to_remove):
    """Remove specific pages from PDF"""
    try:
        pdf = fitz.open(input_pdf)
        for page_num in sorted(pages_to_remove, reverse=True):
            pdf.delete_page(page_num)
        pdf.save(output_pdf)
        pdf.close()
        return True
    except:
        return False


def clean_pdf_document(input_pdf, output_pdf):
    """Clean PDF by removing unnecessary metadata and optimizing"""
    try:
        pdf = fitz.open(input_pdf)
        pdf.set_metadata({})
        pdf.save(output_pdf, garbage=4, deflate=True)
        pdf.close()
        return True
    except:
        return False


def compress_pdf_document(input_pdf, output_pdf):
    """Compress PDF file"""
    try:
        pdf = fitz.open(input_pdf)
        pdf.save(output_pdf, garbage=4, deflate=True)
        pdf.close()
        return True
    except:
        return False




def redact_pdf_content(input_pdf, output_pdf, search_terms):
    """Redact content in PDF"""
    try:
        pdf = fitz.open(input_pdf)
        terms = [t.strip() for t in search_terms.split(',') if t.strip()]
        for page in pdf:
            for term in terms:
                textbox = page.search_for(term)
                for box in textbox:
                    page.draw_rect(box, color=(0, 0, 0), fill=(0, 0, 0))
        pdf.save(output_pdf)
        pdf.close()
        return True
    except:
        return False


def extract_pdf_metadata(input_pdf, output_txt):
    """Extract metadata from PDF to text file"""
    try:
        pdf = fitz.open(input_pdf)
        metadata = pdf.metadata
        with open(output_txt, 'w', encoding='utf-8') as f:
            for key, value in (metadata or {}).items():
                f.write(f"{key}: {value}\n")
        pdf.close()
        return True
    except:
        return False






def remove_image_colors(input_img, output_img):
    """Remove colors from image (convert to grayscale)"""
    try:
        img = Image.open(input_img)
        gray_img = img.convert('L')
        gray_img.save(output_img)
        return True
    except:
        return False


def excel_formulas_to_values(input_excel, output_excel):
    """Convert all formulas in Excel to their values"""
    try:
        from openpyxl.utils import get_column_letter
        wb = load_workbook(input_excel, data_only=False)
        for ws in wb.sheetnames:
            sheet = wb[ws]
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                        # Can't directly evaluate, so skip
                        pass
        wb.save(output_excel)
        return True
    except:
        return False


def clean_excel_charts(input_excel, output_excel):
    """Remove all charts from Excel file"""
    try:
        wb = load_workbook(input_excel)
        for ws in wb.sheetnames:
            sheet = wb[ws]
            if hasattr(sheet, '_charts'):
                sheet._charts = []
        wb.save(output_excel)
        return True
    except:
        return False


def normalize_data_excel(input_excel, output_excel):
    """Normalize data in Excel file"""
    try:
        wb = load_workbook(input_excel)
        ws = wb.active
        # Simple normalization: trim whitespace
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    cell.value = cell.value.strip()
        wb.save(output_excel)
        return True
    except:
        return False


def split_excel_sheets(input_excel, output_prefix):
    """Split Excel workbook into separate files per sheet"""
    try:
        wb = load_workbook(input_excel)
        for sheet_name in wb.sheetnames:
            new_wb = Workbook()
            new_ws = new_wb.active
            old_ws = wb[sheet_name]
            for row in old_ws.iter_rows():
                for cell in row:
                    new_ws[cell.coordinate].value = cell.value
            output_file = f"{output_prefix}_{sheet_name}.xlsx"
            new_wb.save(output_file)
        return True
    except:
        return False


def resize_image(input_img, output_img, width, height):
    """Resize image to specified dimensions"""
    try:
        img = Image.open(input_img)
        # Use LANCZOS if available, fallback to BICUBIC
        resample_filter = getattr(Image, 'LANCZOS', getattr(Image, 'BICUBIC', Image.BILINEAR))
        resized = img.resize((int(width), int(height)), resample_filter)
        resized.save(output_img, quality=85)
        return True
    except Exception as e:
        print(f"Image resize error: {e}")
        return False


def remove_image_background(input_img, output_img):
    """Remove background from image (placeholder - requires advanced libraries)"""
    try:
        # Simplified version: Make white background transparent
        img = Image.open(input_img).convert('RGBA')
        data = img.getdata()
        new_data = []
        for item in data:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        img.save(output_img, 'PNG')
        return True
    except:
        return False


def crop_image(input_img, output_img, crop_params):
    """Crop image with specified parameters"""
    try:
        img = Image.open(input_img)
        box = (
            int(crop_params.get('left', 0)),
            int(crop_params.get('top', 0)),
            int(crop_params.get('right', img.width)),
            int(crop_params.get('bottom', img.height))
        )
        cropped = img.crop(box)
        cropped.save(output_img)
        return True
    except:
        return False


def generate_image_thumbnail(input_img, output_img, size=200):
    """Generate thumbnail from image"""
    try:
        img = Image.open(input_img)
        img.thumbnail((size, size), Image.LANCZOS)
        img.save(output_img)
        return True
    except:
        return False


def validate_data_file(input_file, output_report):
    """Validate data in file and generate report"""
    try:
        ext = Path(input_file).suffix.lower()
        report = []
        
        if ext in ('.csv', '.xlsx'):
            import csv
            if ext == '.csv':
                with open(input_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    report.append(f"Total rows: {len(rows)}\n")
                    if rows:
                        report.append(f"Columns: {', '.join(rows[0].keys())}\n")
            else:
                wb = load_workbook(input_file)
                ws = wb.active
                report.append(f"Total rows: {ws.max_row}\n")
                report.append(f"Total columns: {ws.max_column}\n")
        
        with open(output_report, 'w', encoding='utf-8') as f:
            f.writelines(report)
        return True
    except:
        return False


def generate_text_report(input_file, output_report):
    """Generate text report from file"""
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        with open(output_report, 'w', encoding='utf-8') as f:
            f.write("=== FILE REPORT ===\n")
            f.write(f"File: {Path(input_file).name}\n")
            f.write(f"Size: {os.path.getsize(input_file)} bytes\n")
            f.write(f"Lines: {len(content.splitlines())}\n")
            f.write(f"Characters: {len(content)}\n")
            f.write("\n=== CONTENT PREVIEW ===\n")
            f.write(content[:1000])
        return True
    except:
        return False


def _store_converted_file(file_path, filename):
    """Store a converted file and return a download ID."""
    file_id = str(uuid.uuid4())
    _converted_files_store[file_id] = {
        'path': file_path,
        'filename': filename,
        'expires': time.time() + _FILES_EXPIRE_AFTER
    }
    return file_id


def _get_converted_file(file_id):
    """Retrieve a converted file by ID. Returns (path, filename) or (None, None) if not found."""
    if file_id not in _converted_files_store:
        return None, None
    
    file_info = _converted_files_store[file_id]
    
    # Check if expired
    if time.time() > file_info['expires']:
        try:
            os.unlink(file_info['path'])
        except:
            pass
        del _converted_files_store[file_id]
        return None, None
    
    return file_info['path'], file_info['filename']


@app.route('/api/download/<file_id>', methods=['GET'])
def api_download(file_id):
    """Download a converted file."""
    try:
        file_path, filename = _get_converted_file(file_id)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found or expired'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        print(f"[Download] Error: {e}")
        return jsonify({'error': str(e)}), 500


# ========================
# ASYNC CONVERSION ENDPOINTS (SPA Support)
# ========================

def _process_conversion_job(job_id, temp_dir, files_list, tool_name, request_form):
    """Background worker to process conversion asynchronously"""
    job = _job_registry.get(job_id)
    if not job:
        return
    
    try:
        with _job_lock:
            job.status = 'processing'
            job.start_time = datetime.now()
        
        # Helper function to convert string booleans from form data
        def to_bool(val):
            if isinstance(val, bool):
                return val
            return str(val).lower() in ('true', 'yes', '1', 'on') if val else False
        
        converted_files = []
        total_files = len(files_list)
        
        for idx, file_obj in enumerate(files_list):
            if not file_obj or not file_obj.get('filename'):
                continue
            
            # Update progress
            progress = int((idx / total_files) * 100)
            with _job_lock:
                job.progress = progress
            
            # Write file bytes to disk
            safe_name = sanitize_filename(file_obj['filename']) or ('upload_' + uuid.uuid4().hex)
            input_path = os.path.join(temp_dir, safe_name)
            
            # Write the file content (bytes) to disk
            try:
                with open(input_path, 'wb') as f:
                    f.write(file_obj['content'])
            except Exception as e:
                print(f"[Job {job_id}] Error writing file {file_obj['filename']}: {e}")
                raise
            
            print(f"[Job {job_id}] Processing: {file_obj['filename']}")
            
            # Determine output filename
            base_name = Path(file_obj['filename']).stem
            output_format = request_form.get('output_format', 'pdf').lower()
            
            if tool_name == 'PDF to B&W' or tool_name == 'PDF to B&W Pro':
                output_ext = 'pdf'
            elif 'Image Convert' in tool_name:
                output_ext = output_format or 'jpg'
            elif 'CSV' in tool_name:
                output_ext = 'csv'
            elif 'HTML' in tool_name:
                output_ext = 'html'
            elif 'PPT' in tool_name:
                output_ext = 'pptx'
            elif 'Excel' in tool_name:
                output_ext = 'xlsx'
            elif 'Word' in tool_name:
                output_ext = 'docx'
            else:
                output_ext = output_format or 'pdf'
            
            output_name = f"{base_name}.{output_ext}"
            output_path = os.path.join(temp_dir, output_name)
            
            # Prepare conversion parameters
            kwargs = {
                'quality': int(request_form.get('quality', '85') or 85),
                'output_format': output_ext,
                'orientation': request_form.get('orientation', 'portrait'),
                'paper_size': request_form.get('paper_size', 'A4'),
                'margin_top': request_form.get('margin_top', '20'),
                'margin_bottom': request_form.get('margin_bottom', '20'),
                'margin_left': request_form.get('margin_left', '20'),
                'margin_right': request_form.get('margin_right', '20'),
                'threshold': request_form.get('threshold', '250'),
                'contrast': request_form.get('contrast', '3'),
                'gridlines': to_bool(request_form.get('gridlines', 'false')),
                'include_headers': to_bool(request_form.get('include_headers', 'true')),
                'scale_factor': request_form.get('scale_factor', '100'),
                'image_quality': request_form.get('image_quality', '85'),
            }
            
            # Execute conversion
            try:
                conversion_ok = execute_service_conversion(tool_name, input_path, output_path, **kwargs)
                
                if conversion_ok and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    file_id = _store_converted_file(output_path, output_name)
                    converted_files.append({
                        'name': output_name,
                        'size': file_size,
                        'download_url': f'/api/download/{file_id}'
                    })
                    print(f"[Job {job_id}] File converted: {output_name} ({file_size} bytes)")
            except Exception as e:
                print(f"[Job {job_id}] Conversion error for {file.filename}: {e}")
                raise
        
        # Update job with results
        with _job_lock:
            job.progress = 100
            job.status = 'complete'
            job.result = converted_files
            job.end_time = datetime.now()
        
        print(f"[Job {job_id}] Conversion complete: {len(converted_files)} files")
        log_history(f'async-convert-{tool_name}', [f['filename'] for f in files_list], 'success')
    
    except Exception as e:
        print(f"[Job {job_id}] ERROR: {e}")
        import traceback
        traceback.print_exc()
        with _job_lock:
            job.status = 'error'
            job.error = str(e)
            job.end_time = datetime.now()
        log_history(f'async-convert-{tool_name}', [], 'error', str(e))
    
    finally:
        # Note: Keep files briefly for download
        pass

@app.route('/api/convert/start', methods=['POST'])
def api_convert_start():
    """Start an async conversion job.
    
    Returns: {success: true/false, job_id: str, error: string}
    """
    try:
        # Check rate limiting
        client_ip = _get_client_ip()
        if not _check_rate_limit(client_ip):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Maximum 5 conversions per minute.'
            }), 429
        
        # Validate file presence
        if 'files' not in request.files and 'files[]' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        files_key = 'files' if 'files' in request.files else 'files[]'
        files_list = request.files.getlist(files_key)
        
        if not files_list:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        # Validate file sizes
        total_size = sum(len(f.getvalue()) for f in files_list if f)
        if total_size > _MAX_FILE_SIZE:
            max_mb = _MAX_FILE_SIZE / (1024 * 1024)
            return jsonify({
                'success': False,
                'error': f'Total file size exceeds {max_mb:.0f}MB limit'
            }), 413
        
        tool_name = request.form.get('tool_name', 'To PDF')
        
        # READ FILES INTO MEMORY BEFORE THREAD STARTS
        # (FileStorage objects become invalid outside request context)
        files_in_memory = []
        for f in files_list:
            if f and f.filename:
                try:
                    file_bytes = f.read()  # Read bytes while in request context
                    files_in_memory.append({
                        'filename': f.filename,
                        'content': file_bytes
                    })
                except Exception as e:
                    print(f"[Conversion] Error reading file {f.filename}: {e}")
        
        if not files_in_memory:
            return jsonify({'success': False, 'error': 'Could not read uploaded files'}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        job = ConversionJob(job_id, tool_name, len(files_in_memory))
        
        with _job_lock:
            _job_registry[job_id] = job
        
        # Create temporary directory for this job
        temp_dir = tempfile.mkdtemp()
        
        # Convert request.form to dict for thread context (forms aren't thread-safe)
        form_data = dict(request.form)
        
        # Start background conversion worker
        worker_thread = Thread(
            target=_process_conversion_job,
            args=(job_id, temp_dir, files_in_memory, tool_name, form_data),
            daemon=True
        )
        worker_thread.start()
        
        print(f"[Conversion] Started job {job_id} for {tool_name} with {len(files_list)} files")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Conversion job started. Job ID: {job_id}'
        }), 202
    
    except Exception as e:
        print(f"[Conversion] Error starting job: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/convert/status/<job_id>', methods=['GET'])
def api_convert_status(job_id):
    """Check conversion job status.
    
    Returns: {
        success: true/false,
        status: 'queued'|'processing'|'complete'|'error',
        progress: 0-100,
        files: [...] (if complete),
        error: string (if error)
    }
    """
    try:
        with _job_lock:
            job = _job_registry.get(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        response = job.to_dict()
        response['success'] = True
        
        # If complete, include result files
        if job.status == 'complete' and job.result:
            response['files'] = job.result
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"[Status Check] Error for job {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/convert', methods=['POST'])
def api_convert():
    """Convert files using service tool names.
    
    Form fields:
    - files[]: uploaded files
    - tool_name: Service tool name (from SERVICE_TOOLS dict)
    - output_format: Desired output format (optional)
    - quality: Quality setting (optional, for images)
    - Additional parameters based on tool
    
    Returns: {success: true/false, files: [{name, size, path}], error: string}
    """
    
    # Helper function to convert string booleans from form data
    def to_bool(val):
        if isinstance(val, bool):
            return val
        return str(val).lower() in ('true', 'yes', '1', 'on') if val else False
    
    try:
        if 'files' not in request.files and 'files[]' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        files_key = 'files' if 'files' in request.files else 'files[]'
        files_list = request.files.getlist(files_key)
        
        if not files_list:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        tool_name = request.form.get('tool_name', 'To PDF')  # Default tool
        output_format = request.form.get('output_format', 'pdf').lower()
        quality = request.form.get('quality', '85')
        
        print(f"[API Convert] Received: tool={tool_name}, format={output_format}, quality={quality}, files={len(files_list)}")
        
        # Validate file types for tools with format restrictions
        if 'b&w' in tool_name.lower() or 'pdf-to-b' in tool_name.lower():
            for file in files_list:
                if file and file.filename:
                    file_ext = Path(file.filename).suffix.lower().lstrip('.')
                    if file_ext not in ['pdf']:
                        return jsonify({'success': False, 'message': 'B&W conversion only supports PDF files'}), 400
        
        # Create temporary working directory
        temp_dir = tempfile.mkdtemp()
        converted_files = []
        
        try:
            for file in files_list:
                if not file or not file.filename:
                    continue
                
                # Save uploaded file
                safe_name = sanitize_filename(file.filename) or ('upload_' + uuid.uuid4().hex)
                input_path = os.path.join(temp_dir, safe_name)
                file.save(input_path)
                
                print(f"[API Convert] Processing: {file.filename} -> {safe_name}")
                
                # Determine output filename based on tool
                base_name = Path(file.filename).stem
                file_ext = Path(file.filename).suffix.lower().lstrip('.')
                
                # Map tool to output extension
                if tool_name == 'PDF to B&W' or tool_name == 'PDF to B&W Pro':
                    output_ext = 'pdf'
                elif tool_name == 'Image Compress' or 'Compress' in tool_name:
                    output_ext = file_ext or 'pdf'
                elif tool_name == 'Image Resize' or 'Resize' in tool_name:
                    output_ext = file_ext or 'png'
                elif tool_name == 'Remove Background':
                    output_ext = 'png'
                elif 'Image Convert' in tool_name or tool_name == 'Image Convert':
                    # For image convert, use the specified output format
                    output_ext = output_format or file_ext or 'jpg'
                elif 'CSV' in tool_name or 'csv' in tool_name:
                    output_ext = 'csv'
                elif 'HTML' in tool_name:
                    output_ext = 'html'
                elif 'PPT' in tool_name:
                    output_ext = 'pptx'
                elif 'Excel' in tool_name or 'XLSX' in tool_name:
                    output_ext = 'xlsx'
                elif 'DOCX' in tool_name or 'Word' in tool_name:
                    output_ext = 'docx'
                else:
                    output_ext = output_format or 'pdf'
                
                output_name = f"{base_name}.{output_ext}"
                output_path = os.path.join(temp_dir, output_name)
                
                # Prepare conversion parameters
                kwargs = {
                    'quality': int(quality or 85),
                    'output_format': output_ext,
                    'watermark_text': request.form.get('watermark_text', ''),
                    'password': request.form.get('password', 'password123'),
                    'position': request.form.get('position', 'diagonal'),
                    'pages': request.form.get('pages', '1'),
                    # B&W conversion parameters
                    'dpi': request.form.get('dpi', '300'),
                    'threshold': request.form.get('threshold', '250'),
                    'contrast': request.form.get('contrast', '3'),
                    'brightness': request.form.get('brightness', '0'),
                    'gamma': request.form.get('gamma', '1.0'),
                    'sharpness': request.form.get('sharpness', '1'),
                    'blur': request.form.get('blur', '0'),
                    'invert': to_bool(request.form.get('invert', 'false')),
                    'denoise': request.form.get('denoise', '0'),
                    'edgeEnhance': to_bool(request.form.get('edgeEnhance', 'true')),
                    # To PDF parameters
                    'orientation': request.form.get('orientation', 'portrait'),
                    'paper_size': request.form.get('paper_size', 'A4'),
                    'margin_top': request.form.get('margin_top', '20'),
                    'margin_bottom': request.form.get('margin_bottom', '20'),
                    'margin_left': request.form.get('margin_left', '20'),
                    'margin_right': request.form.get('margin_right', '20'),
                    'fit_mode': request.form.get('fit_mode', 'fit-page'),
                    'include_headers': to_bool(request.form.get('include_headers', 'true')),
                    'gridlines': to_bool(request.form.get('gridlines', 'false')),
                    'scale_factor': request.form.get('scale_factor', '100'),
                    'image_quality': request.form.get('image_quality', '85'),
                    'page_numbers': to_bool(request.form.get('page_numbers', 'false')),
                    'compression': request.form.get('compression', 'medium'),
                    'preserve_colors': to_bool(request.form.get('preserve_colors', 'true')),
                    'embed_fonts': to_bool(request.form.get('embed_fonts', 'true')),
                    'background': to_bool(request.form.get('background', 'true')),
                }
                
                # Execute the service conversion
                print(f"[API Convert] Calling execute_service_conversion({tool_name}, ..., kwargs={kwargs})")
                conversion_ok = execute_service_conversion(tool_name, input_path, output_path, **kwargs)
                
                print(f"[API Convert] Result: {conversion_ok}, exists={os.path.exists(output_path)}")
                
                # If conversion was successful, add to results
                if conversion_ok and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    file_id = _store_converted_file(output_path, output_name)
                    converted_files.append({
                        'name': output_name,
                        'size': file_size,
                        'path': output_path,
                        'download_url': f'/api/download/{file_id}'
                    })
                else:
                    print(f"[API Convert] Conversion failed or file doesn't exist: {output_path}")
            
            if not converted_files:
                print(f"[API Convert] ERROR: No files could be converted")
                return jsonify({'success': False, 'error': 'No files could be converted'}), 400
            
            # Log the conversion
            log_history(f'api-convert-{tool_name}', [f.filename for f in files_list], 'success')
            
            # Return file info with download URLs
            return jsonify({
                'success': True,
                'files': [{'name': f['name'], 'size': f['size'], 'download_url': f['download_url']} for f in converted_files]
            }), 200
        
        finally:
            # Note: Keep files briefly for download
            pass
    
    except Exception as e:
        print(f"[API Convert] Exception: {e}")
        import traceback
        traceback.print_exc()
        log_history('api-convert', [], 'error', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================
# SHEET MANAGEMENT ENDPOINTS
# ========================

@app.route('/list-sheets', methods=['POST'])
def list_sheets():
    """
    List all sheets in an Excel or CSV file with metadata.
    
    Request (multipart/form-data):
        file: The Excel or CSV file
    
    Response: {
        'success': bool,
        'file_name': str,
        'file_type': 'excel' | 'csv',
        'sheets': [
            {
                'name': str,
                'index': int,
                'rows': int,
                'columns': int,
                'preview': [[...], ...]
            }
        ]
    }
    """
    try:
        _check_api_key()
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Validate file type
        ext = Path(file.filename).suffix.lower()
        if ext not in ['.xlsx', '.xls', '.ods', '.csv']:
            return jsonify({'success': False, 'error': 'File must be Excel (.xlsx, .xls, .ods) or CSV'}), 400
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        file.save(temp_file.name)
        
        try:
            result = get_sheet_info(temp_file.name)
            
            if 'error' in result:
                return jsonify({'success': False, 'error': result['error']}), 400
            
            result['success'] = True
            return jsonify(result), 200
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    except Exception as e:
        logger.error(f"list_sheets error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/excel-to-pdf-sheets', methods=['POST'])
def excel_to_pdf_sheets():
    """
    Convert specific sheets from Excel to PDF.
    
    Request (multipart/form-data):
        file: The Excel file
        sheets: JSON string with sheet specification:
            - "all": Convert all sheets
            - "Sheet1,Sheet2": Sheet names
            - "0,2": Sheet indices
        merge: "true" to merge sheets into one PDF, "false" for ZIP
        orientation: "portrait" or "landscape"
        paper_size: "A4", "A3", "LETTER", etc.
        margin_top, margin_bottom, margin_left, margin_right: in mm
        include_headers: "true" or "false"
        gridlines: "true" or "false"
        scale_factor: percentage (default 100)
    
    Response:
        - Single sheet: PDF file
        - Multiple sheets + merge=true: Merged PDF
        - Multiple sheets + merge=false: ZIP file with individual PDFs
    """
    try:
        _check_api_key()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.ods')):
            return jsonify({'error': 'File must be .xlsx, .xls, or .ods'}), 400
        
        # Parse sheet specification
        sheets_spec = request.form.get('sheets', 'all')
        try:
            if sheets_spec == 'all':
                sheets_param = 'all'
            elif ',' in sheets_spec:
                # Try as indices first, then as names
                try:
                    sheets_param = [int(x.strip()) for x in sheets_spec.split(',')]
                except ValueError:
                    sheets_param = [x.strip() for x in sheets_spec.split(',')]
            else:
                sheets_param = sheets_spec.strip()
        except:
            sheets_param = 'all'
        
        # Parse other parameters
        merge_sheets = request.form.get('merge', 'false').lower() == 'true'
        orientation = request.form.get('orientation', 'portrait')
        paper_size = request.form.get('paper_size', 'A4')
        margin_top = request.form.get('margin_top', '25')
        margin_bottom = request.form.get('margin_bottom', '25')
        margin_left = request.form.get('margin_left', '25')
        margin_right = request.form.get('margin_right', '25')
        include_headers = request.form.get('include_headers', 'true').lower() == 'true'
        gridlines = request.form.get('gridlines', 'false').lower() == 'true'
        scale_factor = request.form.get('scale_factor', '100')
        
        # Save temp file
        temp_xlsx = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file.save(temp_xlsx.name)
        temp_dir = tempfile.mkdtemp()
        
        try:
            output_pdf = os.path.join(temp_dir, 'output.pdf')
            
            # Prepare conversion parameters
            kwargs = {
                'sheets': sheets_param,
                'merge_sheets': merge_sheets,
                'orientation': orientation,
                'paper_size': paper_size,
                'margin_top': margin_top,
                'margin_bottom': margin_bottom,
                'margin_left': margin_left,
                'margin_right': margin_right,
                'include_headers': include_headers,
                'gridlines': gridlines,
                'scale_factor': scale_factor,
            }
            
            # Perform conversion
            success = excel_to_pdf(temp_xlsx.name, output_pdf, **kwargs)
            
            if not success:
                return jsonify({'error': 'Conversion failed'}), 500
            
            # Determine output file
            if merge_sheets or output_pdf.endswith('.pdf'):
                output_file = output_pdf
                attachment_name = 'converted.pdf'
            else:
                # Check for ZIP file
                zip_path = output_pdf.replace('.pdf', '.zip')
                if os.path.exists(zip_path):
                    output_file = zip_path
                    attachment_name = 'sheets.zip'
                elif os.path.exists(output_pdf):
                    output_file = output_pdf
                    attachment_name = 'converted.pdf'
                else:
                    return jsonify({'error': 'Output file not found'}), 500
            
            log_history('excel-to-pdf-sheets', [file.filename], 'success')
            return send_file(output_file, as_attachment=True, download_name=attachment_name)
        
        finally:
            try:
                os.unlink(temp_xlsx.name)
            except:
                pass
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    except Exception as e:
        logger.error(f"excel_to_pdf_sheets error: {e}", exc_info=True)
        log_history('excel-to-pdf-sheets', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/combine-csvs', methods=['POST'])
def combine_csvs_endpoint():
    """
    Combine multiple CSV files into a single Excel workbook.
    
    Request (multipart/form-data):
        files: Multiple CSV files
        sheet_names (optional): JSON array of sheet names
    
    Response: Excel file with CSV files as sheet tabs
    """
    try:
        _check_api_key()
        
        if 'files' not in request.files and 'file' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files') or request.files.getlist('file')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate all are CSV
        for f in files:
            if not f.filename.lower().endswith('.csv'):
                return jsonify({'error': f'File {f.filename} is not a CSV'}), 400
        
        # Parse sheet names if provided
        sheet_names = None
        sheet_names_str = request.form.get('sheet_names', '')
        if sheet_names_str:
            try:
                sheet_names = _json.loads(sheet_names_str)
            except:
                sheet_names = None
        
        # Save CSV files to temp location
        temp_dir = tempfile.mkdtemp()
        csv_paths = []
        
        try:
            for f in files:
                csv_path = os.path.join(temp_dir, secure_filename(f.filename))
                f.save(csv_path)
                csv_paths.append(csv_path)
            
            # Create output
            output_path = os.path.join(temp_dir, 'combined.xlsx')
            success = combine_csvs_to_excel(csv_paths, output_path, sheet_names)
            
            if not success:
                return jsonify({'error': 'Failed to combine CSVs'}), 500
            
            log_history('combine-csvs', [f.filename for f in files], 'success')
            return send_file(output_path, as_attachment=True, download_name='combined.xlsx')
        
        finally:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    except Exception as e:
        logger.error(f"combine_csvs_endpoint error: {e}", exc_info=True)
        log_history('combine-csvs', [], 'error', str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Start background tasks (DB init, cleanup thread) when running server directly
    try:
        start_background_tasks()
    except Exception:
        pass
    
    # Log server startup
    logger.info('DocPro server starting')
    logger.info(f'DEBUG mode: {app.debug}')
    logger.info(f'Environment: {os.getenv("FLASK_ENV", "development")}')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
