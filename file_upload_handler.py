"""
Phase 15.2: File Upload Handler
Handles document uploads, chunked file transfers, progress tracking, and file validation
"""

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime
from pathlib import Path
import os
import hashlib
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# ========== CONFIGURATION ==========
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'json', 'xml',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
    'zip', 'rar', '7z'
}

# In-memory upload tracking (replace with database in production)
upload_sessions: Dict[str, Dict] = {}  # {session_id: upload_info}
file_chunks: Dict[str, Dict] = {}      # {upload_id: {chunks, total_chunks, etc.}}

# ========== UPLOAD MANAGER ==========
class UploadManager:
    """Handles file uploads with chunking and progress tracking"""
    
    def __init__(self, upload_folder=UPLOAD_FOLDER):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_hash(file_content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """Validate file before upload"""
        if not self.allowed_file(filename):
            return False, f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        if file_size > MAX_FILE_SIZE:
            return False, f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        
        return True, "Valid"
    
    def create_upload_session(self, filename: str, file_size: int, 
                             user_id: str, document_id: str) -> Dict:
        """Create a new upload session for chunked upload"""
        session_id = f"upload_{datetime.utcnow().timestamp()}_{user_id}"
        
        # Validate file
        valid, message = self.validate_file(filename, file_size)
        if not valid:
            return {'error': message}
        
        # Calculate required chunks
        chunk_size = 5 * 1024 * 1024  # 5MB per chunk
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        session = {
            'session_id': session_id,
            'filename': secure_filename(filename),
            'original_filename': filename,
            'file_size': file_size,
            'total_chunks': total_chunks,
            'chunk_size': chunk_size,
            'user_id': user_id,
            'document_id': document_id,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'  # pending, uploading, completed, failed
        }
        
        upload_sessions[session_id] = session
        file_chunks[session_id] = {
            'chunks': {},
            'received_chunks': 0,
            'total_chunks': total_chunks
        }
        
        logger.info(f"Upload session created: {session_id}")
        return session
    
    def upload_chunk(self, session_id: str, chunk_number: int, 
                     chunk_data: bytes) -> Tuple[bool, Dict]:
        """Receive and store a file chunk"""
        if session_id not in upload_sessions:
            return False, {'error': 'Invalid session'}
        
        if session_id not in file_chunks:
            return False, {'error': 'Session not found in chunks'}
        
        session = upload_sessions[session_id]
        chunks_info = file_chunks[session_id]
        
        # Validate chunk number
        if chunk_number < 0 or chunk_number >= chunks_info['total_chunks']:
            return False, {'error': 'Invalid chunk number'}
        
        # Store chunk in memory
        chunks_info['chunks'][chunk_number] = chunk_data
        chunks_info['received_chunks'] = len(chunks_info['chunks'])
        
        # Calculate progress
        progress = (chunks_info['received_chunks'] / chunks_info['total_chunks']) * 100
        
        logger.info(f"Chunk {chunk_number} received for {session_id} ({progress:.1f}%)")
        
        return True, {
            'session_id': session_id,
            'chunk': chunk_number,
            'received_chunks': chunks_info['received_chunks'],
            'total_chunks': chunks_info['total_chunks'],
            'progress': progress,
            'status': 'uploading'
        }
    
    def complete_upload(self, session_id: str) -> Tuple[bool, Dict]:
        """Assemble chunks and complete upload"""
        if session_id not in upload_sessions:
            return False, {'error': 'Invalid session'}
        
        session = upload_sessions[session_id]
        chunks_info = file_chunks[session_id]
        
        # Check all chunks received
        if chunks_info['received_chunks'] != chunks_info['total_chunks']:
            return False, {
                'error': f"Missing chunks. Received: {chunks_info['received_chunks']}, "
                         f"Expected: {chunks_info['total_chunks']}"
            }
        
        try:
            # Assemble file from chunks
            file_path = os.path.join(self.upload_folder, session['filename'])
            
            with open(file_path, 'wb') as f:
                for i in range(chunks_info['total_chunks']):
                    f.write(chunks_info['chunks'][i])
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = self.get_file_hash(f.read())
            
            # Update session
            session['status'] = 'completed'
            session['completed_at'] = datetime.utcnow().isoformat()
            session['file_hash'] = file_hash
            session['file_path'] = file_path
            
            logger.info(f"Upload completed: {session_id}")
            
            return True, {
                'session_id': session_id,
                'status': 'completed',
                'filename': session['original_filename'],
                'file_size': session['file_size'],
                'file_hash': file_hash,
                'timestamp': session['completed_at']
            }
        
        except Exception as e:
            session['status'] = 'failed'
            logger.error(f"Upload completion failed: {e}")
            return False, {'error': f'Upload failed: {str(e)}'}
    
    def get_upload_progress(self, session_id: str) -> Dict:
        """Get current upload progress"""
        if session_id not in upload_sessions:
            return {'error': 'Invalid session'}
        
        session = upload_sessions[session_id]
        chunks_info = file_chunks.get(session_id, {})
        
        progress = 0
        if chunks_info.get('total_chunks', 0) > 0:
            progress = (chunks_info.get('received_chunks', 0) / chunks_info['total_chunks']) * 100
        
        return {
            'session_id': session_id,
            'filename': session['original_filename'],
            'status': session['status'],
            'file_size': session['file_size'],
            'received_chunks': chunks_info.get('received_chunks', 0),
            'total_chunks': chunks_info.get('total_chunks', 0),
            'progress': progress,
            'created_at': session['created_at']
        }
    
    def cancel_upload(self, session_id: str) -> Tuple[bool, str]:
        """Cancel an upload session"""
        if session_id not in upload_sessions:
            return False, 'Invalid session'
        
        try:
            session = upload_sessions.pop(session_id)
            file_chunks.pop(session_id, None)
            
            # Delete partial file if exists
            if 'file_path' in session and os.path.exists(session['file_path']):
                os.remove(session['file_path'])
            
            logger.info(f"Upload cancelled: {session_id}")
            return True, 'Upload cancelled'
        
        except Exception as e:
            logger.error(f"Cancel failed: {e}")
            return False, str(e)


# ========== FLASK ROUTE HANDLERS ==========
def register_upload_routes(app):
    """Register file upload routes"""
    from flask import request, jsonify
    
    manager = UploadManager()
    
    @app.route('/api/upload/create-session', methods=['POST'])
    def create_upload_session_route():
        """Create new upload session"""
        try:
            data = request.get_json()
            filename = data.get('filename')
            file_size = data.get('file_size')
            user_id = data.get('user_id')
            document_id = data.get('document_id', '')
            
            if not all([filename, file_size, user_id]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            session = manager.create_upload_session(filename, file_size, user_id, document_id)
            
            if 'error' in session:
                return jsonify(session), 400
            
            return jsonify({
                'success': True,
                'data': session,
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200
        
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload/chunk', methods=['POST'])
    def upload_chunk_route():
        """Upload a file chunk"""
        try:
            session_id = request.form.get('session_id')
            chunk_number = int(request.form.get('chunk_number', 0))
            
            if 'chunk' not in request.files:
                return jsonify({'error': 'No chunk provided'}), 400
            
            chunk_file = request.files['chunk']
            chunk_data = chunk_file.read()
            
            success, result = manager.upload_chunk(session_id, chunk_number, chunk_data)
            
            if not success:
                return jsonify(result), 400
            
            return jsonify({
                'success': True,
                'data': result,
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200
        
        except Exception as e:
            logger.error(f"Chunk upload error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload/complete', methods=['POST'])
    def complete_upload_route():
        """Complete file upload"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            
            success, result = manager.complete_upload(session_id)
            
            if not success:
                return jsonify(result), 400
            
            return jsonify({
                'success': True,
                'data': result,
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200
        
        except Exception as e:
            logger.error(f"Upload completion error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload/progress/<session_id>', methods=['GET'])
    def get_progress_route(session_id):
        """Get upload progress"""
        try:
            progress = manager.get_upload_progress(session_id)
            
            if 'error' in progress:
                return jsonify(progress), 400
            
            return jsonify({
                'success': True,
                'data': progress,
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200
        
        except Exception as e:
            logger.error(f"Progress error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload/cancel', methods=['POST'])
    def cancel_upload_route():
        """Cancel upload"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            
            success, message = manager.cancel_upload(session_id)
            
            return jsonify({
                'success': success,
                'message': message,
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200 if success else 400
        
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return jsonify({'error': str(e)}), 500


# ========== FILE UPLOAD API REFERENCE ==========
"""
REST API ENDPOINTS:

1. Create Upload Session
   POST /api/files/create-session
   Request: {
       "filename": "document.pdf",
       "file_size": 52428800,
       "user_id": "user123",
       "document_id": "doc456"
   }
   Response: {
       "success": true,
       "data": {
           "session_id": "upload_123456_user123",
           "filename": "document.pdf",
           "file_size": 52428800,
           "total_chunks": 11,
           "chunk_size": 5242880,
           "status": "pending"
       }
   }

2. Upload Chunk
   POST /api/files/upload-chunk
   Form Data:
       - session_id: "upload_123456_user123"
       - chunk_number: 0
       - chunk: <binary file chunk>
   Response: {
       "success": true,
       "data": {
           "session_id": "upload_123456_user123",
           "chunk": 0,
           "received_chunks": 1,
           "total_chunks": 11,
           "progress": 9.1,
           "status": "uploading"
       }
   }

3. Complete Upload
   POST /api/files/complete-upload
   Request: {"session_id": "upload_123456_user123"}
   Response: {
       "success": true,
       "data": {
           "session_id": "upload_123456_user123",
           "status": "completed",
           "filename": "document.pdf",
           "file_size": 52428800,
           "file_hash": "abc123...",
           "timestamp": "2026-03-05T12:00:00Z"
       }
   }

4. Get Upload Progress
   GET /api/files/progress/{session_id}
   Response: {
       "success": true,
       "data": {
           "session_id": "upload_123456_user123",
           "filename": "document.pdf",
           "status": "uploading",
           "file_size": 52428800,
           "received_chunks": 5,
           "total_chunks": 11,
           "progress": 45.5
       }
   }

5. Cancel Upload
   POST /api/files/cancel
   Request: {"session_id": "upload_123456_user123"}
   Response: {
       "success": true,
       "message": "Upload cancelled"
   }

CHUNKED UPLOAD WORKFLOW:
1. Client calls create-session with file metadata
2. Client splits file into chunks (5MB each)
3. Client uploads each chunk via upload-chunk
4. Client can poll progress via progress endpoint
5. When all chunks uploaded, client calls complete-upload
6. Server assembles file and returns success

FILE VALIDATION:
- Allowed formats: PDF, Office, Images, Archives, Text
- Max file size: 100MB
- Chunk size: 5MB
- File hash: SHA256
"""
