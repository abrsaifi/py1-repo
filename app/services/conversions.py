import os
import tempfile
import shutil
import zipfile
from pathlib import Path
from PIL import Image
import io
import subprocess

try:
    import imageio_ffmpeg
except Exception:
    imageio_ffmpeg = None

try:
    import fitz
except Exception:
    fitz = None


IMAGE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'}
PDF_ALLOWED_EXTENSIONS = {'pdf'}
HTML_ALLOWED_EXTENSIONS = {'html', 'htm'}
SPREADSHEET_ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'ods', 'csv'}
TEXT_ALLOWED_EXTENSIONS = {'txt'}
AUDIO_ALLOWED_EXTENSIONS = {'mp3', 'wav'}
VIDEO_ALLOWED_EXTENSIONS = {'mp4', 'webm'}


def _coerce_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default


def _coerce_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'on'}
    return bool(value)


def _remove_background(image, tolerance=50):
    rgba_image = image.convert('RGBA')
    background_color = rgba_image.getpixel((0, 0))[:3]
    pixels = rgba_image.load()

    for x in range(rgba_image.width):
        for y in range(rgba_image.height):
            red, green, blue, alpha = pixels[x, y]
            distance = abs(red - background_color[0]) + abs(green - background_color[1]) + abs(blue - background_color[2])
            if distance <= max(int(tolerance) * 3, 0):
                pixels[x, y] = (red, green, blue, 0)

    return rgba_image


def _transform_image(image, parameters=None):
    parameters = parameters or {}
    transformed = image.copy()
    width = _coerce_int(parameters.get('width'))
    height = _coerce_int(parameters.get('height'))

    if width and height and width > 0 and height > 0:
        transformed = transformed.resize((width, height), Image.Resampling.LANCZOS)

    if 'tolerance' in parameters:
        transformed = _remove_background(transformed, tolerance=_coerce_int(parameters.get('tolerance'), 50))

    return transformed


def _save_image(img, output_path, target_format, quality=85, lossless=False, remove_metadata=False):
    fmt = target_format.lower().lstrip('.')

    if remove_metadata:
        metadata_free = Image.new(img.mode, img.size)
        metadata_free.putdata(list(img.getdata()))
        img = metadata_free

    if fmt in ('jpg', 'jpeg'):
        if img.mode in ('RGBA', 'LA') or ('A' in img.getbands()):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.convert('RGBA').split()[-1])
            img = background
        else:
            img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=quality)
    elif fmt == 'png':
        img.save(output_path, 'PNG')
    elif fmt == 'webp':
        save_kwargs = {'quality': quality}
        if lossless:
            save_kwargs['lossless'] = True
        try:
            img.save(output_path, 'WEBP', **save_kwargs)
        except Exception:
            img.convert('RGB').save(output_path, 'WEBP', **save_kwargs)
    elif fmt == 'gif':
        img.save(output_path, 'GIF')
    elif fmt in ('tiff', 'tif'):
        img.save(output_path, 'TIFF')
    elif fmt == 'bmp':
        img.save(output_path, 'BMP')
    else:
        img.save(output_path)


def convert_image_format(input_path, output_path, target_format, quality=85, lossless=False):
    try:
        img = Image.open(input_path)
        _save_image(img, output_path, target_format, quality=quality, lossless=lossless)
        return True
    except Exception as e:
        print(f"Image conversion error: {e}")
        return False


def validate_image_file(path):
    try:
        if not os.path.exists(path):
            return False, 'file_missing'
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext not in IMAGE_ALLOWED_EXTENSIONS:
            return False, 'bad_extension'
        with Image.open(path) as im:
            im.verify()
        return True, ''
    except Exception as e:
        return False, str(e)


def _generate_preview_from_pdf(pdf_path, dpi=150):
    try:
        if fitz is None:
            return None
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return None
        page = doc[0]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes('png')
        doc.close()
        return img_bytes
    except Exception:
        return None


def image_to_pdf(image_path, output_pdf):
    try:
        img = Image.open(image_path)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_pdf, 'PDF')
        return True
    except Exception:
        return False


def _get_ffmpeg_executable():
    if imageio_ffmpeg is not None:
        try:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                return ffmpeg_path
        except Exception:
            pass

    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path

    raise RuntimeError('ffmpeg_not_available')


def _run_ffmpeg(input_path, output_path, ffmpeg_args):
    command = [_get_ffmpeg_executable(), '-y', '-i', input_path, *ffmpeg_args, output_path]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or 'ffmpeg_failed')
    return os.path.exists(output_path)


def convert_audio_format(input_path, output_path, target_format):
    fmt = target_format.lower().lstrip('.')
    if fmt == 'wav':
        return _run_ffmpeg(input_path, output_path, ['-vn', '-acodec', 'pcm_s16le'])
    if fmt == 'mp3':
        return _run_ffmpeg(input_path, output_path, ['-vn', '-acodec', 'libmp3lame', '-b:a', '192k'])
    raise ValueError(f'Unsupported audio target: {target_format}')


