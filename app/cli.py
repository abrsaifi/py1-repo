"""Package CLI and entry points using Click."""
import sys
import click

from .pdf_handler import pdf_to_images, images_to_pdf
from .image_processor import process_images_to_bw
from .file_utils import save_images_to_temp, cleanup_temp_files


@click.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.option("--dpi", default=300, help="DPI for rasterizing PDF pages")
@click.option("--threshold", default=128, help="Threshold for B/W conversion")
def pdf_to_true_bw(input_pdf, output_pdf, dpi, threshold):
    """Convert PDF to true black and white."""
    pages = pdf_to_images(input_pdf, dpi=dpi)
    bw_images = process_images_to_bw(pages, threshold)
    temp_files = save_images_to_temp(bw_images)
    try:
        images_to_pdf(temp_files, output_pdf)
        click.echo(f"Converted to true B/W: {output_pdf}")
    finally:
        cleanup_temp_files(temp_files)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    return pdf_to_true_bw.main(args=argv)


if __name__ == "__main__":
    pdf_to_true_bw()
