"""
PDF manipulation and processing tools.
"""

import os
import io
import tempfile
from pathlib import Path
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter


def encrypt_pdf(input_path, output_path, password):
    """Encrypt a PDF with a password."""
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


def decrypt_pdf(input_pdf, output_pdf, password):
    """Decrypt an encrypted PDF given the user password."""
    try:
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


def split_pdf(input_pdf, output_dir, page_ranges):
    """Split PDF into multiple files based on page ranges
    page_ranges: list of tuples [(start1, end1), (start2, end2), ...]
    Page numbers are 1-indexed
    """
    try:
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
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        # Convert to 0-indexed set
        pages_set = set(p - 1 for p in pages_to_remove if p > 0)
        
        for page_num, page in enumerate(reader.pages):
            if page_num not in pages_set:
                writer.add_page(page)
        
        with open(output_pdf, 'wb') as f:
            writer.write(f)
        
        return True
    except Exception as e:
        print(f"Remove pages error: {e}")
        return False


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
                # Use fitz search function to find text
                text_rects = page.search_for(keyword, flags=fitz.TEXT_PRESERVE_WHITESPACE)
                
                for rect in text_rects:
                    # Draw redaction rectangle
                    page.draw_rect(rect, color=redaction_color, fill=redaction_color)
                    redacted_count += 1
        
        pdf_doc.save(output_pdf, deflate=True)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Redaction error: {e}")
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
