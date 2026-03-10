# WebSocket Real-Time Updates - Implementation Guide

## Overview
WebSocket connections replace HTTP polling for real-time job status updates. Using Socket.io, clients get instant notifications when jobs progress, complete, or error.

**Benefits:**
- ✅ Instant updates (no polling delays)
- ✅ Reduced bandwidth (single connection vs repeated HTTP requests)
- ✅ Lower server load (no polling overhead)
- ✅ Better battery life on mobile (fewer requests)
- ✅ Bidirectional communication

---

## Server Events

The server broadcasts these events to clients watching a job:

### `job_started`
Emitted when a conversion job begins.

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_name": "To PDF",
  "file_count": 3,
  "status": "processing",
  "progress": 0,
  "timestamp": "2026-02-24T15:30:00"
}
```

### `job_progress`
Emitted periodically during conversion (if job supports progress updates).

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 45,
  "message": "Processing file 2 of 3"
}
```

### `job_completed`
Emitted when conversion finishes successfully.

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "complete",
  "progress": 100,
  "files_created": 3,
  "result": [
    {
      "name": "document1.pdf",
      "size": 524288,
      "path": "/uploads/abc123.pdf"
    }
  ],
  "timestamp": "2026-02-24T15:35:00"
}
```

### `job_error`
Emitted if conversion fails.

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "error",
  "error": "File format not supported",
  "timestamp": "2026-02-24T15:35:00"
}
```

---

## Client Implementation (Vanilla JavaScript)

### Basic Setup

```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<script>
  // Connect to WebSocket server
  const socket = io('http://localhost:5000', {
    transports: ['websocket', 'polling']  // Fallback to polling if WebSocket unavailable
  });
  
  // Listen for connection
  socket.on('connect', () => {
    console.log('Connected to real-time updates');
  });
  
  // Listen for disconnection
  socket.on('disconnect', () => {
    console.log('Disconnected from real-time updates');
  });
</script>
```

### Watch a Job

```javascript
function watchJob(jobId) {
  // Join the job's WebSocket room
  socket.emit('watch_job', { job_id: jobId });
  
  // Listen for job start
  socket.on('job_started', (data) => {
    console.log(`Job ${data.job_id} started:`, data);
    updateUI({ status: 'processing', progress: 0 });
  });
  
  // Listen for progress updates
  socket.on('job_progress', (data) => {
    console.log(`Job ${data.job_id} progress: ${data.progress}%`);
    updateProgressBar(data.progress);
  });
  
  // Listen for completion
  socket.on('job_completed', (data) => {
    console.log(`Job ${data.job_id} complete!`, data);
    updateUI({ 
      status: 'complete', 
      progress: 100,
      files: data.result 
    });
    displayDownloadLinks(data.result);
  });
  
  // Listen for errors
  socket.on('job_error', (data) => {
    console.error(`Job ${data.job_id} failed:`, data.error);
    updateUI({ status: 'error', error_message: data.error });
  });
}

// Stop watching a job
function unwatchJob(jobId) {
  socket.emit('unwatch_job', { job_id: jobId });
}
```

