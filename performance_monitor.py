"""
Performance Monitoring Module
Tracks execution times, OCR engine usage, and system metrics
"""

import logging
import time
import json
from datetime import datetime
from functools import wraps
from pathlib import Path
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# PERFORMANCE TRACKER
# ============================================================================

class PerformanceTracker:
    """Track and log performance metrics"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.metrics = {
            'ocr_operations': [],
            'batch_operations': [],
            'image_operations': [],
            'pdf_operations': [],
            'data_exports': []
        }
        self.start_time = datetime.now()
    
    def log_ocr_operation(self, engine, duration, text_length, success):
        """Log OCR operation metrics"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'engine': engine,
            'duration_seconds': duration,
            'text_length': text_length,
            'success': success,
            'words_per_second': text_length / duration if duration > 0 else 0
        }
        self.metrics['ocr_operations'].append(metric)
        
        logger.info(
            f"OCR Operation | Engine: {engine} | Time: {duration:.2f}s | "
            f"Text: {text_length} chars | Speed: {metric['words_per_second']:.0f} chars/s"
        )
    
    def log_batch_operation(self, operation_type, file_count, duration, success):
        """Log batch operation metrics"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'file_count': file_count,
            'duration_seconds': duration,
            'success': success,
            'avg_file_time': duration / file_count if file_count > 0 else 0
        }
        self.metrics['batch_operations'].append(metric)
        
        logger.info(
            f"Batch {operation_type} | Files: {file_count} | Time: {duration:.2f}s | "
            f"Avg: {metric['avg_file_time']:.2f}s/file"
        )
    
    def log_image_operation(self, operation, file_size_kb, duration, success):
        """Log image processing metrics"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'file_size_kb': file_size_kb,
            'duration_seconds': duration,
            'success': success,
            'speed_kb_per_sec': file_size_kb / duration if duration > 0 else 0
        }
        self.metrics['image_operations'].append(metric)
        
        logger.info(
            f"Image {operation} | Size: {file_size_kb:.1f}KB | Time: {duration:.2f}s | "
            f"Speed: {metric['speed_kb_per_sec']:.1f}KB/s"
        )
    
    def log_pdf_operation(self, operation, page_count, duration, success):
        """Log PDF processing metrics"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'page_count': page_count,
            'duration_seconds': duration,
            'success': success,
            'pages_per_second': page_count / duration if duration > 0 else 0
        }
        self.metrics['pdf_operations'].append(metric)
        
        logger.info(
            f"PDF {operation} | Pages: {page_count} | Time: {duration:.2f}s | "
            f"Speed: {metric['pages_per_second']:.2f} pages/s"
        )
    
    def log_data_export(self, format_type, row_count, duration, success):
        """Log data export metrics"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'format': format_type,
            'row_count': row_count,
            'duration_seconds': duration,
            'success': success,
            'rows_per_second': row_count / duration if duration > 0 else 0
        }
        self.metrics['data_exports'].append(metric)
        
        logger.info(
            f"Data Export to {format_type} | Rows: {row_count} | Time: {duration:.2f}s | "
            f"Speed: {metric['rows_per_second']:.0f} rows/s"
        )
    
    def get_statistics(self):
        """Get aggregated performance statistics"""
        stats = {
            'collection_period': {
                'start': self.start_time.isoformat(),
                'end': datetime.now().isoformat()
            },
            'ocr': self._get_ocr_stats(),
            'batch': self._get_batch_stats(),
            'images': self._get_image_stats(),
            'pdfs': self._get_pdf_stats(),
            'exports': self._get_export_stats()
        }
        return stats
    
    def _get_ocr_stats(self):
        """Calculate OCR statistics"""
        if not self.metrics['ocr_operations']:
            return None
        
        ops = self.metrics['ocr_operations']
        durations = [op['duration_seconds'] for op in ops]
        successful = [op for op in ops if op['success']]
        
        return {
            'total_operations': len(ops),
            'successful': len(successful),
            'failure_rate': (1 - len(successful) / len(ops)) * 100,
            'avg_duration_seconds': sum(durations) / len(durations),
            'min_duration_seconds': min(durations),
            'max_duration_seconds': max(durations),
            'total_characters_processed': sum(op['text_length'] for op in ops),
            'engine_breakdown': self._count_by_engine(ops)
        }
    
    def _get_batch_stats(self):
        """Calculate batch operation statistics"""
        if not self.metrics['batch_operations']:
            return None
        
        ops = self.metrics['batch_operations']
        durations = [op['duration_seconds'] for op in ops]
        successful = [op for op in ops if op['success']]
        
        return {
            'total_operations': len(ops),
            'total_files_processed': sum(op['file_count'] for op in ops),
            'successful': len(successful),
            'avg_duration_seconds': sum(durations) / len(durations),
            'total_duration_seconds': sum(durations),
            'operation_breakdown': self._count_by_operation(ops)
        }
    
    def _get_image_stats(self):
        """Calculate image operation statistics"""
        if not self.metrics['image_operations']:
            return None
        
        ops = self.metrics['image_operations']
        durations = [op['duration_seconds'] for op in ops]
        successful = [op for op in ops if op['success']]
        
        return {
            'total_operations': len(ops),
            'successful': len(successful),
            'total_data_processed_mb': sum(op['file_size_kb'] for op in ops) / 1024,
            'avg_duration_seconds': sum(durations) / len(durations),
            'operation_breakdown': self._count_by_operation(ops)
        }
    
    def _get_pdf_stats(self):
        """Calculate PDF operation statistics"""
        if not self.metrics['pdf_operations']:
            return None
        
        ops = self.metrics['pdf_operations']
        durations = [op['duration_seconds'] for op in ops]
        successful = [op for op in ops if op['success']]
        
        return {
            'total_operations': len(ops),
            'successful': len(successful),
            'total_pages_processed': sum(op['page_count'] for op in ops),
            'avg_duration_seconds': sum(durations) / len(durations),
            'total_duration_seconds': sum(durations),
            'operation_breakdown': self._count_by_operation(ops)
        }
    
    def _get_export_stats(self):
        """Calculate export statistics"""
        if not self.metrics['data_exports']:
            return None
        
        ops = self.metrics['data_exports']
        durations = [op['duration_seconds'] for op in ops]
        successful = [op for op in ops if op['success']]
        
        return {
            'total_exports': len(ops),
            'successful': len(successful),
            'total_rows_exported': sum(op['row_count'] for op in ops),
            'avg_duration_seconds': sum(durations) / len(durations),
            'format_breakdown': self._count_by_format(ops)
        }
    
    @staticmethod
    def _count_by_engine(operations):
        """Count operations by OCR engine"""
        engines = {}
        for op in operations:
            engine = op['engine']
            if engine not in engines:
                engines[engine] = 0
            engines[engine] += 1
        return engines
    
    @staticmethod
    def _count_by_operation(operations):
        """Count by operation type"""
        ops = {}
        for op in operations:
            op_type = op.get('operation_type') or op.get('operation')
            if op_type not in ops:
                ops[op_type] = 0
            ops[op_type] += 1
        return ops
    
    @staticmethod
    def _count_by_format(operations):
        """Count by format type"""
        formats = {}
        for op in operations:
            fmt = op['format']
            if fmt not in formats:
                formats[fmt] = 0
            formats[fmt] += 1
        return formats
    
    def export_report(self, filepath='performance_report.json'):
        """Export performance metrics to JSON file"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'raw_metrics': self.metrics
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Performance report exported to {filepath}")
        return filepath


# ============================================================================
# DECORATORS
# ============================================================================

def track_performance(operation_type):
    """Decorator to automatically track function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracker = PerformanceTracker()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log based on operation type
                if 'ocr' in operation_type.lower():
                    engine = kwargs.get('engine', 'unknown')
                    text_length = len(result) if isinstance(result, str) else 0
                    tracker.log_ocr_operation(engine, duration, text_length, True)
                elif 'batch' in operation_type.lower():
                    files = kwargs.get('files', [])
                    tracker.log_batch_operation(operation_type, len(files), duration, True)
                elif 'image' in operation_type.lower():
                    file_size = kwargs.get('file_size', 0)
                    tracker.log_image_operation(operation_type, file_size, duration, True)
                elif 'pdf' in operation_type.lower():
                    pages = kwargs.get('pages', 0)
                    tracker.log_pdf_operation(operation_type, pages, duration, True)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {operation_type}: {str(e)}")
                raise
        
        return wrapper
    return decorator


