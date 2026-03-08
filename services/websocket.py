"""
WebSocket server for real-time job updates.
Uses Socket.io for bidirectional communication with clients.
"""

from socketio import Server, ASGIApp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time job updates"""
    
    def __init__(self):
        self.sio = Server(
            async_mode='threading',
            cors_allowed_origins='*',
            ping_timeout=10,
            ping_interval=5
        )
        self.connected_clients = {}  # {session_id: {user_id, job_ids}}
        self.job_watchers = {}  # {job_id: [session_ids]}
    
    def register_handlers(self, app):
        """Register Socket.io event handlers with Flask app"""
        
        @self.sio.on('connect')
        def handle_connect(sid, environ):
            """Handle client connection"""
            logger.info(f"Client connected: {sid}")
            self.connected_clients[sid] = {
                'user_id': None,
                'job_ids': [],
                'connected_at': datetime.now().isoformat()
            }
            return True
        
        @self.sio.on('disconnect')
        def handle_disconnect(sid):
            """Handle client disconnect"""
            logger.info(f"Client disconnected: {sid}")
            if sid in self.connected_clients:
                # Clean up job watchers
                job_ids = self.connected_clients[sid].get('job_ids', [])
                for job_id in job_ids:
                    if job_id in self.job_watchers:
                        self.job_watchers[job_id].discard(sid)
                        if not self.job_watchers[job_id]:
                            del self.job_watchers[job_id]
                del self.connected_clients[sid]
        
        @self.sio.on('authenticate')
        def handle_authenticate(sid, data):
            """Authenticate user for WebSocket connection"""
            user_id = data.get('user_id')
            token = data.get('token')
            
            if sid in self.connected_clients:
                self.connected_clients[sid]['user_id'] = user_id
                logger.info(f"Client authenticated: {sid} -> {user_id}")
                return {'success': True, 'message': 'Authenticated'}
            
            return {'success': False, 'message': 'Connection not found'}
        
        @self.sio.on('watch_job')
        def handle_watch_job(sid, data):
            """Start watching a job for updates"""
            job_id = data.get('job_id')
            
            if not job_id:
                return {'success': False, 'error': 'job_id required'}
            
            if sid not in self.connected_clients:
                return {'success': False, 'error': 'Not connected'}
            
            # Add to client's watched jobs
            self.connected_clients[sid]['job_ids'].append(job_id)
            
            # Add client to job's watchers
            if job_id not in self.job_watchers:
                self.job_watchers[job_id] = set()
            self.job_watchers[job_id].add(sid)
            
            logger.info(f"Client {sid} watching job {job_id}")
            return {'success': True, 'message': f'Watching job {job_id}'}
        
        @self.sio.on('unwatch_job')
        def handle_unwatch_job(sid, data):
            """Stop watching a job"""
            job_id = data.get('job_id')
            
            if job_id and sid in self.connected_clients:
                self.connected_clients[sid]['job_ids'].remove(job_id)
                
                if job_id in self.job_watchers:
                    self.job_watchers[job_id].discard(sid)
                    if not self.job_watchers[job_id]:
                        del self.job_watchers[job_id]
                
                logger.info(f"Client {sid} stopped watching job {job_id}")
            
            return {'success': True}
    
    def broadcast_job_update(self, job_id, data):
        """Send job update to all clients watching this job"""
        if job_id in self.job_watchers:
            watchers = list(self.job_watchers[job_id])
            for sid in watchers:
                if sid in self.connected_clients:
                    try:
                        self.sio.emit('job_update', {
                            'job_id': job_id,
                            'data': data,
                            'timestamp': datetime.now().isoformat()
                        }, to=sid)
                    except Exception as e:
                        logger.error(f"Failed to send update to {sid}: {e}")
    
    def notify_job_started(self, job_id, job_data):
        """Notify watchers that job has started"""
        self.broadcast_job_update(job_id, {
            'event': 'started',
            'status': 'processing',
            'progress': 0,
            'job_data': job_data
        })
    
    def notify_job_progress(self, job_id, progress, message=''):
        """Notify watchers of job progress"""
        self.broadcast_job_update(job_id, {
            'event': 'progress',
            'progress': progress,
            'message': message
        })
    
    def notify_job_completed(self, job_id, result_data):
        """Notify watchers that job is complete"""
        self.broadcast_job_update(job_id, {
            'event': 'completed',
            'status': 'complete',
            'progress': 100,
            'result': result_data
        })
    
    def notify_job_error(self, job_id, error_message):
        """Notify watchers of job error"""
        self.broadcast_job_update(job_id, {
            'event': 'error',
            'status': 'error',
            'error': error_message
        })
    
    def get_active_connections(self):
        """Get count of active WebSocket connections"""
        return len(self.connected_clients)
    
    def get_watched_jobs(self):
        """Get list of jobs being watched"""
        return list(self.job_watchers.keys())
    
    def emit_to_user(self, user_id, event, data):
        """Send event to all connections for a specific user"""
        sids = [
            sid for sid, info in self.connected_clients.items()
            if info['user_id'] == user_id
        ]
        for sid in sids:
            try:
                self.sio.emit(event, data, to=sid)
            except Exception as e:
                logger.error(f"Failed to emit to user {user_id}: {e}")


# Global WebSocket manager instance
_ws_manager = None

def get_websocket_manager():
    """Get or create global WebSocket manager instance"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
