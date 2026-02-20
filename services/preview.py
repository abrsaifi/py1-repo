"""
Preview generation service for conversion tools.
"""

import os
import tempfile
import io
import base64
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
from .utils import DOCUMENT_ALLOWED_EXTENSIONS, IMAGE_ALLOWED_EXTENSIONS
import logging

logger = logging.getLogger('docpro')


def _generate_preview_from_pdf(pdf_path, dpi=150):
    """Render the first page of a PDF to PNG bytes and return bytes."""
    try:
        logger.info(f'Generating single preview from PDF: {pdf_path}')
        if not os.path.exists(pdf_path):
            logger.error(f'PDF file does not exist: {pdf_path}')
            return None
        
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            logger.warning(f'PDF file is empty: {pdf_path}')
            doc.close()
            return None
        
        page = doc[0]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes('png')
        doc.close()
        logger.info(f'Successfully generated preview from page 1')
        return img_bytes
    except Exception as e:
        logger.error(f'Error generating preview from PDF: {e}', exc_info=True)
        return None


def _generate_previews_from_pdf(pdf_path, max_pages=3, dpi=150):
    """Render up to max_pages from a PDF and return list of PNG bytes."""
    out = []
    try:
        logger.info(f'Opening PDF for preview: {pdf_path}')
        if not os.path.exists(pdf_path):
            logger.error(f'PDF file does not exist: {pdf_path}')
            return []
        
        doc = fitz.open(pdf_path)
        total = len(doc)
        logger.info(f'PDF has {total} pages, rendering up to {max_pages}')
        
        count = min(total, max_pages)
        for i in range(count):
            try:
                page = doc[i]
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_bytes = pix.tobytes('png')
                out.append(img_bytes)
                logger.info(f'Successfully rendered page {i+1}/{count}')
            except Exception as e:
                logger.error(f'Error rendering page {i+1}: {e}', exc_info=True)
                continue
        
        doc.close()
        logger.info(f'Successfully generated {len(out)} preview images')
    except Exception as e:
        logger.error(f'Error opening/processing PDF {pdf_path}: {e}', exc_info=True)
        return []
    
    return out


def generate_image_preview(image_path):
    """Generate a PNG preview from an image file."""
    try:
        img = Image.open(image_path)
        buf = io.BytesIO()
        img.convert('RGBA').save(buf, format='PNG')
        buf.seek(0)
        data = base64.b64encode(buf.read()).decode('ascii')
        return f'data:image/png;base64,{data}'
    except Exception:
        return None
