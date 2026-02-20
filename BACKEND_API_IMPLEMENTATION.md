# Backend API Implementation Guide - Dashboard Endpoints

## Overview

The enhanced dashboard requires several API endpoints to function. This guide details what needs to be implemented or modified in the backend.

## Required Endpoints Summary

| Endpoint | Method | Priority | Status | Location |
|----------|--------|----------|--------|----------|
| `/api/analytics/summary` | GET | Critical | Check | analytics.py |
| `/api/files/list` | GET | High | Implement | files.py |
| `/api/files/{id}/download` | GET | High | Implement | files.py |
| `/api/files/{id}` | DELETE | High | Implement | files.py |
| `/api/jobs/queue` | GET | High | Implement | queue.py |
| `/api/users/list` | GET | Medium | Extend | users.py |
| `/api/users/{id}` | DELETE | Medium | Extend | users.py |

## 1. Analytics Endpoint (CRITICAL)

### Current Status
Check if `/api/analytics/summary` exists in your codebase. The dashboard expects this endpoint to return comprehensive analytics data.

### Required Response Format

```python
@analytics_bp.route('/api/analytics/summary', methods=['GET'])
@require_auth
def get_analytics_summary():
    """Get comprehensive analytics summary."""
    try:
        # Get user ID from auth
        user_id = session.get('user_id')
        
        # Query database for metrics
        conversions = Conversion.query.filter_by(user_id=user_id).all()
        
        # Calculate metrics
        total_files = len(conversions)
        total_operations = sum(c.operation_count for c in conversions)
        successful = sum(1 for c in conversions if c.status == 'success')
        success_rate = (successful / total_operations * 100) if total_operations > 0 else 0
        total_data_mb = sum(c.file_size / (1024*1024) for c in conversions)
        
        # Get processing times
        processing_times = [c.processing_time for c in conversions if c.processing_time]
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Get last 7 days operations
        from datetime import datetime, timedelta
        daily_data = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date()
            count = len([c for c in conversions if c.created_at.date() == date])
            daily_data[date.isoformat()] = count
        
        daily_operations = [daily_data.get((datetime.now() - timedelta(days=i)).date().isoformat(), 0) 
                           for i in range(6, -1, -1)]
        
        # Get operation distribution
        distribution = {}
        for conv in conversions:
            op_type = conv.file_type or 'Unknown'
            distribution[op_type] = distribution.get(op_type, 0) + 1
        
        return jsonify({
            'total_files': total_files,
            'total_operations': total_operations,
            'success_rate': round(success_rate, 2),
            'total_data_mb': round(total_data_mb, 2),
            'avg_processing_time': round(avg_time * 1000),  # Convert to ms
            'peak_operations_per_hour': 45,  # TODO: Calculate from actual data
            'api_requests': total_operations * 2,  # Estimated requests
            'daily_operations': daily_operations,
            'operation_distribution': distribution
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Expected Response

```json
{
  "total_files": 42,
  "total_operations": 156,
  "success_rate": 98.5,
  "total_data_mb": 2048.5,
  "avg_processing_time": 2340,
  "peak_operations_per_hour": 45,
  "api_requests": 540,
  "daily_operations": [15, 22, 18, 25, 20, 30, 26],
  "operation_distribution": {
    "PDF": 45,
    "Excel": 38,
    "Image": 42,
    "Word": 25,
    "Archive": 6
  }
}
```

---

## 2. Files Endpoints (HIGH PRIORITY)

These endpoints are required for the File Browser tab to function.

### File List Endpoint

```python
@files_bp.route('/api/files/list', methods=['GET'])
@require_auth
def list_files():
    """Get list of uploaded files."""
    try:
        user_id = session.get('user_id')
        
        # Query uploaded files from database or storage
        files = []
        
        # Option A: Database-backed
        uploads = Upload.query.filter_by(user_id=user_id).all()
        for upload in uploads:
            files.append({
                'id': upload.id,
                'name': upload.filename,
                'size': upload.file_size,
                'created_at': upload.created_at.isoformat()
            })
        
        # Option B: File system-backed
        upload_dir = f'uploads/{user_id}'
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                filepath = os.path.join(upload_dir, filename)
                if os.path.isfile(filepath):
                    files.append({
                        'id': filename,
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'created_at': datetime.fromtimestamp(
                            os.path.getctime(filepath)
                        ).isoformat()
                    })
        
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### File Download Endpoint

