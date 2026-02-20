"""Handle PDF conversion operations."""
from pdf2image import convert_from_path
import img2pdf


def pdf_to_images(input_pdf, dpi=300):
    """Convert PDF pages to PIL Image objects."""
    pages = convert_from_path(input_pdf, dpi=dpi)
    return pages


def images_to_pdf(images, output_pdf):
    """Convert image files back to PDF."""
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(images))
