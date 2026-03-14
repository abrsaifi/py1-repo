
"""Handle PDF conversion operations with defensive import errors.

This module provides small helper wrappers but gives actionable
error messages when optional system packages are missing.
"""

import os
import tempfile
import zipfile
from pathlib import Path

try:
    from pdf2image import convert_from_path
except Exception as e:  # pragma: no cover - environment-specific
    raise ImportError(
        "pdf2image is required for PDF -> image conversion. "
        "Install it with `pip install pdf2image` and ensure poppler is installed on your system. "
        f"(Original error: {e})"
    )

try:
    import img2pdf
except Exception as e:  # pragma: no cover - environment-specific
    raise ImportError(
        "img2pdf is required for image -> PDF conversion. "
        "Install it with `pip install img2pdf`. (Original error: {0})".format(e)
    )


def pdf_to_images(input_pdf, dpi=300):
    """Convert PDF pages to PIL Image objects."""
    try:
        pages = convert_from_path(input_pdf, dpi=dpi)
        return pages
    except Exception:
        # Fallback: try PyMuPDF (fitz) if poppler/pdfinfo is not available
        try:
            import fitz  # PyMuPDF
            from PIL import Image

            doc = fitz.open(input_pdf)
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=dpi)
                mode = "RGB" if pix.n < 4 else "RGBA"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                images.append(img)
            return images
        except Exception as e:
            raise RuntimeError(
                "Failed to convert PDF to images. Ensure poppler is installed or install PyMuPDF. "
                f"(Original error: {e})"
            )


def images_to_pdf(images, output_pdf):
    """Convert image files back to PDF."""
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(images))


class PDFHandler:
    """Compatibility wrapper used by Celery PDF tasks."""

    def process(self, input_path, output_format, params=None):
        params = params or {}
        target_format = output_format.lower().lstrip('.')
        temp_dir = tempfile.mkdtemp(prefix='docpro-pdf-')

        if target_format == 'pdf':
            return {'path': input_path, 'size': os.path.getsize(input_path)}

        images = pdf_to_images(input_path, dpi=int(params.get('dpi', 300)))
        if not images:
            raise RuntimeError(f'PDF conversion produced no pages: {input_path}')

        if target_format in {'png', 'jpg', 'jpeg', 'webp'}:
            if len(images) == 1:
                output_path = os.path.join(temp_dir, f"{Path(input_path).stem}.{target_format}")
                save_format = 'JPEG' if target_format in {'jpg', 'jpeg'} else target_format.upper()
                image = images[0].convert('RGB') if save_format == 'JPEG' else images[0]
                image.save(output_path, save_format)
                return {'path': output_path, 'size': os.path.getsize(output_path)}

            archive_path = os.path.join(temp_dir, f"{Path(input_path).stem}-{target_format}.zip")
            with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for index, image in enumerate(images, start=1):
                    page_path = os.path.join(temp_dir, f"page-{index}.{target_format}")
                    save_format = 'JPEG' if target_format in {'jpg', 'jpeg'} else target_format.upper()
                    rendered = image.convert('RGB') if save_format == 'JPEG' else image
                    rendered.save(page_path, save_format)
                    archive.write(page_path, arcname=os.path.basename(page_path))
            return {'path': archive_path, 'size': os.path.getsize(archive_path)}

        raise ValueError(f'Unsupported PDF output format: {output_format}')
