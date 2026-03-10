"""
Enhanced OCR Service with PaddleOCR (primary) and Tesseract (fallback)
Provides intelligent text extraction with multiple OCR backends
"""

import os
import logging
from typing import List, Tuple, Optional, Dict
from pathlib import Path

logger = logging.getLogger('docpro.ocr')

# Import OCR libraries with graceful fallbacks
try:
    import paddleocr
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    paddleocr = None

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None
    Image = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

# Global OCR engine instances
_PADDLEOCR_ENGINE = None
_EASYOCR_ENGINE = None


# ============================================================================
# PaddleOCR Engine (Primary - Fastest)
# ============================================================================

def get_paddleocr_engine(use_gpu: bool = False):
    """
    Get or initialize PaddleOCR engine (primary OCR method).
    
    PaddleOCR advantages:
    - Fast inference (optimized for CPU/GPU)
    - High accuracy for multiple languages
    - Lightweight model (~135MB)
    - Good for real-time applications
    
    Args:
        use_gpu: Whether to use GPU acceleration (default: False for compatibility)
        
    Returns:
        PaddleOCR reader instance or None if unavailable
    """
    global _PADDLEOCR_ENGINE
    
    if not PADDLEOCR_AVAILABLE:
        logger.warning("PaddleOCR not installed. Install with: pip install paddleocr")
        return None
    
    if _PADDLEOCR_ENGINE is None:
        try:
            logger.info(f"Initializing PaddleOCR (GPU: {use_gpu})")
            # Initialize with compatible parameters
            try:
                # Try newer PaddleOCR version parameters
                _PADDLEOCR_ENGINE = paddleocr.PaddleOCR(
                    use_angle_cls=True,
                    use_gpu=use_gpu,
                    lang='en'
                )
            except TypeError:
                # Fallback for versions that don't support use_gpu parameter
                logger.debug("Trying PaddleOCR without use_gpu parameter")
                _PADDLEOCR_ENGINE = paddleocr.PaddleOCR(
                    use_angle_cls=True,
                    lang='en'
                )
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            _PADDLEOCR_ENGINE = None
    
    return _PADDLEOCR_ENGINE


