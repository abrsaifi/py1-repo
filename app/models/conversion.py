"""Conversion history model."""
from datetime import datetime
from . import db
import enum

class ConversionStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Conversion(db.Model):
    """File conversion history."""
    __tablename__ = 'conversions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # File information
    input_filename = db.Column(db.String(500), nullable=False)
    input_format = db.Column(db.String(50), nullable=False)
    output_filename = db.Column(db.String(500))
    output_format = db.Column(db.String(50), nullable=False)
    
    # File paths/storage
    input_path = db.Column(db.String(1000))
    output_path = db.Column(db.String(1000))
    
    # Size information (in bytes)
    input_size = db.Column(db.Integer, default=0)
    output_size = db.Column(db.Integer, default=0)
    
    # Conversion parameters
    parameters = db.Column(db.JSON, default={})
    
    # Status tracking
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed, cancelled
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Processing info
    processing_time = db.Column(db.Float)  # in seconds
    worker_id = db.Column(db.String(255))  # Which worker processed this
    
    # UI Tracking
    is_downloaded = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'input_filename': self.input_filename,
            'input_format': self.input_format,
            'output_filename': self.output_filename,
            'output_format': self.output_format,
            'input_size': self.input_size,
            'output_size': self.output_size,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time': self.processing_time,
            'is_downloaded': self.is_downloaded,
            'download_count': self.download_count,
        }
    
    def __repr__(self):
        return f'<Conversion {self.id}: {self.input_filename} -> {self.output_format}>'
