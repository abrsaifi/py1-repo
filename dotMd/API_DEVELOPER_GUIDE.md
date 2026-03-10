# API Reference: Document Processing System

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Base URL**: `https://your-domain.com/api`

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Format & Headers](#format--headers)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Batch Image Processing](#batch-image-processing)
6. [Batch PDF Processing](#batch-pdf-processing)
7. [Smart Crop](#smart-crop)
8. [PDF Form Filling](#pdf-form-filling)
9. [Data Export](#data-export)
10. [Status Codes](#status-codes)
11. [Code Examples](#code-examples)

---

## Authentication

### API Key Authentication

All API requests require an API key in the header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-domain.com/api/batch-process-images
```

### Getting Your API Key

1. Log in to dashboard
2. Go to Settings → API Keys
3. Click "Generate New Key"
4. Copy key (saved only once)

### JWT Token Authentication

Alternative method using JWT tokens:

```bash
# Get token
curl -X POST https://your-domain.com/api/auth/token \
  -d '{"email":"user@example.com","password":"password"}'

# Response
{"token": "eyJhbGciOiJIUzI1NiI..."}

# Use in request
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiI..." \
  https://your-domain.com/api/batch-process-images
```

---

## Format & Headers

### Request Headers

```http
Content-Type: multipart/form-data         # For file uploads
Authorization: Bearer YOUR_API_KEY        # Authentication
User-Agent: YourApp/1.0                   # Recommended
```

### Response Format

All responses are JSON:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Processing complete",
  "timestamp": "2026-02-26T10:30:00Z"
}
```

### Common Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success` or `error` |
| `data` | object | Response payload |
| `message` | string | Human-readable message |
| `timestamp` | string | ISO 8601 timestamp |
| `request_id` | string | Unique request identifier |

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type not supported. Allowed: jpg, png, bmp",
    "details": {
      "provided": "gif",
      "allowed": ["jpg", "png", "bmp", "tiff"]
    }
  },
  "timestamp": "2026-02-26T10:30:00Z"
}
```

### Error Codes Reference

| Code | HTTP | Meaning | Solution |
|------|------|---------|----------|
| `INVALID_FILE_TYPE` | 400 | Wrong file format | Check supported formats |
| `FILE_TOO_LARGE` | 413 | Exceeds size limit | Use smaller file |
| `UNSUPPORTED_OPERATION` | 400 | Invalid operation | Check operation list |
| `PROCESSING_FAILED` | 500 | Processing error | Retry or contact support |
| `UNAUTHORIZED` | 401 | Invalid/missing API key | Check API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait before retrying |
| `RESOURCE_NOT_FOUND` | 404 | File/resource missing | Verify resource ID |
| `INVALID_PARAMETERS` | 400 | Bad parameters | Check parameter format |

### Handling Errors

```python
import requests

try:
    response = requests.post(
        'https://api.domain.com/batch-process-images',
        files={'files': open('image.jpg', 'rb')},
        data={'operation': 'compress'},
        headers={'Authorization': 'Bearer KEY'}
    )
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    error = e.response.json()
    print(f"Error: {error['error']['code']}")
    print(f"Message: {error['error']['message']}")
except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")
```

---

## Rate Limiting

### Limits by Plan

| Plan | Requests/Hour | Concurrent | File Size |
|------|---|---|---|
| Free | 60 | 1 | 10MB |
| Pro | 1000 | 5 | 100MB |
| Enterprise | Unlimited | 50 | 500MB |

### Rate Limit Headers

Responses include rate limit info:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 942
X-RateLimit-Reset: 1645854600
```

### Handling Rate Limits

```python
import time
import requests

max_retries = 3
for attempt in range(max_retries):
    response = requests.post(...)
    if response.status_code == 429:
        reset_time = int(response.headers['X-RateLimit-Reset'])
        wait_seconds = reset_time - time.time()
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        continue
    break
```

---

## Batch Image Processing

### Endpoint

```http
POST /batch-process-images
```

### Parameters

| Name | Type | Required | Values |
|------|------|----------|--------|
| `files` | file[] | Yes | JPG, PNG, BMP, TIFF, GIF |
| `operation` | string | Yes | `compress`, `resize`, `convert`, `thumbnail` |
| `quality` | integer | No | 1-100 (default: 85) |
| `width` | integer | No | 1-4000 (for resize) |
| `height` | integer | No | 1-4000 (for resize) |

### Request

```bash
curl -X POST https://api.domain.com/batch-process-images \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "operation=compress" \
  -F "quality=80"
```

### Response

```json
{
  "status": "success",
  "data": {
    "processed_count": 2,
    "files": [
      {
        "original": "image1.jpg",
        "output": "image1_compressed.jpg",
        "original_size": 2048576,
        "output_size": 614400,
        "savings_percent": 70,
        "processing_time_ms": 1200
      },
      {
        "original": "image2.png",
        "output": "image2_compressed.jpg",
        "original_size": 1572864,
        "output_size": 491520,
        "savings_percent": 69,
        "processing_time_ms": 980
      }
    ],
    "total_processing_time_ms": 2180,
    "download_url": "https://api.domain.com/download/batch_12345"
  },
  "message": "2 images processed successfully"
}
```

### Operations

#### compress
- Reduces file size
- Maintains quality
- Quality parameter: 1-100

#### resize
- Resizes to specified dimensions
- Maintains aspect ratio if one dimension omitted
- Default: 800x600

#### convert
- Converts to JPG format
- Improves compatibility
- Auto-converts PNG, BMP, TIFF

#### thumbnail
- Creates 200x200 preview
- Fast generation
- Great for galleries

---

## Batch PDF Processing

### Endpoint

```http
POST /batch-process-pdfs
```

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `files` | file[] | Yes | PDF files |
| `operations` | string[] | Yes | Array of operations |
| `password` | string | No | For encrypt operation |
| `watermark_text` | string | No | Custom watermark (default: "DRAFT") |

### Request

```bash
curl -X POST https://api.domain.com/batch-process-pdfs \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "operations=compress" \
  -F "operations=watermark" \
  -F "watermark_text=CONFIDENTIAL"
```

### Response

```json
{
  "status": "success",
  "data": {
    "processed_count": 2,
    "files": [
      {
        "original": "document1.pdf",
        "output": "document1_processed.pdf",
        "original_size": 5242880,
        "output_size": 2097152,
        "operations_applied": ["compress", "watermark"],
        "processing_time_ms": 3400
      }
    ],
    "download_url": "https://api.domain.com/download/batch_pdf_12345"
  }
}
```

### Operations

#### compress
- Size reduction: 30-60%
- Maintains readability

#### encrypt
- 256-bit AES encryption
- Requires `password` parameter

#### watermark
- Adds text overlay
- Default: "DRAFT"
- Custom: use `watermark_text` parameter

#### clean
- Removes metadata
- Strips embedded files
- Removes form data

#### black_and_white
- Converts to grayscale
- Reduces size
- Better for printing

---

## Smart Crop

### Endpoint

```http
POST /smart-crop-images
```

### Parameters

| Name | Type | Required | Values |
|------|------|----------|--------|
| `file` | file | Yes | JPG, PNG, BMP |
| `mode` | string | No | `content`, `border`, `document` (default: content) |

### Request

```bash
curl -X POST https://api.domain.com/smart-crop-images \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@photo.jpg" \
  -F "mode=content"
```

### Response

```json
{
  "status": "success",
  "data": {
    "original_dimensions": {
      "width": 2400,
      "height": 2000
    },
    "cropped_dimensions": {
      "width": 1800,
      "height": 1500
    },
    "crop_coordinates": {
      "x1": 300,
      "y1": 250,
      "x2": 2100,
      "y2": 1750
    },
    "output_file": "photo_cropped.jpg",
    "savings_percent": 33,
    "processing_time_ms": 2400,
    "download_url": "https://api.domain.com/download/file_12345"
  }
}
```

### Crop Modes

| Mode | Best For | Algorithm |
|------|----------|-----------|
| `content` | Photos, products | AI content detection |
| `border` | Scans, documents | Border removal |
| `document` | Document photos | Perspective correction |

---

## PDF Form Filling

### Endpoint

```http
POST /fill-pdf-forms
```

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file` | file | Yes | Fillable PDF form |
| `field_data` | JSON | Yes | Form field values |

### Request

```bash
curl -X POST https://api.domain.com/fill-pdf-forms \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@form.pdf" \
  -F 'field_data={"First_Name":"John","Last_Name":"Doe"}'
```

### Response

```json
{
  "status": "success",
  "data": {
    "input_file": "form.pdf",
    "output_file": "form_filled.pdf",
    "fields_filled": 4,
    "fields_total": 5,
    "unfilled_fields": ["Signature"],
    "processing_time_ms": 800,
    "download_url": "https://api.domain.com/download/file_12345"
  },
  "message": "4 of 5 fields filled successfully"
}
```

### Field Data Format

```json
{
  "Field_Name_1": "value1",
  "Field_Name_2": "value2",
  "Field_Name_3": 12345,
  "Field_Name_4": true
}
```

---

## Data Export

### Endpoint

```http
POST /export-data-pdf
```

### Parameters

| Name | Type | Required | Values |
|------|------|----------|--------|
| `file` | file | Yes | CSV, XLSX, JSON |
| `output_format` | string | No | `pdf` or `excel` (default: pdf) |
| `report_type` | string | No | `summary`, `detailed`, `table` (default: table) |

### Request

```bash
curl -X POST https://api.domain.com/export-data-pdf \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@data.csv" \
  -F "output_format=pdf" \
  -F "report_type=summary"
```

### Response

```json
{
  "status": "success",
  "data": {
    "input_file": "data.csv",
    "input_format": "csv",
    "output_file": "report.pdf",
    "output_format": "pdf",
    "rows_processed": 150,
    "total_size_bytes": 51200,
    "processing_time_ms": 3200,
    "download_url": "https://api.domain.com/download/file_12345"
  }
}
```

---

## Status Codes

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | File processed |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid API key |
| 413 | Payload Too Large | File exceeds limit |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Processing failed |
| 503 | Service Unavailable | Maintenance mode |

---

## Code Examples

### Python

```python
import requests
import json

# Setup
API_KEY = "your_api_key"
BASE_URL = "https://api.domain.com"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Batch compress images
with open('image.jpg', 'rb') as f:
    files = {'files': f}
    data = {'operation': 'compress', 'quality': 85}
    response = requests.post(
        f"{BASE_URL}/batch-process-images",
        files=files,
        data=data,
        headers=headers
    )

result = response.json()
if result['status'] == 'success':
    download_url = result['data']['download_url']
    print(f"Download: {download_url}")
else:
    print(f"Error: {result['error']['message']}")
```

### JavaScript

```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.domain.com';

async function batchProcessImages(files, operation) {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });
  formData.append('operation', operation);
  
  try {
    const response = await fetch(
      `${BASE_URL}/batch-process-images`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`
        },
        body: formData
      }
    );
    
    const result = await response.json();
    if (result.status === 'success') {
      window.location.href = result.data.download_url;
    } else {
      console.error(result.error.message);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}

// Usage
const fileInput = document.getElementById('file-input');
batchProcessImages(fileInput.files, 'compress');
```

### cURL

```bash
#!/bin/bash

API_KEY="your_api_key"
BASE_URL="https://api.domain.com"

# Fill PDF form
curl -X POST "$BASE_URL/fill-pdf-forms" \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@form.pdf" \
  -F 'field_data={
    "First_Name": "John",
    "Last_Name": "Doe",
    "Email": "john@example.com"
  }'
```

### Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const apiKey = 'your_api_key';
const baseURL = 'https://api.domain.com';

async function smartCropImage(imagePath, mode = 'content') {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  form.append('mode', mode);
  
  try {
    const response = await axios.post(
      `${baseURL}/smart-crop-images`,
      form,
      {
        headers: {
          ...form.getHeaders(),
          'Authorization': `Bearer ${apiKey}`
        }
      }
    );
    
    console.log('Cropped dimensions:', response.data.data.cropped_dimensions);
    return response.data.data.download_url;
  } catch (error) {
    console.error('Error:', error.response?.data?.error?.message);
  }
}

// Usage
smartCropImage('photo.jpg', 'content').then(downloadUrl => {
  console.log('Download:', downloadUrl);
});
```

---

## Webhooks

### Webhook Configuration

For async processing, register webhooks in dashboard:

```
Settings → Integrations → Webhooks
```

### Webhook Events

```json
{
  "event": "processing.completed",
  "timestamp": "2026-02-26T10:30:00Z",
  "data": {
    "request_id": "req_12345",
    "status": "success",
    "file_count": 5,
    "download_url": "https://api.domain.com/download/batch_12345"
  }
}
```

### Event Types

- `processing.started` - Processing began
- `processing.progress` - Partial completion (10%, 50%, etc.)
- `processing.completed` - All files processed
- `processing.failed` - Fatal error occurred

---

## Support & Debugging

### Debug Mode

Enable verbose logging:

```bash
curl -X POST https://api.domain.com/batch-process-images \
  -H "X-Debug: true" \
  -F "files=@image.jpg" \
  -F "operation=compress"
```

Response includes:
- timing information
- processing steps
- memory usage
- OCR engine used (if applicable)

### Getting Help

- **API Docs**: docs.company.com/api
- **Status**: status.company.com
- **Support**: support@company.com
- **Slack**: #api-support (enterprise only)

---

**Last Updated**: February 26, 2026  
**API Version**: 1.0.0  
**Status**: ✅ Production Ready
