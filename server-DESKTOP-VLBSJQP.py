import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from PIL import Image
import tempfile
import shutil
import io
from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor, Inches
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XlImage
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import inch
from io import BytesIO
import pdfplumber
import easyocr
from pypdf import PdfWriter
from pathlib import Path
import zipfile
from datetime import datetime
import logging
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# configure logging
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
try:
    file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'server.log'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
except Exception:
    pass


def _log_uploaded_files_by_field(field_name):
    try:
        files = request.files.getlist(field_name) if field_name in request.files else []
        fnames = [f.filename for f in files if getattr(f, 'filename', '')]
        app.logger.info(f"Upload field '{field_name}' files: {fnames}")
    except Exception:
        try:
            app.logger.info(f"Upload field '{field_name}' files present (could not enumerate)")
        except Exception:
            pass


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    app.logger.warning(f"RequestEntityTooLarge: {e}")
    flash('Uploaded file is too large. Maximum allowed size is 16 MB.')
    return redirect(url_for('index'))


@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    import traceback
    tb = traceback.format_exc()
    app.logger.error(f"Unhandled Exception: {e}\n{tb}")
    flash('An internal server error occurred while processing the file.')
    return redirect(url_for('index'))


# Detailed request dump logging (headers, form fields, file fields and sizes)
@app.before_request
def _log_request_dump():
    try:
        # Basic request info
        method = request.method
        path = request.path
        content_length = request.content_length
        app.logger.info(f"REQ: {method} {path} content_length={content_length}")

        # headers (print common headers only to avoid huge output)
        hdrs = {k: v for k, v in request.headers.items() if k.lower() in ('content-type', 'content-length', 'user-agent', 'referer', 'host', 'accept')}
        app.logger.info(f"REQ HEADERS: {hdrs}")

        # form keys
        try:
            form_keys = list(request.form.keys())
            app.logger.info(f"REQ FORM KEYS: {form_keys}")
        except Exception:
            app.logger.info("REQ FORM KEYS: (unable to read form)")

        # files: enumerate field names and sizes
        try:
            file_info = []
            for field in request.files:
                files = request.files.getlist(field)
                for f in files:
                    # Avoid seeking/reading the file stream here (can consume the stream
                    # and make the file unavailable to the view). Use provided metadata.
                    size = getattr(f, 'content_length', None)
                    file_info.append((field, f.filename, size))
            app.logger.info(f"REQ FILES: {file_info}")
        except Exception:
            app.logger.info("REQ FILES: (unable to enumerate files)")
    except Exception:
        # Don't break the request on logging failure
        try:
            app.logger.exception('Failed to dump request')
        except Exception:
            pass


@app.after_request
def _log_response(resp):
    try:
        app.logger.info(f"RESP: status={resp.status} content_length={resp.content_length}")
    except Exception:
        pass
    return resp

PDF_ALLOWED_EXTENSIONS = {'pdf'}
IMAGE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'}
DOCUMENT_ALLOWED_EXTENSIONS = {'docx', 'doc'}
EXCEL_ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Cache EasyOCR Reader (initialization can be very slow)
_EASYOCR_READER = None


def get_easyocr_reader():
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        _EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
    return _EASYOCR_READER

# --- Conversion history (simple SQLite) ---
import sqlite3
import json

HISTORY_DB = os.path.join(os.path.dirname(__file__), 'conversion_history.db')

def init_history_db():
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

def log_history(operation, files, status='success', message=''):
    try:
        conn = sqlite3.connect(HISTORY_DB)
        c = conn.cursor()
        c.execute('INSERT INTO history (timestamp, operation, files, status, message) VALUES (?, ?, ?, ?, ?)',
                  (datetime.utcnow().isoformat(), operation, json.dumps(files), status, message))
        conn.commit()
        conn.close()
    except Exception:
        pass

# initialize DB at startup
init_history_db()

def allowed_file(filename, file_type='pdf'):
    if '.' not in filename:
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
    return False

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

def docx_to_pdf(docx_path, output_pdf):
    """Convert DOCX to PDF"""
    # Extract text and create PDF with reportlab
    try:
        doc = DocxDocument(docx_path)
        c = pdf_canvas.Canvas(output_pdf, pagesize=letter)
        y = letter[1] - 40
        
        for para in doc.paragraphs:
            if para.text.strip():
                c.drawString(40, y, para.text[:80])  # Limit text width
                y -= 20
                if y < 40:
                    c.showPage()
                    y = letter[1] - 40
        
        c.save()
        return True
    except Exception as e:
        print(f"DOCX to PDF error: {e}")
        return False