```python
@files_bp.route('/api/files/<file_id>/download', methods=['GET'])
@require_auth
def download_file(file_id):
    """Download specific file."""
    try:
        user_id = session.get('user_id')
        
        # Option A: Database-backed
        upload = Upload.query.filter_by(
            id=file_id, 
            user_id=user_id
        ).first()
        
        if not upload:
            return jsonify({'error': 'File not found'}), 404
        
        # Get file path
        file_path = upload.file_path
        
        # Option B: File system lookup
        file_path = f'uploads/{user_id}/{file_id}'
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=upload.filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### File Delete Endpoint

```python
@files_bp.route('/api/files/<file_id>', methods=['DELETE'])
@require_auth
def delete_file(file_id):
    """Delete specific file."""
    try:
        user_id = session.get('user_id')
        
        # Option A: Database-backed deletion
        upload = Upload.query.filter_by(
            id=file_id,
            user_id=user_id
        ).first()
        
        if not upload:
            return jsonify({'error': 'File not found'}), 404
        
        # Delete from storage
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
        
        # Delete from database
        db.session.delete(upload)
        db.session.commit()
        
        # Option B: File system-only deletion
        file_path = f'uploads/{user_id}/{file_id}'
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

### Required File Model

If using database backing, ensure your `Upload` or `File` model includes:

```python
class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # In bytes
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50))  # pdf, xlsx, png, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('uploads', lazy=True))
```

---

## 3. Operation Queue Endpoint (HIGH PRIORITY)

Required for the Operation Queue tab to function.

```python
@queue_bp.route('/api/jobs/queue', methods=['GET'])
@require_auth
def get_queue():
    """Get current operation queue status."""
    try:
        user_id = session.get('user_id')
        
        # Query pending/active jobs
        jobs = ConversionJob.query.filter_by(
            user_id=user_id,
            status__in=['pending', 'processing']
        ).all()
        
        # Also include recent completed jobs (last 10)
        recent = ConversionJob.query.filter_by(
            user_id=user_id,
            status__in=['completed', 'failed']
        ).order_by(ConversionJob.created_at.desc()).limit(10).all()
        
        jobs.extend(recent)
        
        queue_data = []
        for job in jobs:
            queue_data.append({
                'id': job.id,
                'operation': job.operation_type,  # e.g., "PDF to Excel"
                'status': job.status,  # pending, processing, completed, failed
                'progress': job.progress or 0,  # 0-100
                'created_at': job.created_at.isoformat(),
                'completed_at': job.completed_at.isoformat() if job.completed_at else None
            })
        
        return jsonify({'jobs': queue_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Required Job Model

```python
class ConversionJob(db.Model):
    __tablename__ = 'conversion_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    operation_type = db.Column(db.String(100), nullable=False)  # "PDF to Excel", etc.
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    input_file_id = db.Column(db.String(36), db.ForeignKey('uploads.id'))
    output_file_id = db.Column(db.String(36), db.ForeignKey('uploads.id'))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('jobs', lazy=True))
