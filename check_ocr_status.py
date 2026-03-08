#!/usr/bin/env python
"""Quick check for PaddleOCR installation status."""

from services.ocr_enhanced import get_ocr_status
from services.ocr import get_ocr_engines_status

print("="*70)
print("OCR ENGINE STATUS CHECK")
print("="*70)

status = get_ocr_status()
print("\nAvailable Engines:")
for engine, available in status.items():
    symbol = "✓" if available else "✗"
    print(f"  {symbol} {engine.upper()}: {'Installed & Available' if available else 'Not installed'}")

print("\n" + "="*70)
sys_status = get_ocr_engines_status()
print(f"Primary Engine: {sys_status['primary_engine'].upper()}")
print("="*70)

if status.get('paddleocr'):
    print("\n✅ PADDLEOCR IS INSTALLED & ACTIVE")
    print("   System is running with 2-3x faster text extraction!")
else:
    print("\n⚠️  PaddleOCR not installed")
    print("   System is using EasyOCR as primary engine")
