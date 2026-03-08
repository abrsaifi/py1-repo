"""
Integration Tests for Document Processing Features
Tests all new features end-to-end with real file operations
Run with: pytest integration_test.py -v
"""

import pytest
import requests
import json
import os
import tempfile
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF

API_BASE = "http://localhost:5000/api/features"

# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img = Image.new('RGB', (800, 600), color='red')
        img.save(f.name)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_pdf():
    """Create a sample PDF for testing"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((50, 50), "Sample PDF for Testing")
        doc.save(f.name)
        doc.close()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def multiple_images(sample_image):
    """Create multiple sample images"""
    images = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (600 + i*100, 400 + i*100), color=(i*50, i*80, i*100))
            img.save(f.name)
            images.append(f.name)
    yield images
    for img in images:
        os.unlink(img)


@pytest.fixture
def multiple_pdfs(sample_pdf):
    """Create multiple sample PDFs"""
    pdfs = []
    for i in range(2):
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), f"PDF Document {i+1}")
            doc.save(f.name)
            doc.close()
            pdfs.append(f.name)
    yield pdfs
    for pdf in pdfs:
        os.unlink(pdf)


# ============================================================================
# TEST 1: BATCH IMAGE OPERATIONS
# ============================================================================

class TestBatchImageOperations:
    """Test batch image processing functionality"""
    
    def test_batch_images_compress(self, multiple_images):
        """Test image compression operation"""
        files = []
        for img_path in multiple_images:
            files.append(('files', open(img_path, 'rb')))
        
        try:
            response = requests.post(
                f"{API_BASE}/batch-process-images",
                files=files,
                data={'operation': 'compress'}
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            result = response.json()
            
            assert 'processed_count' in result
            assert result['processed_count'] == len(multiple_images)
            assert 'operation' in result
            assert result['operation'] == 'compress'
            pytest.skip("✓ PASS: Batch image compression")
        finally:
            for _, file_obj in files:
                file_obj.close()
    
    def test_batch_images_resize(self, sample_image):
        """Test image resize operation"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-images",
                files={'files': f},
                data={'operation': 'resize'}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result['operation'] == 'resize'
    
    def test_batch_images_convert(self, sample_image):
        """Test image format conversion"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-images",
                files={'files': f},
                data={'operation': 'convert'}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result['operation'] == 'convert'
    
    def test_batch_images_thumbnail(self, sample_image):
        """Test thumbnail generation"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-images",
                files={'files': f},
                data={'operation': 'thumbnail'}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result['operation'] == 'thumbnail'


# ============================================================================
# TEST 2: BATCH PDF OPERATIONS
# ============================================================================

class TestBatchPDFOperations:
    """Test batch PDF processing functionality"""
    
    def test_batch_pdfs_compress(self, sample_pdf):
        """Test PDF compression"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data={'operation': 'compress'}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert 'processed_count' in result
    
    def test_batch_pdfs_encrypt(self, sample_pdf):
        """Test PDF encryption"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data={'operation': 'encrypt'}
            )
        
        assert response.status_code == 200
    
    def test_batch_pdfs_watermark(self, sample_pdf):
        """Test PDF watermarking"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data={'operation': 'watermark'}
            )
        
        assert response.status_code == 200
    
    def test_batch_pdfs_clean(self, sample_pdf):
        """Test PDF cleaning (remove metadata, etc)"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data={'operation': 'clean'}
            )
        
        assert response.status_code == 200
    
    def test_batch_pdfs_bw(self, sample_pdf):
        """Test convert PDF to black & white"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data={'operation': 'bw'}
            )
        
        assert response.status_code == 200
    
    def test_batch_pdfs_multiple_operations(self, sample_pdf):
        """Test multiple PDF operations at once"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data=[('operation', 'compress'), ('operation', 'clean')]
            )
        
        assert response.status_code == 200


# ============================================================================
# TEST 3: SMART CROP
# ============================================================================