```

---

## 4. User Management Endpoints (MEDIUM PRIORITY)

These are for the admin User Management tab.

### User List Endpoint (Admin Only)

```python
@users_bp.route('/api/users/list', methods=['GET'])
@require_auth
@require_admin
def list_users():
    """Get list of all users (admin only)."""
    try:
        # Get all users
        users = User.query.all()
        
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'role': user.role or 'user',
                'status': user.status or 'active'
            })
        
        return jsonify({'users': user_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### User Delete Endpoint (Admin Only)

```python
@users_bp.route('/api/users/<user_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_user(user_id):
    """Delete user account (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting self
        if user.id == session.get('user_id'):
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Delete user and associated data
        # This cascades to uploads, jobs, etc. if configured
        db.session.delete(user)
        db.session.commit()
        
        # Optional: Clean up file storage
        user_dir = f'uploads/{user_id}'
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

### Admin Check Decorator

```python
def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Forbidden'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
```

---

## 5. Routes Registration

### Directory Structure

```
app/api/routes/
├── __init__.py
├── analytics.py      (check if exists)
├── files.py          (create)
├── queue.py          (create)
├── users.py          (extend)
└── uploads.py        (may exist)
```

### Create Missing Route Files

#### app/api/routes/files.py

```python
from flask import Blueprint, jsonify, request, send_file, session
from flask_cors import cross_origin
from app.services.file_cleanup import cleanup_old_files
from app.utils.file_validator import validate_file
import os
import uuid
from datetime import datetime

files_bp = Blueprint('files', __name__)

@files_bp.before_request
def require_auth():
    """Require authentication for all routes."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

@files_bp.route('/api/files/list', methods=['GET'])
@cross_origin()
def list_files():
    """List user's uploaded files."""
    # Implementation from above
    pass

@files_bp.route('/api/files/<file_id>/download', methods=['GET'])
@cross_origin()
def download_file(file_id):
    """Download specific file."""
    # Implementation from above
    pass

@files_bp.route('/api/files/<file_id>', methods=['DELETE'])
@cross_origin()
def delete_file(file_id):
    """Delete specific file."""
    # Implementation from above
    pass
```

#### app/api/routes/queue.py

```python
from flask import Blueprint, jsonify, session
from flask_cors import cross_origin

queue_bp = Blueprint('queue', __name__)

@queue_bp.before_request
def require_auth():
    """Require authentication for all routes."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

@queue_bp.route('/api/jobs/queue', methods=['GET'])
@cross_origin()
def get_queue():
    """Get operation queue."""
    # Implementation from above
    pass
```

### Register in app/main.py

```python
from app.api.routes.files import files_bp
from app.api.routes.queue import queue_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(files_bp)
    app.register_blueprint(queue_bp)
    # ... other blueprints
    
    return app
```

---

## 6. Database Models

Ensure your models include these fields. Add to `app/config.py` or model files:

```python
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    api_key = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ConversionJob(db.Model):
    __tablename__ = 'conversion_jobs'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    operation_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    progress = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


class Conversion(db.Model):
    __tablename__ = 'conversions'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    input_file = db.Column(db.String(255))
    output_file = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    operation_count = db.Column(db.Integer, default=1)
    processing_time = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 7. Testing Endpoints

### Using curl

```bash
# Test Analytics
curl -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/analytics/summary

# Test Files List
curl -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/files/list

# Test File Download
curl -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/files/file_id/download \
  -o downloaded_file

# Test File Delete
curl -X DELETE \
  -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/files/file_id

# Test Queue
curl -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/jobs/queue

# Test Users List (admin)
curl -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/users/list

# Test User Delete (admin)
curl -X DELETE \
  -H "X-API-Key: your_api_key" \
  http://localhost:5000/api/users/user_id
```

### Using Python

```python
import requests

headers = {
    'X-API-Key': 'your_api_key'
}

# Test analytics
response = requests.get(
    'http://localhost:5000/api/analytics/summary',
    headers=headers
)
print(response.json())

# Test files
response = requests.get(
    'http://localhost:5000/api/files/list',
    headers=headers
)
print(response.json())

# Test queue
response = requests.get(
    'http://localhost:5000/api/jobs/queue',
    headers=headers
)
print(response.json())
```

---

## 8. Implementation Checklist

### Phase 1: Critical (Do First)
- [ ] Verify `/api/analytics/summary` exists and returns correct format
- [ ] Fix analytics endpoint response format if needed
- [ ] Test analytics endpoint in dashboard

### Phase 2: File Management
- [ ] Create `app/api/routes/files.py`
- [ ] Implement `/api/files/list`
- [ ] Implement `/api/files/{id}/download`
- [ ] Implement `/api/files/{id}` DELETE
- [ ] Test all file endpoints

### Phase 3: Queue Management
- [ ] Create `app/api/routes/queue.py`
- [ ] Implement `/api/jobs/queue`
- [ ] Ensure database tracks job status
- [ ] Test queue endpoint

### Phase 4: User Management
- [ ] Extend existing users routes
- [ ] Implement `/api/users/list` with admin check
- [ ] Implement `/api/users/{id}` DELETE with admin check
- [ ] Test user endpoints

### Phase 5: Integration
- [ ] Register all blueprints in `main.py`
- [ ] Test dashboard with real data
- [ ] Verify permissions and auth
- [ ] Check CORS configuration

---

## 9. Common Issues & Solutions

### Issue: CORS Errors
**Solution**: Add `@cross_origin()` decorator to routes
```python
from flask_cors import cross_origin

@files_bp.route('/api/files/list', methods=['GET'])
@cross_origin()
def list_files():
    pass
```

### Issue: Files Not Downloading
**Solution**: Check `send_file()` parameters
```python
return send_file(
    file_path,
    as_attachment=True,
    download_name=original_filename
)
```

### Issue: Auth Failures
**Solution**: Verify session and API key checks
```python
user_id = session.get('user_id')
if not user_id:
    return jsonify({'error': 'Unauthorized'}), 401
```

### Issue: Database Errors
**Solution**: Ensure models are registered and migrations run
```bash
flask db upgrade
```

---

**Last Updated:** February 16, 2026
**Status:** Ready for Implementation
**Estimated Time:** 2-4 hours for full implementation
