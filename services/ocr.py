"""
Optical Character Recognition (OCR) service.
Handles text extraction from images and PDFs.
"""

import os
import tempfile
import fitz  # PyMuPDF


def ocr_extract_text(image_or_pdf_path, output_txt):
    """Extract text from image or PDF using EasyOCR"""
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        extracted_text = []
        
        # Check if it's a PDF or image
        if image_or_pdf_path.lower().endswith('.pdf'):
            # Extract images from PDF
            pdf_doc = fitz.open(image_or_pdf_path)
            for page_num, page in enumerate(pdf_doc, 1):
                # Convert PDF page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                with tempfile.NamedTemporaryFile(suffix=f"_page_{page_num}.png", delete=False) as timg:
                    img_path = timg.name
                pix.save(img_path)
                
                # Run OCR on page
                results = reader.readtext(img_path)
                extracted_text.append(f"--- PAGE {page_num} ---")
                for detection in results:
                    text = detection[1]
                    confidence = detection[2]
                    extracted_text.append(f"{text} ({confidence:.2%} confidence)")
                
                try:
                    os.remove(img_path)
                except:
                    pass
            pdf_doc.close()
        else:
            # Direct image OCR
            results = reader.readtext(image_or_pdf_path)
            for detection in results:
                text = detection[1]
                confidence = detection[2]
                extracted_text.append(f"{text} ({confidence:.2%} confidence)")
        
        # Save to text file
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(extracted_text))
        
        return True
    except Exception as e:
        print(f"OCR error: {e}")
        import traceback
        traceback.print_exc()
        return False


def ocr_extract_with_language(image_or_pdf_path, output_txt, languages=['en']):
    """Extract text from image or PDF using EasyOCR with language selection"""
    try:
        from easyocr import Reader
        
        reader = Reader(languages, gpu=False)
        extracted_text = []
        
        # Check if it's a PDF or image
        if image_or_pdf_path.lower().endswith('.pdf'):
            # Extract images from PDF
            pdf_doc = fitz.open(image_or_pdf_path)
            for page_num, page in enumerate(pdf_doc, 1):
                # Convert PDF page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                with tempfile.NamedTemporaryFile(suffix=f"_page_{page_num}.png", delete=False) as timg:
                    img_path = timg.name
                pix.save(img_path)
                
                # Run OCR on page
                results = reader.readtext(img_path)
                extracted_text.append(f"\n=== PAGE {page_num} ===\n")
                for detection in results:
                    text = detection[1]
                    confidence = detection[2]
                    extracted_text.append(f"{text} [{confidence:.1%}]")
                
                try:
                    os.remove(img_path)
                except:
                    pass
            pdf_doc.close()
        else:
            # Direct image OCR
            results = reader.readtext(image_or_pdf_path)
            for detection in results:
                text = detection[1]
                confidence = detection[2]
                extracted_text.append(f"{text} [{confidence:.1%}]")
        
        # Save to text file
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(extracted_text))
        
        return True
    except Exception as e:
        print(f"OCR error: {e}")
        import traceback
        traceback.print_exc()
        return False
