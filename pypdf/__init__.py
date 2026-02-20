# Shim for pypdf to maintain compatibility when only PyPDF2 is installed.
# This file re-exports PdfReader, PdfWriter, PdfMerger from PyPDF2.
try:
    from PyPDF2 import PdfReader, PdfWriter, PdfMerger  # type: ignore
except Exception as e:
    # If neither PyPDF2 nor pypdf are installed, raise ImportError
    raise ImportError('pypdf shim requires PyPDF2 to be present: ' + str(e))

__all__ = ['PdfReader', 'PdfWriter', 'PdfMerger']
