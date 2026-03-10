# Advanced Features Implementation Guide

**Date:** February 25, 2026  
**Version:** 2.0  
**Status:** ✅ Complete & Validated

---

## Overview

This guide documents all the new advanced features added to the Document Converter API, including:
1. ✅ Additional conversion types (PPT→PDF, HTML→PDF, CSV→PDF, Text→PDF)
2. ✅ Conversion history tracking per user
3. ✅ User settings and preferences management
4. ✅ Batch conversion support
5. ✅ Webhook notifications system
6. ✅ Enhanced database schema

---

## 1. New Conversion Endpoints

### 1.1 PowerPoint to PDF Conversion
**Endpoint:** `POST /api/conversions/pptx-to-pdf`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST http://localhost:5000/api/conversions/pptx-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@presentation.pptx"
```

**Response Format:**
```json
{
  "success": true,
  "file": {
    "name": "presentation.pdf",
    "size": 1048576,
    "download_url": "/api/download/abc12345"
  }
}
```

**Supported Formats:** .pptx, .ppt, .odp

**Features:**
- Automatic LibreOffice conversion
- Full presentation support
- Preserves formatting and layouts
- 60-second timeout per file

---

### 1.2 HTML to PDF Conversion
**Endpoint:** `POST /api/conversions/html-to-pdf`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST http://localhost:5000/api/conversions/html-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello</h1></body></html>"
  }'
```

**Response Format:**
```json
{
  "success": true,
  "file": {
    "name": "document.pdf",
    "size": 524288,
    "download_url": "/api/download/def67890"
  }
}
```

**Parameters:**
- `html` (required): HTML content as string

**Features:**
- WeasyPrint support (primary)
- wkhtmltopdf fallback
- CSS styling preserved
- Full HTML5 support

---

### 1.3 CSV to PDF Conversion
**Endpoint:** `POST /api/conversions/csv-to-pdf`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST http://localhost:5000/api/conversions/csv-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"
```

**Response Format:**
```json
{
  "success": true,
  "file": {
    "name": "spreadsheet.pdf",
    "size": 2097152,
    "download_url": "/api/download/ghi45678"
  }
}
```

**Features:**
- Uses pandas for CSV parsing
- ReportLab for PDF generation
- Formatted table layout
- Header row styling
- Grid formatting

---

### 1.4 Text to PDF Conversion
**Endpoint:** `POST /api/conversions/text-to-pdf`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST http://localhost:5000/api/conversions/text-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is my document content.\nLine 2.",
    "filename": "my-document.txt"
  }'
```

**Response Format:**
```json
{
  "success": true,
  "file": {
    "name": "document.pdf",
    "size": 131072,
    "download_url": "/api/download/jkl90123"
  }
}
```

**Parameters:**
- `text` (required): Plain text content
- `filename` (optional): Original filename for reference

**Features:**
- ReportLab PDF generation
- Automatic paragraph spacing
- UTF-8 encoding support
- Clean formatting

---

## 2. Conversion History API

### 2.1 Get User Conversion History
**Endpoint:** `GET /api/user/conversions`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X GET "http://localhost:5000/api/user/conversions?limit=50&tool=pdf-to-docx" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Query Parameters:**
- `limit` (optional): Max records to return (default: 50)
- `tool` (optional): Filter by conversion tool name

**Response Format:**
```json
{
  "success": true,
  "conversions": [
    {
      "id": 1,
      "user_id": 123,
      "conversion_id": "conv_abc123",
      "tool_name": "pdf-to-docx",
      "input_format": "pdf",
      "output_format": "docx",
      "file_count": 1,
      "file_size_bytes": 2048576,
      "duration_seconds": 5.2,
      "status": "success",
      "created_at": "2026-02-25T10:30:45",
      "completed_at": "2026-02-25T10:30:50"
    }
  ]
}
```

---

