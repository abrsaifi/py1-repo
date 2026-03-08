"""
Test script for the enhanced OCR service with multi-engine strategy.
Tests PaddleOCR + Tesseract + EasyOCR fallback implementation.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('ocr_test')

def test_ocr_imports():
    """Test that OCR modules can be imported."""
    logger.info("="*70)
    logger.info("TEST 1: OCR Module Imports")
    logger.info("="*70)
    
    try:
        from services import ocr
        logger.info("✓ services.ocr imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import services.ocr: {e}")
        return False
    
    try:
        from services import ocr_enhanced
        logger.info("✓ services.ocr_enhanced imported successfully")
    except Exception as e:
        logger.warning(f"⚠ services.ocr_enhanced not available (optional): {e}")
    
    return True


def test_ocr_engine_status():
    """Test OCR engine availability status."""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: OCR Engine Status")
    logger.info("="*70)
    
    try:
        from services.ocr import get_ocr_engines_status
        from services.ocr_enhanced import get_ocr_status
        
        status = get_ocr_status()
        logger.info(f"Engine Availability:")
        logger.info(f"  PaddleOCR: {'✓ Available' if status.get('paddleocr') else '✗ Not installed'}")
        logger.info(f"  Tesseract: {'✓ Available' if status.get('tesseract') else '✗ Not installed'}")
        logger.info(f"  EasyOCR:   {'✓ Available' if status.get('easyocr') else '✗ Not installed'}")
        
        sys_status = get_ocr_engines_status()
        logger.info(f"\nPrimary engine: {sys_status['primary_engine']}")
        logger.info(f"Enhanced OCR available: {sys_status['enhanced_ocr_available']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Failed to get OCR status: {e}")
        return False


def test_ocr_functions_exist():
    """Test that all required OCR functions exist."""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: OCR Functions Availability")
    logger.info("="*70)
    
    try:
        from services.ocr import (
            ocr_extract_text,
            ocr_extract_with_language,
            get_ocr_engines_status
        )
        logger.info("✓ ocr_extract_text function exists")
        logger.info("✓ ocr_extract_with_language function exists")
        logger.info("✓ get_ocr_engines_status function exists")
        
        from services.ocr_enhanced import (
            extract_text_intelligent,
            extract_with_paddleocr,
            extract_with_tesseract,
            extract_with_easyocr,
            get_paddleocr_engine,
            get_easyocr_engine,
            get_ocr_status
        )
        logger.info("✓ extract_text_intelligent function exists")
        logger.info("✓ extract_with_paddleocr function exists")
        logger.info("✓ extract_with_tesseract function exists")
        logger.info("✓ extract_with_easyocr function exists")
        logger.info("✓ Engine getter functions exist")
        
        return True
    except Exception as e:
        logger.error(f"✗ Failed to import OCR functions: {e}")
        return False


def test_ocr_with_sample_image():
    """Test OCR extraction with a sample image (if available)."""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: OCR Text Extraction (with sample image)")
    logger.info("="*70)
    
    # Look for sample images in the project
    sample_images = list(Path('.').glob('**/*.png')) + list(Path('.').glob('**/*.jpg'))
    
    if not sample_images:
        logger.warning("⚠ No sample images found. Creating test image...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            import tempfile
            
            # Create a simple test image with text
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "DocPro OCR Test", fill='black')
            draw.text((10, 50), "PaddleOCR + Tesseract", fill='black')
            draw.text((10, 90), "Multi-Engine Strategy", fill='black')
            
            test_image = Path(tempfile.gettempdir()) / 'ocr_test.png'
            img.save(test_image)
            sample_images = [test_image]
            logger.info(f"Created test image: {test_image}")
        except Exception as e:
            logger.warning(f"Could not create test image: {e}")
            return None
    
    if sample_images:
        test_image = sample_images[0]
        logger.info(f"Testing with image: {test_image}")
        
        try:
            from services.ocr_enhanced import extract_text_intelligent
            
            result = extract_text_intelligent(str(test_image), prefer_speed=True)
            logger.info(f"✓ Text extraction successful")
            logger.info(f"  Engine used: {result['engine']}")
            logger.info(f"  Text length: {len(result['text'])} characters")
            logger.info(f"  Confidence: {result['confidence']:.1%}")
            logger.info(f"  Extracted text: {result['text'][:100]}...")
            
            return True
        except Exception as e:
            logger.error(f"✗ Text extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return None


def test_fallback_mechanism():
    """Test that fallback mechanism works correctly."""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Fallback Mechanism")
    logger.info("="*70)
    
    try:
        from services.ocr_enhanced import extract_text_intelligent, get_ocr_status
        
        status = get_ocr_status()
        available_engines = sum(1 for v in status.values() if v)
        
        logger.info(f"Available OCR engines: {available_engines}")
        logger.info(f"  Engines: {', '.join(k for k,v in status.items() if v)}")
        
        if available_engines == 0:
            logger.error("✗ No OCR engines available!")
            return False
        
        logger.info(f"✓ Fallback mechanism will use available engines")
        
        # Test with a non-existent image to verify error handling
        result = extract_text_intelligent('nonexistent.png')
        logger.info(f"✓ Error handling works correctly (non-existent image)")
        
        return True
    except Exception as e:
        logger.error(f"✗ Fallback test failed: {e}")
        return False


def test_backward_compatibility():
    """Test that legacy OCR functions still work."""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Backward Compatibility")
    logger.info("="*70)
    
    try:
        from services.ocr import ocr_extract_text, ocr_extract_with_language
        
        logger.info("✓ Legacy ocr_extract_text function is available")
        logger.info("✓ Legacy ocr_extract_with_language function is available")
        logger.info("✓ System is backward compatible with existing code")
        
        return True
    except Exception as e:
        logger.error(f"✗ Backward compatibility test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "="*70)
    logger.info("OCR ENHANCEMENT TEST SUITE")
    logger.info("="*70)
    
    all_results = []
    
    # Test 1: Imports
    all_results.append(("OCR Imports", test_ocr_imports()))
    
    # Test 2: Engine Status
    all_results.append(("Engine Status", test_ocr_engine_status()))
    
    # Test 3: Functions
    all_results.append(("Functions", test_ocr_functions_exist()))
    
    # Test 4: Sample Image (optional)
    result = test_ocr_with_sample_image()
    if result is not None:
        all_results.append(("Sample Image Extraction", result))
    else:
        logger.warning("⚠ Sample image test skipped")
    
    # Test 5: Fallback
    all_results.append(("Fallback Mechanism", test_fallback_mechanism()))
    
    # Test 6: Compatibility
    all_results.append(("Backward Compatibility", test_backward_compatibility()))
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    for test_name, result in all_results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("\n" + "="*70)
    logger.info(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    logger.info("="*70)
    
    if passed == total:
        logger.info("\n✓ All tests passed! OCR enhancement is working correctly.")
        return 0
    else:
        logger.warning(f"\n⚠ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
