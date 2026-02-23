# Async Conversion Testing Guide

## What Was Implemented

### Backend Changes (server.py)
1. ✅ **Job Tracking System**
   - `ConversionJob` class to track conversion state
   - `_job_registry` dictionary stores all active/completed jobs
   - Thread-safe updates with `_job_lock`

2. ✅ **Rate Limiting**
   - `_check_rate_limit(ip_address)` - Max 5 conversions per minute per IP
   - Returns 429 (Too Many Requests) when exceeded

3. ✅ **File Size Validation**
   - Server-side: Max 100MB total file size
   - Client-side: Checks before sending, warns if >50MB
   - Returns 413 (Payload Too Large) if exceeded

4. ✅ **New Async Endpoints**
   - `POST /api/convert/start` - Start job, returns job_id immediately (HTTP 202)
   - `GET /api/convert/status/<job_id>` - Check job progress anytime
   - `_process_conversion_job()` - Background worker runs in separate thread

### Frontend Changes (templates/Index.html)
1. ✅ **Client-Side File Size Check**
   - Validation before upload (100MB max)
   - Warning if file > 50MB

2. ✅ **Async Job Flow**
   - Start job via `/api/convert/start` → Get job_id
   - Poll `/api/convert/status/{job_id}` every 1 second
   - Update progress bar in real-time
   - Show results when complete

3. ✅ **Progress Bar UI**
   - Visual progress indicator (0-100%)
   - Shows status messages
   - Disappears when conversion ends
   - Hides/shows based on conversion state

4. ✅ **Error Handling**
   - Rate limit errors (429)
   - File size errors (413)
   - Conversion timeout (30 minutes max)
   - Detailed error messages shown to user

---

## How to Test

### Test 1: Basic Async Conversion
```
1. Open http://localhost:5000
2. Click "To PDF" tool
3. Upload a small PDF or image file
4. Click "start conversion"
   → Status: Shows progress bar starting
   → Poll loop begins checking job status every 1 second
   → Progress updates in real-time
   → When complete: Downloads appear automatically
5. Check browser DevTools Console
   → Should see: "[Conversion] Job started: <job_id>"
   → Should see: "[Job <id>] Status: processing Progress: X%"
   → Should see: "[Job <id>] Status: complete ..."
```

**Expected Result**: File converts with real-time progress shown

### Test 2: Rate Limiting
```
1. Start 6 conversions in quick succession (within 60 seconds)
   → Conversions 1-5: Should succeed
   → Conversion 6: Should show error message
      "Rate limit exceeded. Maximum 5 conversions per minute."
   → HTTP Status: 429
2. Wait 60 seconds
3. Try conversion 6 again
   → Should succeed now (limit window expired)
```

**Expected Result**: 6th attempt blocked with 429 error, works after 60s

### Test 3: Large File Validation
```
1. Try to upload file >100MB
   → Client-side: Shows error before sending
      "Total file size exceeds 100MB"
   → File is NOT sent to server
2. Try file between 50-100MB
   → Client-side: Shows warning
      "Warning: Large files may take longer to convert"
   → File IS sent to server
   → Should convert successfully
```

**Expected Result**: Prevents uploads >100MB, warns on 50-100MB

### Test 4: Job Status Polling
```
1. Start a conversion
2. While converting, check browser DevTools Network tab
   → Should see multiple `/api/convert/status/<job_id>` requests
   → Requests happen every ~1 second
   → Each returns current progress (0-100%)
3. When complete
   → Last status request returns files array
   → Polling stops
   → Downloads appear
```

**Expected Result**: Continuous status polling with progress updates

### Test 5: Timeout Handling
```
1. If conversion takes >30 minutes
   → Polling loop hits max attempts (1800)
   → Shows error: "Conversion timeout: Job took too long"
   → Button re-enabled for next attempt
```

**Expected Result**: Conversion times out gracefully after 30 min

---

## Key Metrics to Monitor

### Response Times
- `POST /api/convert/start`: Should return <100ms (just queues job)
- `GET /api/convert/status/<job_id>`: Should return <50ms (instant lookup)
- Actual conversion: Depends on file size (polling shows progress)

### Network Efficiency
- Initial request: 1x POST to `/api/convert/start`
- Polling: 1x GET per second until complete
- Example: 10 second conversion = ~10 status requests = ~500 bytes total polling overhead

### Load Distribution
- Main thread: Handles HTTP requests, status lookups
- Worker thread: Handles actual conversion work
- Result: UI stays responsive, conversion happens in background

