"""
Image processing and manipulation service.
Handles image format conversions, resizing, compression, background removal, etc.
"""

import os
import io
import tempfile
import shutil
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import fitz  # PyMuPDF
from pathlib import Path


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


def pdf_to_true_bw(input_pdf, output_pdf, dpi=300, threshold=250, contrast=3.0, 
                   sharpness=2.5, brightness=0, gamma=1.0, blur=0, invert=False, denoise=0):
    """Convert PDF to true black and white with advanced image processing."""
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import letter
    import numpy as np
    
    try:
        # Open PDF
        doc = fitz.open(input_pdf)
        c = pdf_canvas.Canvas(output_pdf, pagesize=letter)
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            
            # Render at specified DPI
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Apply brightness adjustment
            if brightness and brightness != 0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.0 + (brightness / 100.0))
            
            # Apply gamma correction
            if gamma and gamma != 1.0:
                img_array = np.array(img, dtype=np.float32) / 255.0
                img_array = np.power(img_array, 1.0 / gamma)
                img = Image.fromarray((img_array * 255).astype(np.uint8))
            
            # Convert to grayscale
            img_gray = img.convert('L')
            
            # Apply denoise if specified
            if denoise and denoise > 0:
                img_gray = img_gray.filter(ImageFilter.MedianFilter(size=int(denoise + 1)))
            
            # Apply sharpness
            if sharpness and sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(img_gray.convert('RGB'))
                img_gray = enhancer.enhance(float(sharpness)).convert('L')
            
            # Apply contrast
            if contrast and contrast != 1:
                enhancer = ImageEnhance.Contrast(img_gray)
                img_gray = enhancer.enhance(float(contrast))
            
            # Apply threshold to convert to true B&W
            if threshold is not None:
                img_bw = img_gray.point(lambda x: 255 if x > threshold else 0, '1')
                img_bw = img_bw.convert('RGB')
                processed_img = img_bw
            else:
                processed_img = img_gray.convert('RGB')
            
            # Apply blur if specified
            if blur and blur > 0:
                processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=float(blur)))
            
            # Apply color inversion
            if invert:
                processed_img = ImageOps.invert(processed_img.convert('RGB'))
            
            # Save temp image and draw on PDF
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                temp_img_path = tmp.name
            processed_img.save(temp_img_path)
            
            # Draw on PDF (fit to letter size)
            c.drawImage(temp_img_path, 0, 0, width=letter[0], height=letter[1])
            c.showPage()
            
            try:
                os.unlink(temp_img_path)
            except:
                pass
        
        c.save()
        doc.close()
        return True
    except Exception as e:
        print(f"PDF to B&W error: {e}")
        import traceback
        traceback.print_exc()
        return False


def resize_image_route():
    """Resize an image."""
    # This is a route function - will be implemented in server.py
    pass


def compress_image_route():
    """Compress an image file."""
    # This is a route function - will be implemented in server.py
    pass


def bg_to_white_route():
    """Convert background of an image to white."""
    # This is a route function - will be implemented in server.py
    pass