### 2.2 Get Specific Conversion Details
**Endpoint:** `GET /api/user/conversions/<conversion_id>`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X GET "http://localhost:5000/api/user/conversions/conv_abc123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Format:**
```json
{
  "success": true,
  "conversion": {
    "id": 1,
    "user_id": 123,
    "conversion_id": "conv_abc123",
    "tool_name": "pdf-to-docx",
    "input_format": "pdf",
    "output_format": "docx",
    "file_count": 1,
    "file_size_bytes": 2048576,
    "duration_seconds": 5.2,
    "status": "success",
    "created_at": "2026-02-25T10:30:45",
    "completed_at": "2026-02-25T10:30:50"
  }
}
```

---

### 2.3 Delete Conversion Record
**Endpoint:** `DELETE /api/user/conversions/<conversion_id>`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X DELETE "http://localhost:5000/api/user/conversions/conv_abc123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Format:**
```json
{
  "success": true,
  "message": "Conversion removed from history"
}
```

---

## 3. User Settings API

### 3.1 Get User Settings
**Endpoint:** `GET /api/user/settings`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X GET "http://localhost:5000/api/user/settings" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Format:**
```json
{
  "success": true,
  "settings": {
    "id": 1,
    "user_id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "theme": "light",
    "notifications_enabled": true,
    "compression_level": 5,
    "auto_delete_minutes": 60,
    "api_calls_limit": 100,
    "batch_size_limit": 10,
    "created_at": "2026-02-25T10:00:00",
    "updated_at": "2026-02-25T10:00:00"
  }
}
```

**Settings Fields:**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `theme` | string | "light" | UI theme preference (light/dark) |
| `notifications_enabled` | boolean | true | Enable email notifications |
| `compression_level` | integer | 5 | PDF compression (1-9) |
| `auto_delete_minutes` | integer | 60 | Auto-delete files after N minutes |
| `api_calls_limit` | integer | 100 | Monthly API call limit |
| `batch_size_limit` | integer | 10 | Max files per batch conversion |

---

### 3.2 Update User Settings
**Endpoint:** `POST /api/user/settings`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST "http://localhost:5000/api/user/settings" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "compression_level": 7,
    "notifications_enabled": false,
    "auto_delete_minutes": 120
  }'
```

**Response Format:**
```json
{
  "success": true,
  "message": "Settings updated"
}
```

**Available Updates:**
- `theme`: "light" or "dark"
- `notifications_enabled`: true/false
- `compression_level`: 1-9
- `auto_delete_minutes`: 1-10080
- `api_calls_limit`: 1-10000
- `batch_size_limit`: 1-50

---

## 4. Batch Conversion API

### 4.1 Batch Convert Files
**Endpoint:** `POST /api/conversions/batch`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST "http://localhost:5000/api/conversions/batch" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "tool=pdf-to-docx" \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf" \
  -F "files=@file3.pdf"
```

**Response Format:**
```json
{
  "success": true,
  "batch_id": "batch_abc123def456",
  "processed": 3,
  "total": 3,
  "files": [
    {
      "name": "file1.pdf",
      "status": "processed"
    },
    {
      "name": "file2.pdf",
      "status": "processed"
    },
    {
      "name": "file3.pdf",
      "status": "processed"
    }
  ]
}
```

**Features:**
- Process up to 10 files per batch
- Automatic error handling per file
- Batch progress tracking
- Individual file status reporting

**Batch Statistics:**
- Max files: 10 per request
- Timeout: 5 minutes per batch
- Automatic retry: Enabled
- Error tolerance: Per-file

---

## 5. Webhooks API

### 5.1 Create Webhook
**Endpoint:** `POST /api/webhooks`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X POST "http://localhost:5000/api/webhooks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/webhook",
    "name": "My Webhook",
    "events": ["conversion_complete", "conversion_error"]
  }'
