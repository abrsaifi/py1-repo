# Document Converter API Reference

## Overview

The Document Converter provides a comprehensive REST API for file format conversions. All endpoints support authentication via JWT tokens.

**Base URL**: `http://localhost:5000/api`  
**API Version**: 2.0

---

## Authentication

### Register User

```http
POST /api/auth/register
```

**Request:**
```json
{
  "username": "myuser",
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "myuser",
    "email": "user@example.com"
  }
}
```

**Status Codes:**
- `201`: User created successfully
- `400`: Validation error (invalid email, weak password, etc.)
- `409`: User already exists

---

### Login

```http
POST /api/auth/login
```

**Request:**
```json
{
  "username": "myuser",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "myuser",
    "email": "user@example.com"
  }
}
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid credentials
- `404`: User not found

---

## File Conversions

### PDF to DOCX (Word)

Convert PDF documents to Microsoft Word format.

```http
POST /api/conversions/pdf-to-docx
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | file | Yes | PDF file to convert |

**Response (200 OK):**
```json
{
  "success": true,
  "file": {
    "name": "document.docx",
    "size": 25432,
    "download_url": "/api/download/file-id-12345"
  }
}
```

**Example - cURL:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  http://localhost:5000/api/conversions/pdf-to-docx
```

**Example - Python:**
```python
import requests

token = "YOUR_JWT_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:5000/api/conversions/pdf-to-docx",
        files=files,
        headers=headers
    )

result = response.json()
if result["success"]:
    print(f"Download: {result['file']['download_url']}")
    # Download the file
    file_response = requests.get(
        f"http://localhost:5000{result['file']['download_url']}",
        headers=headers
    )
    with open("converted_document.docx", "wb") as out:
        out.write(file_response.content)
```

**Example - JavaScript/Fetch:**
```javascript
const token = "YOUR_JWT_TOKEN";
const formData = new FormData();
formData.append("file", documentFile);

const response = await fetch("/api/conversions/pdf-to-docx", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
if (result.success) {
  // Download the converted file
  window.location.href = result.file.download_url;
}
```

**Status Codes:**
- `200`: Conversion successful
- `400`: Invalid input or unsupported file format
- `401`: Unauthorized (missing/invalid token)
- `500`: Conversion failed

---

### DOCX to PDF

Convert Microsoft Word documents to PDF.

```http
POST /api/conversions/docx-to-pdf
```

**Form Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| file | file | Yes |

**Response:** Same as PDF to DOCX

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.docx" \
  http://localhost:5000/api/conversions/docx-to-pdf
```

---

### Image to PDF

Convert image files (JPG, PNG, GIF, BMP, WebP) to PDF.

```http
POST /api/conversions/image-to-pdf
```

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| files[] | file | Yes | One or more image files |
| orientation | string | No | 'portrait' or 'landscape' (default: 'portrait') |

**Supported Image Formats:**
- JPG/JPEG
- PNG
- GIF
- BMP
- WebP

**Response (200 OK):**
```json
{
  "success": true,
  "file": {
    "name": "document.pdf",
    "size": 45231,
    "download_url": "/api/download/file-id-67890"
  }
}
```

**Example - Multiple Images:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files[]=@image1.jpg" \
  -F "files[]=@image2.png" \
  -F "orientation=landscape" \
  http://localhost:5000/api/conversions/image-to-pdf
```

---

### XLSX to PDF

Convert Excel spreadsheets to PDF.

```http
POST /api/conversions/xlsx-to-pdf
```

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | file | Yes | Excel file (.xlsx or .xls) |
| sheet | string | No | Sheet name or index to convert |

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@spreadsheet.xlsx" \
  http://localhost:5000/api/conversions/xlsx-to-pdf
```

---

### PDF to Image

Convert PDF pages to image files.

```http
POST /api/conversions/pdf-to-image
```

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | file | Yes | PDF file |
| pages | string | No | Page range: "all", "1-5", "2,4,6" (default: "all") |
| format | string | No | Output format: 'jpg', 'png', 'webp' (default: 'jpg') |
| quality | integer | No | Quality 0-100 (default: 85, only for JPG) |

**Response (200 OK):**
```json
{
  "success": true,
  "files": [
    {
      "name": "page_1.jpg",
      "size": 12345,
      "download_url": "/api/download/file-id-001"
    },
    {
      "name": "page_2.jpg",
      "size": 13456,
      "download_url": "/api/download/file-id-002"
    }
  ],
  "message": "Converted 2 pages to JPG"
}
```

**Example - Convert Pages 1-3 to PNG:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "pages=1-3" \
  -F "format=png" \
  http://localhost:5000/api/conversions/pdf-to-image
```

---

### Merge PDFs

Merge multiple PDF files into one.

```http
POST /api/conversions/merge
```

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| files[] | file | Yes | PDF files to merge (minimum 2) |

**Response (200 OK):**
```json
{
  "success": true,
  "file": {
    "name": "merged.pdf",
    "size": 125431,
    "download_url": "/api/download/file-id-merged-123"
  }
}
```

**Example - Merge 3 PDFs:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files[]=@doc1.pdf" \
  -F "files[]=@doc2.pdf" \
  -F "files[]=@doc3.pdf" \
  http://localhost:5000/api/conversions/merge
```

---

## File Download

Download converted files by ID.

```http
GET /api/download/<file_id>
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| file_id | string | File ID returned from conversion response |

**Response:**
- Binary file data (application/octet-stream)

**Headers:**
```
Content-Disposition: attachment; filename="document.docx"
Content-Type: application/octet-stream
Content-Length: 25432
```

**Example:**
```bash
curl -O -J \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/download/file-id-12345
```

**Status Codes:**
- `200`: File returned successfully
- `404`: File not found
- `410`: File expired (1-hour TTL)

---

## API Documentation

Get comprehensive API documentation in JSON format.

```http
GET /api/docs
```

**Response:** JSON object with full API specification

**Example:**
```bash
curl http://localhost:5000/api/docs
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error description"
}
```

### Common Error Codes

| Status | Error | Description |
|--------|-------|-------------|
| 400 | "No file provided" | Request missing file parameter |
| 400 | "Invalid input" | File format not supported |
| 401 | "Unauthorized" | Missing or invalid authentication token |
| 404 | "File not found" | Download file doesn't exist |
| 410 | "File expired" | Download file TTL exceeded (1 hour) |
| 500 | "Conversion failed" | Internal server error during processing |

---

## Rate Limits

- **Requests per minute**: 60
- **Maximum file size**: 16 MB
- **File retention**: 1 hour

---

## Supported Formats

### Input Formats
```
Documents: PDF, DOCX, DOC, XLSX, XLS, PPT, PPTX
Images: JPG, PNG, GIF, BMP, WebP, SVG
Data: CSV, JSON, HTML
```

### Output Formats
```
Documents: PDF, DOCX, XLSX, PPT, PPTX
Images: JPG, PNG, WebP
Data: CSV, HTML
```

---

## Testing Quick Reference

### 1. Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

### 3. Convert PDF to DOCX
```bash
# Save token from login response
TOKEN="your_token_here"