def convert_video_format(input_path, output_path, target_format):
    fmt = target_format.lower().lstrip('.')
    if fmt == 'mp4':
        return _run_ffmpeg(
            input_path,
            output_path,
            ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '128k'],
        )
    if fmt == 'webm':
        return _run_ffmpeg(
            input_path,
            output_path,
            ['-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '36', '-c:a', 'libopus', '-b:a', '96k'],
        )
    raise ValueError(f'Unsupported video target: {target_format}')


class ConversionService:
    """Compatibility wrapper for background task imports."""

    OFFICE_INPUT_EXTENSIONS = {'doc', 'docx', 'odt', 'ppt', 'pptx', 'xls', 'xlsx', 'ods', 'csv'}

    @staticmethod
    def _build_output_path(input_path, output_format, parameters=None):
        parameters = parameters or {}
        requested_output = parameters.get('output_path')
        if requested_output:
            return requested_output

        suffix = f".{output_format.lower().lstrip('.')}"
        temp_dir = tempfile.mkdtemp(prefix='docpro-convert-')
        return os.path.join(temp_dir, f"{Path(input_path).stem}{suffix}")

    @classmethod
    def convert(cls, input_path, output_format, parameters=None):
        parameters = parameters or {}
        if not input_path or not os.path.exists(input_path):
            raise FileNotFoundError(f'Input file not found: {input_path}')

        input_ext = Path(input_path).suffix.lower().lstrip('.')
        target_format = output_format.lower().lstrip('.')
        output_path = cls._build_output_path(input_path, target_format, parameters)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if input_ext in IMAGE_ALLOWED_EXTENSIONS and target_format == 'pdf':
            success = image_to_pdf(input_path, output_path)
        elif input_ext in IMAGE_ALLOWED_EXTENSIONS and target_format in IMAGE_ALLOWED_EXTENSIONS:
            image = Image.open(input_path)
            image = _transform_image(image, parameters)
            _save_image(
                image,
                output_path,
                target_format,
                quality=_coerce_int(parameters.get('quality'), 85),
                lossless=_coerce_bool(parameters.get('lossless'), False),
                remove_metadata=_coerce_bool(parameters.get('removeMetadata'), False),
            )
            success = os.path.exists(output_path)
        elif input_ext in cls.OFFICE_INPUT_EXTENSIONS and target_format == 'pdf':
            from services.document_conversion import soffice_to_pdf
            success = soffice_to_pdf(input_path, output_path, timeout=int(parameters.get('timeout', 120)))
        elif input_ext in PDF_ALLOWED_EXTENSIONS and target_format == 'docx':
            from services.document_conversion import pdf_to_word
            success = pdf_to_word(input_path, output_path)
        elif input_ext in PDF_ALLOWED_EXTENSIONS and target_format == 'xlsx':
            from services.document_conversion import pdf_to_excel
            success = pdf_to_excel(input_path, output_path)
        elif input_ext in PDF_ALLOWED_EXTENSIONS and target_format == 'pptx':
            from services.document_conversion import pdf_to_powerpoint
            success = pdf_to_powerpoint(input_path, output_path)
        elif input_ext in PDF_ALLOWED_EXTENSIONS and target_format == 'html':
            from services.document_conversion import pdf_to_html
            success = pdf_to_html(input_path, output_path)
        elif input_ext in SPREADSHEET_ALLOWED_EXTENSIONS and target_format == 'csv':
            from services.document_conversion import excel_to_csv
            success = excel_to_csv(input_path, output_path, sheet_name=parameters.get('sheet_name'))
        elif input_ext == 'csv' and target_format == 'xlsx':
            from app.services.data_tools import csv_to_excel_file
            success = csv_to_excel_file(input_path, output_path)
        elif input_ext in HTML_ALLOWED_EXTENSIONS and target_format == 'pdf':
            from services.document_conversion import html_to_pdf
            success = html_to_pdf(input_path, output_path)
        elif input_ext in TEXT_ALLOWED_EXTENSIONS and target_format == 'pdf':
            from services.document_conversion import text_to_pdf
            with open(input_path, 'r', encoding='utf-8-sig', errors='ignore') as handle:
                success = text_to_pdf(handle.read(), output_path, font_size=_coerce_int(parameters.get('font_size'), 11))
        elif input_ext in AUDIO_ALLOWED_EXTENSIONS and target_format in AUDIO_ALLOWED_EXTENSIONS:
            success = convert_audio_format(input_path, output_path, target_format)
        elif input_ext in VIDEO_ALLOWED_EXTENSIONS and target_format in VIDEO_ALLOWED_EXTENSIONS:
            success = convert_video_format(input_path, output_path, target_format)
        else:
            raise ValueError(f'Unsupported conversion: .{input_ext} -> .{target_format}')

        if not success or not os.path.exists(output_path):
            raise RuntimeError(f'Conversion failed: .{input_ext} -> .{target_format}')

        return {
            'output_path': output_path,
            'output_size': os.path.getsize(output_path),
        }
