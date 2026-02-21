import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path

PDF_ALLOWED_EXTENSIONS = {'pdf'}
IMAGE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'}
DOCUMENT_ALLOWED_EXTENSIONS = {'docx', 'doc'}
EXCEL_ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Configuration
MAX_FILE_SIZE_MB = 100  # 100 MB limit
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


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
    return ext in (PDF_ALLOWED_EXTENSIONS | IMAGE_ALLOWED_EXTENSIONS | DOCUMENT_ALLOWED_EXTENSIONS | EXCEL_ALLOWED_EXTENSIONS)


def sanitize_filename(name: str) -> str:
    try:
        if not name:
            return ''
        safe = secure_filename(name)
        if not safe:
            return uuid.uuid4().hex
        if len(safe) > 200:
            base, dot, ext = safe.rpartition('.')
            if dot and ext:
                safe = base[:180] + '.' + ext[:18]
            else:
                safe = safe[:200]
        return safe
    except Exception:
        return uuid.uuid4().hex


def validate_file(file_obj, allowed_exts=None):
    """
    Validate file before processing
    Returns: (is_valid, error_message)
    """
    # Handle both file objects with filename and raw file-like objects
    if not file_obj:
        return False, 'No file selected'
    
    # Get filename from various sources
    filename = getattr(file_obj, 'filename', None)
    if not filename:
        # Try to extract from file path (for file objects from open())
        name_attr = getattr(file_obj, 'name', None)
        if name_attr:
            filename = os.path.basename(name_attr)
        else:
            filename = ''
    
    if not filename or filename.strip() == '':
        return False, 'File must have a filename'
    
    # Check file size
    try:
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)
    except Exception:
        return False, 'Unable to determine file size'
    
    if file_size == 0:
        return False, 'File is empty'
    
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f'File size exceeds {MAX_FILE_SIZE_MB}MB limit (Current: {file_size / (1024*1024):.1f}MB)'
    
    # Check file extension
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if not ext:
        return False, 'File has no extension'
    
    # Check against allowed extensions if provided
    allowed_set = set(allowed_exts) if allowed_exts else (PDF_ALLOWED_EXTENSIONS | IMAGE_ALLOWED_EXTENSIONS | DOCUMENT_ALLOWED_EXTENSIONS | EXCEL_ALLOWED_EXTENSIONS | {'csv', 'txt'})
    if ext not in allowed_set:
        return False, f'File type .{ext} not allowed. Allowed: {", ".join(allowed_set)}'
    
    # Check for suspicious patterns
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, 'Invalid filename'
    
    return True, None


def get_file_size_mb(file_obj):
    """Get file size in MB - handles both file paths and file-like objects"""
    try:
        # If it's a string path
        if isinstance(file_obj, str):
            return Path(file_obj).stat().st_size / (1024 * 1024)
        
        # If it's a Path object
        if isinstance(file_obj, Path):
            return file_obj.stat().st_size / (1024 * 1024)
        
        # If it's a file-like object
        if hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
            current_pos = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size_bytes = file_obj.tell()
            file_obj.seek(current_pos)  # Restore position
            return size_bytes / (1024 * 1024)
        
        # Fallback
        return 0
    except Exception:
        return 0