curl -X POST http://localhost:5000/api/conversions/pdf-to-docx \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample.pdf"
```

### 4. Download Converted File
```bash
FILE_ID="file-id-from-response"
TOKEN="your_token_here"

curl -X GET http://localhost:5000/api/download/$FILE_ID \
  -H "Authorization: Bearer $TOKEN" \
  -O -J
```

---

## Python SDK Example

```python
import requests
import json

class DocumentConverter:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def register(self, username, email, password):
        """Register a new user."""
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        return response.json()
    
    def login(self, username, password):
        """Login and store token."""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        result = response.json()
        if result["success"]:
            self.token = result["token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        return result
    
    def pdf_to_docx(self, input_file, output_file=None):
        """Convert PDF to DOCX."""
        with open(input_file, "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.base_url}/conversions/pdf-to-docx",
                files=files
            )
        
        result = response.json()
        if result["success"] and output_file:
            self._download_file(
                result["file"]["download_url"],
                output_file
            )
        return result
    
    def image_to_pdf(self, image_files, orientation="portrait"):
        """Convert images to PDF."""
        files = [("files[]", open(img, "rb")) for img in image_files]
        data = {"orientation": orientation}
        
        response = self.session.post(
            f"{self.base_url}/conversions/image-to-pdf",
            files=files,
            data=data
        )
        return response.json()
    
    def _download_file(self, url, output_file):
        """Download a file by ID."""
        response = self.session.get(url)
        with open(output_file, "wb") as f:
            f.write(response.content)

# Usage
converter = DocumentConverter()

# Register and login
converter.register("newuser", "user@example.com", "SecurePass123")
converter.login("newuser", "SecurePass123")

# Convert PDF to DOCX
result = converter.pdf_to_docx("input.pdf", "output.docx")
print(result)
```

---

## Changelog

### v2.0 (Current)
- New RESTful endpoints for common conversions
- JWT authentication
- Comprehensive API documentation
- File download by ID feature
- 1-hour file retention policy

---

## Support

For issues, feature requests, or questions, please contact support.
