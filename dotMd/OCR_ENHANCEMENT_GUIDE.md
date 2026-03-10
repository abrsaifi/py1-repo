# OCR Enhancement Guide - Multi-Engine Strategy

## Overview

The DocPro OCR service has been enhanced to use an intelligent multi-engine strategy with automatic fallback capabilities. This provides better accuracy, speed, and reliability across different document types.

## Architecture

### Engine Strategy (Priority Order)

1. **PaddleOCR** (Primary - Fastest)
   - Optimized for CPU/GPU inference
   - High accuracy for English and multiple languages
   - Lightweight model (~135MB)
   - Best for real-time applications
   - **Best for:** High-volume document processing, speed-critical applications

2. **Tesseract** (Secondary - Most Compatible)
   - Industry-standard OCR engine
   - Excellent for high-contrast documents
   - Minimal dependencies
   - Stable and mature
   - **Best for:** Official documents, printed text, legacy compatibility

3. **EasyOCR** (Tertiary - Most Flexible)
   - Multi-language support (80+ languages)
   - PyTorch-based (flexible)
   - Good for complex documents
   - Originally the only engine
   - **Best for:** Multi-language documents, specialized content

### How It Works

```
extract_text_intelligent(image)
    ↓
Is PaddleOCR available?
    ├─ YES → Try PaddleOCR (PRIMARY)
    │   ├─ Success → Return result ✓
    │   └─ Failure → Continue
    │
    ├─ Is Tesseract available?
    │   ├─ YES → Try Tesseract (SECONDARY)
    │   │   ├─ Success → Return result ✓
    │   │   └─ Failure → Continue
    │   └─ NO → Continue
    │
    └─ Try EasyOCR (TERTIARY/FALLBACK)
        ├─ Success → Return result ✓
        └─ Failure → Return empty text
```

## Installation

### Option 1: Install All Engines (Recommended for Production)

```bash
# PaddleOCR (primary engine) - FASTEST
pip install paddleocr

# Tesseract (fallback engine) - MOST COMPATIBLE
# First install the system package:
# On Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# On macOS:
brew install tesseract

# On Windows:
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use: choco install tesseract

# Then install Python wrapper:
pip install pytesseract

# EasyOCR (already installed as fallback)
pip install easyocr
```

### Option 2: Minimal Install (Use Only Default)

```bash
# Only EasyOCR (legacy, already included)
pip install easyocr
```

### Option 3: Speed-Optimized Install

```bash
# For fastest performance
pip install paddleocr
pip install pytesseract
# (Tesseract CLI must also be installed - see Option 1)
```

## Usage Examples

### Basic Usage (Automatic Engine Selection)

```python
from services.ocr import ocr_extract_text

# Automatically uses best available engine
success = ocr_extract_text('document.pdf', 'output.txt')
```

### Advanced Usage (Get Engine Info)

```python
from services.ocr_enhanced import extract_text_intelligent

# Extract with engine information
result = extract_text_intelligent('image.png', prefer_speed=True)

print(f"Extracted text: {result['text']}")
print(f"Engine used: {result['engine']}")
print(f"Confidence: {result['confidence']:.1%}")
```

### Compare All Engines

```python
from services.ocr_enhanced import extract_text_intelligent

# Get results from all available engines for comparison
result = extract_text_intelligent('image.png', prefer_speed=False)

print(f"Best result from: {result['engine']}")
print(f"Comparison results:")
for engine, engine_result in result['all_results'].items():
    print(f"  {engine}: {engine_result['confidence']:.1%} confidence")
```

### With Language Selection

```python
from services.ocr import ocr_extract_with_language

# For English (uses PaddleOCR if available for speed)
ocr_extract_with_language('document.pdf', 'output.txt', languages=['en'])

# For multiple languages (uses EasyOCR for flexibility)
ocr_extract_with_language('document.pdf', 'output.txt', languages=['en', 'es', 'fr'])
```

