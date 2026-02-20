"""
Watermarking service for PDFs.
Handles text watermarks, image watermarks, and various positioning options.
"""

import os
import math
import fitz  # PyMuPDF
from PIL import Image as PILImage


def add_watermark(input_pdf, output_pdf, watermark_text, opacity=0.3, position='diagonal',
                 font_size=60, color=(0.5, 0.5, 0.5), fontname='helv', pages=None, 
                 rotation=0, scale=1.0):
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
            
            # Insert text with rotation
            shape = page.new_shape()
            shape.insert_textbox(
                fitz.Rect(x - 200, y - 50, x + 200, y + 50),
                watermark_text,
                fontsize=adjusted_font_size,
                color=color,
                fontname=fontname,
                align=fitz.TEXT_ALIGN_CENTER
            )
            shape.commit(mod="keep", matrix=fitz.Matrix().rotate_around(fitz.Point(x, y), angle))
        
        pdf_doc.save(output_pdf, deflate=True)
        pdf_doc.close()
        return True
    except Exception as e:
        print(f"Watermark error: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_image_watermark(input_pdf, output_pdf, image_path, position='center', 
                       scale=100, scale_unit='percent', pages=None):
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
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Calculate image dimensions
            if scale_unit == 'inches':
                img_width = scale * 72  # Convert inches to points
                img_height = img_width * pil_img.height / pil_img.width
            else:  # percent
                img_width = (width * scale) / 100
                img_height = img_width * pil_img.height / pil_img.width
            
            # Position calculation
            padding = 20
            if position == 'center':
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
