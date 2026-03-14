"""
Phase 15.1: WebSocket Real-time Features
Handles real-time collaboration, live notifications, activity feeds, and user presence
"""

from copy import deepcopy
from flask import current_app, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from datetime import datetime, timezone
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

# ========== DATA STRUCTURES ==========
# In-memory storage for real-time data (replace with database in production)
active_users: Dict[str, Dict] = {}  # {client_id: {user_id, username, room, connected_at}}
document_collaborators: Dict[str, Set] = {}  # {document_id: set of user_ids}
live_notifications: Dict[str, List] = {}  # {user_id: [notifications]}
activity_feeds: Dict[str, List] = {}  # {room_id: [activities]}


class WebSocketManager:
    """Manages job-watch connections and real-time job update events."""

    def __init__(self):
        self.sio = None
        self.connected_clients = {}
        self.job_watchers = {}
        self._registered_socketio_id = None

    def reset_state(self):
        self.connected_clients = {}
        self.job_watchers = {}

    def track_connection(self, sid):
        self.connected_clients[sid] = {
            'user_id': None,
            'job_ids': [],
            'connected_at': datetime.now(timezone.utc).isoformat(),
        }

    def remove_connection(self, sid):
        if sid not in self.connected_clients:
            return

        for job_id in list(self.connected_clients[sid].get('job_ids', [])):
            watchers = self.job_watchers.get(job_id)
            if watchers is None:
                continue
            watchers.discard(sid)
            if not watchers:
                del self.job_watchers[job_id]

        del self.connected_clients[sid]

    def register_handlers(self, socketio):
        if socketio is None:
            raise ValueError('socketio instance is required')

        socketio_id = id(socketio)
        self.sio = socketio
        self.reset_state()

        if self._registered_socketio_id == socketio_id:
            return self

        self._registered_socketio_id = socketio_id

        @socketio.on('authenticate')
        def handle_authenticate(data):
            sid = request.sid
            user_id = data.get('user_id')

            if sid not in self.connected_clients:
                self.track_connection(sid)

            self.connected_clients[sid]['user_id'] = user_id
            logger.info('Client authenticated: %s -> %s', sid, user_id)
            return {'success': True, 'message': 'Authenticated'}

        @socketio.on('watch_job')
        def handle_watch_job(data):
            sid = request.sid
            job_id = data.get('job_id')

            if not job_id:
                return {'success': False, 'error': 'job_id required'}

            if sid not in self.connected_clients:
                self.track_connection(sid)

            if job_id not in self.connected_clients[sid]['job_ids']:
                self.connected_clients[sid]['job_ids'].append(job_id)

            self.job_watchers.setdefault(job_id, set()).add(sid)
            logger.info('Client %s watching job %s', sid, job_id)
            return {'success': True, 'message': f'Watching job {job_id}'}

        @socketio.on('unwatch_job')
        def handle_unwatch_job(data):
            sid = request.sid
            job_id = data.get('job_id')

            if job_id and sid in self.connected_clients:
                if job_id in self.connected_clients[sid]['job_ids']:
                    self.connected_clients[sid]['job_ids'].remove(job_id)

                watchers = self.job_watchers.get(job_id)
                if watchers is not None:
                    watchers.discard(sid)
                    if not watchers:
                        del self.job_watchers[job_id]

                logger.info('Client %s stopped watching job %s', sid, job_id)

            return {'success': True}

        return self

    def broadcast_job_update(self, job_id, data):
        if self.sio is None:
            logger.warning('Job update skipped because no Socket.IO server is registered')
            return

        for sid in list(self.job_watchers.get(job_id, set())):
            if sid not in self.connected_clients:
                continue
            try:
                self.sio.emit('job_update', {
                    'job_id': job_id,
                    'data': data,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }, to=sid)
            except Exception as exc:
                logger.error('Failed to send update to %s: %s', sid, exc)

    def notify_job_started(self, job_id, job_data):
        self.broadcast_job_update(job_id, {
            'event': 'started',
            'status': 'processing',
            'progress': 0,
            'job_data': job_data,
        })

    def notify_job_progress(self, job_id, progress, message=''):
        self.broadcast_job_update(job_id, {
            'event': 'progress',
            'progress': progress,
            'message': message,
        })

    def notify_job_completed(self, job_id, result_data):
        self.broadcast_job_update(job_id, {
            'event': 'completed',
            'status': 'complete',
            'progress': 100,
            'result': result_data,
        })

    def notify_job_error(self, job_id, error_message):
        self.broadcast_job_update(job_id, {
            'event': 'error',
            'status': 'error',
            'error': error_message,
        })

    def get_active_connections(self):
        return len(self.connected_clients)

    def get_watched_jobs(self):
        return list(self.job_watchers.keys())

    def emit_to_user(self, user_id, event, data):
        if self.sio is None:
            return
        for sid, info in self.connected_clients.items():
            if info['user_id'] != user_id:
                continue
            try:
                self.sio.emit(event, data, to=sid)
            except Exception as exc:
                logger.error('Failed to emit to user %s: %s', user_id, exc)