def measure_time(func):
    """Simple decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Starting {func.__name__}")
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.debug(f"Completed {func.__name__} in {duration:.2f}s")
        return result
    return wrapper


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Usage in your code:

from performance_monitor import PerformanceTracker, track_performance

# Get the singleton tracker
tracker = PerformanceTracker()

# Log operations
tracker.log_ocr_operation('paddleocr', 1.5, 500, True)
tracker.log_batch_operation('compress', 10, 5.2, True)
tracker.log_image_operation('resize', 250, 0.5, True)
tracker.log_pdf_operation('watermark', 20, 3.2, True)
tracker.log_data_export('pdf', 1000, 2.5, True)

# Get statistics
stats = tracker.get_statistics()
print(stats)

# Export report
tracker.export_report('performance_metrics.json')

# Use decorator on functions
@track_performance('ocr')
def extract_text(image_path, engine='paddleocr'):
    # Your code here
    pass
"""

if __name__ == '__main__':
    # Example usage
    tracker = PerformanceTracker()
    
    # Simulate some operations
    tracker.log_ocr_operation('paddleocr', 1.2, 450, True)
    tracker.log_ocr_operation('easyocr', 2.5, 450, True)
    tracker.log_batch_operation('compress', 5, 8.3, True)
    tracker.log_batch_operation('resize', 10, 15.2, True)
    tracker.log_image_operation('resize', 250, 0.8, True)
    tracker.log_pdf_operation('watermark', 15, 4.5, True)
    tracker.log_data_export('pdf', 500, 1.2, True)
    
    # Print statistics
    print("\n" + "="*60)
    print("PERFORMANCE STATISTICS")
    print("="*60)
    
    stats = tracker.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Export report
    tracker.export_report('performance_report.json')
    print("\nReport exported to performance_report.json")
