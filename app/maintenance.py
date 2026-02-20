"""Database optimization and maintenance"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'docpro_database.db'

def optimize_database():
    """Run database optimization"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        print("🚀 Starting database optimization...")
        
        # Create indexes for fast queries
        print("📝 Creating indexes...")
        
        # Users indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key)')
        
        # Conversion history indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_user_id ON conversion_history(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_operation ON conversion_history(operation_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_status ON conversion_history(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_created ON conversion_history(created_at)')
        
        # Analytics indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_operation ON analytics(operation_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(created_at)')
        
        # Webhook indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhooks_user ON webhooks(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhooks_event ON webhooks(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook ON webhook_logs(webhook_id)')
        
        conn.commit()
        print("✅ Indexes created")
        
        # Vacuum database to reclaim space
        print("🧹 Vacuuming database...")
        cursor.execute('VACUUM')
        print("✅ Database vacuumed")
        
        # Analyze for query optimization
        print("📊 Analyzing tables...")
        cursor.execute('ANALYZE')
        print("✅ Database analyzed")
        
        # Get database stats
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0] / (1024 * 1024)  # Convert to MB
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversion_history")
        history_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analytics")
        analytics_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Statistics:")
        print(f"  Size: {db_size:.2f} MB")
        print(f"  Users: {user_count}")
        print(f"  Conversion History: {history_count}")
        print(f"  Analytics Records: {analytics_count}")
        
        print("\n✨ Database optimization complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        conn.close()

def backup_database(backup_path: str = None):
    """Backup database"""
    if backup_path is None:
        backup_path = str(DB_PATH) + '.backup'
    
    try:
        print(f"💾 Backing up database to {backup_path}...")
        
        import shutil
        shutil.copy2(str(DB_PATH), backup_path)
        
        print("✅ Database backed up successfully")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        raise

def cleanup_old_logs(days: int = 30):
    """Clean up old webhook logs"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        print(f"🧹 Cleaning logs older than {days} days...")
        
        cursor.execute(f'''
            DELETE FROM webhook_logs
            WHERE created_at < datetime('now', '-{days} days')
        ''')
        
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ Deleted {deleted} old webhook logs")
    finally:
        conn.close()

def cleanup_old_events(days: int = 90):
    """Clean up old webhook events"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        print(f"🧹 Cleaning events older than {days} days...")
        
        cursor.execute(f'''
            DELETE FROM webhook_events
            WHERE created_at < datetime('now', '-{days} days')
        ''')
        
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ Deleted {deleted} old webhook events")
    finally:
        conn.close()

def check_database_health():
    """Check database integrity"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        print("🏥 Checking database health...")
        
        cursor.execute('PRAGMA integrity_check')
        result = cursor.fetchone()[0]
        
        if result == 'ok':
            print("✅ Database integrity: OK")
            return True
        else:
            print(f"⚠️  Database integrity issues: {result}")
            return False
    finally:
        conn.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database maintenance utilities')
    parser.add_argument('--optimize', action='store_true', help='Optimize database')
    parser.add_argument('--backup', action='store_true', help='Backup database')
    parser.add_argument('--cleanup-logs', action='store_true', help='Clean old logs')
    parser.add_argument('--cleanup-events', action='store_true', help='Clean old events')
    parser.add_argument('--check', action='store_true', help='Check database health')
    parser.add_argument('--all', action='store_true', help='Run all maintenance')
    
    args = parser.parse_args()
    
    if args.all or args.optimize:
        optimize_database()
    
    if args.all or args.backup:
        backup_database()
    
    if args.all or args.cleanup_logs:
        cleanup_old_logs()
    
    if args.all or args.cleanup_events:
        cleanup_old_events()
    
    if args.all or args.check:
        check_database_health()