_ws_manager = None


def get_websocket_manager():
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager

# ========== WEBSOCKET SETUP ==========
def init_websocket(app):
    """Initialize WebSocket server with Flask app"""
    socketio = SocketIO(
        app,
        cors_allowed_origins=['http://localhost:3000', 'http://localhost:5173'],
        ping_timeout=10,
        ping_interval=5
    )
    websocket_manager = get_websocket_manager().register_handlers(socketio)
    app.extensions['job_websocket_manager'] = websocket_manager
    app.websocket_manager = websocket_manager
    
    # ========== USER CONNECTION EVENTS ==========
    @socketio.on('connect')
    def handle_connect():
        """User connects to WebSocket"""
        try:
            client_id = request.sid
            websocket_manager = current_app.extensions.get('job_websocket_manager')
            if websocket_manager is not None:
                websocket_manager.track_connection(client_id)
            logger.info(f"Client connected: {client_id}")
            emit('connection_response', {
                'status': 'connected',
                'client_id': client_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Connection error: {e}")
            emit('error', {'message': 'Connection failed'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """User disconnects from WebSocket"""
        try:
            client_id = request.sid
            websocket_manager = current_app.extensions.get('job_websocket_manager')
            if websocket_manager is not None:
                websocket_manager.remove_connection(client_id)
            if client_id in active_users:
                user_info = active_users[client_id]
                room = user_info.get('room')
                
                # Notify others in room
                if room:
                    emit('user_left', {
                        'user_id': user_info['user_id'],
                        'username': user_info['username'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }, to=room)
                    
                    # Log activity
                    log_activity(room, 'user_left', {
                        'username': user_info['username'],
                        'time': datetime.now(timezone.utc).isoformat()
                    })
                
                del active_users[client_id]
            
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Disconnection error: {e}")
    
    # ========== USER PRESENCE & ROOM EVENTS ==========
    @socketio.on('user_joined')
    def handle_user_joined(data):
        """User joins a collaboration room"""
        try:
            client_id = request.sid
            user_id = data.get('user_id')
            username = data.get('username')
            room = data.get('room')
            
            if not all([user_id, username, room]):
                emit('error', {'message': 'Missing required fields'})
                return
            
            # Store user info
            active_users[client_id] = {
                'user_id': user_id,
                'username': username,
                'room': room,
                'connected_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Track document collaborators
            if room not in document_collaborators:
                document_collaborators[room] = set()
            document_collaborators[room].add(user_id)
            
            # Join room
            join_room(room)
            
            # Notify others
            emit('user_joined_room', {
                'user_id': user_id,
                'username': username,
                'active_users': list(document_collaborators.get(room, set())),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, to=room)
            
            # Log activity
            log_activity(room, 'user_joined', {
                'username': username,
                'active_count': len(document_collaborators.get(room, set())),
                'time': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"User {username} joined room {room}")
        except Exception as e:
            logger.error(f"Join room error: {e}")
            emit('error', {'message': 'Failed to join room'})
    
    @socketio.on('get_active_users')
    def handle_get_active_users(data):
        """Get list of active users in a room"""
        try:
            room = data.get('room')
            if not room:
                emit('error', {'message': 'Room not specified'})
                return
            
            active_in_room = [
                {
                    'user_id': info['user_id'],
                    'username': info['username'],
                    'connected_at': info['connected_at']
                }
                for client_id, info in active_users.items()
                if info.get('room') == room
            ]
            
            emit('active_users_list', {
                'room': room,
                'count': len(active_in_room),
                'users': active_in_room,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Get active users error: {e}")
    
    # ========== REAL-TIME COLLABORATION EVENTS ==========
    @socketio.on('document_updated')
    def handle_document_updated(data):
        """Document content updated (for real-time co-editing)"""
        try:
            room = data.get('room')
            document_id = data.get('document_id')
            user_id = data.get('user_id')
            username = data.get('username')
            changes = data.get('changes', {})
            
            # Broadcast to all users in room
            emit('document_changed', {
                'document_id': document_id,
                'user_id': user_id,
                'username': username,
                'changes': changes,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, to=room, skip_sid=request.sid)
            
            # Log activity
            log_activity(room, 'document_updated', {
                'document_id': document_id,
                'username': username,
                'type': changes.get('type', 'unknown'),
                'time': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Document {document_id} updated by {username}")
        except Exception as e:
            logger.error(f"Document update error: {e}")
    
    @socketio.on('comment_added')
    def handle_comment_added(data):
        """Comment added to document"""
        try:
            room = data.get('room')
            document_id = data.get('document_id')
            user_id = data.get('user_id')
            username = data.get('username')
            comment = data.get('comment')
            
            comment_obj = {
                'id': f"comment_{datetime.now(timezone.utc).timestamp()}",
                'document_id': document_id,
                'user_id': user_id,
                'username': username,
                'text': comment,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Broadcast to all users
            emit('new_comment', comment_obj, to=room)
            
            # Log activity
            log_activity(room, 'comment_added', {
                'document_id': document_id,
                'username': username,
                'preview': comment[:50] + '...' if len(comment) > 50 else comment,
                'time': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Comment added to {document_id} by {username}")
        except Exception as e:
            logger.error(f"Comment error: {e}")
    
    @socketio.on('cursor_moved')
    def handle_cursor_moved(data):
        """User cursor position in shared document (for awareness)"""
        try:
            room = data.get('room')
            user_id = data.get('user_id')
            username = data.get('username')
            position = data.get('position')  # {line, column}
            
            # Broadcast to others (not back to sender)
            emit('cursor_update', {
                'user_id': user_id,
                'username': username,
                'position': position,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, to=room, skip_sid=request.sid)
            
        except Exception as e:
            logger.error(f"Cursor update error: {e}")
    
    # ========== NOTIFICATION EVENTS ==========
    @socketio.on('send_notification')
    def handle_send_notification(data):
        """Send real-time notification to users"""
        try:
            recipient_id = data.get('recipient_id')
            sender_id = data.get('sender_id')
            sender_name = data.get('sender_name')
            notification_type = data.get('type')  # 'share', 'comment', 'mention', etc.
            message = data.get('message')
            
            notification = {
                'id': f"notif_{datetime.now(timezone.utc).timestamp()}",
                'type': notification_type,
                'from': sender_name,
                'from_id': sender_id,
                'message': message,
                'read': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Store notification
            if recipient_id not in live_notifications:
                live_notifications[recipient_id] = []
            live_notifications[recipient_id].append(notification)
            
            # Emit to recipient's room (if connected)
            emit('notification_received', notification, to=f"user_{recipient_id}")
            
            logger.info(f"Notification sent to {recipient_id}: {notification_type}")
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    @socketio.on('mark_notification_read')
    def handle_mark_notification_read(data):
        """Mark notification as read"""
        try:
            user_id = data.get('user_id')
            notification_id = data.get('notification_id')
            
            for notif in live_notifications.get(user_id, []):
                if notif.get('id') == notification_id:
                    notif['read'] = True
                    break
            
            emit('notification_marked_read', {
                'notification_id': notification_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Mark read error: {e}")
    
    @socketio.on('get_notifications')
    def handle_get_notifications(data):
        """Get user's notifications"""
        try:
            user_id = data.get('user_id')
            notifs = live_notifications.get(user_id, [])
            
            emit('notifications_list', {
                'user_id': user_id,
                'count': len(notifs),
                'unread': sum(1 for n in notifs if not n.get('read', True)),
                'notifications': notifs,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Get notifications error: {e}")
    
    # ========== ACTIVITY FEED EVENTS ==========
    @socketio.on('get_activity_feed')
    def handle_get_activity_feed(data):
        """Get activity feed for a room/document"""
        try:
            room = data.get('room')
            limit = data.get('limit', 20)
            
            activities = activity_feeds.get(room, [])
            recent = activities[-limit:] if len(activities) > limit else activities
            
            emit('activity_feed', {
                'room': room,
                'count': len(recent),
                'total': len(activities),
                'activities': recent,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Activity feed error: {e}")
    
    # ========== TYPING INDICATOR EVENTS ==========
    @socketio.on('user_typing')
    def handle_user_typing(data):
        """User is typing (show indicator to others)"""
        try:
            room = data.get('room')
            user_id = data.get('user_id')
            username = data.get('username')
            
            emit('user_typing_indicator', {
                'user_id': user_id,
                'username': username,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, to=room, skip_sid=request.sid)
        except Exception as e:
            logger.error(f"Typing indicator error: {e}")
    
    @socketio.on('user_stopped_typing')
    def handle_user_stopped_typing(data):
        """User stopped typing"""
        try:
            room = data.get('room')
            user_id = data.get('user_id')
            
            emit('user_stopped_typing', {
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, to=room, skip_sid=request.sid)
        except Exception as e:
            logger.error(f"Stop typing error: {e}")
    
    # ========== HELPER FUNCTIONS ==========
    def log_activity(room: str, action: str, details: Dict):
        """Log activity for audit trail"""
        if room not in activity_feeds:
            activity_feeds[room] = []
        
        activity = {
            'id': f"activity_{datetime.now(timezone.utc).timestamp()}",
            'action': action,
            'details': details,
            'timestamp': details.get('time', datetime.now(timezone.utc).isoformat())
        }
        
        activity_feeds[room].append(activity)
        
        # Keep only last 500 activities
        if len(activity_feeds[room]) > 500:
            activity_feeds[room] = activity_feeds[room][-500:]
    
    def broadcast_to_room(room: str, event: str, data: Dict):
        """Broadcast event to all users in a room"""
        socketio.emit(event, data, to=room)
    
    return socketio


# ========== WEBSOCKET API REFERENCE ==========
"""
CLIENT → SERVER EVENTS:

1. User Presence
   - 'user_joined': {user_id, username, room}
   - 'get_active_users': {room}

2. Document Collaboration
   - 'document_updated': {room, document_id, user_id, username, changes}
   - 'comment_added': {room, document_id, user_id, username, comment}
   - 'cursor_moved': {room, user_id, username, position}

3. Notifications
   - 'send_notification': {recipient_id, sender_id, sender_name, type, message}
   - 'mark_notification_read': {user_id, notification_id}
   - 'get_notifications': {user_id}

4. Activity Feed
   - 'get_activity_feed': {room, limit}

5. Typing Indicators
   - 'user_typing': {room, user_id, username}
   - 'user_stopped_typing': {room, user_id}


SERVER → CLIENT EVENTS:

1. Connection
   - 'connection_response': {status, client_id, timestamp}
   - 'error': {message}

2. User Events
   - 'user_joined_room': {user_id, username, active_users, timestamp}
   - 'user_left': {user_id, username, timestamp}
   - 'active_users_list': {room, count, users, timestamp}

3. Document Changes
   - 'document_changed': {document_id, user_id, username, changes, timestamp}
   - 'new_comment': {id, document_id, user_id, username, text, timestamp}
   - 'cursor_update': {user_id, username, position, timestamp}

4. Notifications
   - 'notification_received': {id, type, from, message, timestamp}
   - 'notification_marked_read': {notification_id, timestamp}
   - 'notifications_list': {user_id, count, unread, notifications, timestamp}

5. Activity Feed
   - 'activity_feed': {room, count, total, activities, timestamp}

6. Typing
   - 'user_typing_indicator': {user_id, username, timestamp}
   - 'user_stopped_typing': {user_id, timestamp}
"""
