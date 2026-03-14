from flask import Blueprint, request, jsonify, send_file, current_app
import io
import os
import tempfile
import shutil
import uuid
import zipfile
from pathlib import Path
import json
import fitz
from pypdf import PdfReader
from app.utils.file_validator import sanitize_filename
from app.services import conversions
from app.services.advanced import add_watermark, ocr_extract_text as advanced_ocr_extract_text, parse_page_numbers
from app.services.conversions import validate_image_file
from app.services.data_tools import (
    clean_charts_workbook,
    database_export_file,
    dataset_validation_report,
    formulas_to_values_file,
    normalize_dataset_file,
    pdf_export_file,
    read_history_records,
    reporting_output_file,
    split_sheet_outputs,
    write_json_file,
)
from services.document_conversion import text_to_pdf
from services.image_processing import pdf_to_true_bw
from services.pdf_tools import (
    clean_autoformat_pdf,
    decrypt_pdf,
    encrypt_pdf,
    extract_pdf_pages,
    merge_pdf,
    pdf_remove_metadata,
    redact_pdf,
    remove_pages_from_pdf,
    split_pdf,
)

bp = Blueprint('uploads', __name__)


GENERIC_TARGET_MIME_TYPES = {
    'csv': 'text/csv',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'html': 'text/html',
    'json': 'application/json',
    'mp3': 'audio/mpeg',
    'mp4': 'video/mp4',
    'pdf': 'application/pdf',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'sql': 'text/plain; charset=utf-8',
    'txt': 'text/plain; charset=utf-8',
    'wav': 'audio/wav',
    'webm': 'video/webm',
    'xml': 'application/xml',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'zip': 'application/zip',
}

GENERIC_TARGETS = (
    conversions.IMAGE_ALLOWED_EXTENSIONS
    | conversions.PDF_ALLOWED_EXTENSIONS
    | conversions.AUDIO_ALLOWED_EXTENSIONS
    | conversions.VIDEO_ALLOWED_EXTENSIONS
    | {'csv', 'docx', 'html', 'pptx', 'xlsx'}
)


PDF_TOOL_ALIASES = {
    'compress-pdf': 'clean-pdf',
    'compress-pdf-lossless': 'clean-pdf',
    'decrypt-pdf-remove': 'decrypt-pdf',
    'encrypt-pdf-aes256': 'encrypt-pdf',
    'merge-pdf-smart': 'merge-pdf',
    'redact-pdf-permanent': 'redact-pdf',
    'remove-pages-range': 'remove-pages',
    'split-pdf-batch': 'split-pdf',
    'watermark-image-text': 'watermark-pdf',
}

PDF_ACTION_TOOLS = {
    'clean-pdf',
    'decrypt-pdf',
    'encrypt-pdf',
    'extract-pdf',
    'merge-pdf',
    'redact-pdf',
    'remove-pages',
    'split-pdf',
    'watermark-pdf',
}

SPECIAL_TOOL_ALIASES = {
    'clean-deskew': 'clean-deskew',
    'convert-history': 'convert-history',
    'csv-to-excel': 'csv-to-excel',
    'data-validator': 'data-validator',
    'database-export': 'database-export',
    'extract-extended': 'extract-extended',
    'formulas-to-values': 'formulas-to-values',
    'metadata-clean': 'metadata-cleaner',
    'no-colors': 'no-colors',
    'normalize-data': 'normalize-data',
    'ocr-searchable': 'ocr-searchable',
    'pdf-ocr': 'pdf-ocr',
    'pdf-to-bw-pro': 'pdf-to-bw',
    'pdf-export': 'pdf-export',
    'reporting': 'reporting',
    'split-sheets': 'split-sheets',
}

SPECIAL_TOOL_SLUGS = {
    'bulk-convert',
    'clean-charts',
    'create-zip',
    'convert-history',
    'csv-to-excel',
    'data-validator',
    'database-export',
    'extract-extended',
    'formulas-to-values',
    'json-formatter',
    'metadata-cleaner',
    'no-colors',
    'normalize-data',
    'ocr-searchable',
    'pdf-ocr',
    'pdf-to-bw',
    'pdf-export',
    'reporting',
    'split-sheets',
    'text-formatter',
    'text-to-pdf',
    'zip-extractor',
    *SPECIAL_TOOL_ALIASES.keys(),
}