---

## API Response Examples

### Start Conversion (Success)
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Conversion job started. Job ID: 550e8400..."
}
```
**Status**: 202 Accepted

### Check Status (Processing)
```json
{
  "success": true,
  "status": "processing",
  "progress": 45,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_name": "To PDF",
  "file_count": 1,
  "has_result": false,
  "error": null,
  "elapsed_seconds": 2.5
}
```

### Check Status (Complete)
```json
{
  "success": true,
  "status": "complete",
  "progress": 100,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_name": "To PDF",
  "file_count": 1,
  "has_result": true,
  "error": null,
  "elapsed_seconds": 8.2,
  "files": [
    {
      "name": "document.pdf",
      "size": 45280,
      "download_url": "/api/download/abc123..."
    }
  ]
}
```

### Rate Limit Error
```json
{
  "success": false,
  "error": "Rate limit exceeded. Maximum 5 conversions per minute."
}
```
**Status**: 429 Too Many Requests

### File Size Error
```json
{
  "success": false,
  "error": "Total file size exceeds 100MB limit"
}
```
**Status**: 413 Payload Too Large

---

## Implementation Details

### Thread Safety
```python
_job_lock = Lock()  # Prevents race conditions

# All job registry updates are protected:
with _job_lock:
    _job_registry[job_id] = job  # Safe
    job.progress = 50             # Safe
    job.status = 'complete'       # Safe
```

### Job Lifecycle
```
1. User clicks "start conversion"
2. POST /api/convert/start
   ├─ Validate files
   ├─ Check rate limit
   ├─ Create ConversionJob(status='queued')
   ├─ Start background worker thread
   └─ Return job_id (HTTP 202)

3. Frontend polls GET /api/convert/status/{job_id}
   ├─ Every 1 second
   ├─ Backend returns current progress
   └─ Updates progress bar UI

4. Background worker processes files
   ├─ Updates job.progress (0-100)
   ├─ Updates job.status → 'processing'
   ├─ Runs conversion
   ├─ Stores results in job.result
   └─ Updates job.status → 'complete' or 'error'

5. Frontend detects completion
   ├─ Stops polling loop
   ├─ Shows download links
   └─ Re-enables button
```

### Rate Limiting Logic
```python
# Tracks timestamps of requests per IP
_conversion_rate_limit = {
    '192.168.1.100': [t1, t2, t3, t4, t5],  # 5 requests
    # ... more IPs
}

# On new request:
# 1. Remove timestamps older than 60 seconds
# 2. If 5+ requests in last 60 seconds → BLOCKED
# 3. If <5 requests → ALLOWED (add new timestamp)
```

---

## Backward Compatibility

### Old Endpoint Still Works
- `/api/convert` (POST) - Still available for synchronous conversion
- Returns immediately with converted files (if file is small/fast)
- Should NOT be used for large files or slow conversions

### Reasons to Use New Async API
- ✅ Better for large files (no timeout)
- ✅ Real-time progress feedback
- ✅ Rate limiting protection
- ✅ File size validation
- ✅ Non-blocking UI
- ✅ Network interruption tolerance

---

## Next Steps / Future Improvements

1. **WebSockets** (Optional)
   - Replace polling with server-sent events
   - Reduces network traffic
   - Real-time updates without client polling

2. **Resume Failed Jobs**
   - Store job history in database
   - Allow re-running failed conversions
   - Persist across server restarts

3. **User Accounts** (If needed)
   - Track conversions per user
   - Per-user rate limiting
   - Conversion history/dashboard

4. **Job Cleanup**
   - Remove old jobs from memory
   - Implement job expiration
   - Archive completed jobs to database

---

## Troubleshooting

### Issue: Progress bar not updating
- **Check**: Did polling loop start? (DevTools Network tab)
- **Fix**: Verify `/api/convert/status/<job_id>` endpoint exists

### Issue: Conversion never completes
- **Check**: Does server.log show conversion errors?
- **Fix**: Check if `execute_service_conversion()` is working

### Issue: Rate limiting too strict
- **Edit**: `_rate_limit_max_requests = 5` (adjust number)
- **Edit**: `_rate_limit_window = 60` (adjust seconds)

### Issue: Files being deleted before download
- **Note**: Files stored in `_converted_files_store` for 1 hour
- **Adjust**: `_FILES_EXPIRE_AFTER = 3600` (in seconds)

