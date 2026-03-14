"""Handle image processing operations."""
import os
import tempfile
from pathlib import Path

from PIL import Image

from app.services.conversions import convert_image_format


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


class ImageProcessor:
    """Compatibility wrapper used by Celery image tasks."""

    def process(self, input_path, output_format, params=None):
        params = params or {}
        output_path = params.get('output_path')
        if not output_path:
            temp_dir = tempfile.mkdtemp(prefix='docpro-image-')
            output_path = os.path.join(temp_dir, f"{Path(input_path).stem}.{output_format.lower().lstrip('.')}")

        success = convert_image_format(
            input_path,
            output_path,
            output_format,
            quality=int(params.get('quality', 85)),
            lossless=bool(params.get('lossless', False)),
        )
        if not success or not os.path.exists(output_path):
            raise RuntimeError(f'Image conversion failed: {input_path} -> {output_format}')

        return {
            'path': output_path,
            'size': os.path.getsize(output_path),
        }