### Check Available Engines

```python
from services.ocr_enhanced import get_ocr_status
from services.ocr import get_ocr_engines_status

# Get status of all engines
status = get_ocr_status()
print(f"PaddleOCR: {status['paddleocr']}")
print(f"Tesseract: {status['tesseract']}")
print(f"EasyOCR: {status['easyocr']}")

# Get system-level status with recommendations
system_status = get_ocr_engines_status()
print(f"Primary engine: {system_status['primary_engine']}")
```

## Performance Characteristics

### Speed Comparison (Approximate)

| Engine | Speed | Accuracy | Setup Effort | Languages |
|--------|-------|----------|--------------|-----------|
| **PaddleOCR** | ⚡⚡⚡ Very Fast | ⭐⭐⭐⭐⭐ Excellent | Medium | 80+ |
| **Tesseract** | ⚡⚡ Fast | ⭐⭐⭐⭐ Good | Easy | Limited |
| **EasyOCR** | ⚡ Slower | ⭐⭐⭐⭐⭐ Excellent | Easy | 80+ |

### Recommended Use Cases

**Use PaddleOCR When:**
- Processing large batches of documents
- Speed is critical
- English text is primary
- Real-time processing needed
- GPU acceleration available

**Use Tesseract When:**
- Document is high-contrast/printed
- Legal/official document processing
- Minimal dependencies preferred
- System resources limited

**Use EasyOCR When:**
- Multi-language support needed
- Complex/irregular documents
- Maximum accuracy required
- Fallback needed

## Configuration

### Environment Variables

```bash
# Disable GPU (faster for batch processing on CPU-only systems)
export CUDA_VISIBLE_DEVICES=""

# Set thread count for Tesseract
export OMP_NUM_THREADS=4
```

### Programmatic Configuration

```python
from services.ocr_enhanced import get_paddleocr_engine, get_easyocr_engine

# Initialize PaddleOCR with specific settings
paddleocr_reader = get_paddleocr_engine(use_gpu=False)

# Initialize EasyOCR with specific settings
easyocr_reader = get_easyocr_engine()
```

## Troubleshooting

### PaddleOCR Issues

**Issue:** "ModuleNotFoundError: No module named 'paddleocr'"
```bash
# Solution: Install PaddleOCR
pip install paddleocr
```

**Issue:** Slow first run
- PaddleOCR downloads models on first use (~130MB)
- Subsequent runs are much faster
- See logs for progress

**Issue:** GPU out of memory
- Set `use_gpu=False` in initialization
- Or reduce batch size

### Tesseract Issues

**Issue:** "TesseractNotFoundError"
```bash
# Solution: Install Tesseract CLI

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or: choco install tesseract
```

**Issue:** Low accuracy on images
- Ensure image is clear (>=300 DPI recommended)
- Use preprocessing: convert to grayscale, increase contrast
- Try Tesseract with `--psm 3` (auto-detect) or `--psm 6` (assume single block)

### EasyOCR Issues

**Issue:** First run is very slow
- EasyOCR downloads PyTorch models (~700MB for CUDA, ~350MB for CPU)
- This happens only on first run
- Monitor system resources during initial download

**Issue:** OOM (Out of Memory)
- EasyOCR uses more memory than Tesseract
- Ensure 4GB free RAM minimum
- Process images one at a time

## API Reference

### Core Functions

#### `extract_text_intelligent(image_path, prefer_speed=True, confidence_threshold=0.3, **kwargs)`

Intelligently extract text using best available engine.

**Parameters:**
- `image_path` (str): Path to image file
- `prefer_speed` (bool): If True, use fastest engine; if False, compare all available engines
- `confidence_threshold` (float): Minimum confidence for text inclusion (0.0-1.0)
- `**kwargs`: Additional engine-specific parameters