```

**Response Format:**
```json
{
  "success": true,
  "webhook_id": "hook_abc123",
  "secret_key": "secret_def456",
  "message": "Webhook created successfully"
}
```

**Parameters:**
- `url` (required): HTTPS endpoint to receive events
- `name` (optional): Friendly webhook name
- `events` (optional): List of events to subscribe to

**Available Events:**
- `conversion_complete`: Conversion finished successfully
- `conversion_error`: Conversion failed
- `batch_complete`: Batch conversion finished
- `file_upload`: New file uploaded
- `settings_change`: User settings changed

---

### 5.2 Get User Webhooks
**Endpoint:** `GET /api/webhooks`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X GET "http://localhost:5000/api/webhooks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Format:**
```json
{
  "success": true,
  "webhooks": [
    {
      "id": 1,
      "user_id": 123,
      "webhook_id": "hook_abc123",
      "name": "My Webhook",
      "url": "https://your-domain.com/webhook",
      "events": "[\"conversion_complete\", \"conversion_error\"]",
      "is_active": 1,
      "created_at": "2026-02-25T10:00:00",
      "last_triggered": "2026-02-25T10:30:45"
    }
  ]
}
```

---

### 5.3 Delete Webhook
**Endpoint:** `DELETE /api/webhooks/<webhook_id>`

**Authentication:** Bearer Token (Required)

**Request:**
```bash
curl -X DELETE "http://localhost:5000/api/webhooks/hook_abc123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Format:**
```json
{
  "success": true,
  "message": "Webhook deleted"
}
```

---

## 6. Database Schema Updates

### 6.1 New Tables Created

**user_settings Table:**
```sql
CREATE TABLE user_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER UNIQUE,
  username TEXT UNIQUE,
  email TEXT,
  theme TEXT DEFAULT 'light',
  notifications_enabled INTEGER DEFAULT 1,
  compression_level INTEGER DEFAULT 5,
  auto_delete_minutes INTEGER DEFAULT 60,
  api_calls_limit INTEGER DEFAULT 100,
  batch_size_limit INTEGER DEFAULT 10,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
```

**user_conversions Table:**
```sql
CREATE TABLE user_conversions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  conversion_id TEXT,
  tool_name TEXT,
  input_format TEXT,
  output_format TEXT,
  file_count INTEGER,
  file_size_bytes INTEGER,
  duration_seconds REAL,
  status TEXT,
  created_at TEXT,
  completed_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
```

**webhooks Table:**
```sql
CREATE TABLE webhooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  webhook_id TEXT UNIQUE,
  name TEXT,
  url TEXT,
  events TEXT,
  is_active INTEGER DEFAULT 1,
  secret_key TEXT,
  created_at TEXT,
  last_triggered TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
```

**webhook_logs Table:**
```sql
CREATE TABLE webhook_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  webhook_id TEXT,
  event_type TEXT,
  status_code INTEGER,
  payload TEXT,
  response TEXT,
  created_at TEXT,
  FOREIGN KEY(webhook_id) REFERENCES webhooks(webhook_id)
);
```

**batch_conversions Table:**
```sql
CREATE TABLE batch_conversions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT UNIQUE,
  user_id INTEGER,
  name TEXT,
  tool_name TEXT,
  total_files INTEGER,
  processed_files INTEGER,
  status TEXT,
  created_at TEXT,
  completed_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 7. Error Handling

All new endpoints follow consistent error handling:

**Error Response Format:**
```json
{
  "success": false,
  "error": "Error message describing the issue"
}
```

**HTTP Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created (POST) |
| 400 | Bad request (missing parameters) |
| 401 | Unauthorized (invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found (resource doesn't exist) |
| 500 | Server error |

---

## 8. Rate Limiting & Quotas

**Default Limits per User:**
- API calls: 100 per month
- Batch size: 10 files per request
- Webhook events: 1000 per month
- File retention: 1 hour (configurable)
- Max file size: 16 MB per file

---

## 9. Python SDK Example

```python
import requests
import json

