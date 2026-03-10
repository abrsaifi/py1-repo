# Job Resumption Guide

## Overview

The Job Resumption feature allows users to automatically retry failed conversions without needing to re-configure parameters. When a conversion fails, users can simply resume from the `/api/convert/resume` endpoint with new files, and all original conversion parameters are preserved.

**Status:** ✅ Production Ready

---

## Key Features

- **Parameter Preservation** - Original conversion settings are saved and reused
- **Automatic Linking** - Original and resumed jobs are linked in the database for audit trails
- **Retry Tracking** - System tracks number of retries and retry history
- **User-Friendly** - Simple one-click resumption from the API
- **Graceful Handling** - Only allows resuming jobs with `error` or `failed` status

---

## API Endpoint

### Retry a Failed Conversion

**Endpoint:** `POST /api/convert/resume/{job_id}`

**Purpose:** Resume a failed conversion with new files

**Required Parameters:**
- `job_id` (URL path) - The ID of the failed job to retry
- `files` or `files[]` (form data) - New file(s) to convert (required)

**Optional Parameters:**
- Any form parameters sent (will be ignored, original parameters used)

**Response:**
```json
{
  "success": true,
  "new_job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_job_id": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
  "message": "Resumption job started. New Job ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Error Responses:**

1. **Invalid Job ID Format** (400)
   ```json
   {
     "success": false,
     "error": "Invalid job ID format"
   }
   ```

2. **Job Not Found** (404)
   ```json
   {
     "success": false,
     "error": "Original job {job_id} not found"
   }
   ```

3. **Job Not Failed** (400)
   ```json
   {
     "success": false,
     "error": "Job status is \"processing\", not failed. Only failed jobs can be resumed."
   }
   ```

4. **No Files Provided** (400)
   ```json
   {
     "success": false,
     "error": "No files provided for resumption. Please upload files to retry."
   }
   ```

5. **Files Too Large** (413)
   ```json
   {
     "success": false,
     "error": "Total file size exceeds 100MB limit"
   }
   ```

6. **Rate Limit Exceeded** (429)
   ```json
   {
     "success": false,
     "error": "Rate limit exceeded. Maximum 5 conversions per minute."
   }
   ```

---

## Implementation Details

### Database Changes

**Metadata Stored with Jobs:**
```json
{
  "tool": "To PDF",
  "form_data": {
    "quality": "high",
    "margin": "10mm",
    ...
  },
  "original_file_names": ["document.docx", "image.jpg"],
  "retry_of": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
  "retry_count": 1,
  "retried_at": "2026-02-24T14:30:45.123456"
}
```

**Retry Linking:**
- Original jobs get `retried_by` field pointing to new job_id
- Resumed jobs get `retry_of` field pointing to original job_id
- Each provides an audit trail of conversion attempts

### Process Flow

1. User calls `/api/convert/resume/{original_job_id}`
2. System validates:
   - Original job exists and is failed
   - New files provided and within size limits
   - Rate limit not exceeded
3. System creates new job with:
   - New `job_id` (UUID)
   - Same `tool_name` as original
   - New files from request
   - Preserved `form_data` from original metadata
   - Metadata linking back to original job
4. System broadcasts `job_started` WebSocket event (if enabled)
5. Background worker processes conversion with:
   - New files
   - Original parameters
   - Same conversion logic as initial job
6. On completion, original job updated with `retried_by` reference

### Supported Job Statuses

Only jobs with these statuses can be resumed:
- `error` - Conversion encountered an error
- `failed` - Conversion failed during processing

Jobs with these statuses CANNOT be resumed:
- `queued` - Not started yet
- `processing` - Still running
- `complete` - Already succeeded
- `cancelled` - User cancelled

---

## Usage Examples

### cURL Example

```bash
#!/bin/bash

# First, start a conversion that will fail
ORIGINAL_JOB_ID="f1e2d3c4-b5a6-7890-1234-567890abcdef"

# Then, resume with new files
curl -X POST http://localhost:5000/api/convert/resume/$ORIGINAL_JOB_ID \
  -F "files=@document_v2.pdf" \
  -H "Accept: application/json"