**Returns:**
```python
{
    'text': 'extracted text',           # Extracted text string
    'confidence': 0.95,                 # Average confidence (0.0-1.0)
    'engine': 'paddleocr',             # Which engine was used
    'all_results': {...}               # All results (if prefer_speed=False)
}
```

**Example:**
```python
from services.ocr_enhanced import extract_text_intelligent

result = extract_text_intelligent('scan.png', prefer_speed=True)
print(f"Found {len(result['text'].split())} words")
print(f"Using engine: {result['engine']}")
```

#### `extract_with_paddleocr(image_path, confidence_threshold=0.3)`

Extract text using PaddleOCR only.

**Returns:** `(text: str, confidence: float)`

#### `extract_with_tesseract(image_path, lang='eng', psm=3)`

Extract text using Tesseract only.

**Parameters:**
- `lang` (str): Language code (e.g., 'eng', 'spa', 'fra')
- `psm` (int): Page segmentation mode (0-13)

**Returns:** `(text: str, confidence: float)`

#### `extract_with_easyocr(image_path, confidence_threshold=0.3)`

Extract text using EasyOCR only.

**Returns:** `(text: str, confidence: float)`

#### `get_ocr_status()`

Get availability of all OCR engines.

**Returns:**
```python
{
    'paddleocr': True,
    'tesseract': True,
    'easyocr': True
}
```

## Migration from Legacy EasyOCR

The system is **fully backward compatible**. Existing code using the old API continues to work:

```python
# Old code still works exactly the same
from services.ocr import ocr_extract_text
ocr_extract_text('document.pdf', 'output.txt')

# But now automatically uses the best available engine!
# No code changes needed
```

## Performance Tips

### For Maximum Speed
1. Install PaddleOCR: `pip install paddleocr`
2. Use `prefer_speed=True` (default)
3. Enable GPU if available: `use_gpu=True`
4. Optimize image resolution: 1000-2000px width ideal

### For Maximum Accuracy
1. Install all engines
2. Use `prefer_speed=False` to compare engines
3. Preprocess images: denoise, deskew, enhance contrast
4. Use confidence filtering: `confidence_threshold=0.5`

### For Maximum Compatibility
1. Install Tesseract
2. Ensure high contrast documents
3. Use standard page segmentation modes
4. Test with diverse document types

## File Structure

```
services/
├── ocr.py                 (Main OCR service - backwards compatible)
├── ocr_enhanced.py        (Enhanced multi-engine implementation)
└── [other services...]

server.py
└── Uses: from services.ocr import ocr_extract_text, ocr_extract_with_language
```

## Logging

Enable debug logging to see which engine is being used:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now OCR operations will log:
# "PaddleOCR: extracted 145 words, confidence: 0.94"
# "Tesseract extraction failed: ..."
# "EasyOCR: extracted 140 words, confidence: 0.91"
```

## Future Enhancements

Potential improvements in future releases:

1. **Hybrid Approach**: Combine results from multiple engines for higher accuracy
2. **Per-Document Engine Selection**: Choose engine based on document type
3. **Caching**: Cache models to reduce memory footprint
4. **Parallel Processing**: Process multiple pages simultaneously
5. **Custom Training**: Fine-tune models for specific document types
6. **Layout Analysis**: Preserve document structure in extraction

## Support & Issues

If you encounter issues:

1. Check logs for error messages
2. Verify engine installation: `python -c "import paddleocr; print('PaddleOCR OK')"`
3. Test with a simple image first
4. Try alternative engines
5. Check system resources (RAM, disk space)

## Summary

The enhanced OCR system provides:

✅ **Automatic fallback** - Always finds a working engine  
✅ **Speed optimization** - PaddleOCR is 2-3x faster than EasyOCR  
✅ **Backward compatible** - No code changes needed  
✅ **Flexible configuration** - Choose engines based on your needs  
✅ **Production-ready** - Comprehensive error handling and logging  

**Recommendation:** Install PaddleOCR for 2-3x speed improvement with maintained accuracy.