def extract_with_paddleocr(image_path: str, **kwargs) -> Tuple[str, float]:
    """
    Extract text from image using PaddleOCR.
    
    Args:
        image_path: Path to image file
        **kwargs: Additional arguments (confidence_threshold, etc.)
        
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    engine = get_paddleocr_engine()
    if engine is None:
        return "", 0.0
    
    confidence_threshold = kwargs.get('confidence_threshold', 0.3)
    
    try:
        logger.debug(f"PaddleOCR extracting from: {image_path}")
        result = engine.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return "", 0.0
        
        # Extract text and confidence from results
        texts = []
        confidences = []
        for line in result:
            for word_info in line:
                text, confidence = word_info[1], word_info[2]
                if confidence >= confidence_threshold:
                    texts.append(text)
                    confidences.append(confidence)
        
        extracted_text = ' '.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        logger.info(f"PaddleOCR: extracted {len(texts)} words, confidence: {avg_confidence:.2%}")
        return extracted_text, avg_confidence
    
    except Exception as e:
        logger.error(f"PaddleOCR extraction failed: {e}")
        return "", 0.0


# ============================================================================
# Tesseract OCR (Fallback - Most Compatible)
# ============================================================================

def extract_with_tesseract(image_path: str, **kwargs) -> Tuple[str, float]:
    """
    Extract text from image using Tesseract (fallback method).
    
    Tesseract advantages:
    - Most widely supported OCR engine
    - Excellent for high-contrast documents
    - Small installation footprint
    - Stable and mature
    
    Args:
        image_path: Path to image file
        **kwargs: Additional arguments (lang, psm, etc.)
        
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract not installed. Install with: pip install pytesseract")
        return "", 0.0
    
    try:
        # Check if tesseract CLI is available
        pytesseract.get_tesseract_version()
    except Exception as e:
        logger.error(f"Tesseract CLI not found: {e}. Install tesseract-ocr system package.")
        return "", 0.0
    
    try:
        lang = kwargs.get('lang', 'eng')
        psm = kwargs.get('psm', 3)  # Auto page segmentation mode
        
        logger.debug(f"Tesseract extracting from: {image_path}")
        img = Image.open(image_path)
        
        # Extract text with configuration
        custom_config = f'--psm {psm}'
        extracted_text = pytesseract.image_to_string(img, lang=lang, config=custom_config)
        
        # Get confidence scores for each line
        data = pytesseract.image_to_data(img, lang=lang, config=custom_config, output_type='dict')
        confidences = [int(conf) / 100 for conf in data['confidence'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        logger.info(f"Tesseract: extracted {len(extracted_text.split())} words, confidence: {avg_confidence:.2%}")
        return extracted_text.strip(), avg_confidence
    
    except Exception as e:
        logger.error(f"Tesseract extraction failed: {e}")
        return "", 0.0


# ============================================================================
# EasyOCR (Fallback - Most Flexible)
# ============================================================================

def get_easyocr_engine():
    """
    Get or initialize EasyOCR engine (secondary fallback).
    
    EasyOCR advantages:
    - Multi-language support
    - PyTorch-based (flexible)
    - Good for complex documents
    
    Returns:
        EasyOCR reader instance or None if unavailable
    """
    global _EASYOCR_ENGINE
    
    if not EASYOCR_AVAILABLE:
        return None
    
    if _EASYOCR_ENGINE is None:
        try:
            logger.info("Initializing EasyOCR")
            _EASYOCR_ENGINE = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            _EASYOCR_ENGINE = None
    
    return _EASYOCR_ENGINE


def extract_with_easyocr(image_path: str, **kwargs) -> Tuple[str, float]:
    """Extract text using EasyOCR (third fallback)."""
    engine = get_easyocr_engine()
    if engine is None:
        return "", 0.0
    
    confidence_threshold = kwargs.get('confidence_threshold', 0.3)
    
    try:
        logger.debug(f"EasyOCR extracting from: {image_path}")
        result = engine.readtext(image_path)
        
        if not result:
            return "", 0.0
        
        texts = []
        confidences = []
        for (bbox, text, confidence) in result:
            if confidence >= confidence_threshold:
                texts.append(text)
                confidences.append(confidence)
        
        extracted_text = ' '.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        logger.info(f"EasyOCR: extracted {len(texts)} words, confidence: {avg_confidence:.2%}")
        return extracted_text, avg_confidence
    
    except Exception as e:
        logger.error(f"EasyOCR extraction failed: {e}")
        return "", 0.0


# ============================================================================
# Intelligent Multi-Engine OCR with Fallback Chain
# ============================================================================

def extract_text_intelligent(
    image_path: str,
    prefer_speed: bool = True,
    confidence_threshold: float = 0.3,
    **kwargs
) -> Dict[str, any]:
    """
    Intelligently extract text using best available OCR engine.
    
    Strategy:
    1. Try PaddleOCR (fastest, high accuracy) - PRIMARY
    2. Fall back to Tesseract (most compatible) - SECONDARY
    3. Fall back to EasyOCR (most flexible) - TERTIARY
    
    Args:
        image_path: Path to image file
        prefer_speed: If True, prioritize PaddleOCR; if False, compare all available
        confidence_threshold: Minimum confidence for text extraction (0.0-1.0)
        **kwargs: Additional OCR parameters
        
    Returns:
        Dict containing:
        {
            'text': extracted text,
            'confidence': average confidence score,
            'engine': which engine was used,
            'all_results': results from all attempted engines (if prefer_speed=False)
        }
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return {
            'text': '',
            'confidence': 0.0,
            'engine': 'none',
            'error': 'Image file not found'
        }
    
    logger.info(f"Starting intelligent OCR extraction: {Path(image_path).name}")
    
    if prefer_speed:
        # Fast path: use PaddleOCR if available
        if PADDLEOCR_AVAILABLE:
            text, confidence = extract_with_paddleocr(image_path, confidence_threshold=confidence_threshold, **kwargs)
            if text:
                logger.info(f"✓ PaddleOCR succeeded with {confidence:.1%} confidence")
                return {
                    'text': text,
                    'confidence': confidence,
                    'engine': 'paddleocr',
                    'all_results': None
                }
        
        # Fallback to Tesseract
        if TESSERACT_AVAILABLE:
            text, confidence = extract_with_tesseract(image_path, **kwargs)
            if text:
                logger.info(f"✓ Tesseract succeeded with {confidence:.1%} confidence")
                return {
                    'text': text,
                    'confidence': confidence,
                    'engine': 'tesseract',
                    'all_results': None
                }
        
        # Last resort: EasyOCR
        text, confidence = extract_with_easyocr(image_path, confidence_threshold=confidence_threshold, **kwargs)
        logger.info(f"EasyOCR result with {confidence:.1%} confidence")
        return {
            'text': text,
            'confidence': confidence,
            'engine': 'easyocr',
            'all_results': None
        }
    
    else:
        # Compare mode: try all engines and return best result
        all_results = {}
        
        if PADDLEOCR_AVAILABLE:
            text, conf = extract_with_paddleocr(image_path, confidence_threshold=confidence_threshold, **kwargs)
            all_results['paddleocr'] = {'text': text, 'confidence': conf}
        
        if TESSERACT_AVAILABLE:
            text, conf = extract_with_tesseract(image_path, **kwargs)
            all_results['tesseract'] = {'text': text, 'confidence': conf}
        
        text, conf = extract_with_easyocr(image_path, confidence_threshold=confidence_threshold, **kwargs)
        all_results['easyocr'] = {'text': text, 'confidence': conf}
        
        # Find best result (non-empty with highest confidence)
        best_engine = None
        best_text = ''
        best_confidence = 0.0
        
        for engine, result in all_results.items():
            if result['text'] and result['confidence'] > best_confidence:
                best_engine = engine
                best_text = result['text']
                best_confidence = result['confidence']
        
        logger.info(f"Comparison: Best result from {best_engine} with {best_confidence:.1%} confidence")
        
        return {
            'text': best_text,
            'confidence': best_confidence,
            'engine': best_engine,
            'all_results': all_results
        }


def extract_text(image_path: str, **kwargs) -> str:
    """
    Simple text extraction wrapper.
    
    Args:
        image_path: Path to image file
        **kwargs: Additional OCR parameters
        
    Returns:
        Extracted text string
    """
    result = extract_text_intelligent(image_path, prefer_speed=True, **kwargs)
    return result.get('text', '')


def get_ocr_status() -> Dict[str, bool]:
    """
    Get status of available OCR engines.
    
    Returns:
        Dictionary with availability status of each engine
    """
    return {
        'paddleocr': PADDLEOCR_AVAILABLE,
        'tesseract': TESSERACT_AVAILABLE,
        'easyocr': EASYOCR_AVAILABLE,
    }


# ============================================================================
# Module Information
# ============================================================================

__all__ = [
    'extract_text_intelligent',
    'extract_text',
    'extract_with_paddleocr',
    'extract_with_tesseract',
    'extract_with_easyocr',
    'get_paddleocr_engine',
    'get_easyocr_engine',
    'get_ocr_status',
]

if __name__ == '__main__':
    # Test the module
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("OCR Service Status")
    print("="*70)
    
    status = get_ocr_status()
    for engine, available in status.items():
        symbol = "✓" if available else "✗"
        print(f"{symbol} {engine.upper()}: {'Available' if available else 'Not installed'}")
    
    print("\nTo install missing engines:")
    print("  PaddleOCR:  pip install paddleocr")
    print("  Tesseract:  pip install pytesseract && apt-get install tesseract-ocr")
    print("  EasyOCR:    pip install easyocr")
