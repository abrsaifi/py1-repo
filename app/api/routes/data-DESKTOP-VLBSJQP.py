from flask import Blueprint, request, jsonify, send_file, current_app
import tempfile
import os
import shutil
import json
import csv
import time
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import pandas as pd
from app.utils.file_validator import sanitize_filename, validate_file, get_file_size_mb
from app.services.history import log_history
from app.services.database import DatabaseManager, init_db
from app.utils.logger_enhanced import OperationLogger, AuditLogger

bp = Blueprint('data', __name__)

# Initialize database on blueprint import
try:
    init_db()
except:
    pass


@bp.route('/data/duplicate-remover', methods=['POST'])
def duplicate_remover():
    """Remove duplicate rows from CSV/Excel files"""
    op_logger = OperationLogger('duplicate-remover')
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    user_id = None
    record_id = None
    
    try:
        # Authentication
        if api_key:
            provided = request.headers.get('X-API-Key') or request.args.get('api_key')
            if provided != api_key:
                op_logger.log_error('Unauthorized access attempt')
                return jsonify({'success': False, 'error': 'unauthorized'}), 401
        
        f = request.files.get('file')
        
        # Validate file
        is_valid, error_msg = validate_file(f, ['csv', 'xlsx', 'xls', 'txt'])
        if not is_valid:
            op_logger.log_error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 400
        
        temp_dir = tempfile.mkdtemp()
        start_time = time.time()
        
        # Log operation start - get file size from file object
        file_size_mb = get_file_size_mb(f)
        op_logger.log_start(filename=f.filename, file_size_mb=file_size_mb)
        
        # Create database record
        record_id = DatabaseManager.add_conversion_record('duplicate-remover', f.filename, 'processing', user_id)
        
        try:
            safe_name = sanitize_filename(f.filename) or f.filename
            in_path = os.path.join(temp_dir, safe_name)
            f.save(in_path)
            
            ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''
            
            if ext in ['csv', 'txt']:
                df = pd.read_csv(in_path)
            elif ext in ['xlsx', 'xls']:
                df = pd.read_excel(in_path)
            else:
                raise ValueError(f'Unsupported format: {ext}')
            
            initial_rows = len(df)
            df_deduplicated = df.drop_duplicates()
            removed_rows = initial_rows - len(df_deduplicated)
            
            out_name = f"{Path(safe_name).stem}_no_duplicates.{ext if ext in ['csv', 'xlsx'] else 'xlsx'}"
            out_path = os.path.join(temp_dir, out_name)
            
            if ext == 'csv':
                df_deduplicated.to_csv(out_path, index=False)
            else:
                df_deduplicated.to_excel(out_path, index=False)
            
            duration_ms = (time.time() - start_time) * 1000
            output_size_mb = get_file_size_mb(out_path)
            
            # Update database record
            DatabaseManager.update_conversion_record(record_id, 'success', out_name, 
                                                    int(output_size_mb * 1024), duration_ms=duration_ms)
            DatabaseManager.update_analytics('duplicate-remover', True, output_size_mb)
            
            # Log operation success
            op_logger.log_success(removed_rows=removed_rows, output_file=out_name)
            
            try:
                log_history(app.config.get('HISTORY_DB', 'conversion_history.db'), 
                           'duplicate_remover', [f.filename], status='success')
            except Exception:
                pass
            
            # Send file and return response directly (cleanup in finally will happen after response is sent)
            return send_file(out_path, as_attachment=True, download_name=out_name, mimetype='text/csv' if ext == 'csv' else 'application/vnd.ms-excel')
        
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
    
    except Exception as e:
        op_logger.log_error(str(e), exception_type=type(e).__name__)
        
        if record_id:
            DatabaseManager.update_conversion_record(record_id, 'failed', error_message=str(e))
        DatabaseManager.update_analytics('duplicate-remover', False)
        
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/data/validate', methods=['POST'])
def data_validator():
    """Validate data quality and format"""
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        safe_name = sanitize_filename(f.filename) or f.filename
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''

        if ext in ['csv', 'txt']:
            df = pd.read_csv(in_path)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(in_path)
        else:
            return jsonify({'success': False, 'error': 'unsupported_format'}), 400

        # Validation checks
        validation_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'duplicate_rows': len(df) - len(df.drop_duplicates()),
            'quality_score': 0
        }

        # Calculate quality score (0-100)
        missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100 if len(df) > 0 else 0
        quality_score = max(0, 100 - (missing_pct + duplicate_pct))
        validation_report['quality_score'] = round(quality_score, 2)

        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'),
                       'data_validator', [f.filename], status='success')
        except Exception:
            pass

        return jsonify({'success': True, 'report': validation_report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@bp.route('/data/export-pdf', methods=['POST'])
def pdf_export():
    """Export data to PDF with custom formatting"""
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        safe_name = sanitize_filename(f.filename) or f.filename
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''

        if ext in ['csv', 'txt']:
            df = pd.read_csv(in_path)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(in_path)
        else:
            return jsonify({'success': False, 'error': 'unsupported_format'}), 400

        # Generate PDF report using reportlab
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors

            out_name = f"{Path(safe_name).stem}_export.pdf"
            out_path = os.path.join(temp_dir, out_name)

            doc = SimpleDocTemplate(out_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=20
            )
            story.append(Paragraph(f"Data Export Report: {Path(safe_name).stem}", title_style))
            story.append(Spacer(1, 0.3 * inch))

            # Add table
            data = [list(df.columns)] + df.values.tolist()
            table = Table(data, colWidths=[letter[0] / len(df.columns) - 0.2 * inch] * len(df.columns))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)

            doc.build(story)

            try:
                log_history(app.config.get('HISTORY_DB', 'conversion_history.db'),
                           'pdf_export', [f.filename], status='success')
            except Exception:
                pass

            return send_file(out_path, as_attachment=True, download_name=out_name)
        except ImportError:
            return jsonify({'success': False, 'error': 'reportlab_not_installed'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@bp.route('/data/reporting', methods=['POST'])
def basic_reporting():
    """Generate charts and summaries from data"""
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        safe_name = sanitize_filename(f.filename) or f.filename
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''

        if ext in ['csv', 'txt']:
            df = pd.read_csv(in_path)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(in_path)
        else:
            return jsonify({'success': False, 'error': 'unsupported_format'}), 400

        # Generate summary statistics
        report = {
            'file_name': safe_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'summary_statistics': {}
        }

        # Calculate summary stats for numerical columns
        for col in df.select_dtypes(include=['number']).columns:
            report['summary_statistics'][col] = {
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
            }

        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'),
                       'basic_reporting', [f.filename], status='success')
        except Exception:
            pass

        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@bp.route('/data/database-connect', methods=['POST'])
def database_integration():
    """Connect to database and sync data"""
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    try:
        data = request.get_json() or {}
        db_type = data.get('db_type', '')  # mysql, postgresql, mongodb, etc.
        host = data.get('host', '')
        port = data.get('port', '')
        database = data.get('database', '')
        username = data.get('username', '')
        # Note: password should never be stored, only used for connection
        
        if not all([db_type, host, database]):
            return jsonify({'success': False, 'error': 'missing_credentials'}), 400

        # This is a demonstration endpoint
        # In production, you'd validate and create actual connections
        connection_info = {
            'status': 'ready',
            'db_type': db_type,
            'host': host,
            'port': port or 'default',
            'database': database,
            'username': username,
            'message': 'Database connection configured. Ready for data sync operations.'
        }

        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'),
                       'database_integration', [f"DB:{database}"], status='success')
        except Exception:
            pass

        return jsonify({'success': True, 'connection': connection_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
