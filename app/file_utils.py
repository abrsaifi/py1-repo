"""Handle file operations and cleanup."""
import os


def save_images_to_temp(images):
    """Save images to temporary PNG files."""
    temp_files = []
    for i, img in enumerate(images):
        temp_path = f"_temp_page_{i}.png"
        img.save(temp_path)
        temp_files.append(temp_path)
    return temp_files


def cleanup_temp_files(temp_files):
    """Remove temporary files."""
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
