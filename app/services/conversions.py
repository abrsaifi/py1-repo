import os
import tempfile
import shutil
import zipfile
from pathlib import Path
from PIL import Image
import io

try:
    import fitz
except Exception:
    fitz = None


IMAGE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'}


def convert_image_format(input_path, output_path, target_format, quality=85, lossless=False):
    try:
        img = Image.open(input_path)
        fmt = target_format.lower().lstrip('.')

        if fmt in ('jpg', 'jpeg'):
            if img.mode in ('RGBA', 'LA') or ('A' in img.getbands()):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.convert('RGBA').split()[-1])
                img = background
            else:
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality)
        elif fmt == 'png':
            img.save(output_path, 'PNG')
        elif fmt == 'webp':
            save_kwargs = {'quality': quality}
            if lossless:
                save_kwargs['lossless'] = True
            try:
                img.save(output_path, 'WEBP', **save_kwargs)
            except Exception:
                img.convert('RGB').save(output_path, 'WEBP', **save_kwargs)
        elif fmt in ('tiff', 'tif'):
            img.save(output_path, 'TIFF')
        else:
            img.save(output_path)

        return True
    except Exception as e:
        print(f"Image conversion error: {e}")
        return False


def validate_image_file(path):
    try:
        if not os.path.exists(path):
            return False, 'file_missing'
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext not in IMAGE_ALLOWED_EXTENSIONS:
            return False, 'bad_extension'
        with Image.open(path) as im:
            im.verify()
        return True, ''
    except Exception as e:
        return False, str(e)


def _generate_preview_from_pdf(pdf_path, dpi=150):
    try:
        if fitz is None:
            return None
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return None
        page = doc[0]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes('png')
        doc.close()
        return img_bytes
    except Exception:
        return None


def image_to_pdf(image_path, output_pdf):
    try:
        img = Image.open(image_path)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_pdf, 'PDF')
        return True
    except Exception:
        return False
