
"""Handle PDF conversion operations with defensive import errors.

This module provides small helper wrappers but gives actionable
error messages when optional system packages are missing.
"""

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
