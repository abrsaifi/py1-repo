# Services module - contains all conversion and processing services
from .utils import *
from .pdf_tools import *
from .document_conversion import *
from .image_processing import *
from .watermark import *
from .preview import *
from .ocr import *

__all__ = [
    # Utils
    'allowed_file',
    'sanitize_filename',
    'validate_image_file',
    'parse_page_numbers',
    'get_easyocr_reader',
    'is_rate_limited',
    '_check_api_key',
    'cleanup_old_upload_dirs',
    'init_history_db',
    'log_history',
    'set_app',
    # PDF Tools
    'encrypt_pdf',
    'decrypt_pdf',
    'pdf_remove_metadata',
    'extract_pdf_pages',
    'split_pdf',
    'merge_pdf',
    'remove_pages_from_pdf',
    'redact_pdf',
    'clean_autoformat_pdf',
    # Document Conversion
    'docx_to_pdf',
    'soffice_to_pdf',
    'excel_to_pdf',
    'powerpoint_to_pdf',
    'pdf_to_word',
    'pdf_to_excel',
    'pdf_to_powerpoint',
    'excel_to_csv',
    'html_to_pdf',
    'pdf_to_html',
    'url_to_pdf',
    'text_to_pdf',
    # Image Processing
    'convert_image_format',
    'image_to_pdf',
    'pdf_to_true_bw',
    # Watermark
    'add_watermark',
    'add_image_watermark',
    # Preview
    '_generate_preview_from_pdf',
    '_generate_previews_from_pdf',
    # OCR
    'ocr_extract_text',
    'ocr_extract_with_language',
]
