"""Comprehensive test suite for all features"""
import pytest
import tempfile
import os
import json
from pathlib import Path
from app import create_app
from app.services.database import init_db, DatabaseManager
from app.services.auth import AuthManager
from app.utils.logger_enhanced import setup_logging

@pytest.fixture
def app():
    """Create app for testing"""
    app = create_app({
        'TESTING': True,
        'UPLOAD_API_KEY': None
    })
    
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

class TestDuplicateRemover:
    """Test Duplicate Remover feature"""
    
    def create_test_csv(self):
        """Create test CSV file with duplicates"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write("Name,Email,Age\n")
        temp_file.write("John Doe,john@example.com,30\n")
        temp_file.write("Jane Smith,jane@example.com,25\n")
        temp_file.write("John Doe,john@example.com,30\n")  # Duplicate
        temp_file.write("Bob Johnson,bob@example.com,35\n")
        temp_file.close()
        return temp_file.name
    
    def test_duplicate_remover_success(self, client):
        """Test successful duplicate removal"""
        csv_file = self.create_test_csv()
        
        try:
            with open(csv_file, 'rb') as f:
                response = client.post('/api/data/duplicate-remover', 
                    data={'file': (f, 'test.csv')})
            
            assert response.status_code == 200
            assert response.content_type.startswith('text/csv')
        finally:
            os.unlink(csv_file)
    
    def test_duplicate_remover_empty_file(self, client):
        """Test with empty file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                response = client.post('/api/data/duplicate-remover',
                    data={'file': (f, 'empty.csv')})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
        finally:
            os.unlink(temp_file.name)

class TestDataValidator:
    """Test Data Validator feature"""
    
    def create_test_csv(self):
        """Create test CSV file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write("Name,Score,Status\n")
        temp_file.write("Alice,95,Pass\n")
        temp_file.write("Bob,87,Pass\n")
        temp_file.write("Charlie,,Pending\n")  # Missing value
        temp_file.close()
        return temp_file.name
    
    def test_data_validator_success(self, client):
        """Test successful data validation"""
        csv_file = self.create_test_csv()
        
        try:
            with open(csv_file, 'rb') as f:
                response = client.post('/api/data/validate',
                    data={'file': (f, 'test.csv')})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert 'report' in data
            assert 'quality_score' in data['report']
        finally:
            os.unlink(csv_file)

class TestPDFExport:
    """Test PDF Export feature"""
    
    def create_test_csv(self):
        """Create test CSV file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write("Product,Price\n")
        temp_file.write("Laptop,1200\n")
        temp_file.write("Mouse,25\n")
        temp_file.close()
        return temp_file.name
    
    def test_pdf_export_success(self, client):
        """Test successful PDF export"""
        csv_file = self.create_test_csv()
        
        try:
            with open(csv_file, 'rb') as f:
                response = client.post('/api/data/export-pdf',
                    data={'file': (f, 'test.csv'), 'format': 'table'})
            
            assert response.status_code == 200
            assert response.content_type == 'application/pdf'
        finally:
            os.unlink(csv_file)

class TestBasicReporting:
    """Test Basic Reporting feature"""
    
    def create_test_csv(self):
        """Create test CSV file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write("Month,Sales,Expenses\n")
        temp_file.write("January,50000,30000\n")
        temp_file.write("February,55000,32000\n")
        temp_file.close()
        return temp_file.name
    
    def test_reporting_success(self, client):
        """Test successful reporting"""
        csv_file = self.create_test_csv()
        
        try:
            with open(csv_file, 'rb') as f:
                response = client.post('/api/data/reporting',
                    data={'file': (f, 'test.csv')})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert 'report' in data
        finally:
            os.unlink(csv_file)

class TestDatabaseIntegration:
    """Test Database Integration feature"""
    
    def test_database_connect_success(self, client):
        """Test successful database connection"""
        response = client.post('/api/data/database-connect',
            json={
                'db_type': 'postgresql',
                'host': 'localhost',
                'port': '5432',
                'database': 'testdb',
                'username': 'admin'
            },
            headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'connection' in data

class TestAuthentication:
    """Test Authentication features"""
    
    def test_create_user(self):
        """Test user creation"""
        success, user_id, api_key = AuthManager.create_user(
            'testuser', 'test@example.com', 'password123')
        
        assert success == True
        assert user_id is not None
        assert api_key is not None
    
    def test_authenticate_user(self):
        """Test user authentication"""
        AuthManager.create_user('testuser2', 'test2@example.com', 'password123')
        
        success, user_id = AuthManager.authenticate_user('testuser2', 'password123')
        assert success == True
        assert user_id is not None
    
    def test_verify_api_key(self):
        """Test API key verification"""
        success, user_id, api_key = AuthManager.create_user(
            'testuser3', 'test3@example.com', 'password123')
        
        verified_user_id = AuthManager.verify_api_key(api_key)
        assert verified_user_id == user_id

class TestFileValidation:
    """Test file validation"""
    
    def test_file_size_validation(self):
        """Test file size validation"""
        from app.utils.file_validator import validate_file
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write("test")
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                is_valid, error = validate_file(f, ['csv'])
            
            assert is_valid == True
            assert error is None
        finally:
            os.unlink(temp_file.name)

class TestDatabaseOperations:
    """Test database operations"""
    
    def test_add_conversion_record(self):
        """Test adding conversion record"""
        record_id = DatabaseManager.add_conversion_record(
            'test_operation', 'test_file.csv', 'processing', user_id=1)
        
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_update_analytics(self):
        """Test updating analytics"""
        DatabaseManager.update_analytics('test_op', success=True, file_size_mb=1.5)
        
        analytics = DatabaseManager.get_analytics()
        assert len(analytics) > 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
