"""
Document format conversion service.
Handles conversions between DOCX, XLSX, PPTX, PDF, HTML, TXT, and CSV.
"""

import os
import io
import tempfile
import shutil
import subprocess
from pathlib import Path
import uuid

import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
from docx import Document as DocxDocument
from reportlab.lib.pagesizes import letter, A4, A3, landscape, portrait
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Border, Side, Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XlImage

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

from datetime import datetime
import csv as csv_module

# Configure logger
import logging
logger = logging.getLogger(__name__)


# ========================
# SHEET MANAGEMENT FUNCTIONS
# ========================

def get_sheet_info(file_path):
    """
    Get information about all sheets in Excel or CSV file.
    Returns: {
        'file_name': str,
        'file_type': 'excel' | 'csv',
        'sheets': [
            {
                'name': str,
                'index': int,
                'rows': int,
                'columns': int,
                'preview': [[cell_value, ...], ...] (first 5 rows)
            }
        ]
    }
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.xlsx', '.xls', '.ods']:
            return _get_excel_sheets(file_path)
        elif file_ext == '.csv':
            return _get_csv_sheets(file_path)
        else:
            return {'error': f'Unsupported format: {file_ext}'}
    except Exception as e:
        logger.error(f"Error reading sheets: {e}")
        return {'error': str(e)}


def _get_excel_sheets(file_path):
    """Get sheet information from Excel file"""
    try:
        wb = load_workbook(file_path, data_only=True)
        file_name = Path(file_path).name
        
        sheets = []
        for idx, sheet_name in enumerate(wb.sheetnames):
            ws = wb[sheet_name]
            
            # Get dimensions
            max_row = ws.max_row
            max_col = ws.max_column
            
            # Get preview (first 5 rows)
            preview = []
            for row_idx, row in enumerate(ws.iter_rows(max_row=5, values_only=True), 1):
                preview.append(list(row))
            
            sheets.append({
                'name': sheet_name,
                'index': idx,
                'rows': max_row,
                'columns': max_col,
                'preview': preview
            })
        
        wb.close()
        
        return {
            'file_name': file_name,
            'file_type': 'excel',
            'sheets': sheets
        }
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return {'error': str(e)}


def _get_csv_sheets(file_path):
    """Get sheet information from CSV file (treats entire CSV as one sheet)"""
    try:
        file_name = Path(file_path).name
        preview = []
        row_count = 0
        col_count = 0
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv_module.reader(f)
            for row_idx, row in enumerate(reader):
                row_count += 1
                if row_idx == 0:
                    col_count = len(row)
                if row_idx < 5:
                    preview.append(row)
        
        return {
            'file_name': file_name,
            'file_type': 'csv',
            'sheets': [{
                'name': Path(file_path).stem,
                'index': 0,
                'rows': row_count,
                'columns': col_count,
                'preview': preview
            }]
        }
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return {'error': str(e)}


def combine_csvs_to_excel(csv_files, output_path, sheet_names=None):
    """
    Combine multiple CSV files into a single Excel workbook.
    
    Args:
        csv_files: List of CSV file paths
        output_path: Output Excel file path
        sheet_names: Optional list of sheet names (defaults to filenames)
    
    Returns: True if successful, False otherwise
    """
    try:
        wb = Workbook()
        wb.remove(wb.active)  # Remove default empty sheet
        
        for idx, csv_file in enumerate(csv_files):
            # Determine sheet name
            if sheet_names and idx < len(sheet_names):
                sheet_name = sheet_names[idx]
            else:
                sheet_name = Path(csv_file).stem[:31]  # Excel max 31 chars
            
            # Read CSV and add to workbook
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv_module.reader(f)
                ws = wb.create_sheet(sheet_name)
                
                for row_idx, row in enumerate(reader, 1):
                    for col_idx, value in enumerate(row, 1):
                        ws.cell(row=row_idx, column=col_idx, value=value)
        
        wb.save(output_path)
        wb.close()
        logger.info(f"Created multi-sheet Excel: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error combining CSVs: {e}")
        return False


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


def docx_to_pdf(docx_path, output_pdf, preserve_colors=True, preserve_images=True):
    """Convert DOCX to PDF with color and image preservation using LibreOffice"""
    try:
        # Use LibreOffice for best formatting/color/image preservation
        import subprocess
        from pathlib import Path
        
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        # LibreOffice command for DOCX -> PDF conversion
        cmd = [
            get_soffice_path(),
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', out_dir,
            docx_path
        ]
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        if result.returncode == 0:
            # Find the generated PDF (LibreOffice creates it with original filename stem)
            temp_pdf = os.path.join(out_dir, f"{Path(docx_path).stem}.pdf")
            
            if os.path.exists(temp_pdf):
                # Move to target location if different
                if os.path.abspath(temp_pdf) != os.path.abspath(output_pdf):
                    shutil.move(temp_pdf, output_pdf)
                return True
        
        # Fallback: Try with LibreOffice's native conversion
        return False
        
    except Exception as e:
        print(f"DOCX to PDF error (LibreOffice): {e}")
        
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


def _create_property(name, value):
    try:
        from com.sun.star.beans import PropertyValue
        p = PropertyValue()
        p.Name = name
        p.Value = value
        return p
    except Exception:
        return None


def soffice_to_pdf(input_path, output_pdf, timeout=60):
    """Hybrid conversion: try UNO daemon first, fall back to `soffice` CLI.

    Uses environment variables to control daemon host/port:
      - LIBREOFFICE_DAEMON_HOST (default: unset)
      - LIBREOFFICE_DAEMON_PORT (default: unset)
      - LIBREOFFICE_PREFER_DAEMON (1/0, default: 1)

    Returns True on success.
    """
    out_dir = os.path.dirname(output_pdf) or '.'
    os.makedirs(out_dir, exist_ok=True)

    host = os.environ.get('LIBREOFFICE_DAEMON_HOST')
    port = os.environ.get('LIBREOFFICE_DAEMON_PORT')
    prefer = os.environ.get('LIBREOFFICE_PREFER_DAEMON', '1')
    use_daemon = bool(host and port and prefer.lower() in ('1', 'true', 'yes'))

    # Attempt UNO daemon conversion if configured
    if use_daemon:
        try:
            import uno
            # Resolve a remote office component context
            local_ctx = uno.getComponentContext()
            resolver = local_ctx.ServiceManager.createInstanceWithContext(
                'com.sun.star.bridge.UnoUrlResolver', local_ctx
            )
            uno_url = f'uno:socket,host={host},port={port};urp;StarOffice.ComponentContext'
            ctx = resolver.resolve(uno_url)
            smgr = ctx.ServiceManager
            desktop = smgr.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)

            # Map extension -> export filter
            ext = Path(input_path).suffix.lower()
            filter_name = 'writer_pdf_Export'
            if ext in ('.xls', '.xlsx', '.ods', '.csv'):
                filter_name = 'calc_pdf_Export'
            elif ext in ('.ppt', '.pptx', '.odp'):
                filter_name = 'impress_pdf_Export'

            # Build UNO file URLs and property arrays
            file_url = uno.systemPathToFileUrl(os.path.abspath(input_path))
            pdf_url = uno.systemPathToFileUrl(os.path.abspath(output_pdf))

            hidden_prop = _create_property('Hidden', True)
            load_props = tuple(p for p in (hidden_prop,) if p is not None)

            # Load document
            component = desktop.loadComponentFromURL(file_url, '_blank', 0, load_props)

            # Prepare export properties
            filter_prop = _create_property('FilterName', filter_name)
            store_props = tuple(p for p in (filter_prop,) if p is not None)

            # Store (export) to PDF
            component.storeToURL(pdf_url, store_props)
            try:
                component.close(True)
            except Exception:
                try:
                    component.dispose()
                except Exception:
                    pass

            if os.path.exists(output_pdf):
                return True
            # If UNO produced the file in out_dir with original stem, try to move
            produced = os.path.join(out_dir, f"{Path(input_path).stem}.pdf")
            if os.path.exists(produced):
                try:
                    if os.path.exists(output_pdf):
                        os.remove(output_pdf)
                except Exception:
                    pass
                shutil.move(produced, output_pdf)
                return os.path.exists(output_pdf)

        except Exception as e:
            logger.warning(f"UNO daemon conversion failed: {e}; falling back to CLI")

    # Fallback to CLI-based soffice conversion
    try:
        cmd = [
            get_soffice_path(),
            '--headless',
            '--nologo',
            '--nolockcheck',
            '--nodefault',
            '--nofirststartwizard',
            '--convert-to',
            'pdf',
            '--outdir',
            out_dir,
            input_path,
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            logger.error(f"soffice CLI conversion failed: {proc.returncode} stdout={proc.stdout} stderr={proc.stderr}")
            return False

        produced = os.path.join(out_dir, f"{Path(input_path).stem}.pdf")
        if not os.path.exists(produced):
            return False

        if os.path.abspath(produced) != os.path.abspath(output_pdf):
            try:
                if os.path.exists(output_pdf):
                    os.remove(output_pdf)
            except Exception:
                pass
            shutil.move(produced, output_pdf)

        return os.path.exists(output_pdf)
    except Exception as e:
        logger.error(f"soffice CLI conversion exception: {e}")
        return False


def excel_to_pdf(excel_path, output_pdf, **kwargs):
    """
    Convert Excel to PDF with sheet selection support.
    
    Parameters:
        excel_path: Path to Excel file
        output_pdf: Output PDF path
        **kwargs:
            sheets: 'all' | list of sheet names/indices | single sheet name/index
            merge_sheets: If True and sheets is list, merge into one PDF
            orientation: 'portrait' | 'landscape'
            paper_size: 'A4', 'A3', 'LETTER', etc.
            margin_top, margin_bottom, margin_left, margin_right: in mm
            include_headers: bool
            gridlines: bool
            scale_factor: percentage (default 100)
    
    Returns: True if successful, False otherwise
    """
    try:
        # Get parameters
        sheets_param = kwargs.get('sheets', 'all')
        merge_sheets = kwargs.get('merge_sheets', False)
        orientation = kwargs.get('orientation', 'portrait').lower()
        paper_size = kwargs.get('paper_size', 'A4').upper()
        margin_top = float(kwargs.get('margin_top', 25))
        margin_bottom = float(kwargs.get('margin_bottom', 25))
        margin_left = float(kwargs.get('margin_left', 25))
        margin_right = float(kwargs.get('margin_right', 25))
        include_headers = kwargs.get('include_headers', True)
        gridlines = kwargs.get('gridlines', False)
        scale_factor = float(kwargs.get('scale_factor', 100))
        
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        # Load workbook to get sheet names
        wb = load_workbook(excel_path)
        
        # Determine which sheets to convert
        if sheets_param == 'all':
            sheets_to_convert = wb.sheetnames
        elif isinstance(sheets_param, str):
            sheets_to_convert = [sheets_param]
        elif isinstance(sheets_param, list):
            sheets_to_convert = sheets_param
        else:
            sheets_to_convert = [wb.sheetnames[0]]  # Default to first sheet
        
        wb.close()
        
        logger.info(f"Converting sheets: {sheets_to_convert}, merge={merge_sheets}")
        
        created_pdfs = []
        
        # Create temporary modified Excel for each sheet
        for sheet_name in sheets_to_convert:
            temp_excel = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False).name
            shutil.copy(excel_path, temp_excel)
            
            try:
                # Load and modify workbook to show only target sheet
                wb = load_workbook(temp_excel)
                
                # Hide all sheets except the target one
                for sheet in wb.sheetnames:
                    wb[sheet].sheet_state = 'hidden' if sheet != sheet_name else 'visible'
                
                ws = wb[sheet_name]
                
                # Apply page setup parameters
                from openpyxl.worksheet.page import PageMargins, PrintOptions
                
                paper_size_map = {
                    'A4': 9, 'A3': 8, 'A5': 11,
                    'LETTER': 1, 'LEGAL': 5,
                }
                
                ws.page_setup.paperSize = paper_size_map.get(paper_size, 9)
                ws.page_setup.orientation = 'landscape' if orientation == 'landscape' else 'portrait'
                
                ws.page_margins = PageMargins(
                    left=margin_left / 25.4,
                    right=margin_right / 25.4,
                    top=margin_top / 25.4,
                    bottom=margin_bottom / 25.4,
                    header=0.3,
                    footer=0.3
                )
                
                ws.print_options = PrintOptions(
                    horizontalCentered=False,
                    verticalCentered=False
                )
                
                # Apply gridlines and headers settings
                if gridlines:
                    ws.sheet_view.showGridLines = True
                if include_headers:
                    ws.print_options.printHeadings = True
                
                ws.page_setup.scale = int(scale_factor)
                
                wb.save(temp_excel)
                wb.close()
                
                # Convert with LibreOffice
                soffice = get_soffice_path()
                cmd = [
                    soffice,
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', out_dir,
                    temp_excel
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=120)
                
                if result.returncode == 0:
                    generated_pdf = os.path.join(out_dir, f"{Path(temp_excel).stem}.pdf")
                    if os.path.exists(generated_pdf):
                        created_pdfs.append((sheet_name, generated_pdf))
                        logger.info(f"Created PDF for sheet '{sheet_name}'")
                
            finally:
                try:
                    os.unlink(temp_excel)
                except:
                    pass
        
        if not created_pdfs:
            logger.error("No PDFs were created")
            return False
        
        # Handle single vs multiple PDFs
        if len(created_pdfs) == 1:
            # Single PDF - just move it
            _, pdf_path = created_pdfs[0]
            if os.path.abspath(pdf_path) != os.path.abspath(output_pdf):
                shutil.move(pdf_path, output_pdf)
            logger.info(f"Created PDF: {output_pdf}")
            return True
        
        elif merge_sheets:
            # Merge multiple PDFs into one
            from pypdf import PdfMerger
            merger = PdfMerger()
            
            try:
                for sheet_name, pdf_path in created_pdfs:
                    merger.append(pdf_path)
                
                merger.write(output_pdf)
                merger.close()
                
                # Cleanup individual PDFs
                for _, pdf_path in created_pdfs:
                    try:
                        os.unlink(pdf_path)
                    except:
                        pass
                
                logger.info(f"Merged {len(created_pdfs)} sheets into: {output_pdf}")
                return True
            except Exception as e:
                logger.error(f"Error merging PDFs: {e}")
                merger.close()
                return False
        
        else:
            # Multiple PDFs - create a zip file
            import zipfile
            zip_path = output_pdf.replace('.pdf', '.zip')
            
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for sheet_name, pdf_path in created_pdfs:
                        arcname = f"{sheet_name}.pdf"
                        zf.write(pdf_path, arcname=arcname)
                
                # Cleanup individual PDFs
                for _, pdf_path in created_pdfs:
                    try:
                        os.unlink(pdf_path)
                    except:
                        pass
                
                logger.info(f"Created ZIP with {len(created_pdfs)} sheets: {zip_path}")
                return True
            except Exception as e:
                logger.error(f"Error creating ZIP: {e}")
                return False
        
    except Exception as e:
        logger.error(f"Excel to PDF error: {e}", exc_info=True)
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


def powerpoint_to_pdf(pptx_path, output_pdf):
    """Convert PowerPoint presentation to PDF using LibreOffice"""
    try:
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
        
        print(f"LibreOffice conversion failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
        return False
        
    except Exception as e:
        print(f"PowerPoint to PDF error: {e}")
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


def html_to_pdf(html_file, output_pdf, **kwargs):
    """Convert HTML file to PDF using LibreOffice"""
    try:
        out_dir = os.path.dirname(output_pdf) or '.'
        os.makedirs(out_dir, exist_ok=True)
        
        # Ensure html_file is an absolute path
        html_file = os.path.abspath(html_file)
        
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
        
        print(f"LibreOffice HTML to PDF conversion failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
        return False
        
    except Exception as e:
        print(f"HTML to PDF error: {e}")
        return False


def pdf_to_html(pdf_path, output_html):
    """Convert PDF to HTML preserving document structure"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PDF to HTML Conversion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .page {
            page-break-after: always;
            border: 1px solid #ddd;
            margin-bottom: 20px;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #999;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .text {
            margin: 10px 0;
        }
    </style>
