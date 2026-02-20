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
    if not file_obj:
        return False, 'No file selected'

    # Support Werkzeug FileStorage (`filename`) and raw file objects (`name`)
    filename_attr = getattr(file_obj, 'filename', None) or getattr(file_obj, 'name', None)
    if not filename_attr or str(filename_attr) == '':
        return False, 'No file selected'
    
    # Check file size (supports file-like objects)
    try:
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)
    except Exception:
        # If the object doesn't support seek/tell, try to use file path
        try:
            size_bytes = os.path.getsize(filename_attr)
            file_size = size_bytes
        except Exception:
            return False, 'Unable to determine file size'
    
    if file_size == 0:
        return False, 'File is empty'
    
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f'File size exceeds {MAX_FILE_SIZE_MB}MB limit (Current: {file_size / (1024*1024):.1f}MB)'
    
    # Check file extension
    filename = os.path.basename(str(filename_attr))
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


def get_file_size_mb(file_path):
    """Get file size in MB"""
    # Handle file-like objects (streams)
    if hasattr(file_path, 'seek') and hasattr(file_path, 'tell'):
        current_pos = file_path.tell()
        file_path.seek(0, 2)  # Seek to end
        size_bytes = file_path.tell()
        file_path.seek(current_pos)  # Restore position
        return size_bytes / (1024 * 1024)
    
    # Handle file paths (str or Path)
    if isinstance(file_path, str):
        file_path = Path(file_path)
    return file_path.stat().st_size / (1024 * 1024)