class DocumentConverterSDK:
    def __init__(self, api_url="http://localhost:5000/api", token=None):
        self.api_url = api_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    def login(self, username, password):
        """Login and get token"""
        response = requests.post(
            f"{self.api_url}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.headers = {"Authorization": f"Bearer {self.token}"}
            return self.token
        return None
    
    def pptx_to_pdf(self, file_path):
        """Convert PowerPoint to PDF"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.api_url}/conversions/pptx-to-pdf",
                headers=self.headers,
                files=files
            )
        return response.json() if response.status_code == 200 else None
    
    def get_conversion_history(self, limit=50):
        """Get conversion history"""
        response = requests.get(
            f"{self.api_url}/user/conversions?limit={limit}",
            headers=self.headers
        )
        return response.json()
    
    def get_settings(self):
        """Get user settings"""
        response = requests.get(
            f"{self.api_url}/user/settings",
            headers=self.headers
        )
        return response.json()
    
    def update_settings(self, **kwargs):
        """Update user settings"""
        response = requests.post(
            f"{self.api_url}/user/settings",
            headers=self.headers,
            json=kwargs
        )
        return response.json()
    
    def create_webhook(self, url, name=None, events=None):
        """Create webhook"""
        response = requests.post(
            f"{self.api_url}/webhooks",
            headers=self.headers,
            json={
                "url": url,
                "name": name or "New Webhook",
                "events": events or ["conversion_complete", "conversion_error"]
            }
        )
        return response.json()
    
    def batch_convert(self, tool, file_paths):
        """Batch convert files"""
        files = [('files', open(fp, 'rb')) for fp in file_paths]
        response = requests.post(
            f"{self.api_url}/conversions/batch",
            headers=self.headers,
            data={'tool': tool},
            files=files
        )
        return response.json()
```

---

## 10. Implementation Checklist

- ✅ Database schema updated with 5 new tables
- ✅ PPT/PPTX to PDF conversion endpoint
- ✅ HTML to PDF conversion endpoint
- ✅ CSV to PDF conversion endpoint
- ✅ Text to PDF conversion endpoint
- ✅ User conversion history API
- ✅ User settings management API
- ✅ Batch conversion endpoint
- ✅ Webhook management system
- ✅ Helper functions for token verification
- ✅ Python code validation (no syntax errors)
- ✅ Comprehensive documentation

---

## 11. Testing Instructions

### Test New Conversions:
```bash
# PPT to PDF
curl -X POST http://localhost:5000/api/conversions/pptx-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample.pptx"

# HTML to PDF
curl -X POST http://localhost:5000/api/conversions/html-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Test</h1>"}'

# CSV to PDF
curl -X POST http://localhost:5000/api/conversions/csv-to-pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample.csv"
```

### Test History:
```bash
curl -X GET "http://localhost:5000/api/user/conversions?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test User Settings:
```bash
curl -X GET http://localhost:5000/api/user/settings \
  -H "Authorization: Bearer YOUR_TOKEN"

curl -X POST http://localhost:5000/api/user/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark", "compression_level": 8}'
```

---

## 12. Next Steps

**Future Enhancement Opportunities:**

1. **Additional Conversion Types:**
   - Excel to Image
   - Markdown to PDF
   - JSON to PDF

2. **Webhook Enhancements:**
   - Webhook retry mechanism
   - Event filtering per webhook
   - Webhook logs API

3. **Performance Features:**
   - Conversion caching
   - Parallel processing
   - Progress streaming

4. **Analytics:**
   - User metrics endpoint
   - Conversion statistics
   - Usage reports

---

## 13. Support & Troubleshooting

For issues or questions:
1. Check if Bearer token is valid (24-hour expiry)
2. Verify file format matches endpoint requirements
3. Check server logs for detailed error messages
4. Ensure LibreOffice is installed for PPT conversion

---

**End of Advanced Features Guide**