def excel_to_pdf(excel_path, output_pdf):
    """Convert Excel to PDF"""
    try:
        from openpyxl.drawing.image import Image as XlImage
        workbook = load_workbook(excel_path)
        worksheet = workbook.active
        
        c = pdf_canvas.Canvas(output_pdf, pagesize=A4)
        y = A4[1] - 40
        
        for row in worksheet.iter_rows(values_only=True):
            row_text = ' | '.join(str(cell) if cell else '' for cell in row)
            if row_text.strip():
                c.drawString(40, y, row_text[:100])
                y -= 15
                if y < 40:
                    c.showPage()
                    y = A4[1] - 40
        
        c.save()
        return True
    except Exception as e:
        print(f"Excel to PDF error: {e}")
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
                import tempfile
                import cv2
                import numpy as np

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

def pdf_to_true_bw(input_pdf, output_pdf, dpi=300, threshold=250, contrast=3.0, sharpness=2.5):
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
        
        # Convert RGB to grayscale - this handles colored lines (purple/magenta)
        gray = img.convert("L")
        
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
                img_path = f"/tmp/page_{page_num}.png"
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

def add_watermark(input_pdf, output_pdf, watermark_text, opacity=0.3, position='diagonal'):
    """Add text watermark to PDF"""
    try:
        pdf_doc = fitz.open(input_pdf)
        
        for page_num, page in enumerate(pdf_doc):
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            if position == 'diagonal':
                # Diagonal watermark position
                x = width / 2
                y = height / 2
                angle = 45
            elif position == 'top':
                x = width / 2
                y = 50
                angle = 0
            elif position == 'bottom':
                x = width / 2
                y = height - 50
                angle = 0
            else:  # center
                x = width / 2
                y = height / 2
                angle = 0
            
            # Add watermark text
            page.insert_textbox(
                fitz.Rect(0, 0, width, height),
                watermark_text,
                fontsize=60,
                color=(0.5, 0.5, 0.5),  # Gray color
                textbox=None,
                fontname="helv"
            )
        
        pdf_doc.save(output_pdf, deflate=True)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Watermark error: {e}")
        return False

def encrypt_pdf(input_pdf, output_pdf, password, permissions="all"):
    """Encrypt PDF with password protection"""
    try:
        pdf_reader = open(input_pdf, 'rb')
        pdf_writer = PdfWriter()
        
        # Read all pages from input
        from pypdf import PdfReader
        reader = PdfReader(pdf_reader)
        for page in reader.pages:
            pdf_writer.add_page(page)
        
        # Encrypt with password
        user_password = password
        owner_password = password + "_owner"
        
        pdf_writer.encrypt(user_password, owner_password)
        
        # Write encrypted PDF
        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        pdf_reader.close()
        return True
    except Exception as e:
        print(f"Encryption error: {e}")
        return False

