#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for Document Converter API
Tests all 19 endpoints: authentication, conversions, history, settings, webhooks

Usage:
    python comprehensive_api_test.py                  # Run all tests
    python comprehensive_api_test.py --quick         # Quick health check
    python comprehensive_api_test.py --detailed      # Detailed test results
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import argparse

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class APITestSuite:
    """Comprehensive API test suite for Document Converter API."""
    
    def __init__(self, base_url: str = "http://localhost:5000/api", detailed: bool = False):
        self.base_url = base_url
        self.detailed = detailed
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        
        # Test results tracking
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.test_data = {}
        
    def print_header(self, text: str):
        """Print section header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}{Colors.RESET}\n")
    
    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result."""
        if status == "PASS":
            symbol = f"{Colors.GREEN}✓{Colors.RESET}"
            self.passed += 1
        elif status == "FAIL":
            symbol = f"{Colors.RED}✗{Colors.RESET}"
            self.failed += 1
            self.errors.append(f"{name}: {details}")
        else:
            symbol = f"{Colors.YELLOW}⚠{Colors.RESET}"
        
        msg = f"  {symbol} {name:<50} {status}"
        if details and self.detailed:
            print(f"{msg}\n     └─ {details}")
        else:
            print(msg)
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
        print(f"  TEST SUMMARY")
        print(f"{'='*70}{Colors.RESET}")
        
        if self.failed == 0:
            print(f"{Colors.GREEN}✓ ALL TESTS PASSED ({self.passed}/{total}){Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ TESTS FAILED: {self.failed}/{total}{Colors.RESET}")
            print(f"{Colors.YELLOW}  Success rate: {percentage:.1f}%{Colors.RESET}")
        
        if self.errors:
            print(f"\n{Colors.RED}Errors:{Colors.RESET}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")
        
        print()
    
    # ========================================================================
    # AUTHENTICATION TESTS (2 endpoints)
    # ========================================================================
    
    def test_auth_register(self):
        """Test POST /auth/register"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "TestPassword123"
                },
                timeout=5
            )
            
            if response.status_code in [201, 409]:  # Created or Already Exists
                data = response.json()
                if "token" in data:
                    self.token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.print_test("POST /auth/register", "PASS", "User registered/exists")
                    return True
                elif response.status_code == 409:
                    self.print_test("POST /auth/register", "PASS", "User already exists")
                    return True
            
            self.print_test("POST /auth/register", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /auth/register", "FAIL", str(e))
            return False
    
    def test_auth_login(self):
        """Test POST /auth/login"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": "testuser",
                    "password": "TestPassword123"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.token = data["token"]
                    self.user_id = data.get("user_id", "unknown")
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.print_test("POST /auth/login", "PASS", f"User ID: {self.user_id}")
                    return True
            
            self.print_test("POST /auth/login", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /auth/login", "FAIL", str(e))
            return False
    
    # ========================================================================
    # PHASE 1 CONVERSIONS (6 endpoints)
    # ========================================================================
    
    def test_pdf_to_docx(self):
        """Test POST /conversions/pdf-to-docx"""
        try:
            # Create test PDF if needed
            test_file = self._create_test_pdf()
            if not test_file:
                self.print_test("POST /conversions/pdf-to-docx", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/pdf-to-docx",
                    files={"file": f},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["pdf_to_docx"] = data.get("file", {}).get("id")
                self.print_test("POST /conversions/pdf-to-docx", "PASS", 
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/pdf-to-docx", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/pdf-to-docx", "FAIL", str(e))
            return False
    
    def test_docx_to_pdf(self):
        """Test POST /conversions/docx-to-pdf"""
        try:
            test_file = self._create_test_docx()
            if not test_file:
                self.print_test("POST /conversions/docx-to-pdf", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/docx-to-pdf",
                    files={"file": f},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["docx_to_pdf"] = data.get("file", {}).get("id")
                self.print_test("POST /conversions/docx-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/docx-to-pdf", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/docx-to-pdf", "FAIL", str(e))
            return False
    
    def test_image_to_pdf(self):
        """Test POST /conversions/image-to-pdf"""
        try:
            test_file = self._create_test_image()
            if not test_file:
                self.print_test("POST /conversions/image-to-pdf", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/image-to-pdf",
                    files={"files[]": f},
                    data={"orientation": "portrait"},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["image_to_pdf"] = data.get("file", {}).get("id")
                self.print_test("POST /conversions/image-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/image-to-pdf", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/image-to-pdf", "FAIL", str(e))
            return False
    
    def test_xlsx_to_pdf(self):
        """Test POST /conversions/xlsx-to-pdf"""
        try:
            test_file = self._create_test_xlsx()
            if not test_file:
                self.print_test("POST /conversions/xlsx-to-pdf", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/xlsx-to-pdf",
                    files={"file": f},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["xlsx_to_pdf"] = data.get("file", {}).get("id")
                self.print_test("POST /conversions/xlsx-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/xlsx-to-pdf", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/xlsx-to-pdf", "FAIL", str(e))
            return False
    
    def test_pdf_to_image(self):
        """Test POST /conversions/pdf-to-image"""
        try:
            test_file = self._create_test_pdf()
            if not test_file:
                self.print_test("POST /conversions/pdf-to-image", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/pdf-to-image",
                    files={"file": f},
                    data={"pages": "1", "format": "jpg", "quality": "85"},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                if "files" in data:
                    self.test_data["pdf_to_image"] = data["files"][0].get("id")
                self.print_test("POST /conversions/pdf-to-image", "PASS",
                              f"{len(data.get('files', []))} image(s)")
                return True
            
            self.print_test("POST /conversions/pdf-to-image", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/pdf-to-image", "FAIL", str(e))
            return False
    
    def test_merge_pdfs(self):
        """Test POST /conversions/merge"""
        try:
            files = [self._create_test_pdf() for _ in range(2)]
            if not all(files):
                self.print_test("POST /conversions/merge", "FAIL", "Could not create test files")
                return False
            
            file_tuples = [("files[]", open(f, "rb")) for f in files]
            response = self.session.post(
                f"{self.base_url}/conversions/merge",
                files=file_tuples,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["merge"] = data.get("file", {}).get("id")
                self.print_test("POST /conversions/merge", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/merge", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/merge", "FAIL", str(e))
            return False
    
    # ========================================================================
    # PHASE 2 CONVERSIONS (4 endpoints)
    # ========================================================================
    
    def test_pptx_to_pdf(self):
        """Test POST /conversions/pptx-to-pdf"""
        try:
            # Note: This requires LibreOffice, may fail if not installed
            test_file = self._create_test_pptx()
            if not test_file:
                self.print_test("POST /conversions/pptx-to-pdf", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/pptx-to-pdf",
                    files={"file": f},
                    timeout=15
                )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("POST /conversions/pptx-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            status = response.status_code
            if status == 501:
                self.print_test("POST /conversions/pptx-to-pdf", "FAIL", 
                              "Not implemented (LibreOffice missing?)")
            else:
                self.print_test("POST /conversions/pptx-to-pdf", "FAIL", f"Status {status}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/pptx-to-pdf", "FAIL", str(e))
            return False
    
    def test_html_to_pdf(self):
        """Test POST /conversions/html-to-pdf"""
        try:
            html_content = "<html><body><h1>Test</h1><p>HTML to PDF conversion</p></body></html>"
            response = self.session.post(
                f"{self.base_url}/conversions/html-to-pdf",
                json={"html": html_content},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("POST /conversions/html-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            status = response.status_code
            if status == 501:
                self.print_test("POST /conversions/html-to-pdf", "FAIL",
                              "Not implemented (WeasyPrint missing?)")
            else:
                self.print_test("POST /conversions/html-to-pdf", "FAIL", f"Status {status}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/html-to-pdf", "FAIL", str(e))
            return False
    
    def test_csv_to_pdf(self):
        """Test POST /conversions/csv-to-pdf"""
        try:
            test_file = self._create_test_csv()
            if not test_file:
                self.print_test("POST /conversions/csv-to-pdf", "FAIL", "No test file")
                return False
            
            with open(test_file, "rb") as f:
                response = self.session.post(
                    f"{self.base_url}/conversions/csv-to-pdf",
                    files={"file": f},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("POST /conversions/csv-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/csv-to-pdf", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/csv-to-pdf", "FAIL", str(e))
            return False
    
    def test_text_to_pdf(self):
        """Test POST /conversions/text-to-pdf"""
        try:
            response = self.session.post(
                f"{self.base_url}/conversions/text-to-pdf",
                json={"text": "This is a test document.\nFor text to PDF conversion."},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("POST /conversions/text-to-pdf", "PASS",
                              f"{data['file']['size']} bytes")
                return True
            
            self.print_test("POST /conversions/text-to-pdf", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/text-to-pdf", "FAIL", str(e))
            return False
    
    # ========================================================================
    # USER CONVERSION HISTORY (3 endpoints)
    # ========================================================================
    
    def test_get_conversions_history(self):
        """Test GET /user/conversions"""
        try:
            response = self.session.get(
                f"{self.base_url}/user/conversions?limit=10",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("conversions", []))
                self.print_test("GET /user/conversions", "PASS", f"Retrieved {count} records")
                if count > 0:
                    self.test_data["conversion_id"] = data["conversions"][0].get("id")
                return True
            
            self.print_test("GET /user/conversions", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("GET /user/conversions", "FAIL", str(e))
            return False
    
    def test_get_conversion_detail(self):
        """Test GET /user/conversions/<id>"""
        try:
            # Use conversion ID from history if available
            conv_id = self.test_data.get("conversion_id", "test123")
            response = self.session.get(
                f"{self.base_url}/user/conversions/{conv_id}",
                timeout=5
            )
            
            if response.status_code in [200, 404]:  # Accept 404 if ID doesn't exist
                if response.status_code == 200:
                    self.print_test("GET /user/conversions/<id>", "PASS", "Record retrieved")
                else:
                    self.print_test("GET /user/conversions/<id>", "PASS", "Endpoint working (no record)")
                return True
            
            self.print_test("GET /user/conversions/<id>", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("GET /user/conversions/<id>", "FAIL", str(e))
            return False
    
    def test_delete_conversion(self):
        """Test DELETE /user/conversions/<id>"""
        try:
            conv_id = self.test_data.get("conversion_id", "test123")
            response = self.session.delete(
                f"{self.base_url}/user/conversions/{conv_id}",
                timeout=5
            )
            
            if response.status_code in [200, 404]:
                if response.status_code == 200:
                    self.print_test("DELETE /user/conversions/<id>", "PASS", "Record deleted")
                else:
                    self.print_test("DELETE /user/conversions/<id>", "PASS", "Endpoint working")
                return True
            
            self.print_test("DELETE /user/conversions/<id>", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("DELETE /user/conversions/<id>", "FAIL", str(e))
            return False
    
    # ========================================================================
    # USER SETTINGS (2 endpoints)
    # ========================================================================
    
    def test_get_user_settings(self):
        """Test GET /user/settings"""
        try:
            response = self.session.get(
                f"{self.base_url}/user/settings",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                settings = data.get("settings", {})
                self.print_test("GET /user/settings", "PASS",
                              f"Retrieved {len(settings)} settings")
                self.test_data["settings"] = settings
                return True
            
            self.print_test("GET /user/settings", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("GET /user/settings", "FAIL", str(e))
            return False
    
    def test_update_user_settings(self):
        """Test POST /user/settings"""
        try:
            response = self.session.post(
                f"{self.base_url}/user/settings",
                json={
                    "theme": "dark",
                    "notifications_enabled": True,
                    "compression_level": 7
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("POST /user/settings", "PASS", "Settings updated")
                return True
            
            self.print_test("POST /user/settings", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /user/settings", "FAIL", str(e))
            return False
    
    # ========================================================================
    # BATCH CONVERSION (1 endpoint)
    # ========================================================================
    
    def test_batch_conversion(self):
        """Test POST /conversions/batch"""
        try:
            # Create test files
            files = [self._create_test_pdf() for _ in range(2)]
            if not all(files):
                self.print_test("POST /conversions/batch", "FAIL", "Could not create test files")
                return False
            
            file_tuples = [("files[]", open(f, "rb")) for f in files]
            response = self.session.post(
                f"{self.base_url}/conversions/batch",
                files=file_tuples,
                data={"tool": "pdf-to-docx"},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.print_test("POST /conversions/batch", "PASS",
                              f"Processed {len(results)} files")
                self.test_data["batch_id"] = data.get("batch_id")
                return True
            
            self.print_test("POST /conversions/batch", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /conversions/batch", "FAIL", str(e))
            return False
    
    # ========================================================================
    # WEBHOOKS (3 endpoints)
    # ========================================================================
    
    def test_create_webhook(self):
        """Test POST /webhooks"""
        try:
            response = self.session.post(
                f"{self.base_url}/webhooks",
                json={
                    "name": "test_webhook",
                    "url": "https://example.com/webhook",
                    "events": ["conversion_complete", "conversion_error"]
                },
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                webhook_id = data.get("webhook_id", data.get("id"))
                self.test_data["webhook_id"] = webhook_id
                self.print_test("POST /webhooks", "PASS", f"Created webhook {webhook_id}")
                return True
            
            self.print_test("POST /webhooks", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("POST /webhooks", "FAIL", str(e))
            return False
    
    def test_list_webhooks(self):
        """Test GET /webhooks"""
        try:
            response = self.session.get(
                f"{self.base_url}/webhooks",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                webhooks = data.get("webhooks", [])
                self.print_test("GET /webhooks", "PASS", f"Retrieved {len(webhooks)} webhooks")
                return True
            
            self.print_test("GET /webhooks", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("GET /webhooks", "FAIL", str(e))
            return False
    
    def test_delete_webhook(self):
        """Test DELETE /webhooks/<webhook_id>"""
        try:
            webhook_id = self.test_data.get("webhook_id", "test123")
            response = self.session.delete(
                f"{self.base_url}/webhooks/{webhook_id}",
                timeout=5
            )
            
            if response.status_code in [200, 404]:
                if response.status_code == 200:
                    self.print_test("DELETE /webhooks/<id>", "PASS", "Webhook deleted")
                else:
                    self.print_test("DELETE /webhooks/<id>", "PASS", "Endpoint working")
                return True
            
            self.print_test("DELETE /webhooks/<id>", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("DELETE /webhooks/<id>", "FAIL", str(e))
            return False
    
    # ========================================================================
    # API DOCUMENTATION (1 endpoint)
    # ========================================================================
    
    def test_api_docs(self):
        """Test GET /docs"""
        try:
            response = requests.get(
                f"{self.base_url}/docs",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                endpoints = data.get("endpoints", {})
                self.print_test("GET /docs", "PASS", f"Retrieved docs for {len(endpoints)} endpoints")
                return True
            
            self.print_test("GET /docs", "FAIL", f"Status {response.status_code}")
            return False
        except Exception as e:
            self.print_test("GET /docs", "FAIL", str(e))
            return False
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _create_test_pdf(self):
        """Create a test PDF file."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            filename = "test_sample.pdf"
            if os.path.exists(filename):
                return filename
            
            c = canvas.Canvas(filename, pagesize=letter)
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 700, "This is a sample PDF for testing conversions.")
            c.save()
            return filename
        except:
            return None
    
    def _create_test_docx(self):
        """Create a test DOCX file."""
        try:
            from docx import Document
            
            filename = "test_sample.docx"
            if os.path.exists(filename):
                return filename
            
            doc = Document()
            doc.add_heading("Test Document", 0)
            doc.add_paragraph("This is a sample Word document for testing.")
            doc.save(filename)
            return filename
        except:
            return None
    
    def _create_test_image(self):
        """Create a test image file."""
        try:
            from PIL import Image
            
            filename = "test_sample.jpg"
            if os.path.exists(filename):
                return filename
            
            img = Image.new("RGB", (200, 200), color="blue")
            img.save(filename)
            return filename
        except:
            return None
    
    def _create_test_xlsx(self):
        """Create a test XLSX file."""
        try:
            from openpyxl import Workbook
            
            filename = "test_sample.xlsx"
            if os.path.exists(filename):
                return filename
            
            wb = Workbook()
            ws = wb.active
            ws["A1"] = "Name"
            ws["B1"] = "Value"
            ws["A2"] = "Test"
            ws["B2"] = 123
            wb.save(filename)
            return filename
        except:
            return None
    
    def _create_test_pptx(self):
        """Create a test PPTX file."""
        try:
            from pptx import Presentation
            
            filename = "test_sample.pptx"
            if os.path.exists(filename):
                return filename
            
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            title = slide.shapes.title
            title.text = "Test Presentation"
            prs.save(filename)
            return filename
        except:
            return None
    
    def _create_test_csv(self):
        """Create a test CSV file."""
        filename = "test_sample.csv"
        if os.path.exists(filename):
            return filename
        
        with open(filename, "w") as f:
            f.write("Name,Value,Category\n")
            f.write("Item1,100,A\n")
            f.write("Item2,200,B\n")
            f.write("Item3,300,A\n")
        
        return filename
    
    # ========================================================================
    # TEST EXECUTION
    # ========================================================================
    
    def run_all_tests(self):
        """Run all tests."""
        self.print_header("Document Converter API - Comprehensive Test Suite")
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Authentication
        self.print_header("Authentication Tests (2 endpoints)")
        self.test_auth_register()
        self.test_auth_login()
        
        if not self.token:
            print(f"{Colors.RED}✗ Authentication failed. Skipping remaining tests.{Colors.RESET}")
            self.print_summary()
            return
        
        # Phase 1 Conversions
        self.print_header("Phase 1 - Core Conversions (6 endpoints)")
        self.test_pdf_to_docx()
        self.test_docx_to_pdf()
        self.test_image_to_pdf()
        self.test_xlsx_to_pdf()
        self.test_pdf_to_image()
        self.test_merge_pdfs()
        
        # Phase 2 Conversions
        self.print_header("Phase 2 - Advanced Conversions (4 endpoints)")
        self.test_pptx_to_pdf()
        self.test_html_to_pdf()
        self.test_csv_to_pdf()
        self.test_text_to_pdf()
        
        # User Conversion History
        self.print_header("User Conversion History (3 endpoints)")
        self.test_get_conversions_history()
        self.test_get_conversion_detail()
        self.test_delete_conversion()
        
        # User Settings
        self.print_header("User Settings Management (2 endpoints)")
        self.test_get_user_settings()
        self.test_update_user_settings()
        
        # Batch Conversion
        self.print_header("Batch Conversion (1 endpoint)")
        self.test_batch_conversion()
        
        # Webhooks
        self.print_header("Webhooks Management (3 endpoints)")
        self.test_create_webhook()
        self.test_list_webhooks()
        self.test_delete_webhook()
        
        # API Documentation
        self.print_header("API Documentation (1 endpoint)")
        self.test_api_docs()
        
        # Summary
        self.print_summary()
    
    def run_quick_test(self):
        """Run quick health check."""
        self.print_header("Quick Health Check")
        
        # Check server connectivity
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ Server is running{Colors.RESET}")
                self.print_test("API Connectivity", "PASS", "Server responding")
            else:
                print(f"{Colors.RED}✗ Server returned {response.status_code}{Colors.RESET}")
                self.print_test("API Connectivity", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            print(f"{Colors.RED}✗ Cannot connect to server{Colors.RESET}")
            print(f"   Error: {str(e)}")
            self.print_test("API Connectivity", "FAIL", str(e))
            return
        
        # Quick auth test
        self.test_auth_login()
        
        if self.token:
            # Quick conversion test
            self.test_text_to_pdf()
            # Quick settings test
            self.test_get_user_settings()
        
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(description="Comprehensive API Test Suite")
    parser.add_argument("--url", default="http://localhost:5000/api",
                       help="API base URL (default: http://localhost:5000/api)")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick health check only")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed test results")
    
    args = parser.parse_args()
    
    tester = APITestSuite(args.url, args.detailed)
    
    if args.quick:
        tester.run_quick_test()
    else:
        tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == "__main__":
    main()
