"""
Database module for job persistence.
Stores conversion job history in SQLite for recovery and analytics.
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class JobDatabase:
    """SQLite-based job history and persistence"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            db_path = os.path.join(db_dir, 'jobs.db')
        
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Jobs table - stores conversion job details
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    file_count INTEGER DEFAULT 1,
                    error TEXT,
                    result_path TEXT,
                    ip_address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME,
                    completed_at DATETIME,
                    elapsed_seconds REAL,
                    metadata TEXT
                )
            ''')
            
            # Job history view - for analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    old_status TEXT,
                    new_status TEXT,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
                )
            ''')
            
            # Users table - for authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT
                )
            ''')
            
            # API keys table - for programmatic access
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    secret_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # User favorites table - for storing favorite tools/presets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_favorites (
                    favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    preset_name TEXT,
                    settings TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Update jobs table to link to users
            try:
                cursor.execute('''
                    ALTER TABLE jobs ADD COLUMN user_id TEXT
                ''')
            except sqlite3.OperationalError as e:
                # Column might already exist, which is fine
                if 'duplicate column name' not in str(e):
                    raise
            
            # Indexes for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_jobs_created_at 
                ON jobs(created_at DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_jobs_status 
                ON jobs(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_jobs_ip 
                ON jobs(ip_address)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_jobs_user_id 
                ON jobs(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_users_username 
                ON users(username)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_api_keys_user_id 
                ON api_keys(user_id)
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_job(self, job_id, tool_name, file_count, ip_address=None, metadata=None):
        """Save a job to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO jobs (job_id, tool_name, status, file_count, ip_address, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (job_id, tool_name, 'queued', file_count, ip_address, 
                  json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            logger.debug(f"Job {job_id} saved to database")
        except Exception as e:
            logger.error(f"Failed to save job {job_id}: {e}")
            raise
    
    def update_job(self, job_id, status=None, progress=None, error=None, result_path=None):
        """Update job status, progress, or result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if progress is not None:
                updates.append("progress = ?")
                params.append(progress)
            
            if error is not None:
                updates.append("error = ?")
                params.append(error)
            
            if result_path is not None:
                updates.append("result_path = ?")
                params.append(result_path)
            
            if status == 'processing' and not self._has_started(cursor, job_id):
                updates.append("started_at = CURRENT_TIMESTAMP")
            
            if status in ['complete', 'error']:
                updates.append("completed_at = CURRENT_TIMESTAMP")
            
            params.append(job_id)
            
            if updates:
                cursor.execute(
                    f"UPDATE jobs SET {', '.join(updates)} WHERE job_id = ?",
                    params
                )
                conn.commit()
            
            conn.close()
            logger.debug(f"Job {job_id} updated: {status or 'progress'} = {progress or error or result_path}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            raise
    
    def get_job(self, job_id):
        """Retrieve job details from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM jobs WHERE job_id = ?
            ''', (job_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve job {job_id}: {e}")
            return None
    
    def list_jobs(self, status=None, limit=100, offset=0):
        """List jobs from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM jobs 
                    WHERE status = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (status, limit, offset))
            else:
                cursor.execute('''
                    SELECT * FROM jobs 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []
    
    def cleanup_old_jobs(self, days=7):
        """Delete jobs older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM job_history 
                WHERE job_id IN (
                    SELECT job_id FROM jobs WHERE created_at < ?
                )
            ''', (cutoff_date,))
            
            cursor.execute('''
                DELETE FROM jobs WHERE created_at < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} jobs older than {days} days")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            return 0
    
    def get_metrics(self, days=7):
        """Get conversion metrics for analytics with detailed breakdown"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Overall metrics
            cursor.execute('''
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed,
                       SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as in_progress,
                       AVG(elapsed_seconds) as avg_duration
                FROM jobs 
                WHERE created_at > ?
            ''', (cutoff_date,))
            
            overview_row = dict(cursor.fetchone())
            total_jobs = overview_row.get('total', 0)
            completed = overview_row.get('completed', 0) or 0
            failed = overview_row.get('failed', 0) or 0
            in_progress = overview_row.get('in_progress', 0) or 0
            success_rate = (completed / max(total_jobs, 1)) * 100
            
            # Metrics by tool
            cursor.execute('''
                SELECT tool_name, 
                       COUNT(*) as count,
                       SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) as success_count,
                       AVG(elapsed_seconds) as avg_time_seconds
                FROM jobs 
                WHERE created_at > ?
                GROUP BY tool_name 
                ORDER BY count DESC 
                LIMIT 20
            ''', (cutoff_date,))
            
            by_tool = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                row_dict['failed_count'] = row_dict['count'] - (row_dict['success_count'] or 0)
                by_tool.append(row_dict)
            
            # Metrics by hour
            cursor.execute('''
                SELECT strftime('%Y-%m-%d %H:00', created_at) as hour,
                       COUNT(*) as count,
                       SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) as success_count
                FROM jobs 
                WHERE created_at > ?
                GROUP BY strftime('%Y-%m-%d %H:00', created_at)
                ORDER BY hour DESC
                LIMIT 24
            ''', (cutoff_date,))
            
            by_hour = [dict(row) for row in cursor.fetchall()]
            by_hour.reverse()  # Oldest first
            
            # Timestamps
            cursor.execute('''
                SELECT MIN(created_at) as first_job, MAX(created_at) as last_job
                FROM jobs
                WHERE created_at > ?
            ''', (cutoff_date,))
            
            timestamps_row = dict(cursor.fetchone())
            timestamps = {
                'first_job': timestamps_row.get('first_job'),
                'last_job': timestamps_row.get('last_job')
            }
            
            conn.close()
            
            return {
                'overview': {
                    'total_jobs': total_jobs,
                    'completed': completed,
                    'failed': failed,
                    'in_progress': in_progress,
                    'success_rate': success_rate
                },
                'by_tool': by_tool,
                'by_hour': by_hour,
                'timestamps': timestamps,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                'overview': {
                    'total_jobs': 0,
                    'completed': 0,
                    'failed': 0,
                    'in_progress': 0,
                    'success_rate': 0
                },
                'by_tool': [],
                'by_hour': [],
                'timestamps': {'first_job': None, 'last_job': None},
                'period_days': days
            }
    
    def register_user(self, user_id, username, email, password_hash):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, email, password_hash))
            
            conn.commit()
            conn.close()
            logger.info(f"User registered: {username}")
            return True
        except sqlite3.IntegrityError:
            logger.error(f"Username or email already exists: {username}, {email}")
            return False
        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            return False
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            return None
    
    def create_api_key(self, key_id, user_id, name, secret_hash):
        """Create API key for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_keys (key_id, user_id, name, secret_hash, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key_id, user_id, name, secret_hash))
            
            conn.commit()
            conn.close()
            logger.info(f"API key created for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            return False
    
    def get_api_key(self, key_id):
        """Get API key details"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM api_keys WHERE key_id = ? AND is_active = 1', (key_id,))
            key = cursor.fetchone()
            conn.close()
            return dict(key) if key else None
        except Exception as e:
            logger.error(f"Failed to get API key: {e}")
            return None
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            return False
    
    def get_user_history(self, user_id, limit=50):
        """Get conversion history for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT job_id, tool_name, status, file_count, created_at, 
                       completed_at, elapsed_seconds
                FROM jobs 
                WHERE user_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            history = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return history
        except Exception as e:
            logger.error(f"Failed to get user history: {e}")
            return []
    
    def add_favorite(self, user_id, tool_name, preset_name, settings):
        """Add favorite tool/preset for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_favorites (user_id, tool_name, preset_name, settings, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, tool_name, preset_name, settings))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add favorite: {e}")
            return False
    
    def get_user_favorites(self, user_id):
        """Get user's favorite tools/presets"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT favorite_id, tool_name, preset_name, settings, created_at
                FROM user_favorites 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            favorites = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return favorites
        except Exception as e:
            logger.error(f"Failed to get favorites: {e}")
            return []
    
    def _has_started(self, cursor, job_id):
        """Check if job has already started (started_at is set)"""
        cursor.execute('SELECT started_at FROM jobs WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        return row and row[0] is not None
    
    def mark_job_as_retried(self, original_job_id, new_job_id):
        """Mark original job as retried and link to new job"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get original job metadata
            cursor.execute('SELECT metadata FROM jobs WHERE job_id = ?', (original_job_id,))
            row = cursor.fetchone()
            metadata = json.loads(row[0]) if row and row[0] else {}
            
            # Increment retry count
            metadata['retry_count'] = metadata.get('retry_count', 0) + 1
            metadata['retry_of'] = original_job_id
            metadata['retried_at'] = datetime.now().isoformat()
            
            # Update original job to reflect retry
            original_metadata = json.loads(row[0]) if row and row[0] else {}
            original_metadata['retried_by'] = new_job_id
            original_metadata['retry_timestamp'] = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE jobs SET metadata = ? WHERE job_id = ?
            ''', (json.dumps(original_metadata), original_job_id))
            
            # Update new job with retry metadata
            cursor.execute('''
                UPDATE jobs SET metadata = ? WHERE job_id = ?
            ''', (json.dumps(metadata), new_job_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Job {original_job_id} marked as retried by {new_job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark job as retried: {e}")
            return False
    
    def update_job_metadata(self, job_id, metadata):
        """Update metadata for a job"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE jobs SET metadata = ? WHERE job_id = ?
            ''', (json.dumps(metadata), job_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update job metadata: {e}")
            return False


# Global database instance
_job_db = None

def get_database():
    """Get or create global database instance"""
    global _job_db
    if _job_db is None:
        _job_db = JobDatabase()
    return _job_db
