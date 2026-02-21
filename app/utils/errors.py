"""
Error handling middleware for graceful error responses.
Provides consistent error formatting and logging.
"""

from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from functools import wraps
import logging
from typing import Tuple, Dict, Any
import traceback


logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = 'APP_ERROR',
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ConversionError(AppError):
    """File conversion error."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            status_code=422,
            error_code='CONVERSION_ERROR',
            details=details
        )


class ValidationError(AppError):
    """Input validation error."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            status_code=400,
            error_code='VALIDATION_ERROR',
            details=details
        )


class FileUploadError(AppError):
    """File upload error."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            status_code=400,
            error_code='UPLOAD_ERROR',
            details=details
        )


class ResourceNotFoundError(AppError):
    """Resource not found error."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            status_code=404,
            error_code='NOT_FOUND',
            details=details
        )


class RateLimitError(AppError):
    """Rate limit exceeded error."""
    def __init__(self, message: str = 'Rate limit exceeded'):
        super().__init__(
            message,
            status_code=429,
            error_code='RATE_LIMIT_EXCEEDED'
        )


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        """Handle application errors."""
        logger.warning(
            f'{error.error_code}: {error.message}',
            extra={'details': error.details, 'status': error.status_code}
        )
        
        response = {
            'success': False,
            'error': {
                'code': error.error_code,
                'message': error.message,
            }
        }
        
        if error.details:
            response['error']['details'] = error.details
        
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(f'HTTP {error.code}: {error.name}')
        
        return jsonify({
            'success': False,
            'error': {
                'code': f'HTTP_{error.code}',
                'message': error.description or error.name,
            }
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Handle unexpected errors."""
        logger.error(
            f'Unexpected error: {str(error)}',
            exc_info=True,
            extra={'traceback': traceback.format_exc()}
        )
        
        # Don't expose internal error details in production
        import os
        message = str(error) if os.getenv('FLASK_ENV') != 'production' else 'Internal server error'
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': message,
            }
        }), 500


def validate_input(schema=None):
    """Decorator for input validation."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if schema:
                try:
                    # Validate request data
                    data = request.get_json() if request.is_json else request.form
                    # Add schema validation here (e.g., marshmallow)
                except Exception as e:
                    raise ValidationError(f'Invalid input: {str(e)}')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_errors(f):
    """Decorator for automatic error handling in route handlers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError:
            raise  # Re-raise custom errors
        except Exception as e:
            logger.error(f'Unhandled error in {f.__name__}', exc_info=True)
            raise
    return decorated_function
