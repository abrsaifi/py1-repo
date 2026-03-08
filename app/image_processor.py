"""Handle image processing operations."""
from PIL import Image


def convert_to_bw(image, threshold=128):
    """Convert a PIL Image to pure black and white."""
    # Convert to grayscale first
    gray = image.convert("L")
    
    # Apply threshold to get pure black/white
    bw = gray.point(lambda x: 255 if x > threshold else 0, '1')
    
    return bw


def process_images_to_bw(images, threshold=128):
    """Convert multiple images to black and white."""
    bw_images = []
    for page in images:
        bw = convert_to_bw(page, threshold)
        bw_images.append(bw)
    return bw_images
