"""
Document Converter API Test Suite

This script provides comprehensive testing for the Document Converter API.
It tests all conversion endpoints with sample files.

Usage:
    python test_api.py
    python test_api.py --endpoint pdf-to-docx --file sample.pdf
    python test_api.py --user myuser --password mypass
"""

import requests
import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple

class DocumentConverterTester:
    """Test suite for Document Converter API."""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.test_results = []
    
    def log(self, level: str, message: str):
        """Log a message with level."""
        prefix = f"[{level:8}]"
        print(f"{prefix} {message}")
    
    def log_success(self, message: str):
        self.log("✓ OK", message)
    
    def log_error(self, message: str):
        self.log("✗ ERROR", message)
    
    def log_info(self, message: str):
        self.log("INFO", message)
    
    def log_request(self, method: str, endpoint: str):
        self.log("REQ", f"{method} {endpoint}")
    
    # ========================================================================
    # Authentication Tests
    # ========================================================================
    
    def test_register(self, username: str = "testuser123", 
                     email: str = "test@example.com", 
                     password: str = "TestPass123") -> bool:
        """Test user registration."""
        self.log_info("Testing user registration...")
        
        endpoint = f"{self.base_url}/auth/register"
        self.log_request("POST", "/api/auth/register")
        
        try:
            response = requests.post(
                endpoint,
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )
            
            result = response.json()
            
            if response.status_code == 201 and result.get("success"):
                self.log_success(f"User registered: {username}")
                self.log_info(f"  Token: {result['token'][:50]}...")
                self.token = result["token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                return True
            elif response.status_code == 409:
                self.log_info(f"User already exists: {username}")
                return self.test_login(username, password)
            else:
                self.log_error(f"Registration failed: {result.get('error')}")
                return False
        
        except Exception as e:
            self.log_error(f"Registration error: {str(e)}")
            return False
    
    def test_login(self, username: str = "testuser123", 
                  password: str = "TestPass123") -> bool:
        """Test user login."""
        self.log_info("Testing user login...")
        
        endpoint = f"{self.base_url}/auth/login"
        self.log_request("POST", "/api/auth/login")
        
        try:
            response = requests.post(
                endpoint,
                json={
                    "username": username,
                    "password": password
                }
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success(f"Logged in: {username}")
                self.token = result["token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                return True
            else:
                self.log_error(f"Login failed: {result.get('error')}")
                return False
        
        except Exception as e:
            self.log_error(f"Login error: {str(e)}")
            return False
    
    # ========================================================================
    # Conversion Tests
    # ========================================================================
    
    def test_pdf_to_docx(self, input_file: str = "sample.pdf") -> Tuple[bool, Optional[str]]:
        """Test PDF to DOCX conversion."""
        self.log_info("Testing PDF to DOCX conversion...")
        
        if not os.path.exists(input_file):
            self.log_error(f"Input file not found: {input_file}")
            return False, None
        
        endpoint = f"{self.base_url}/conversions/pdf-to-docx"
        self.log_request("POST", "/api/conversions/pdf-to-docx")
        
        try:
            with open(input_file, "rb") as f:
                files = {"file": f}
                response = self.session.post(endpoint, files=files)
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success("PDF to DOCX conversion successful")
                download_url = result["file"]["download_url"]
                self.log_info(f"  File: {result['file']['name']}")
                self.log_info(f"  Size: {result['file']['size']} bytes")
                self.log_info(f"  Download: {download_url}")
                return True, download_url
            else:
                self.log_error(f"Conversion failed: {result.get('error')}")
                return False, None
        
        except Exception as e:
            self.log_error(f"Conversion error: {str(e)}")
            return False, None
    
    def test_docx_to_pdf(self, input_file: str = "sample.docx") -> Tuple[bool, Optional[str]]:
        """Test DOCX to PDF conversion."""
        self.log_info("Testing DOCX to PDF conversion...")
        
        if not os.path.exists(input_file):
            self.log_error(f"Input file not found: {input_file}")
            return False, None
        
        endpoint = f"{self.base_url}/conversions/docx-to-pdf"
        self.log_request("POST", "/api/conversions/docx-to-pdf")
        
        try:
            with open(input_file, "rb") as f:
                files = {"file": f}
                response = self.session.post(endpoint, files=files)
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success("DOCX to PDF conversion successful")
                download_url = result["file"]["download_url"]
                self.log_info(f"  File: {result['file']['name']}")
                self.log_info(f"  Size: {result['file']['size']} bytes")
                return True, download_url
            else:
                self.log_error(f"Conversion failed: {result.get('error')}")
                return False, None
        
        except Exception as e:
            self.log_error(f"Conversion error: {str(e)}")
            return False, None
    
    def test_image_to_pdf(self, image_files: list = None) -> Tuple[bool, Optional[str]]:
        """Test image to PDF conversion."""
        self.log_info("Testing Image to PDF conversion...")
        
        if image_files is None:
            image_files = ["sample.jpg", "sample.png"]
        
        # Filter existing files
        existing_files = [f for f in image_files if os.path.exists(f)]
        
        if not existing_files:
            self.log_error(f"No input files found: {image_files}")
            return False, None
        
        endpoint = f"{self.base_url}/conversions/image-to-pdf"
        self.log_request("POST", "/api/conversions/image-to-pdf")
        
        try:
            files = [("files[]", open(f, "rb")) for f in existing_files]
            data = {"orientation": "portrait"}
            
            response = self.session.post(endpoint, files=files, data=data)
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success("Image to PDF conversion successful")
                download_url = result["file"]["download_url"]
                self.log_info(f"  File: {result['file']['name']}")
                self.log_info(f"  Size: {result['file']['size']} bytes")
                return True, download_url
            else:
                self.log_error(f"Conversion failed: {result.get('error')}")
                return False, None
        
        except Exception as e:
            self.log_error(f"Conversion error: {str(e)}")
            return False, None
    
    def test_xlsx_to_pdf(self, input_file: str = "sample.xlsx") -> Tuple[bool, Optional[str]]:
        """Test XLSX to PDF conversion."""
        self.log_info("Testing XLSX to PDF conversion...")
        
        if not os.path.exists(input_file):
            self.log_error(f"Input file not found: {input_file}")
            return False, None
        
        endpoint = f"{self.base_url}/conversions/xlsx-to-pdf"
        self.log_request("POST", "/api/conversions/xlsx-to-pdf")
        
        try:
            with open(input_file, "rb") as f:
                files = {"file": f}
                response = self.session.post(endpoint, files=files)
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success("XLSX to PDF conversion successful")
                download_url = result["file"]["download_url"]
                self.log_info(f"  File: {result['file']['name']}")
                self.log_info(f"  Size: {result['file']['size']} bytes")
                return True, download_url
            else:
                self.log_error(f"Conversion failed: {result.get('error')}")
                return False, None
        
        except Exception as e:
            self.log_error(f"Conversion error: {str(e)}")
            return False, None
    
    def test_pdf_to_image(self, input_file: str = "sample.pdf", 
                         pages: str = "1-3", format_type: str = "jpg") -> Tuple[bool, Optional[list]]:
        """Test PDF to image conversion."""
        self.log_info(f"Testing PDF to {format_type.upper()} conversion...")
        
        if not os.path.exists(input_file):
            self.log_error(f"Input file not found: {input_file}")
            return False, None
        
        endpoint = f"{self.base_url}/conversions/pdf-to-image"
        self.log_request("POST", "/api/conversions/pdf-to-image")
        
        try:
            with open(input_file, "rb") as f:
                files = {"file": f}
                data = {
                    "pages": pages,
                    "format": format_type,
                    "quality": "85"
                }
                response = self.session.post(endpoint, files=files, data=data)
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success(f"PDF to {format_type.upper()} conversion successful")
                files_info = result.get("files", [])
                for file_info in files_info:
                    self.log_info(f"  {file_info['name']} - {file_info['size']} bytes")
                return True, [f["download_url"] for f in files_info]
            else:
                self.log_error(f"Conversion failed: {result.get('error')}")
                return False, None
        
        except Exception as e:
            self.log_error(f"Conversion error: {str(e)}")
            return False, None
    
    def test_merge_pdfs(self, input_files: list = None) -> Tuple[bool, Optional[str]]:
        """Test PDF merge."""
        self.log_info("Testing PDF merge...")
        
        if input_files is None:
            input_files = ["sample1.pdf", "sample2.pdf"]
        
        existing_files = [f for f in input_files if os.path.exists(f)]
        
        if len(existing_files) < 2:
            self.log_error(f"Need at least 2 PDF files for merge. Found: {len(existing_files)}")
            return False, None
        
        endpoint = f"{self.base_url}/conversions/merge"
        self.log_request("POST", "/api/conversions/merge")
        
        try:
            files = [("files[]", open(f, "rb")) for f in existing_files]
            response = self.session.post(endpoint, files=files)
            
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.log_success("PDF merge successful")
                download_url = result["file"]["download_url"]
                self.log_info(f"  File: {result['file']['name']}")
                self.log_info(f"  Size: {result['file']['size']} bytes")
                return True, download_url
            else:
                self.log_error(f"Merge failed: {result.get('error')}")
                return False, None
        
        except Exception as e:
            self.log_error(f"Merge error: {str(e)}")
            return False, None
    
    def test_download_file(self, file_id: str, output_name: str = "downloaded_file") -> bool:
        """Test file download."""
        self.log_info(f"Testing file download (ID: {file_id})...")
        
        endpoint = f"{self.base_url}/download/{file_id}"
        self.log_request("GET", f"/api/download/{file_id}")
        
        try:
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                with open(output_name, "wb") as f:
                    f.write(response.content)
                self.log_success(f"File downloaded: {output_name}")
                return True
            else:
                self.log_error(f"Download failed (status {response.status_code})")
                return False
        
        except Exception as e:
            self.log_error(f"Download error: {str(e)}")
            return False
    
    def test_api_docs(self) -> bool:
        """Test API documentation endpoint."""
        self.log_info("Testing API documentation endpoint...")
        
        endpoint = f"{self.base_url}/docs"
        self.log_request("GET", "/api/docs")
        
        try:
            response = requests.get(endpoint)
            
            if response.status_code == 200:
                docs = response.json()
                self.log_success("API documentation retrieved")
                self.log_info(f"  Version: {docs.get('api_version')}")
                self.log_info(f"  Endpoints: {len(docs.get('endpoints', {}))}")
                return True
            else:
                self.log_error(f"Failed to retrieve documentation")
                return False
        
        except Exception as e:
            self.log_error(f"Documentation error: {str(e)}")
            return False
    
    def run_full_test_suite(self):
        """Run all tests."""
        self.log_info("=" * 70)
        self.log_info("Document Converter API Test Suite")
        self.log_info("=" * 70)
        
        # Auth tests
        self.log_info("\n--- AUTHENTICATION TESTS ---")
        self.test_register()
        
        # API docs
        self.log_info("\n--- API DOCUMENTATION ---")
        self.test_api_docs()
        
        # Conversion tests
        self.log_info("\n--- CONVERSION TESTS ---")
        
        if os.path.exists("sample.pdf"):
            success, url = self.test_pdf_to_docx("sample.pdf")
            if success and url:
                self.test_download_file(url.split("/")[-1], "downloaded.docx")
        
        if os.path.exists("sample.docx"):
            self.test_docx_to_pdf("sample.docx")
        
        if os.path.exists("sample.xlsx"):
            self.test_xlsx_to_pdf("sample.xlsx")
        
        if os.path.exists("sample.jpg") or os.path.exists("sample.png"):
            self.test_image_to_pdf()
        
        if os.path.exists("sample.pdf"):
            self.test_pdf_to_image("sample.pdf", "1-2", "jpg")
        
        self.log_info("\n" + "=" * 70)
        self.log_info("Test suite completed")
        self.log_info("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Document Converter API Test Suite"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:5000/api",
        help="API base URL (default: http://localhost:5000/api)"
    )
    parser.add_argument(
        "--endpoint",
        help="Test specific endpoint (pdf-to-docx, docx-to-pdf, etc.)"
    )
    parser.add_argument(
        "--file",
        help="Input file for specific endpoint test"
    )
    parser.add_argument(
        "--user",
        default="testuser123",
        help="Username for testing"
    )
    parser.add_argument(
        "--password",
        default="TestPass123",
        help="Password for testing"
    )
    
    args = parser.parse_args()
    
    tester = DocumentConverterTester(args.url)
    
    # Authenticate first
    if not tester.test_login(args.user, args.password):
        if not tester.test_register(args.user, args.password):
            print("Failed to authenticate")
            sys.exit(1)
    
    if args.endpoint:
        # Test specific endpoint
        if args.endpoint == "pdf-to-docx":
            success, url = tester.test_pdf_to_docx(args.file or "sample.pdf")
        elif args.endpoint == "docx-to-pdf":
            success, url = tester.test_docx_to_pdf(args.file or "sample.docx")
        elif args.endpoint == "image-to-pdf":
            success, url = tester.test_image_to_pdf()
        elif args.endpoint == "xlsx-to-pdf":
            success, url = tester.test_xlsx_to_pdf(args.file or "sample.xlsx")
        elif args.endpoint == "pdf-to-image":
            success, urls = tester.test_pdf_to_image(args.file or "sample.pdf")
        elif args.endpoint == "merge":
            success, url = tester.test_merge_pdfs()
        else:
            print(f"Unknown endpoint: {args.endpoint}")
            sys.exit(1)
    else:
        # Run full test suite
        tester.run_full_test_suite()


if __name__ == "__main__":
    main()

            print(f"Preview: {result.get('preview_type')}")
            print("\n✅ Conversion successful with all new features!")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"Error: {response.text}")
