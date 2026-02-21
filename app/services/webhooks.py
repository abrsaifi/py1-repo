"""Webhook system for DocPro"""
import json
import requests
from datetime import datetime
import sqlite3
from pathlib import Path
from app.utils.logger_enhanced import get_logger
import hmac
import hashlib

logger = get_logger('webhooks')
DB_PATH = Path(__file__).parent.parent / 'docpro_database.db'

class WebhookManager:
    """Manage webhooks for event notifications"""
    
    @staticmethod
    def init_webhooks_table():
        """Initialize webhooks table"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                url TEXT NOT NULL,
                secret TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id INTEGER NOT NULL,
                event TEXT NOT NULL,
                status_code INTEGER,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def register_webhook(user_id: int, event_type: str, url: str, secret: str = None) -> int:
        """Register a webhook"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO webhooks (user_id, event_type, url, secret)
                VALUES (?, ?, ?, ?)
            ''', (user_id, event_type, url, secret))
            
            conn.commit()
            webhook_id = cursor.lastrowid
            logger.info(f'Webhook registered: {webhook_id}')
            return webhook_id
        finally:
            conn.close()
    
    @staticmethod
    def trigger_event(user_id: int, event_type: str, payload: dict):
        """Trigger webhook event"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            # Get active webhooks for this event
            cursor.execute('''
                SELECT id, url, secret FROM webhooks
                WHERE user_id=? AND event_type=? AND is_active=1
            ''', (user_id, event_type))
            
            webhooks = cursor.fetchall()
            
            # Log event
            cursor.execute('''
                INSERT INTO webhook_events (user_id, event_type, payload)
                VALUES (?, ?, ?)
            ''', (user_id, event_type, json.dumps(payload)))
            
            conn.commit()
            
            # Send to each webhook
            for webhook_id, url, secret in webhooks:
                WebhookManager._send_webhook(webhook_id, url, secret, event_type, payload)
        
        finally:
            conn.close()
    
    @staticmethod
    def _send_webhook(webhook_id: int, url: str, secret: str, event_type: str, payload: dict):
        """Send webhook to URL"""
        try:
            # Create signature
            signature = ''
            if secret:
                signature = hmac.new(
                    secret.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'X-DocPro-Event': event_type,
                'X-DocPro-Signature': signature
            }
            
            response = requests.post(url, json={
                'event': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': payload
            }, headers=headers, timeout=10)
            
            # Log result
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO webhook_logs (webhook_id, event, status_code, response)
                VALUES (?, ?, ?, ?)
            ''', (webhook_id, event_type, response.status_code, response.text[:500]))
            conn.commit()
            conn.close()
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f'Webhook {webhook_id} sent successfully: {response.status_code}')
            else:
                logger.warning(f'Webhook {webhook_id} failed: {response.status_code}')
        
        except Exception as e:
            logger.error(f'Webhook {webhook_id} error: {str(e)}')
    
    @staticmethod
    def get_webhooks(user_id: int) -> list:
        """Get all webhooks for user"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, event_type, url, is_active, created_at
            FROM webhooks WHERE user_id=?
        ''', (user_id,))
        
        webhooks = cursor.fetchall()
        conn.close()
        return webhooks
    
    @staticmethod
    def disable_webhook(webhook_id: int, user_id: int):
        """Disable a webhook"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE webhooks SET is_active=0
            WHERE id=? AND user_id=?
        ''', (webhook_id, user_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_webhook(webhook_id: int, user_id: int):
        """Delete a webhook"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM webhooks WHERE id=? AND user_id=?
        ''', (webhook_id, user_id))
        
        conn.commit()
        conn.close()
