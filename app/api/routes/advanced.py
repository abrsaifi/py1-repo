"""Advanced features API endpoints"""
from flask import Blueprint, request, jsonify
from app.services.advanced_features import (
    CacheManager, BulkProcessor, PerformanceOptimizer,
    DataAggregator, DataQualityMetrics, ScheduledTasks, DataExporter
)
from app.services.database import DatabaseManager
from app.utils.logger_enhanced import OperationLogger
import pandas as pd
import tempfile
import os

bp = Blueprint('advanced', __name__)

@bp.route('/features/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached results"""
    try:
        CacheManager.clear_cache()
        return jsonify({'success': True, 'message': 'Cache cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/features/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    try:
        stats = {
            'cache_enabled': True,
            'default_ttl_hours': 24,
            'message': 'Cache system active'
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/features/quality-check', methods=['POST'])
def quality_check():
    """Check data quality metrics"""
    op_logger = OperationLogger('quality-check')
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        op_logger.log_start(filename=file.filename)
        
        # Read file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        file.save(temp_file.name)
        
        try:
            df = pd.read_csv(temp_file.name)
            metrics = DataQualityMetrics.get_quality_details(df)
            
            op_logger.log_success(rows=len(df), columns=len(df.columns))
            
            return jsonify({
                'success': True,
                'metrics': metrics
            }), 200
        finally:
            os.unlink(temp_file.name)
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/features/bulk-process', methods=['POST'])
def bulk_process():
    """Process multiple files in bulk"""
    op_logger = OperationLogger('bulk-process')
    try:
        files = request.files.getlist('files')
        operation = request.form.get('operation', 'duplicate-remover')
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        op_logger.log_start(file_count=len(files), operation=operation)
        
        # Process sync
        processor = BulkProcessor(operation, files, lambda: None)
        results, errors = processor.process_sync()
        
        op_logger.log_success(success_count=len(results), error_count=len(errors))
        
        return jsonify({
            'success': True,
            'results': {
                'processed': len(results),
                'failed': len(errors),
                'errors': errors
            }
        }), 200
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/features/merge-files', methods=['POST'])
def merge_files():
    """Merge multiple CSV/Excel files"""
    op_logger = OperationLogger('merge-files')
    try:
        files = request.files.getlist('files')
        file_type = request.form.get('type', 'csv')
        
        if not files or len(files) < 2:
            return jsonify({'error': 'At least 2 files required'}), 400
        
        op_logger.log_start(file_count=len(files), type=file_type)
        
        temp_files = []
        try:
            # Save files temporarily
            for file in files:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                file.save(temp_file.name)
                temp_files.append(temp_file.name)
            
            # Merge
            if file_type == 'csv':
                result_df, summary = DataAggregator.merge_csv_files(temp_files)
                merged_type = 'csv'
            else:
                result_df, summary = DataAggregator.merge_excel_files(temp_files)
                merged_type = 'xlsx'
            
            # Save result
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{merged_type}')
            if merged_type == 'csv':
                result_df.to_csv(output_file.name, index=False)
            else:
                result_df.to_excel(output_file.name, index=False)
            
            op_logger.log_success(rows_merged=len(result_df))
            
            return jsonify({
                'success': True,
                'merged_rows': len(result_df),
                'merged_columns': len(result_df.columns),
                'summary': summary
            }), 200
        
        finally:
            for f in temp_files:
                try:
                    os.unlink(f)
                except:
                    pass
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/features/export/<format>', methods=['POST'])
def export_data(format):
    """Export data in various formats"""
    op_logger = OperationLogger('export')
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        supported_formats = ['json', 'xml', 'parquet', 'html']
        if format not in supported_formats:
            return jsonify({'error': f'Unsupported format. Supported: {supported_formats}'}), 400
        
        op_logger.log_start(filename=file.filename, format=format)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        file.save(temp_file.name)
        
        try:
            df = pd.read_csv(temp_file.name)
            
            if format == 'json':
                result = DataExporter.export_json(df)
                mime_type = 'application/json'
            elif format == 'xml':
                result = DataExporter.export_xml(df)
                mime_type = 'application/xml'
            elif format == 'parquet':
                result = DataExporter.export_parquet(df)
                mime_type = 'application/octet-stream'
            else:  # html
                result = DataExporter.export_html(df)
                mime_type = 'text/html'
            
            op_logger.log_success(format=format)
            
            return jsonify({
                'success': True,
                'format': format,
                'size': len(result) if isinstance(result, (str, bytes)) else 0
            }), 200
        
        finally:
            os.unlink(temp_file.name)
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/features/performance/estimate', methods=['POST'])
def performance_estimate():
    """Estimate processing time and requirements"""
    try:
        file = request.files.get('file')
        operation = request.form.get('operation', 'duplicate-remover')
        
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        # Get file size
        file.seek(0, 2)
        file_size_mb = file.tell() / (1024 * 1024)
        file.seek(0)
        
        # Estimate
        chunk_size = PerformanceOptimizer.get_chunk_size(file_size_mb)
        threads = PerformanceOptimizer.get_thread_count(file_count=1)
        est_time = PerformanceOptimizer.estimate_processing_time(operation, file_size_mb)
        
        return jsonify({
            'success': True,
            'file_size_mb': round(file_size_mb, 2),
            'operation': operation,
            'estimated_time_seconds': est_time,
            'recommended_chunk_size': chunk_size,
            'recommended_threads': threads
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/features/jobs/schedule', methods=['POST'])
def schedule_job():
    """Schedule a task for later execution"""
    op_logger = OperationLogger('schedule-job')
    try:
        data = request.get_json()
        task_type = data.get('task_type')
        scheduled_time = data.get('scheduled_time')
        parameters = data.get('parameters', {})
        
        if not task_type:
            return jsonify({'error': 'task_type required'}), 400
        
        op_logger.log_start(task_type=task_type, scheduled_time=scheduled_time)
        
        job_id = ScheduledTasks.schedule_task(task_type, scheduled_time, parameters)
        
        op_logger.log_success(job_id=job_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'scheduled'
        }), 201
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/features/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    try:
        status = ScheduledTasks.get_task_status(job_id)
        
        if not status:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': status
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
