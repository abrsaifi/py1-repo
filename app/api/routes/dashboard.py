"""Dashboard API endpoints - Analytics, Files, Queue, Users"""
from flask import Blueprint, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

bp = Blueprint('dashboard', __name__)

# Configuration
UPLOAD_DIR = 'uploads'

# ============================================================================
# ANALYTICS ENDPOINT - /api/analytics/summary
# ============================================================================

@bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get comprehensive analytics summary for dashboard"""
    try:
        # Get user ID from session or API key
        user_id = session.get('user_id', 'default')
        
        # Initialize mock data (replace with real DB queries)
        analytics_data = {
            'total_files': 42,
            'total_operations': 156,
            'success_rate': 98.5,
            'total_data_mb': 2048.5,
            'avg_processing_time': 2340,  # milliseconds
            'peak_operations_per_hour': 45,
            'api_requests': 540,
            'daily_operations': [15, 22, 18, 25, 20, 30, 26],  # Last 7 days
            'operation_distribution': {
                'PDF': 45,
                'Excel': 38,
                'Image': 42,
                'Word': 25,
                'Other': 6
            }
        }
        
        return jsonify(analytics_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FILES ENDPOINTS - /api/files/*
# ============================================================================

@bp.route('/files/list', methods=['GET'])
def list_files():
    """Get list of uploaded files for current user"""
    try:
        user_id = session.get('user_id', 'default')
        upload_dir = os.path.join(UPLOAD_DIR, user_id)
        
        files = []
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                filepath = os.path.join(upload_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'id': filename,
                        'name': filename,
                        'size': stat.st_size,  # bytes
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/files/<file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download a specific file"""
    try:
        user_id = session.get('user_id', 'default')
        file_id = secure_filename(file_id)
        filepath = os.path.join(UPLOAD_DIR, user_id, file_id)
        
        # Security check
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Verify user owns file
        real_path = os.path.realpath(filepath)
        base_path = os.path.realpath(os.path.join(UPLOAD_DIR, user_id))
        if not real_path.startswith(base_path):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=file_id
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a specific file"""
    try:
        user_id = session.get('user_id', 'default')
        file_id = secure_filename(file_id)
        filepath = os.path.join(UPLOAD_DIR, user_id, file_id)
        
        # Security check
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Verify user owns file
        real_path = os.path.realpath(filepath)
        base_path = os.path.realpath(os.path.join(UPLOAD_DIR, user_id))
        if not real_path.startswith(base_path):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete file
        os.remove(filepath)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# QUEUE ENDPOINTS - /api/jobs/queue
# ============================================================================

# In-memory job queue (replace with database in production)
active_jobs = {}

@bp.route('/jobs/queue', methods=['GET'])
def get_queue():
    """Get current operation queue status"""
    try:
        user_id = session.get('user_id', 'default')
        
        # Mock job data for demonstration
        jobs = [
            {
                'id': 'job_001',
                'operation': 'PDF to Excel',
                'status': 'completed',
                'progress': 100,
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'id': 'job_002',
                'operation': 'Image Compression',
                'status': 'processing',
                'progress': 45,
                'created_at': (datetime.now() - timedelta(minutes=10)).isoformat()
            },
            {
                'id': 'job_003',
                'operation': 'Word to PDF',
                'status': 'pending',
                'progress': 0,
                'created_at': (datetime.now() - timedelta(minutes=2)).isoformat()
            },
            {
                'id': 'job_004',
                'operation': 'PDF Extract',
                'status': 'completed',
                'progress': 100,
                'created_at': (datetime.now() - timedelta(hours=1)).isoformat()
            }
        ]
        
        return jsonify({'jobs': jobs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get status of specific job"""
    try:
        # Check active jobs
        if job_id in active_jobs:
            return jsonify(active_jobs[job_id]), 200
        
        return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# USER ENDPOINTS - /api/users/* (Admin only)
# ============================================================================

@bp.route('/users/list', methods=['GET'])
def list_users():
    """Get list of all users (admin only)"""
    try:
        # Check if user is admin
        is_admin = session.get('is_admin', False)
        if not is_admin:
            return jsonify({'error': 'Forbidden'}), 403
        
        # Mock user data
        users = [
            {
                'id': '1',
                'username': 'john_doe',
                'email': 'john@example.com',
                'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
                'role': 'user',
                'status': 'active'
            },
            {
                'id': '2',
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'created_at': (datetime.now() - timedelta(days=15)).isoformat(),
                'role': 'user',
                'status': 'active'
            },
            {
                'id': '3',
                'username': 'admin_user',
                'email': 'admin@example.com',
                'created_at': (datetime.now() - timedelta(days=60)).isoformat(),
                'role': 'admin',
                'status': 'active'
            }
        ]
        
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        # Check if user is admin
        is_admin = session.get('is_admin', False)
        if not is_admin:
            return jsonify({'error': 'Forbidden'}), 403
        
        # Prevent deleting self
        current_user = session.get('user_id')
        if current_user == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Delete user (would be in database in production)
        # For now, just return success
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details (admin only)"""
    try:
        # Check if user is admin
        is_admin = session.get('is_admin', False)
        if not is_admin:
            return jsonify({'error': 'Forbidden'}), 403
        
        # Mock user data
        user = {
            'id': user_id,
            'username': f'user_{user_id}',
            'email': f'user{user_id}@example.com',
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'role': 'user',
            'status': 'active',
            'files_count': 5,
            'operations_count': 12
        }
        
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