class TestSmartCrop:
    """Test smart image cropping functionality"""
    
    def test_smart_crop_content_detection(self, sample_image):
        """Test content-based cropping"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/smart-crop-images",
                files={'files': f},
                data={'mode': 'content'}
            )
        
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'image/jpeg' or \
               response.headers.get('content-type') == 'image/png'
        assert len(response.content) > 0
    
    def test_smart_crop_border_removal(self, sample_image):
        """Test border removal cropping"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/smart-crop-images",
                files={'files': f},
                data={'mode': 'border'}
            )
        
        assert response.status_code == 200
    
    def test_smart_crop_document_mode(self, sample_image):
        """Test document detection cropping"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/smart-crop-images",
                files={'files': f},
                data={'mode': 'document'}
            )
        
        assert response.status_code == 200


# ============================================================================
# TEST 4: PDF FORM FILL
# ============================================================================

class TestPDFFormFill:
    """Test PDF form filling functionality"""
    
    def test_form_fill_basic(self, sample_pdf):
        """Test basic form field filling"""
        form_data = {
            "Name": "John Doe",
            "Email": "john@example.com",
            "Phone": "555-1234"
        }
        
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/fill-pdf-forms",
                files={'files': f},
                data={'field_data': json.dumps(form_data)}
            )
        
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/pdf'
    
    def test_form_fill_multiple_fields(self, sample_pdf):
        """Test filling multiple form fields"""
        form_data = {
            "FirstName": "Jane",
            "LastName": "Smith",
            "Address": "123 Main St",
            "City": "Springfield",
            "State": "IL",
            "ZIP": "62701"
        }
        
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/fill-pdf-forms",
                files={'files': f},
                data={'field_data': json.dumps(form_data)}
            )
        
        assert response.status_code == 200


# ============================================================================
# TEST 5: DUPLICATE REMOVAL
# ============================================================================

class TestDuplicateRemoval:
    """Test duplicate image detection and removal"""
    
    def test_remove_duplicates(self, multiple_images):
        """Test removing duplicate images"""
        files = []
        for img_path in multiple_images:
            files.append(('files', open(img_path, 'rb')))
        
        try:
            response = requests.post(
                f"{API_BASE}/remove-duplicate-images",
                files=files
            )
            
            assert response.status_code == 200
            result = response.json()
            assert 'duplicates_found' in result
            assert 'unique_count' in result
        finally:
            for _, file_obj in files:
                file_obj.close()


# ============================================================================
# TEST 6: DATA EXPORT
# ============================================================================

class TestDataExport:
    """Test data export functionality"""
    
    def test_export_csv_to_pdf(self):
        """Test exporting CSV data to PDF"""
        csv_content = "Name,Age,City\nJohn,30,NYC\nJane,25,LA\nBob,35,Chicago"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            with open(csv_path, 'rb') as f:
                response = requests.post(
                    f"{API_BASE}/export-data-pdf",
                    files={'files': f},
                    data={
                        'output_format': 'pdf',
                        'report_type': 'table'
                    }
                )
            
            assert response.status_code == 200
            assert response.headers.get('content-type') == 'application/pdf'
        finally:
            os.unlink(csv_path)
    
    def test_export_json_to_pdf(self):
        """Test exporting JSON data to PDF"""
        json_content = json.dumps([
            {"id": 1, "name": "Item 1", "price": 100},
            {"id": 2, "name": "Item 2", "price": 200}
        ])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            json_path = f.name
        
        try:
            with open(json_path, 'rb') as f:
                response = requests.post(
                    f"{API_BASE}/export-data-pdf",
                    files={'files': f},
                    data={'output_format': 'pdf'}
                )
            
            assert response.status_code == 200
        finally:
            os.unlink(json_path)


# ============================================================================
# TEST 7: REPORT GENERATION
# ============================================================================

class TestReportGeneration:
    """Test report generation functionality"""
    
    def test_generate_summary_report(self):
        """Test generating summary report"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sales Data\nJanuary: $5000\nFebruary: $6000\nMarch: $7000")
            txt_path = f.name
        
        try:
            with open(txt_path, 'rb') as f:
                response = requests.post(
                    f"{API_BASE}/generate-report",
                    files={'files': f},
                    data={'report_type': 'summary'}
                )
            
            assert response.status_code == 200
        finally:
            os.unlink(txt_path)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance metrics"""
    
    def test_batch_processing_speed(self, multiple_images):
        """Verify batch processing completes in reasonable time"""
        import time
        
        files = []
        for img_path in multiple_images:
            files.append(('files', open(img_path, 'rb')))
        
        try:
            start = time.time()
            response = requests.post(
                f"{API_BASE}/batch-process-images",
                files=files,
                data={'operation': 'compress'}
            )
            elapsed = time.time() - start
            
            assert response.status_code == 200
            assert elapsed < 30, f"Processing took {elapsed:.2f}s, expected < 30s"
        finally:
            for _, file_obj in files:
                file_obj.close()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error scenarios and edge cases"""
    
    def test_empty_file_list(self):
        """Test handling of empty file list"""
        response = requests.post(
            f"{API_BASE}/batch-process-images",
            files={},
            data={'operation': 'compress'}
        )
        
        assert response.status_code != 200
    
    def test_invalid_operation(self, sample_image):
        """Test handling of invalid operation"""
        with open(sample_image, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-images",
                files={'files': f},
                data={'operation': 'invalid_op'}
            )
        
        assert response.status_code != 200
    
    def test_invalid_json_form_data(self, sample_pdf):
        """Test handling of invalid JSON in form data"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/fill-pdf-forms",
                files={'files': f},
                data={'field_data': 'invalid json {'}
            )
        
        assert response.status_code != 200


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFullWorkflow:
    """Test complete workflows combining multiple features"""
    
    def test_workflow_image_process_and_crop(self, sample_image):
        """Test workflow: compress image then crop"""
        # Step 1: Compress
        with open(sample_image, 'rb') as f:
            response1 = requests.post(
                f"{API_BASE}/batch-process-images",
                files={'files': f},
                data={'operation': 'compress'}
            )
        
        assert response1.status_code == 200
        
        # Step 2: Crop
        with open(sample_image, 'rb') as f:
            response2 = requests.post(
                f"{API_BASE}/smart-crop-images",
                files={'files': f},
                data={'mode': 'content'}
            )
        
        assert response2.status_code == 200
    
    def test_workflow_batch_pdfs_multiple_ops(self, sample_pdf):
        """Test workflow: compress and encrypt PDF"""
        with open(sample_pdf, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/batch-process-pdfs",
                files={'files': f},
                data=[('operation', 'compress'), ('operation', 'encrypt')]
            )
        
        assert response.status_code == 200


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
