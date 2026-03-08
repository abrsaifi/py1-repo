import os
import sys
from types import SimpleNamespace, ModuleType
from pathlib import Path

import pytest

from services import document_conversion as dc


def test_cli_fallback_creates_pdf(tmp_path, monkeypatch):
    # Create a dummy input file
    in_file = tmp_path / 'test.txt'
    in_file.write_text('hello world')

    out_pdf = tmp_path / 'out.pdf'

    # Fake subprocess.run to create the expected produced PDF file
    class FakeProc:
        def __init__(self, rc=0):
            self.returncode = rc
            self.stdout = ''
            self.stderr = ''

    def fake_run(cmd, capture_output=True, text=True, timeout=60):
        produced = tmp_path / f"{in_file.stem}.pdf"
        produced.write_bytes(b'%PDF-1.4\n%fake-cli')
        return FakeProc(0)

    monkeypatch.setattr(dc, 'subprocess', SimpleNamespace(run=fake_run))

    result = dc.soffice_to_pdf(str(in_file), str(out_pdf), timeout=10)
    assert result is True
    assert out_pdf.exists()
    assert out_pdf.read_bytes().startswith(b'%PDF')


def test_uno_daemon_path(tmp_path, monkeypatch):
    # Create dummy input file
    in_file = tmp_path / 'uno_test.docx'
    in_file.write_text('dummy')
    out_pdf = tmp_path / 'uno_out.pdf'

    # Create a fake 'uno' module with minimal behavior expected by the code.
    fake_uno = ModuleType('uno')

    def systemPathToFileUrl(p):
        return 'file://' + os.path.abspath(p)

    def getComponentContext():
        class LocalCtx:
            def __init__(self):
                self.ServiceManager = self

            def createInstanceWithContext(self, name, ctx):
                # Resolver
                if name == 'com.sun.star.bridge.UnoUrlResolver':
                    class Resolver:
                        def resolve(self, url):
                            class Ctx:
                                def __init__(self):
                                    self.ServiceManager = self

                                def createInstanceWithContext(self, name2, ctx2):
                                    if name2 == 'com.sun.star.frame.Desktop':
                                        class Desktop:
                                            def loadComponentFromURL(self, file_url, target, flags, props):
                                                class Component:
                                                    def storeToURL(self, pdf_url, props2):
                                                        # write to the file path represented by pdf_url
                                                        if pdf_url.startswith('file://'):
                                                            path = pdf_url[len('file://'):]
                                                        else:
                                                            path = pdf_url
                                                        with open(path, 'wb') as f:
                                                            f.write(b'%PDF-1.4\n%fake-uno')

                                                    def close(self, flag):
                                                        pass

                                                    def dispose(self):
                                                        pass

                                                return Component()
                                        return Desktop()

                            return Ctx()

                    return Resolver()

                return None

        return LocalCtx()

    fake_uno.systemPathToFileUrl = systemPathToFileUrl
    fake_uno.getComponentContext = getComponentContext

    # Insert fake module into sys.modules
    monkeypatch.setitem(sys.modules, 'uno', fake_uno)

    # Ensure daemon env vars are set and prefer daemon
    monkeypatch.setenv('LIBREOFFICE_DAEMON_HOST', 'localhost')
    monkeypatch.setenv('LIBREOFFICE_DAEMON_PORT', '2002')
    monkeypatch.setenv('LIBREOFFICE_PREFER_DAEMON', '1')

    # Call the conversion - should succeed via fake UNO
    ok = dc.soffice_to_pdf(str(in_file), str(out_pdf), timeout=10)
    assert ok is True
    assert out_pdf.exists()
    assert out_pdf.read_bytes().startswith(b'%PDF')
