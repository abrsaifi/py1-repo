# Shim for pypdf: prefer the installed pypdf package, fall back to PyPDF2.
import sys
import os

def _load_real_pypdf():
    """Import the real pypdf from site-packages, not this local shim directory."""
    # Temporarily remove the repo root from sys.path so the installed pypdf is found
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _filtered = [p for p in sys.path if os.path.abspath(p) != _repo_root]
    # Remove any cached 'pypdf' entry so a fresh import picks up site-packages
    _cached = sys.modules.pop('pypdf', None)
    _old_path = sys.path[:]
    sys.path[:] = _filtered
    _imported = None
    try:
        import pypdf as _real  # noqa: F401
        _imported = _real
    except ImportError:
        pass
    finally:
        sys.path[:] = _old_path
        # If import succeeded, keep the real module in sys.modules.
        # If it failed, restore whatever was there before (the shim itself).
        if _imported is None:
            if _cached is not None:
                sys.modules['pypdf'] = _cached
            else:
                sys.modules.pop('pypdf', None)
        # else: sys.modules['pypdf'] already points to the real module
    return _imported

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
