"""Main application orchestration."""
from pdf_handler import pdf_to_images, images_to_pdf
from image_processor import process_images_to_bw
from file_utils import save_images_to_temp, cleanup_temp_files


def pdf_to_true_bw(input_pdf, output_pdf, dpi=300, threshold=128):
    """Convert PDF to true black and white."""
    # Convert PDF pages to images
    pages = pdf_to_images(input_pdf, dpi=dpi)
    
    # Process images to black and white
    bw_images = process_images_to_bw(pages, threshold)
    
    # Save images to temp files
    temp_files = save_images_to_temp(bw_images)
    
    # Convert images back to PDF
    images_to_pdf(temp_files, output_pdf)
    
    # Cleanup temp files
    cleanup_temp_files(temp_files)
    
    print(f"Converted to true B/W: {output_pdf}")


# Example usage
if __name__ == "__main__":
    pdf_to_true_bw("input.pdf", "output_bw.pdf")