### Complete Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>File Converter - WebSocket Real-Time</title>
  <style>
    .job-container { margin: 20px; padding: 20px; border: 1px solid #ddd; }
    .progress-bar { width: 100%; height: 30px; background: #f0f0f0; border: 1px solid #ccc; }
    .progress-fill { height: 100%; background: #4CAF50; transition: width 0.3s; }
    .status-badge { padding: 10px; border-radius: 5px; font-weight: bold; }
    .status-processing { background: #fff3cd; }
    .status-complete { background: #d4edda; }
    .status-error { background: #f8d7da; }
  </style>
</head>
<body>
  <h1>File Converter</h1>
  
  <form id="uploadForm">
    <input type="file" id="fileInput" multiple required>
    <select id="toolSelect">
      <option value="To PDF">Convert to PDF</option>
      <option value="To Image">Convert to Image</option>
      <option value="Extract Text">Extract Text</option>
    </select>
    <button type="submit">Start Conversion</button>
  </form>
  
  <div id="jobContainer"></div>
  
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <script>
    const socket = io('http://localhost:5000');
    
    // Form submission
    document.getElementById('uploadForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData();
      const files = document.getElementById('fileInput').files;
      
      for (let file of files) {
        formData.append('files', file);
      }
      
      formData.append('tool_name', document.getElementById('toolSelect').value);
      
      // Get auth token if available
      const token = localStorage.getItem('token');
      if (token) {
        // Would need CORS/custom handling for auth header with file upload
      }
      
      try {
        // Start conversion
        const response = await fetch('/api/convert/start', {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
          const jobId = data.job_id;
          
          // Create UI for this job
          createJobUI(jobId);
          
          // Watch this job for updates
          watchJob(jobId);
        } else {
          alert('Error: ' + data.error);
        }
      } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to start conversion');
      }
    });
    
    // Create UI for job
    function createJobUI(jobId) {
      const container = document.getElementById('jobContainer');
      const jobDiv = document.createElement('div');
      jobDiv.id = `job_${jobId}`;
      jobDiv.className = 'job-container';
      jobDiv.innerHTML = `
        <h3>Job ${jobId.substring(0, 8)}...</h3>
        <div class="status-badge" id="status_${jobId}">Preparing...</div>
        <div class="progress-bar">
          <div class="progress-fill" id="progress_${jobId}" style="width: 0%"></div>
        </div>
        <div id="message_${jobId}"></div>
        <button onclick="unwatchJob('${jobId}')">Cancel</button>
      `;
      container.appendChild(jobDiv);
    }
    
    // Watch job
    function watchJob(jobId) {
      socket.emit('watch_job', { job_id: jobId });
      
      socket.on('job_started', (data) => {
        if (data.job_id === jobId) {
          updateJobStatus(jobId, 'processing', `${data.file_count} files`);
        }
      });
      
      socket.on('job_progress', (data) => {
        if (data.job_id === jobId) {
          document.getElementById(`progress_${jobId}`).style.width = data.progress + '%';
          document.getElementById(`message_${jobId}`).innerText = data.message || '';
        }
      });
      
      socket.on('job_completed', (data) => {
        if (data.job_id === jobId) {
          updateJobStatus(jobId, 'complete', `✅ ${data.files_created} files ready`);
          
          // Create download links
          const messageDiv = document.getElementById(`message_${jobId}`);
          messageDiv.innerHTML = '<h4>Download:</h4>' + 
            data.result.map(f => 
              `<a href="${f.path}" download="${f.name}">${f.name}</a><br>`
            ).join('');
        }
      });
      
      socket.on('job_error', (data) => {
        if (data.job_id === jobId) {
          updateJobStatus(jobId, 'error', `❌ ${data.error}`);
        }
      });
    }
    
    // Unwatch job
    function unwatchJob(jobId) {
      socket.emit('unwatch_job', { job_id: jobId });
      const jobDiv = document.getElementById(`job_${jobId}`);
      if (jobDiv) jobDiv.remove();
    }
    
    // Update job status display
    function updateJobStatus(jobId, status, message) {
      const badge = document.getElementById(`status_${jobId}`);
      if (badge) {
        badge.className = `status-badge status-${status}`;
        badge.innerText = message;
      }
    }
  </script>
</body>
</html>
```

---

## Vue.js Implementation

```vue
<template>
  <div>
    <h1>File Converter (Vue + WebSocket)</h1>
    
    <form @submit.prevent="startConversion">
      <input type="file" v-model="files" multiple required>
      <select v-model="toolName">
        <option>To PDF</option>
        <option>To Image</option>
      </select>
      <button type="submit">Convert</button>
    </form>
    
    <div v-for="job in jobs" :key="job.id" class="job-card">
      <h3>{{ job.id.substring(0, 8) }}...</h3>
      <div :class="['status', job.status]">{{ job.status }}</div>
      <div class="progress">
        <div class="progress-bar" :style="{ width: job.progress + '%' }"></div>
      </div>
      
      <div v-if="job.status === 'complete'" class="downloads">
        <a v-for="file in job.result" :key="file.name" :href="file.path" download>
          {{ file.name }}
        </a>
      </div>
      <div v-if="job.error" class="error">{{ job.error }}</div>
    </div>
  </div>
</template>

<script>
import io from 'socket.io-client';

export default {
  data() {
    return {
      socket: null,
      files: null,
      toolName: 'To PDF',
      jobs: []
    };
  },
  
  mounted() {
    this.socket = io('http://localhost:5000');
    this.socket.on('connect', () => console.log('WebSocket connected'));
  },
  
  methods: {
    async startConversion() {
      const formData = new FormData();
      
      for (let file of this.files) {
        formData.append('files', file);
      }
      formData.append('tool_name', this.toolName);
      
      const response = await fetch('/api/convert/start', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.success) {
        const jobId = data.job_id;
        
        // Add to jobs list
        this.jobs.push({
          id: jobId,
          status: 'processing',
          progress: 0,
          result: [],
          error: null
        });
        
        // Watch this job
        this.watchJob(jobId);
      }
    },
    
    watchJob(jobId) {
      this.socket.emit('watch_job', { job_id: jobId });
      
      const onJobStarted = (data) => {
        if (data.job_id === jobId) {
          const job = this.jobs.find(j => j.id === jobId);
          if (job) job.status = 'processing';
        }
      };
      
      const onJobCompleted = (data) => {
        if (data.job_id === jobId) {
          const job = this.jobs.find(j => j.id === jobId);
          if (job) {
            job.status = 'complete';
            job.progress = 100;
            job.result = data.result;
          }
        }
      };
      
      const onJobError = (data) => {
        if (data.job_id === jobId) {
          const job = this.jobs.find(j => j.id === jobId);
          if (job) {
            job.status = 'error';
            job.error = data.error;
          }
        }
      };
      
      this.socket.on('job_started', onJobStarted);
      this.socket.on('job_completed', onJobCompleted);
      this.socket.on('job_error', onJobError);
    }
  },
  
  beforeUnmount() {
    if (this.socket) this.socket.disconnect();
  }
};
</script>
```

---

## React Implementation

```jsx
import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

function FileConverter() {
  const [socket, setSocket] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [files, setFiles] = useState(null);
  const [toolName, setToolName] = useState('To PDF');
  
  // Initialize WebSocket
  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);
    
    return () => newSocket.disconnect();
  }, []);
  
  const startConversion = async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    for (let file of files) {
      formData.append('files', file);
    }
    formData.append('tool_name', toolName);
    
    const response = await fetch('/api/convert/start', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (data.success) {
      const jobId = data.job_id;
      
      // Add to jobs
      setJobs(prev => [...prev, {
        id: jobId,
        status: 'processing',
        progress: 0,
        result: [],
        error: null
      }]);
      
      // Watch job
      watchJob(jobId);
    }
  };
  
  const watchJob = (jobId) => {
    if (!socket) return;
    
    socket.emit('watch_job', { job_id: jobId });
    
    const handleJobStarted = (data) => {
      if (data.job_id === jobId) {
        setJobs(prev => prev.map(j =>
          j.id === jobId ? { ...j, status: 'processing' } : j
        ));
      }
    };
    
    const handleJobCompleted = (data) => {
      if (data.job_id === jobId) {
        setJobs(prev => prev.map(j =>
          j.id === jobId ? {
            ...j,
            status: 'complete',
            progress: 100,
            result: data.result
          } : j
        ));
      }
    };
    
    const handleJobError = (data) => {
      if (data.job_id === jobId) {
        setJobs(prev => prev.map(j =>
          j.id === jobId ? {
            ...j,
            status: 'error',
            error: data.error
          } : j
        ));
      }
    };
    
    socket.on('job_started', handleJobStarted);
    socket.on('job_completed', handleJobCompleted);
    socket.on('job_error', handleJobError);
  };
  
  return (
    <div>
      <h1>File Converter (React + WebSocket)</h1>
      
      <form onSubmit={startConversion}>
        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
          required
        />
        <select value={toolName} onChange={(e) => setToolName(e.target.value)}>
          <option>To PDF</option>
          <option>To Image</option>
        </select>
        <button type="submit">Convert</button>
      </form>
      
      {jobs.map(job => (
        <div key={job.id} className={`job-card status-${job.status}`}>
          <h3>{job.id.substring(0, 8)}...</h3>
          <div className="status">{job.status}</div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: job.progress + '%' }}
            ></div>
          </div>
          
          {job.status === 'complete' && (
            <div className="downloads">
              {job.result.map(file => (
                <a key={file.name} href={file.path} download>
                  {file.name}
                </a>
              ))}
            </div>
          )}
          {job.error && <div className="error">{job.error}</div>}
        </div>
      ))}
    </div>
  );
}

export default FileConverter;
```

---

## Best Practices

✅ **DO:**
- Reconnect silently when WebSocket drops
- Provide polling fallback for unsupported networks
- Clean up event listeners when unwatching
- Add exponential backoff for reconnection
- Use rooms for job-specific updates

❌ **DON'T:**
- Leave event listeners active after job completes
- Send frequent updates (throttle to 1per second max)
- Rely entirely on WebSocket (always have HTTP fallback)
- Store auth tokens in local storage (use secure cookies)
- Broadcast sensitive data without auth check

---

## Troubleshooting

**WebSocket not connecting?**
- Check CORS settings (should be `*` or specific hostname)
- Verify WebSocket port is not blocked
- Check browser console for errors
- Fallback to polling works but slower

**Missing updates?**
- Ensure job_id matches exactly
- Check that watch_job event was sent
- Verify server logs for emit errors
- Try refresh connection

**High bandwidth?**
- Progress events might be too frequent
- Use throttling/debouncing on client
- Filter unnecessary events

---

Last Updated: February 24, 2026
