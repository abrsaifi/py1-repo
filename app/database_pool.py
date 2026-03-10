"""Database connection pooling and optimization."""
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import event
import os

def configure_database_pooling(app, db):
    """Configure SQLAlchemy connection pooling."""
    
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    is_sqlite = 'sqlite' in db_url
    
    if is_sqlite:
        # SQLite: Use NullPool (no connection pooling)
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': NullPool,
            'connect_args': {'check_same_thread': False}
        }
    else:
        # PostgreSQL/MySQL: Use QueuePool with optimized settings
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': QueuePool,
            'pool_size': int(os.getenv('SQLALCHEMY_POOL_SIZE', 5)),
            'max_overflow': int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 10)),
            'pool_recycle': int(os.getenv('SQLALCHEMY_POOL_RECYCLE', 3600)),
            'pool_pre_ping': True,  # Verify connections before using
            'echo_pool': False,  # Set to True for debugging
        }
    
    # Set echo mode for development
    if app.debug:
        app.config['SQLALCHEMY_ECHO'] = False
    
    return app

@event.listens_for(db.engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Optimize SQLite for better performance."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA mmap_size=30000000000")
    cursor.close()

@event.listens_for(db.engine, "pool_connect")
def receive_pool_connect(dbapi_conn, connection_record):
    """Set connection pool connection parameters."""
    if hasattr(dbapi_conn, 'cursor'):
        cursor = dbapi_conn.cursor()
        # Set application name for PostgreSQL logging
        if hasattr(cursor, 'execute'):
            try:
                cursor.execute("SET application_name = 'docpro'")
                dbapi_conn.commit()
            except:
                pass
        cursor.close()

@event.listens_for(db.engine, "pool_overflow")
def receive_pool_overflow(dbapi_conn, connection_record):
    """Log pool overflow events."""
    print("Database connection pool overflow - consider increasing pool_size")

@event.listens_for(db.engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log connection closures."""
    # Can be used for cleanup
    pass

class DatabaseStats:
    """Track database statistics."""
    
    @staticmethod
    def get_pool_status(engine):
        """Get current pool status."""
        pool = engine.pool
        
        if not hasattr(pool, 'size'):
            return {
                'type': 'NullPool',
                'size': None,
                'checked_out': None,
                'overflow': None
            }
        
        return {
            'type': 'QueuePool',
            'size': pool.size(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'queue_size': pool.queue.qsize() if hasattr(pool, 'queue') else None
        }
    
    @staticmethod
    def get_connection_stats(app):
        """Get database connection statistics."""
        from app.models import db
        
        stats = {
            'pool_status': DatabaseStats.get_pool_status(db.engine),
            'connection_string_safe': str(app.config.get('SQLALCHEMY_DATABASE_URI', '')).replace('@', '***'),
            'echo_enabled': app.config.get('SQLALCHEMY_ECHO', False),
            'track_modifications': app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        }
        
        return stats

class SlowQueryLogger:
    """Log slow database queries."""
    
    @staticmethod
    def setup_slow_query_logging(app, threshold_ms=1000):
        """Setup logging for slow queries."""
        from sqlalchemy import event
        import time
        
        @event.listens_for(db.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(db.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - conn.info['query_start_time'].pop(-1)
            total_time_ms = total_time * 1000
            
            if total_time_ms > threshold_ms:
                app.logger.warning(
                    f"SLOW QUERY ({total_time_ms:.2f}ms): {statement[:100]}..."
                )
