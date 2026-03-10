#!/usr/bin/env python
"""Test all critical imports for the conversion system."""
import sys

print("Testing all critical imports...")
errors = []

try:
    import pdf2image
    print("✓ pdf2image")
except ImportError as e:
    errors.append(f"pdf2image: {e}")

try:
    import img2pdf
    print("✓ img2pdf")
except ImportError as e:
    errors.append(f"img2pdf: {e}")

try:
    from app.pdf_handler import pdf_to_images, images_to_pdf
    print("✓ pdf_handler")
except ImportError as e:
    errors.append(f"pdf_handler: {e}")

try:
    from app.image_processor import process_images_to_bw
    print("✓ image_processor")
except ImportError as e:
    errors.append(f"image_processor: {e}")

try:
    from app.file_utils import save_images_to_temp, cleanup_temp_files
    print("✓ file_utils")
except ImportError as e:
    errors.append(f"file_utils: {e}")

try:
    from docx import Document
    print("✓ python-docx")
except ImportError as e:
    errors.append(f"python-docx: {e}")

try:
    from openpyxl import load_workbook
    print("✓ openpyxl")
except ImportError as e:
    errors.append(f"openpyxl: {e}")

try:
    from pptx import Presentation
    print("✓ python-pptx")
except ImportError as e:
    errors.append(f"python-pptx: {e}")

try:
    import reportlab
    print("✓ reportlab")
except ImportError as e:
    errors.append(f"reportlab: {e}")

try:
    import requests
    print("✓ requests")
except ImportError as e:
    errors.append(f"requests: {e}")

try:
    from bs4 import BeautifulSoup
    print("✓ beautifulsoup4")
except ImportError as e:
    errors.append(f"beautifulsoup4: {e}")

try:
    import pandas as pd
    print("✓ pandas")
except ImportError as e:
    errors.append(f"pandas: {e}")

try:
    import numpy as np
    print("✓ numpy")
except ImportError as e:
    errors.append(f"numpy: {e}")

try:
    from flask import Flask, render_template
    print("✓ Flask")
except ImportError as e:
    errors.append(f"Flask: {e}")

try:
    import easyocr
    print("✓ easyocr")
except ImportError as e:
    errors.append(f"easyocr: {e}")

try:
    import torch
    print("✓ torch")
except ImportError as e:
    errors.append(f"torch: {e}")

try:
    from weasyprint import HTML
    print("✓ weasyprint")
except (ImportError, OSError) as e:
    print("⚠ weasyprint (requires system libraries - OPTIONAL)")

try:
    from PIL import Image
    print("✓ Pillow")
except ImportError as e:
    errors.append(f"Pillow: {e}")

try:
    import cv2
    print("✓ opencv-python")
except ImportError as e:
    errors.append(f"opencv-python: {e}")

try:
    import pythonjsonlogger
    print("✓ python-json-logger")
except ImportError as e:
    errors.append(f"python-json-logger: {e}")

try:
    import pytest
    print("✓ pytest")
except ImportError as e:
    errors.append(f"pytest: {e}")

print("\n" + "="*50)
if errors:
    print(f"❌ {len(errors)} Import Errors:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("✅ ALL IMPORTS SUCCESSFUL!\n")
    sys.exit(0)
