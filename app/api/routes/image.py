from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
import shutil
import zipfile
from pathlib import Path
from app.services import conversions
from app.services.history import log_history
from app.services.conversions import convert_image_format, _generate_preview_from_pdf
from app.utils.file_validator import sanitize_filename
from flask import current_app

bp = Blueprint('image', __name__)


@bp.route('/image/convert', methods=['POST'])
def convert_image():
    # API key and rate limiting are still provided by legacy `server.py` until
    # we fully migrate those helpers. Fall back to checking app config here.
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    files = request.files.getlist('file') or []
    if not files:
        return jsonify({'success': False, 'error': 'no_file'}), 400

    target = request.form.get('target_format', '').strip().lower()
    try:
        quality = int(request.form.get('quality', 85) or 85)
    except Exception:
        quality = 85
    lossless = request.form.get('lossless', 'false').lower() in ('1', 'true', 'on')

    if target not in ('jpg', 'jpeg', 'png', 'webp', 'tiff', 'tif'):
        return jsonify({'success': False, 'error': 'unsupported_target'}), 400

    temp_dir = tempfile.mkdtemp()
    converted = []
    try:
        for f in files:
            if not f or f.filename == '':
                continue
            if not conversions.IMAGE_ALLOWED_EXTENSIONS:
                # defensive: ensure constant exists
                pass
            if not sanitize_filename(f.filename):
                continue
            safe_name = sanitize_filename(f.filename) or f.filename
            in_path = os.path.join(temp_dir, safe_name)
            f.save(in_path)

            out_ext = 'jpg' if target in ('jpg', 'jpeg') else ('tif' if target in ('tiff', 'tif') else target)
            base_name = Path(f.filename).stem
            out_name = f"{base_name}_converted.{out_ext}"
            out_path = os.path.join(temp_dir, out_name)

            ok = convert_image_format(in_path, out_path, target, quality=quality, lossless=lossless)
            if ok and os.path.exists(out_path):
                converted.append((out_name, out_path))

        if not converted:
            return jsonify({'success': False, 'error': 'no_converted_files'}), 500

        if len(converted) == 1:
            name, p = converted[0]
            try:
                log_history(app.config.get('HISTORY_DB', 'conversion_history.db'), 'image_convert', [files[0].filename, target], status='success')
            except Exception:
                pass
            return send_file(p, as_attachment=True, download_name=name)

        zip_path = os.path.join(temp_dir, 'converted_images.zip')
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for name, p in converted:
                zf.write(p, arcname=name)

        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'), 'image_convert_batch', [f.filename for f in files], status='success')
        except Exception:
            pass
        return send_file(zip_path, as_attachment=True, download_name='converted_images.zip')
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@bp.route('/image/compress', methods=['POST'])
def compress_image():
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400
    if not server.allowed_file(f.filename, 'image'):
        return jsonify({'success': False, 'error': 'unsupported_file_type'}), 400

    try:
        quality = int(request.form.get('quality', 85) or 85)
    except Exception:
        quality = 85

    temp_dir = tempfile.mkdtemp()
    try:
        safe_name = sanitize_filename(f.filename) or f.filename
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        ext = Path(safe_name).suffix.lstrip('.').lower()
        out_name = f"{Path(safe_name).stem}_compressed.{ext}"
        out_path = os.path.join(temp_dir, out_name)

        ok = convert_image_format(in_path, out_path, ext, quality=quality, lossless=False)
        if not ok or not os.path.exists(out_path):
            return jsonify({'success': False, 'error': 'compression_failed'}), 500
        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'), 'compress_image', [f.filename], status='success')
        except Exception:
            pass
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