def _app():
    return current_app._get_current_object()


def _upload_chunks_dir(app):
    return app.config.get('UPLOAD_CHUNKS_DIR', os.path.join(tempfile.gettempdir(), 'docpro_uploads'))


def _require_upload_api_key(app):
    api_key = app.config.get('UPLOAD_API_KEY')
    if not api_key:
        return None

    provided = request.headers.get('X-API-Key') or request.args.get('api_key')
    if provided != api_key:
        return jsonify({'success': False, 'error': 'unauthorized'}), 401

    return None


def _send_path_bytes(path, download_name, mimetype=None):
    with open(path, 'rb') as file_handle:
        payload = io.BytesIO(file_handle.read())
    payload.seek(0)
    return send_file(payload, as_attachment=True, download_name=download_name, mimetype=mimetype)


def _coerce_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'on'}
    return bool(value)


def _coerce_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _coerce_float(value, default):
    try:
        return float(value)
    except Exception:
        return default


def _resolve_target_format(target, parameters):
    if target:
        return target.lower().lstrip('.')

    for key in ('output_format', 'format'):
        candidate = parameters.get(key)
        if candidate:
            return str(candidate).lower().lstrip('.')

    return ''


def _normalize_conversion_parameters(parameters, preset_config=None):
    normalized = dict(parameters or {})
    preset_config = preset_config or {}

    if 'quality' not in normalized:
        normalized['quality'] = normalized.get('image_quality', preset_config.get('quality', 85))
    normalized['quality'] = _coerce_int(normalized.get('quality'), 85)

    if 'lossless' not in normalized:
        normalized['lossless'] = normalized.get('compression') == 'none' or preset_config.get('lossless', False)
    normalized['lossless'] = _coerce_bool(normalized.get('lossless'), False)

    normalized['timeout'] = _coerce_int(normalized.get('timeout'), 120)

    return normalized


def _resolve_uploaded_path(app, upload):
    uid = upload.get('upload_id')
    fname = upload.get('filename')
    if not uid or not fname:
        return None

    safe_uid = sanitize_filename(uid)
    upload_dir = os.path.join(_upload_chunks_dir(app), safe_uid)
    assembled_path = os.path.join(upload_dir, sanitize_filename(fname) or Path(fname).name)
    if not os.path.exists(assembled_path):
        return None

    return fname, assembled_path