```

### JavaScript Example

```javascript
async function resumeFailedConversion(originalJobId, filesToRetry) {
  const formData = new FormData();
  
  // Add files to convert
  for (const file of filesToRetry) {
    formData.append('files', file);
  }
  
  try {
    const response = await fetch(
      `/api/convert/resume/${originalJobId}`,
      {
        method: 'POST',
        body: formData
      }
    );
    
    const result = await response.json();
    
    if (result.success) {
      console.log(`Resumption started. New job: ${result.new_job_id}`);
      // Now poll /api/convert/status/{new_job_id} or use WebSocket
      
      // Optional: watch for updates via WebSocket
      if (window.io) {
        const socket = io();
        socket.emit('watch_job', { job_id: result.new_job_id });
        socket.on('job_completed', (event) => {
          if (event.job_id === result.new_job_id) {
            console.log('Resumption completed!', event);
          }
        });
      }
    } else {
      console.error(`Resumption failed: ${result.error}`);
    }
  } catch (error) {
    console.error('Error resuming conversion:', error);
  }
}
```

### Python Example

```python
import requests

def resume_conversion(original_job_id, file_path, api_url='http://localhost:5000'):
    """Resume a failed conversion with a new file."""
    
    url = f'{api_url}/api/convert/resume/{original_job_id}'
    
    with open(file_path, 'rb') as f:
        files = {'files': f}
        response = requests.post(url, files=files)
    
    result = response.json()
    
    if result['success']:
        print(f"✓ Resumption started")
        print(f"  Original Job: {result['original_job_id']}")
        print(f"  New Job ID:   {result['new_job_id']}")
        return result['new_job_id']
    else:
        print(f"✗ Resumption failed: {result['error']}")
        return None


