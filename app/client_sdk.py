"""DocPro Python SDK - Client Library for DocPro API"""
import requests
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import time

class DocProClient:
    """Client for DocPro API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    # Authentication Methods
    def register(self, username: str, email: str, password: str) -> Dict:
        """Register new user"""
        response = self.session.post(f'{self.base_url}/api/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })
        return response.json()
    
    def login(self, username: str, password: str) -> Dict:
        """Login and get API key"""
        response = self.session.post(f'{self.base_url}/api/auth/login', json={
            'username': username,
            'password': password
        })
        data = response.json()
        if data.get('success'):
            self.api_key = data['api_key']
            self.session.headers.update({'X-API-Key': self.api_key})
        return data
    
    def get_current_user(self) -> Dict:
        """Get current authenticated user"""
        response = self.session.get(f'{self.base_url}/api/auth/me')
        return response.json()
    
    def reset_api_key(self) -> Dict:
        """Reset API key"""
        response = self.session.post(f'{self.base_url}/api/auth/reset-api-key')
        data = response.json()
        if data.get('success'):
            self.api_key = data['api_key']
            self.session.headers.update({'X-API-Key': self.api_key})
        return data
    
    # Data Processing Methods
    def remove_duplicates(self, file_path: str) -> bytes:
        """Remove duplicate rows from CSV/Excel"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/data/duplicate-remover',
                files={'file': f}
            )
        return response.content
    
    def validate_data(self, file_path: str) -> Dict:
        """Validate data quality"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/data/validate',
                files={'file': f}
            )
        return response.json()
    
    def export_to_pdf(self, file_path: str, format: str = 'table') -> bytes:
        """Export data to PDF"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/data/export-pdf',
                files={'file': f},
                data={'format': format}
            )
        return response.content
    
    def get_report(self, file_path: str) -> Dict:
        """Get data report with statistics"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/data/reporting',
                files={'file': f}
            )
        return response.json()
    
    # Advanced Features
    def check_data_quality(self, file_path: str) -> Dict:
        """Check comprehensive data quality metrics"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/features/quality-check',
                files={'file': f}
            )
        return response.json()
    
    def bulk_process(self, file_paths: List[str], operation: str = 'duplicate-remover') -> Dict:
        """Process multiple files in bulk"""
        files = [('files', open(p, 'rb')) for p in file_paths]
        response = self.session.post(
            f'{self.base_url}/api/features/bulk-process',
            files=files,
            data={'operation': operation}
        )
        for _, f in files:
            f.close()
        return response.json()
    
    def merge_files(self, file_paths: List[str], file_type: str = 'csv') -> bytes:
        """Merge multiple CSV/Excel files"""
        files = [('files', open(p, 'rb')) for p in file_paths]
        response = self.session.post(
            f'{self.base_url}/api/features/merge-files',
            files=files,
            data={'type': file_type}
        )
        for _, f in files:
            f.close()
        return response.content
    
    def export_data(self, file_path: str, format: str) -> Dict:
        """Export to JSON, XML, Parquet, or HTML"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/features/export/{format}',
                files={'file': f}
            )
        return response.json()
    
    def estimate_processing_time(self, file_path: str, operation: str = 'duplicate-remover') -> Dict:
        """Estimate processing time and resource requirements"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f'{self.base_url}/api/features/performance/estimate',
                files={'file': f},
                data={'operation': operation}
            )
        return response.json()
    
    # Job Scheduling
    def schedule_job(self, task_type: str, scheduled_time: str, parameters: Dict = None) -> Dict:
        """Schedule a task for later execution"""
        response = self.session.post(
            f'{self.base_url}/api/features/jobs/schedule',
            json={
                'task_type': task_type,
                'scheduled_time': scheduled_time,
                'parameters': parameters or {}
            }
        )
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get status of scheduled job"""
        response = self.session.get(f'{self.base_url}/api/features/jobs/{job_id}')
        return response.json()
    
    # Analytics
    def get_analytics(self) -> Dict:
        """Get system analytics"""
        response = self.session.get(f'{self.base_url}/api/analytics/operations')
        return response.json()
    
    def get_operation_analytics(self, operation_type: str) -> Dict:
        """Get analytics for specific operation"""
        response = self.session.get(f'{self.base_url}/api/analytics/operations/{operation_type}')
        return response.json()
    
    def get_analytics_summary(self) -> Dict:
        """Get high-level analytics summary"""
        response = self.session.get(f'{self.base_url}/api/analytics/summary')
        return response.json()
    
    # Cache Management
    def clear_cache(self) -> Dict:
        """Clear all cached results"""
        response = self.session.post(f'{self.base_url}/api/features/cache/clear')
        return response.json()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        response = self.session.get(f'{self.base_url}/api/features/cache/stats')
        return response.json()

# Example Usage
if __name__ == '__main__':
    # Initialize client
    client = DocProClient('http://localhost:5000')
    
    # Register and login
    # result = client.register('testuser', 'test@example.com', 'password123')
    # result = client.login('testuser', 'password123')
    
    # Process files
    # cleaned = client.remove_duplicates('data.csv')
    # with open('cleaned.csv', 'wb') as f:
    #     f.write(cleaned)
    
    # Validate data
    # quality = client.validate_data('data.csv')
    # print(f"Quality Score: {quality['report']['quality_score']}%")
    
    # Get analytics
    # summary = client.get_analytics_summary()
    # print(summary)