</head>
<body>
"""
            
            for page_num, page in enumerate(pdf.pages, 1):
                html_content += f'<div class="page"><h2>Page {page_num}</h2>'
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table_data in tables:
                        if table_data:
                            html_content += '<table>'
                            for row in table_data:
                                html_content += '<tr>'
                                for cell in row:
                                    cell_content = str(cell) if cell else ''
                                    html_content += f'<td>{cell_content}</td>'
                                html_content += '</tr>'
                            html_content += '</table>'
                
                # Extract text
                text = page.extract_text()
                if text:
                    html_content += f'<div class="text"><p>{text.replace(chr(10), "</p><p>")}</p></div>'
                
                html_content += '</div>'
            
            html_content += """
</body>
</html>
"""
            
            # Write HTML file
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        
    except Exception as e:
        print(f"PDF to HTML error: {e}")
        return False


def image_to_pdf(image_path, output_pdf):
    """Convert image to PDF"""
    try:
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
    except Exception as e:
        print(f"Image to PDF error: {e}")
        return False


def pdf_to_excel(pdf_path, output_xlsx):
    """Convert PDF tables to Excel workbook"""
    try:
        import pdfplumber
        from openpyxl import Workbook
        
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table_num, table in enumerate(tables):
                        sheet_name = f"Page {page_num + 1} Table {table_num + 1}"[:31]
                        ws = wb.create_sheet(sheet_name)
                        
                        for row_idx, row in enumerate(table, 1):
                            for col_idx, value in enumerate(row, 1):
                                ws.cell(row=row_idx, column=col_idx, value=value)
        
        wb.save(output_xlsx)
        wb.close()
        logger.info(f"PDF to Excel: {output_xlsx}")
        return True
    except Exception as e:
        logger.error(f"PDF to Excel error: {e}")
        return False


def excel_to_csv(excel_path, output_csv, sheet_name=None):
    """Convert Excel sheet to CSV"""
    try:
        import csv as csv_module
        
        wb = load_workbook(excel_path, data_only=True)
        
        if sheet_name:
            ws = wb[sheet_name]
        else:
            ws = wb.active
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv_module.writer(f)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(row)
        
        wb.close()
        logger.info(f"Excel to CSV: {output_csv}")
        return True
    except Exception as e:
        logger.error(f"Excel to CSV error: {e}")
        return False


def url_to_pdf(webpage_url, output_pdf, timeout=30):
    """Convert webpage URL to PDF"""
    try:
        if requests is None or BeautifulSoup is None:
            logger.error("requests/BeautifulSoup not available")
            return False
        
        response = requests.get(webpage_url, timeout=timeout)
        response.raise_for_status()
        
        # Use WeasyPrint if available
        if WeasyHTML is not None:
            WeasyHTML(string=response.text).write_pdf(output_pdf)
        else:
            logger.error("WeasyPrint not available for URL to PDF")
            return False
        
        logger.info(f"URL to PDF: {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"URL to PDF error: {e}")
        return False


def text_to_pdf(text_content, output_pdf, **kwargs):
    """Convert plain text to PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        
        c = canvas.Canvas(output_pdf, pagesize=letter)
        width, height = letter
        
        margin = 0.5 * inch
        max_width = width - 2 * margin
        text_lines = text_content.split('\n')
        
        y_pos = height - margin
        font_size = kwargs.get('font_size', 11)
        c.setFont("Helvetica", font_size)
        
        for line in text_lines:
            if y_pos < margin:
                c.showPage()
                y_pos = height - margin
                c.setFont("Helvetica", font_size)
            
            c.drawString(margin, y_pos, line[:80])
            y_pos -= font_size + 2
        
        c.save()
        logger.info(f"Text to PDF: {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Text to PDF error: {e}")
        return False