def decrypt_pdf(input_pdf, output_pdf, password):
    """Decrypt an encrypted PDF given the user password."""
    try:
        from pypdf import PdfReader, PdfWriter

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
                    return False, 'incorrect password'
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(output_pdf, 'wb') as out_f:
                writer.write(out_f)
        return True, ''
    except Exception as e:
        print(f"Decryption error: {e}")
        return False, str(e)

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
        pdf_reader = PdfWriter()
        pdf_input = PdfWriter()
        
        with open(input_pdf, 'rb') as f:
            pdf_input.append(f)
        
        total_pages = len(pdf_input.pages)
        output_files = []
        
        for i, (start, end) in enumerate(page_ranges):
            # Convert 1-indexed to 0-indexed
            start_idx = max(0, start - 1)
            end_idx = min(total_pages, end)
            
            if start_idx < end_idx:
                pdf_writer = PdfWriter()
                for page_num in range(start_idx, end_idx):
                    pdf_writer.add_page(pdf_input.pages[page_num])
                
                output_file = os.path.join(output_dir, f"split_{i+1}.pdf")
                with open(output_file, 'wb') as f:
                    pdf_writer.write(f)
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
        pdf_writer = PdfWriter()
        
        for pdf_file in pdf_list:
            with open(pdf_file, 'rb') as f:
                pdf_reader = PdfWriter()
                pdf_reader.append(f)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
        
        with open(output_pdf, 'wb') as f:
            pdf_writer.write(f)
        
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
        pdf_writer = PdfWriter()
        
        with open(input_pdf, 'rb') as f:
            pdf_reader = PdfWriter()
            pdf_reader.append(f)
            total_pages = len(pdf_reader.pages)
        
        # Convert to 0-indexed and create a set for faster lookup
        pages_to_remove_set = set(p - 1 for p in pages_to_remove if 1 <= p <= total_pages)
        
        with open(input_pdf, 'rb') as f:
            pdf_reader = PdfWriter()
            pdf_reader.append(f)
            
            for page_num in range(total_pages):
                if page_num not in pages_to_remove_set:
                    pdf_writer.add_page(pdf_reader.pages[page_num])
        
        with open(output_pdf, 'wb') as f:
            pdf_writer.write(f)
        
        return True
    except Exception as e:
        print(f"Remove pages error: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Accept 'pdf_file' (legacy) or 'files' (template) or 'file'
    if not any(k in request.files for k in ('pdf_file', 'file', 'files')):
        app.logger.info('convert: no file in request.files')
        flash('No files uploaded')
        return redirect(url_for('index'))

    if 'pdf_file' in request.files:
        files = request.files.getlist('pdf_file')
        _log_uploaded_files_by_field('pdf_file')
    elif 'file' in request.files:
        files = request.files.getlist('file')
        _log_uploaded_files_by_field('file')
    else:
        files = request.files.getlist('files')
        _log_uploaded_files_by_field('files')
    
    # Check if any files were selected
    if len(files) == 0 or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))
    
    # Filter valid PDF files
    valid_files = [f for f in files if f and allowed_file(f.filename)]
    
    if len(valid_files) == 0:
        flash('No valid PDF files found. Please upload PDF files only.')
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
            
            # Save uploaded file
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)
            
            # Generate output filename
            output_filename = f"BW_{filename}"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Convert to B/W with custom settings
            pdf_to_true_bw(input_path, output_path, dpi=dpi, threshold=threshold, 
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
            zip_path = os.path.join(temp_dir, 'converted_pdfs.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, file_name in converted_files:
                    zipf.write(file_path, file_name)
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name='converted_pdfs.zip',
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
    # Accept both 'file' and 'files' form field names (some clients send 'files')
    if not any(k in request.files for k in ('file', 'files')):
        app.logger.info('convert_to_pdf: no file in request.files')
        flash('No files uploaded')
        return redirect(url_for('index'))

    if 'file' in request.files:
        files = request.files.getlist('file')
    elif 'files' in request.files:
        files = request.files.getlist('files')
    else:
        # fallback: collect all file storages
        files = [f for f in request.files.values()]

    app.logger.info(f"convert_to_pdf received keys: {list(request.files.keys())}")
    _log_uploaded_files_by_field('file')
    
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
            if ext in IMAGE_ALLOWED_EXTENSIONS:
                image_to_pdf(input_path, output_path)
                converted_files.append((output_path, output_filename))
            
            elif ext in DOCUMENT_ALLOWED_EXTENSIONS:
                if docx_to_pdf(input_path, output_path):
                    converted_files.append((output_path, output_filename))
            
            elif ext in EXCEL_ALLOWED_EXTENSIONS:
                if excel_to_pdf(input_path, output_path):
                    converted_files.append((output_path, output_filename))
            else:
                flash(f'Unsupported file type: {ext}')
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
        app.logger.info('pdf_extract: no files in request.files')
        flash('No files uploaded')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    _log_uploaded_files_by_field('files')
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

@app.route('/ocr', methods=['POST'])
def ocr_route():
    """Extract text from images or PDF using OCR"""
    try:
        files = request.files.getlist('files')
        _log_uploaded_files_by_field('files')
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
    """Add watermark to PDF"""
    try:
        files = request.files.getlist('files')
        _log_uploaded_files_by_field('files')
        watermark_text = request.form.get('watermark_text', 'CONFIDENTIAL')
        position = request.form.get('watermark_position', 'diagonal')
        opacity = float(request.form.get('opacity', 0.3))
        
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
                
                output_pdf = os.path.join(temp_dir, f"{Path(filename).stem}_watermarked.pdf")
                if add_watermark(input_path, output_pdf, watermark_text, opacity, position):
                    converted_files.append(output_pdf)
            
            if len(converted_files) == 1:
                return send_file(converted_files[0], as_attachment=True)
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
        _log_uploaded_files_by_field('files')
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
        _log_uploaded_files_by_field('files')
        
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
        _log_uploaded_files_by_field('files')
        
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
        _log_uploaded_files_by_field('file')
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
        _log_uploaded_files_by_field('files')
        
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
        _log_uploaded_files_by_field('file')
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
            app.logger.info('decrypt_pdf: no file in request.files')
            flash('No file uploaded')
            return redirect(url_for('index'))

        file = request.files['file']
        _log_uploaded_files_by_field('file')
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

if __name__ == '__main__':
    # disable the reloader so logs go to a single process and file
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
