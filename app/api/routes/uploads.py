from flask import Blueprint, request, jsonify, send_file, current_app
import os
import tempfile
import shutil
import uuid
import zipfile
from pathlib import Path
import json
from app.utils.file_validator import sanitize_filename
from app.services.conversions import validate_image_file
from app.services.history import log_history

bp = Blueprint('uploads', __name__)


@bp.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    upload_id = request.form.get('upload_id') or request.headers.get('X-Upload-Id')
    filename = request.form.get('filename') or request.headers.get('X-Upload-Filename')
    try:
        index = int(request.form.get('index', 0))
    except Exception:
        index = 0
    try:
        total = int(request.form.get('total', -1))
    except Exception:
        total = -1

    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    if 'chunk' not in request.files:
        return jsonify({'success': False, 'error': 'no_chunk'}), 400

    if not upload_id:
        upload_id = str(uuid.uuid4())

    chunk_file = request.files['chunk']

    safe_uid = sanitize_filename(upload_id)
    if not safe_uid:
        safe_uid = uuid.uuid4().hex

    upload_dir = os.path.join(app.config.get('UPLOAD_CHUNKS_DIR', os.path.join(tempfile.gettempdir(), 'docpro_uploads')), safe_uid)
    os.makedirs(upload_dir, exist_ok=True)

    chunk_path = os.path.join(upload_dir, f'chunk_{index:06d}')
    chunk_file.save(chunk_path)

    meta_path = os.path.join(upload_dir, 'meta.json')
    try:
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
        meta.setdefault('filename', server.sanitize_filename(filename) or filename)
        if total > 0:
            meta['total'] = total
        with open(meta_path, 'w', encoding='utf-8') as mf:
            json.dump(meta, mf)
    except Exception:
        pass

    assembled = False
    assembled_path = None
    try:
        meta = {}
        if os.path.exists(os.path.join(upload_dir, 'meta.json')):
            with open(os.path.join(upload_dir, 'meta.json'), 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
        expected_total = meta.get('total', total)
        if expected_total and index >= expected_total - 1:
            assembled_path = os.path.join(upload_dir, sanitize_filename(filename) or Path(filename).name)
            total_size = 0
            for i in range(expected_total):
                part = os.path.join(upload_dir, f'chunk_{i:06d}')
                if not os.path.exists(part):
                    return jsonify({'success': False, 'error': 'missing_chunk', 'missing': i}), 500
                total_size += os.path.getsize(part)
                if total_size > int(app.config.get('UPLOAD_MAX_FILE_SIZE', 50 * 1024 * 1024)):
                    return jsonify({'success': False, 'error': 'file_too_large'}), 413
            with open(assembled_path, 'wb') as out_f:
                for i in range(expected_total):
                    part = os.path.join(upload_dir, f'chunk_{i:06d}')
                    with open(part, 'rb') as pf:
                        out_f.write(pf.read())
                    try:
                        os.remove(part)
                    except Exception:
                        pass
            assembled = True
    except Exception:
        assembled = False

    return jsonify({'success': True, 'upload_id': upload_id, 'filename': filename, 'assembled': assembled, 'assembled_path': assembled_path})


@bp.route('/convert-uploaded', methods=['POST'])
def convert_uploaded():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'success': False, 'error': 'invalid_json'}), 400

    uploads = data.get('uploads', [])
    target = (data.get('target_format') or '').lower()
    preset = data.get('preset')
    quality = int(data.get('quality', 85) or 85)
    lossless = bool(data.get('lossless', False))

    # PRESETS can be provided via app config
    PRESETS = app.config.get('PRESETS', {})
    if preset in PRESETS:
        quality = PRESETS[preset]['quality']
        lossless = PRESETS[preset]['lossless']

    if target not in ('jpg', 'jpeg', 'png', 'webp', 'tiff', 'tif'):
        return jsonify({'success': False, 'error': 'unsupported_target'}), 400

    temp_dir = tempfile.mkdtemp()
    converted = []
    try:
        for up in uploads:
            uid = up.get('upload_id')
            fname = up.get('filename')
            if not uid or not fname:
                continue
            safe_uid = sanitize_filename(uid)
            upload_dir = os.path.join(app.config.get('UPLOAD_CHUNKS_DIR', os.path.join(tempfile.gettempdir(), 'docpro_uploads')), safe_uid)
            assembled_path = os.path.join(upload_dir, sanitize_filename(fname) or Path(fname).name)
            ok, msg = validate_image_file(assembled_path)
            if not ok:
                continue

            out_ext = 'jpg' if target in ('jpg', 'jpeg') else ('tif' if target in ('tiff', 'tif') else target)
            out_name = f"{Path(fname).stem}_converted.{out_ext}"
            out_path = os.path.join(temp_dir, out_name)

            ok_conv = conversions.convert_image_format(assembled_path, out_path, target, quality=quality, lossless=lossless)
            if ok_conv:
                converted.append((out_name, out_path))

        if not converted:
            return jsonify({'success': False, 'error': 'no_converted_files'}), 500

        if len(converted) == 1:
            name, p = converted[0]
            return send_file(p, as_attachment=True, download_name=name)

        zip_path = os.path.join(temp_dir, 'converted_images.zip')
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for name, p in converted:
                zf.write(p, arcname=name)

        return send_file(zip_path, as_attachment=True, download_name='converted_images.zip')
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@bp.route('/upload-status', methods=['GET'])
def upload_status():
    if not server._check_api_key():
        return jsonify({'success': False, 'error': 'unauthorized'}), 401

    if server.is_rate_limited():
        return jsonify({'success': False, 'error': 'rate_limited'}), 429

    upload_id = request.args.get('upload_id')
    filename = request.args.get('filename')
    if not upload_id:
        return jsonify({'success': False, 'error': 'missing_upload_id'}), 400

    upload_dir = os.path.join(server.UPLOAD_CHUNKS_DIR, server.sanitize_filename(upload_id) or upload_id)
    if not os.path.exists(upload_dir):
        return jsonify({'success': True, 'chunks': [], 'total': None})

    chunks = []
    for name in os.listdir(upload_dir):
        if name.startswith('chunk_'):
            try:
                idx = int(name.split('_', 1)[1])
                chunks.append(idx)
            except Exception:
                pass
    chunks = sorted(chunks)
    total = None
    meta_path = os.path.join(upload_dir, 'meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
                total = meta.get('total')
        except Exception:
            total = None

    return jsonify({'success': True, 'chunks': chunks, 'total': total})


@bp.route('/admin/purge-uploads', methods=['POST'])
def admin_purge_uploads():
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    try:
        data = request.get_json(silent=True) or {}
        older_than = int(data.get('older_than', app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600)))
    except Exception:
        older_than = app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600)

    now = __import__('time').time()
    removed = 0
    base_dir = app.config.get('UPLOAD_CHUNKS_DIR', os.path.join(tempfile.gettempdir(), 'docpro_uploads'))
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        try:
            mtime = os.path.getmtime(path)
            if now - mtime > older_than:
                shutil.rmtree(path, ignore_errors=True)
                removed += 1
        except Exception:
            pass

    return jsonify({'success': True, 'removed': removed})