def _send_outputs(outputs, archive_name):
    if len(outputs) == 1:
        name, path = outputs[0]
        mimetype = GENERIC_TARGET_MIME_TYPES.get(Path(name).suffix.lower().lstrip('.'))
        return _send_path_bytes(path, name, mimetype=mimetype)

    zip_buffer_path = os.path.join(tempfile.mkdtemp(), archive_name)
    try:
        with zipfile.ZipFile(zip_buffer_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for name, path in outputs:
                zf.write(path, arcname=name)
        return _send_path_bytes(zip_buffer_path, archive_name, mimetype='application/zip')
    finally:
        try:
            shutil.rmtree(os.path.dirname(zip_buffer_path))
        except Exception:
            pass


def _read_text_file(path):
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as handle:
        return handle.read()


def _extract_text_from_pdf(input_path, max_pages=None):
    extracted_parts = []
    try:
        document = fitz.open(input_path)
        page_total = len(document)
        page_limit = page_total if max_pages is None else min(page_total, max_pages)
        for page_index in range(page_limit):
            text = document[page_index].get_text('text').strip()
            if text:
                extracted_parts.append(text)
        document.close()
    except Exception:
        extracted_parts = []

    if extracted_parts:
        return '\n\n'.join(extracted_parts)

    ocr_text = advanced_ocr_extract_text(input_path, max_pages=max_pages)
    return ocr_text if ocr_text is not None else ''


def _write_text_output(path, content):
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(content)


def _resolve_data_output_format(parameters, default='xlsx'):
    output_format = str(parameters.get('output_format') or parameters.get('format') or default).strip().lower()
    return output_format.lstrip('.') or default


def _process_special_tool(tool_slug, uploads, parameters, temp_dir):
    action_slug = SPECIAL_TOOL_ALIASES.get(tool_slug, tool_slug)
    if action_slug == 'convert-history':
        records = read_history_records(_app().config.get('HISTORY_DB', 'conversion_history.db'))
        output_name = 'convert_history.json'
        output_path = os.path.join(temp_dir, output_name)
        write_json_file({'count': len(records), 'records': records}, output_path)
        return [(output_name, output_path)], None

    upload_paths = [resolved for resolved in (_resolve_uploaded_path(_app(), upload) for upload in uploads) if resolved]
    if not upload_paths:
        return None, ('missing_uploads', 400)

    if action_slug == 'create-zip':
        archive_name = f"{Path(upload_paths[0][0]).stem}_bundle.zip"
        archive_path = os.path.join(temp_dir, archive_name)
        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for filename, input_path in upload_paths:
                zf.write(input_path, arcname=Path(filename).name)
        return [(archive_name, archive_path)], None

    filename, input_path = upload_paths[0]
    stem = Path(filename).stem

    if action_slug == 'zip-extractor':
        extracted_outputs = []
        extract_dir = os.path.join(temp_dir, f"extract_{uuid.uuid4().hex}")
        os.makedirs(extract_dir, exist_ok=True)
        try:
            with zipfile.ZipFile(input_path) as zf:
                for member in zf.infolist():
                    if member.is_dir():
                        continue
                    extracted_name = Path(member.filename).name
                    if not extracted_name:
                        continue
                    output_path = os.path.join(extract_dir, sanitize_filename(extracted_name) or extracted_name)
                    with zf.open(member) as source, open(output_path, 'wb') as target_handle:
                        shutil.copyfileobj(source, target_handle)
                    extracted_outputs.append((extracted_name, output_path))
        except Exception:
            return None, ('zip_extract_failed', 500)
        if not extracted_outputs:
            return None, ('zip_extract_failed', 500)
        return extracted_outputs, None

    if action_slug == 'text-to-pdf':
        output_name = f"{stem}_converted.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not text_to_pdf(_read_text_file(input_path), output_path, font_size=_coerce_int(parameters.get('font_size'), 11)):
            return None, ('text_to_pdf_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'csv-to-excel':
        output_name = f"{stem}_converted.xlsx"
        output_path = os.path.join(temp_dir, output_name)
        try:
            result = conversions.ConversionService.convert(input_path, 'xlsx', {'output_path': output_path})
        except Exception:
            result = None
        if not result or not os.path.exists(output_path):
            return None, ('csv_to_excel_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'text-formatter':
        lines = [line.rstrip() for line in _read_text_file(input_path).splitlines()]
        formatted_text = '\n'.join(lines).strip() + ('\n' if lines else '')
        output_name = f"{stem}_formatted.txt"
        output_path = os.path.join(temp_dir, output_name)
        _write_text_output(output_path, formatted_text)
        return [(output_name, output_path)], None

    if action_slug == 'json-formatter':
        output_name = f"{stem}_formatted.json"
        output_path = os.path.join(temp_dir, output_name)
        try:
            parsed = json.loads(_read_text_file(input_path))
        except Exception:
            return None, ('invalid_json', 400)
        _write_text_output(output_path, json.dumps(parsed, indent=2, ensure_ascii=False) + '\n')
        return [(output_name, output_path)], None

    if action_slug == 'pdf-to-bw':
        output_name = f"{stem}_bw.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not pdf_to_true_bw(
            input_path,
            output_path,
            dpi=_coerce_int(parameters.get('dpi'), 300),
            threshold=_coerce_int(parameters.get('threshold'), 250),
            contrast=_coerce_float(parameters.get('contrast'), 3.0),
            sharpness=_coerce_float(parameters.get('sharpness'), 2.5),
            brightness=_coerce_int(parameters.get('brightness'), 0),
            gamma=_coerce_float(parameters.get('gamma'), 1.0),
            blur=_coerce_float(parameters.get('blur'), 0.0),
            invert=_coerce_bool(parameters.get('invert'), False),
            denoise=_coerce_int(parameters.get('denoise'), 0),
        ):
            return None, ('pdf_to_bw_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'clean-deskew':
        output_name = f"{stem}_deskewed.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not clean_autoformat_pdf(input_path, output_path):
            return None, ('clean_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'metadata-cleaner':
        output_name = f"{stem}_metadata_cleaned.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not pdf_remove_metadata(input_path, output_path):
            return None, ('metadata_clean_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'no-colors':
        intermediate_pdf = input_path
        if Path(input_path).suffix.lower() != '.pdf':
            intermediate_pdf = os.path.join(temp_dir, f"{stem}_source.pdf")
            try:
                conversions.ConversionService.convert(input_path, 'pdf', {'output_path': intermediate_pdf})
            except Exception:
                return None, ('no_colors_source_failed', 500)
        output_name = f"{stem}_grayscale.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not pdf_to_true_bw(intermediate_pdf, output_path):
            return None, ('no_colors_failed', 500)
        return [(output_name, output_path)], None

    if action_slug in {'pdf-ocr', 'extract-extended'}:
        max_pages = _coerce_int(parameters.get('max_pages'), None)
        extracted_text = _extract_text_from_pdf(input_path, max_pages=max_pages)
        output_name = f"{stem}_{'ocr' if action_slug == 'pdf-ocr' else 'extracted'}.txt"
        output_path = os.path.join(temp_dir, output_name)
        _write_text_output(output_path, extracted_text)
        return [(output_name, output_path)], None

    if action_slug == 'ocr-searchable':
        max_pages = _coerce_int(parameters.get('max_pages'), None)
        extracted_text = _extract_text_from_pdf(input_path, max_pages=max_pages)
        output_name = f"{stem}_searchable.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not text_to_pdf(extracted_text or f'No text could be extracted from {filename}.', output_path):
            return None, ('ocr_pdf_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'split-sheets':
        output_format = _resolve_data_output_format(parameters, default='separate-files')
        actual_output_format = 'csv' if output_format == 'csv' else 'xlsx'
        outputs = split_sheet_outputs(input_path, temp_dir, output_format=actual_output_format)
        if not outputs:
            return None, ('split_sheets_failed', 500)
        return outputs, None

    if action_slug == 'formulas-to-values':
        output_name = f"{stem}_static.xlsx"
        output_path = os.path.join(temp_dir, output_name)
        if not formulas_to_values_file(input_path, output_path):
            return None, ('formulas_to_values_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'clean-charts':
        output_name = f"{stem}_cleaned.xlsx"
        output_path = os.path.join(temp_dir, output_name)
        if not clean_charts_workbook(input_path, output_path):
            return None, ('clean_charts_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'normalize-data':
        output_format = _resolve_data_output_format(parameters, default='xlsx')
        file_extension = 'csv' if output_format == 'csv' else 'xlsx'
        output_name = f"{stem}_normalized.{file_extension}"
        output_path = os.path.join(temp_dir, output_name)
        if not normalize_dataset_file(
            input_path,
            output_path,
            method=str(parameters.get('method') or 'min-max'),
            handle_missing=str(parameters.get('handle_missing') or 'mean'),
            round_decimals=_coerce_int(parameters.get('round_decimals'), 4),
            output_format=file_extension,
        ):
            return None, ('normalize_data_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'data-validator':
        report = dataset_validation_report(input_path)
        output_name = f"{stem}_validation.json"
        output_path = os.path.join(temp_dir, output_name)
        write_json_file(report, output_path)
        return [(output_name, output_path)], None

    if action_slug == 'pdf-export':
        output_name = f"{stem}_export.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not pdf_export_file(input_path, output_path):
            return None, ('pdf_export_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'reporting':
        output_format = _resolve_data_output_format(parameters, default='pdf')
        output_name = f"{stem}_report.{output_format}"
        output_path = os.path.join(temp_dir, output_name)
        if not reporting_output_file(
            input_path,
            output_path,
            report_type=str(parameters.get('reportType') or 'summary'),
            output_format=output_format,
        ):
            return None, ('reporting_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'database-export':
        output_format = _resolve_data_output_format(parameters, default='csv')
        if output_format not in {'csv', 'json', 'xlsx'}:
            output_format = 'csv'
        output_name = f"{stem}_database_export.{output_format}"
        output_path = os.path.join(temp_dir, output_name)
        if not database_export_file(input_path, output_path, target_format=output_format):
            return None, ('database_export_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'bulk-convert':
        output_format = _resolve_data_output_format(parameters, default='pdf')
        converted_outputs = []
        for bulk_filename, bulk_input_path in upload_paths:
            bulk_output_name = f"{Path(bulk_filename).stem}_bulk.{output_format}"
            bulk_output_path = os.path.join(temp_dir, bulk_output_name)
            try:
                result = conversions.ConversionService.convert(
                    bulk_input_path,
                    output_format,
                    {
                        **parameters,
                        'output_path': bulk_output_path,
                    },
                )
            except Exception:
                result = None
            if result and os.path.exists(bulk_output_path):
                converted_outputs.append((bulk_output_name, bulk_output_path))
        if not converted_outputs:
            return None, ('bulk_convert_failed', 500)
        return converted_outputs, None

    return None, ('unsupported_special_tool', 400)


def _parse_page_ranges(page_input):
    if not page_input:
        return None

    if isinstance(page_input, (list, tuple)):
        page_ranges = []
        for item in page_input:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                start = _coerce_int(item[0], 0)
                end = _coerce_int(item[1], 0)
                if start > 0 and end >= start:
                    page_ranges.append((start, end))
        return page_ranges or None

    segments = []
    for token in str(page_input).split(','):
        part = token.strip()
        if not part:
            continue
        if '-' in part:
            start_text, end_text = part.split('-', 1)
            start = _coerce_int(start_text, 0)
            end = _coerce_int(end_text, 0)
        else:
            start = _coerce_int(part, 0)
            end = start
        if start > 0 and end >= start:
            segments.append((start, end))

    return segments or None


def _get_split_ranges(input_path, parameters):
    split_mode = str(parameters.get('split_mode') or 'individual').strip().lower()
    if split_mode == 'ranges':
        ranges = _parse_page_ranges(
            parameters.get('page_ranges')
            or parameters.get('ranges')
            or parameters.get('pages')
        )
        if ranges:
            return ranges

    page_count = len(PdfReader(input_path).pages)
    return [(index, index) for index in range(1, page_count + 1)]


def _parse_keywords(parameters):
    raw_keywords = (
        parameters.get('keywords')
        or parameters.get('redaction_text')
        or parameters.get('text')
        or parameters.get('find_text')
    )
    if not raw_keywords:
        return []

    if isinstance(raw_keywords, (list, tuple)):
        return [str(keyword).strip() for keyword in raw_keywords if str(keyword).strip()]

    keywords = []
    for line in str(raw_keywords).replace('\n', ',').split(','):
        keyword = line.strip()
        if keyword:
            keywords.append(keyword)
    return keywords


def _process_pdf_action(tool_slug, uploads, parameters, temp_dir):
    action_slug = PDF_TOOL_ALIASES.get(tool_slug, tool_slug)
    upload_paths = [resolved for resolved in (_resolve_uploaded_path(_app(), upload) for upload in uploads) if resolved]
    if not upload_paths:
        return None, ('missing_uploads', 400)

    if action_slug == 'merge-pdf':
        if len(upload_paths) < 2:
            return None, ('merge_requires_multiple_pdfs', 400)
        merged_name = f"{Path(upload_paths[0][0]).stem}_merged.pdf"
        merged_path = os.path.join(temp_dir, merged_name)
        if not merge_pdf([path for _, path in upload_paths], merged_path):
            return None, ('merge_failed', 500)
        return [(merged_name, merged_path)], None

    if action_slug == 'split-pdf':
        split_outputs = []
        for filename, input_path in upload_paths:
            split_dir = os.path.join(temp_dir, f"split_{uuid.uuid4().hex}")
            os.makedirs(split_dir, exist_ok=True)
            ranges = _get_split_ranges(input_path, parameters)
            result_paths = split_pdf(input_path, split_dir, ranges)
            if not result_paths:
                return None, ('split_failed', 500)
            stem = Path(filename).stem
            for index, result_path in enumerate(result_paths, start=1):
                split_outputs.append((f"{stem}_part_{index}.pdf", result_path))
        return split_outputs, None

    filename, input_path = upload_paths[0]
    stem = Path(filename).stem

    if action_slug == 'extract-pdf':
        pages = parse_page_numbers(parameters.get('pages') or parameters.get('page_numbers') or parameters.get('extract_pages'))
        if not pages:
            return None, ('missing_pages', 400)
        output_name = f"{stem}_extracted.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not extract_pdf_pages(input_path, output_path, [page + 1 for page in pages]):
            return None, ('extract_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'remove-pages':
        pages = parse_page_numbers(parameters.get('pages_to_remove') or parameters.get('pages'))
        if not pages:
            return None, ('missing_pages', 400)
        output_name = f"{stem}_pages_removed.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not remove_pages_from_pdf(input_path, [page + 1 for page in pages], output_path):
            return None, ('remove_pages_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'encrypt-pdf':
        password = str(parameters.get('password') or parameters.get('user_password') or '').strip()
        if not password:
            return None, ('missing_password', 400)
        output_name = f"{stem}_encrypted.pdf"
        output_path = os.path.join(temp_dir, output_name)
        encrypted, _ = encrypt_pdf(input_path, output_path, password)
        if not encrypted:
            return None, ('encrypt_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'decrypt-pdf':
        password = str(parameters.get('password') or parameters.get('user_password') or '').strip()
        if not password:
            return None, ('missing_password', 400)
        output_name = f"{stem}_decrypted.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not decrypt_pdf(input_path, output_path, password):
            return None, ('decrypt_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'watermark-pdf':
        watermark_text = str(parameters.get('watermark_text') or parameters.get('text') or parameters.get('watermark') or '').strip()
        if not watermark_text:
            return None, ('missing_watermark_text', 400)
        output_name = f"{stem}_watermarked.pdf"
        output_path = os.path.join(temp_dir, output_name)
        pages = parse_page_numbers(parameters.get('pages'))
        if not add_watermark(
            input_path,
            output_path,
            watermark_text,
            pages=pages,
            rotation=_coerce_int(parameters.get('rotation'), 45),
            opacity=float(parameters.get('opacity', 0.2) or 0.2),
            fontsize=_coerce_int(parameters.get('font_size'), 60),
        ):
            return None, ('watermark_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'redact-pdf':
        keywords = _parse_keywords(parameters)
        if not keywords:
            return None, ('missing_keywords', 400)
        output_name = f"{stem}_redacted.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not redact_pdf(input_path, output_path, keywords):
            return None, ('redact_failed', 500)
        return [(output_name, output_path)], None

    if action_slug == 'clean-pdf':
        output_name = f"{stem}_cleaned.pdf"
        output_path = os.path.join(temp_dir, output_name)
        if not clean_autoformat_pdf(input_path, output_path):
            return None, ('clean_failed', 500)
        return [(output_name, output_path)], None

    return None, ('unsupported_pdf_tool', 400)


@bp.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    app = _app()
    auth_error = _require_upload_api_key(app)
    if auth_error:
        return auth_error

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

    if 'chunk' not in request.files:
        return jsonify({'success': False, 'error': 'no_chunk'}), 400

    if not upload_id:
        upload_id = str(uuid.uuid4())

    if not filename:
        filename = request.files['chunk'].filename or f'{upload_id}.bin'

    chunk_file = request.files['chunk']

    safe_uid = sanitize_filename(upload_id)
    if not safe_uid:
        safe_uid = uuid.uuid4().hex

    upload_dir = os.path.join(_upload_chunks_dir(app), safe_uid)
    os.makedirs(upload_dir, exist_ok=True)

    chunk_path = os.path.join(upload_dir, f'chunk_{index:06d}')
    chunk_file.save(chunk_path)

    meta_path = os.path.join(upload_dir, 'meta.json')
    try:
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
        meta.setdefault('filename', sanitize_filename(filename) or Path(filename).name)
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
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as mf:
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
    app = _app()
    auth_error = _require_upload_api_key(app)
    if auth_error:
        return auth_error

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'success': False, 'error': 'invalid_json'}), 400

    uploads = data.get('uploads', [])
    parameters = dict(data.get('parameters') or {})
    tool_slug = str(data.get('tool_slug') or '').strip()
    if 'quality' in data and 'quality' not in parameters:
        parameters['quality'] = data.get('quality')
    if 'lossless' in data and 'lossless' not in parameters:
        parameters['lossless'] = data.get('lossless')
    target = _resolve_target_format(data.get('target_format'), parameters)
    preset = data.get('preset')

    presets = app.config.get('PRESETS', {})
    preset_config = presets.get(preset, {}) if preset else {}
    conversion_parameters = _normalize_conversion_parameters(parameters, preset_config)

    normalized_tool_slug = PDF_TOOL_ALIASES.get(tool_slug, tool_slug)
    if normalized_tool_slug in PDF_ACTION_TOOLS:
        temp_dir = tempfile.mkdtemp()
        try:
            outputs, error = _process_pdf_action(tool_slug, uploads, conversion_parameters, temp_dir)
            if error:
                message, status_code = error
                return jsonify({'success': False, 'error': message}), status_code
            return _send_outputs(outputs, f'{normalized_tool_slug}.zip')
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    normalized_special_slug = SPECIAL_TOOL_ALIASES.get(tool_slug, tool_slug)
    if normalized_special_slug in SPECIAL_TOOL_SLUGS:
        temp_dir = tempfile.mkdtemp()
        try:
            outputs, error = _process_special_tool(tool_slug, uploads, conversion_parameters, temp_dir)
            if error:
                message, status_code = error
                return jsonify({'success': False, 'error': message}), status_code
            return _send_outputs(outputs, f'{normalized_special_slug}.zip')
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    if not target:
        return jsonify({'success': False, 'error': 'missing_target'}), 400

    if target not in GENERIC_TARGETS:
        return jsonify({'success': False, 'error': 'unsupported_target'}), 400

    temp_dir = tempfile.mkdtemp()
    converted = []
    try:
        for up in uploads:
            resolved = _resolve_uploaded_path(app, up)
            if not resolved:
                continue
            fname, assembled_path = resolved

            file_ext = Path(assembled_path).suffix.lower().lstrip('.')
            if file_ext in conversions.IMAGE_ALLOWED_EXTENSIONS and target in conversions.IMAGE_ALLOWED_EXTENSIONS:
                ok, _ = validate_image_file(assembled_path)
                if not ok:
                    continue

            out_ext = 'jpg' if target in ('jpg', 'jpeg') else ('tif' if target in ('tiff', 'tif') else target)
            out_name = f"{Path(fname).stem}_converted.{out_ext}"
            out_path = os.path.join(temp_dir, out_name)

            try:
                result = conversions.ConversionService.convert(
                    assembled_path,
                    target,
                    {
                        **conversion_parameters,
                        'source_extension': file_ext,
                        'output_path': out_path,
                    },
                )
            except Exception:
                result = None

            if result and os.path.exists(out_path):
                converted.append((out_name, out_path))

        if not converted:
            return jsonify({'success': False, 'error': 'no_converted_files'}), 500
        return _send_outputs(converted, 'converted_images.zip')
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@bp.route('/upload-status', methods=['GET'])
def upload_status():
    app = _app()
    auth_error = _require_upload_api_key(app)
    if auth_error:
        return auth_error

    upload_id = request.args.get('upload_id')
    if not upload_id:
        return jsonify({'success': False, 'error': 'missing_upload_id'}), 400

    upload_dir = os.path.join(_upload_chunks_dir(app), sanitize_filename(upload_id) or upload_id)
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
    app = _app()
    auth_error = _require_upload_api_key(app)
    if auth_error:
        return auth_error

    try:
        data = request.get_json(silent=True) or {}
        older_than = int(data.get('older_than', app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600)))
    except Exception:
        older_than = app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600)

    now = __import__('time').time()
    removed = 0
    base_dir = _upload_chunks_dir(app)
    if not os.path.exists(base_dir):
        return jsonify({'success': True, 'removed': 0})

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
