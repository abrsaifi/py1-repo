import os
import io
import fitz
try:
    import easyocr
except Exception:
    easyocr = None

_EASYOCR_READER = None


def get_easyocr_reader(langs=None, gpu=False):
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        try:
            if easyocr is None:
                return None
            langs = langs or ['en']
            _EASYOCR_READER = easyocr.Reader(langs, gpu=gpu)
        except Exception:
            _EASYOCR_READER = None
    return _EASYOCR_READER


def ocr_extract_text(image_or_pdf_path, max_pages=None):
    """Extract text from image or PDF using EasyOCR if available.

    Returns extracted text as a string, or None on failure.
    """
    reader = get_easyocr_reader()
    if reader is None:
        return None

    out_parts = []
    try:
        if str(image_or_pdf_path).lower().endswith('.pdf'):
            doc = fitz.open(image_or_pdf_path)
            total = len(doc)
            count = total if max_pages is None else min(total, max_pages)
            for i in range(count):
                page = doc[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72), alpha=False)
                img_bytes = pix.tobytes('png')
                res = reader.readtext(img_bytes, detail=0)
                out_parts.append('\n'.join(res))
            doc.close()
        else:
            # image file
            res = reader.readtext(image_or_pdf_path, detail=0)
            out_parts.append('\n'.join(res))

        return '\n\n'.join([p for p in out_parts if p])
    except Exception:
        return None


def parse_page_numbers(pages_input):
    """Parse user page selectors like "1,3,5-7" into 0-indexed ints.

    Returns a list of 0-indexed page numbers or None if input invalid/empty.
    """
    import re
    if not pages_input or not str(pages_input).strip():
        return None

    pages = set()
    tokens = re.split(r'[,\s]+', pages_input.strip())
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if '-' in token:
            parts = token.split('-', 1)
            try:
                a = int(parts[0])
                b = int(parts[1])
                if a <= 0 or b <= 0:
                    continue
                for p in range(a, b + 1):
                    pages.add(p - 1)
            except Exception:
                continue
        else:
            try:
                v = int(token)
                if v <= 0:
                    continue
                pages.add(v - 1)
            except Exception:
                continue

    return sorted(list(pages)) if pages else None


def add_watermark(input_pdf, output_pdf, watermark_text, pages=None, rotation=45, opacity=0.2, fontsize=60):
    """Simple watermark: draws watermark_text centered on each page using PyMuPDF."""
    try:
        doc = fitz.open(input_pdf)
        supported_rotation = rotation if rotation in {0, 90, 180, 270} else 0
        for i in range(len(doc)):
            if pages and i not in pages:
                continue
            page = doc[i]
            rect = page.rect
            # compute center
            center = fitz.Point(rect.width / 2, rect.height / 2)
            page.insert_text(center, watermark_text, fontsize=fontsize, rotate=supported_rotation, color=(0.5, 0.5, 0.5), render_mode=3)
        doc.save(output_pdf)
        doc.close()
        return True
    except Exception:
        return False
