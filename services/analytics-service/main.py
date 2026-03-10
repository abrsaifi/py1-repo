"""
Analytics Service - Flask Application Factory
Provides comprehensive business intelligence, analytics, and reporting capabilities.

Port: 5009
"""

import logging
import os
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from datetime import timedelta
import redis
from sqlalchemy import text

logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """Create Flask application with configuration"""
    
    app = Flask(__name__)
    
    # Load configuration
    from config import config_by_name
    app.config.from_object(config_by_name.get(config_name, config_by_name['development']))
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS')}})
    
    # JWT setup
    jwt = JWTManager(app)
    
    # Database setup
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(
            app.config['SQLALCHEMY_DATABASE_URI'],
            pool_size=app.config.get('SQLALCHEMY_POOL_SIZE', 10),
            max_overflow=app.config.get('SQLALCHEMY_MAX_OVERFLOW', 20),
            echo=app.config.get('SQLALCHEMY_ECHO', False)
        )
        
        SessionLocal = sessionmaker(bind=engine)
        app.SessionLocal = SessionLocal
        
        logger.info(f"✓ Database initialized: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        app.SessionLocal = None
    
    # Redis setup
    try:
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        app.redis_client = redis.from_url(redis_url, decode_responses=True)
        app.redis_client.ping()
        logger.info(f"✓ Redis connected: {redis_url}")
    except Exception as e:
        logger.warning(f"⚠ Redis not available: {e}")
        app.redis_client = None
    
    # Request middleware - tenant extraction and JWT validation
    @app.before_request
    def before_request():
        """Extract tenant context and validate JWT"""
        
        # Skip for health/metrics endpoints and root
        if request.path in ['/', '/health', '/metrics', '/health/', '/metrics/']:
            return
        
        try:
            # Verify JWT
            verify_jwt_in_request()
            claims = get_jwt() or {}
        except Exception as e:
            logger.warning(f"JWT validation failed: {e}")
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
        
        # Extract tenant_id
        tenant_id = request.headers.get('X-Tenant-ID') or claims.get('tenant_id')
        
        if not tenant_id:
            # Try to extract from subdomain
            host = request.host.split('.')[0]
            if host and host != 'localhost':
                tenant_id = host
        
        if not tenant_id:
            return jsonify({'error': 'Bad Request', 'message': 'Missing X-Tenant-ID header'}), 400
        
        # Validate tenant in JWT matches request
        if claims.get('tenant_id') and claims['tenant_id'] != tenant_id:
            return jsonify({'error': 'Forbidden', 'message': 'Tenant mismatch'}), 403
        
        # Store in Flask context
        g.tenant_id = tenant_id
        g.user_id = claims.get('sub')
        g.request_id = request.headers.get('X-Request-ID', str(os.urandom(16).hex()))
    
    # After request - add custom headers
    @app.after_request
    def after_request(response):
        """Add custom headers"""
        response.headers['X-Request-ID'] = getattr(g, 'request_id', '')
        response.headers['X-Tenant-ID'] = getattr(g, 'tenant_id', '')
        response.headers['X-Service'] = 'analytics-service'
        return response
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Rate Limited', 'message': 'Too many requests'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({'error': 'Internal Server Error', 'message': 'An error occurred'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500
    
    # Service endpoints
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - service info"""
        return jsonify({
            'service': 'analytics-service',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'metrics': '/metrics',
                'api': '/api/...'
            },
            'documentation': 'See API_REFERENCE.md'
        }), 200
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        status = {
            'status': 'healthy',
            'service': 'analytics-service',
            'timestamp': str(os.popen('date').read()).strip(),
        }
        
        # Check database
        try:
            if app.SessionLocal:
                session = app.SessionLocal()
                session.execute(text('SELECT 1'))
                session.close()
                status['database'] = 'connected'
            else:
                status['database'] = 'disconnected'
        except Exception as e:
            status['database'] = f'error: {str(e)}'
            status['status'] = 'degraded'
        
        # Check Redis
        try:
            if app.redis_client:
                app.redis_client.ping()
                status['redis'] = 'connected'
            else:
                status['redis'] = 'disconnected'
        except Exception as e:
            status['redis'] = f'error: {str(e)}'
        
        return jsonify(status), 200 if status['status'] == 'healthy' else 503
    
    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Metrics endpoint"""
        try:
            if not app.SessionLocal:
                return jsonify({'error': 'Database unavailable'}), 503
            
            session = app.SessionLocal()
            
            from analytics_models import SystemMetric, Dashboard, Report, Alert
            
            metrics = {
                'total_metrics': session.query(SystemMetric).count(),
                'dashboards': session.query(Dashboard).count(),
                'reports': session.query(Report).count(),
                'alerts': session.query(Alert).count(),
                'uptime_seconds': 0,  # Would calculate from startup time
            }
            
            session.close()
            return jsonify(metrics), 200
        except Exception as e:
            logger.error(f"Metrics endpoint error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Blueprint registration (will be added after blueprints are created)
    try:
        from blueprints import (
            metrics_bp, dashboards_bp, reports_bp, alerts_bp,
            custom_metrics_bp, queries_bp, export_bp
        )
        
        app.register_blueprint(metrics_bp, url_prefix='/api')
        app.register_blueprint(dashboards_bp, url_prefix='/api')
        app.register_blueprint(reports_bp, url_prefix='/api')
        app.register_blueprint(alerts_bp, url_prefix='/api')
        app.register_blueprint(custom_metrics_bp, url_prefix='/api')
        app.register_blueprint(queries_bp, url_prefix='/api')
        app.register_blueprint(export_bp, url_prefix='/api')
        
        logger.info("✓ All blueprints registered")
    except ImportError as e:
        logger.warning(f"⚠ Blueprint import warning: {e}")
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5009, debug=True)


