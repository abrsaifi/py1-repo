# Shim for pypdf: prefer the installed pypdf package, fall back to PyPDF2.
import sys
import os

def _load_real_pypdf():
    """Import the real pypdf from site-packages, not this local shim directory."""
    # Temporarily remove the repo root from sys.path so the installed pypdf is found
    _this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _filtered = [p for p in sys.path if os.path.abspath(p) != _this_dir]
    # Remove any cached 'pypdf' module so we can re-import cleanly
    _cached = sys.modules.pop('pypdf', None)
    _old_path = sys.path[:]
    sys.path[:] = _filtered
    try:
        import pypdf as _real  # noqa: F401
        return _real
    except ImportError:
        return None
    finally:
        sys.path[:] = _old_path
        # Restore the shim in sys.modules
        sys.modules['pypdf'] = sys.modules.get('pypdf') or _cached

_real = _load_real_pypdf()
if _real is not None:
    PdfReader = _real.PdfReader
    PdfWriter = _real.PdfWriter
    PdfMerger = getattr(_real, 'PdfMerger', None)
else:
    try:
        from PyPDF2 import PdfReader, PdfWriter, PdfMerger  # type: ignore
    except Exception as e:
        raise ImportError('pypdf shim: could not find pypdf or PyPDF2: ' + str(e))

__all__ = ['PdfReader', 'PdfWriter', 'PdfMerger']