# Usage
new_job_id = resume_conversion(
    'f1e2d3c4-b5a6-7890-1234-567890abcdef',
    'corrected_document.pdf'
)
```

### Vue.js Example

```vue
<template>
  <div class="resume-section">
    <h3>Resume Failed Conversion</h3>
    
    <div class="form-group">
      <label>Failed Job ID:</label>
      <input v-model="originalJobId" type="text" placeholder="Enter failed job ID">
    </div>
    
    <div class="form-group">
      <label>Upload Corrected Files:</label>
      <input
        @change="onFilesSelected"
        type="file"
        multiple
        ref="fileInput"
      >
      <ul v-if="selectedFiles.length">
        <li v-for="file in selectedFiles" :key="file.name">
          {{ file.name }} ({{ (file.size / 1024).toFixed(1) }} KB)
        </li>
      </ul>
    </div>
    
    <button @click="resumeConversion" :disabled="isLoading">
      {{ isLoading ? 'Resuming...' : 'Resume Conversion' }}
    </button>
    
    <div v-if="resumeStatus" :class="resumeStatus.type">
      {{ resumeStatus.message }}
      <div v-if="resumeStatus.newJobId">
        New Job ID: <code>{{ resumeStatus.newJobId }}</code>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      originalJobId: '',
      selectedFiles: [],
      isLoading: false,
      resumeStatus: null
    }
  },
  methods: {
    onFilesSelected(event) {
      this.selectedFiles = Array.from(event.target.files);
    },
    async resumeConversion() {
      if (!this.originalJobId || !this.selectedFiles.length) {
        this.resumeStatus = {
          type: 'error',
          message: 'Please provide a job ID and select files'
        };
        return;
      }
      
      this.isLoading = true;
      const formData = new FormData();
      
      for (const file of this.selectedFiles) {
        formData.append('files', file);
      }
      
      try {
        const response = await fetch(
          `/api/convert/resume/${this.originalJobId}`,
          {
            method: 'POST',
            body: formData
          }
        );
        
        const result = await response.json();
        
        if (result.success) {
          this.resumeStatus = {
            type: 'success',
            message: 'Resumption job started successfully!',
            newJobId: result.new_job_id
          };
          
          // Watch for completion
          if (window.socket && window.socket.connected) {
            window.socket.emit('watch_job', { job_id: result.new_job_id });
          }
        } else {
          this.resumeStatus = {
            type: 'error',
            message: `Failed to resume: ${result.error}`
          };
        }
      } catch (error) {
        this.resumeStatus = {
          type: 'error',
          message: `Error: ${error.message}`
        };
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>
```

---

## Best Practices

### For Developers

1. **Always Check Status Before Resuming**
   ```javascript
   // Get job status first
   const status = await fetch(`/api/convert/status/${jobId}`).then(r => r.json());
   
   // Only show resume option if failed
   if (status.status === 'error' || status.status === 'failed') {
     showResumeButton();
   }
   ```

2. **Preserve Original File Information**
   - Store the original job ID for reference
   - Track number of retry attempts
   - Consider limiting retries (e.g., max 3 attempts)

3. **Provide User Feedback**
   - Show that new job is processing
   - Maintain link to original job for reference
   - Show retry count to user

4. **Handle Rate Limiting**
   - Resumptions count toward rate limits
   - Implement backoff strategy for retries
   - Consider implementing automatic retry with exponential backoff

### For Users

1. **Review Original Parameters**
   - Parameters are automatically preserved
   - No need to reconfigure conversion settings
   - Focus on fixing the files themselves

2. **Fix the Root Cause**
   - Resumption repeats same conversion
   - If conversion logic failed, re-upload won't help
   - Read error message to understand failure

3. **Check Job History**
   - Use `/api/user/history` to see previous attempts
   - Look for `retry_of` and `retried_by` fields
   - Track successful vs failed conversions

---

## Integration with Other Features

### With User Authentication

Authenticated users can:
- Resume only their own failed jobs
- View retry history in `/api/user/history`
- Access via API keys with appropriate permissions

### With WebSocket Real-Time Updates

When resuming with WebSocket enabled:
- New job broadcasts `job_started` event
- Clients watching original job can be notified of retry
- Real-time progress updates for resumed job

### With Metrics Dashboard

Resumed job metrics:
- Counted separately in retry statistics
- Success rate reflects retry attempts
- Helps identify problematic conversion types

---

## Troubleshooting

### Problem: "Job not found"
**Cause:** Job ID doesn't exist or job was cleaned up
**Solution:** 
- Verify correct job ID from history
- Check that job hasn't expired (7-day retention)
- Use `/api/user/history` to find recent failed jobs

### Problem: "Job status is 'processing', not failed"
**Cause:** Job is still running, can't resume in-progress jobs
**Solution:**
- Wait for job to complete
- Use `/api/convert/status/{job_id}` to check status
- Check server logs for slow conversions

### Problem: "Rate limit exceeded"
**Cause:** Too many conversion attempts in short time
**Solution:**
- Wait 1 minute and retry
- Current limit: 5 conversions per minute per IP
- Authenticated users may have higher limits

### Problem: New job not starting
**Cause:** Files too large, server busy, or temporary directory issue
**Solution:**
- Reduce file size (max 100MB total)
- Check file format compatibility
- Check server disk space
- Review server logs for errors

---

## Future Enhancements

Potential improvements to Job Resumption:

1. **Automatic Retry on Failure**
   - Automatically retry failed conversions
   - Configurable retry policy (max attempts, backoff)
   - Notify user of automatic retry

2. **Partial Resumption**
   - Retry only specific files from large batch
   - Resume from specific point in process
   - Resume with modified parameters

3. **Batch Resumption**
   - Resume multiple failed jobs at once
   - Parallel processing of retries
   - Batch status dashboard

4. **Intelligent Retry Logic**
   - Detect type of failure
   - Suggest fixes (file format, size, etc.)
   - Recommend alternative tools

5. **Retry Analytics**
   - Track which conversions fail most
   - Identify problematic file types
   - Suggest improvements

---

## API Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 202 | Resumption accepted | Job queued successfully |
| 400 | Bad request | Invalid job ID, no files, or job not failed |
| 404 | Not found | Original job doesn't exist |
| 413 | Payload too large | Files exceed size limit |
| 429 | Too many requests | Rate limit exceeded |
| 500 | Server error | Unexpected server error |

---

**Last Updated:** February 24, 2026  
**Version:** 1.0 (Initial Release)
