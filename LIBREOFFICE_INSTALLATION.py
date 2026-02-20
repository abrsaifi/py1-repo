#!/usr/bin/env python3
"""
LibreOffice Installation Guide for Windows
"""

INSTALL_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║              LIBREOFFICE INSTALLATION GUIDE - WINDOWS                      ║
╚════════════════════════════════════════════════════════════════════════════╝

OVERVIEW:
─────────
LibreOffice is required for converting DOC, DOCX, ODT, and ODS files to PDF.
The preview endpoint will work much better with LibreOffice installed.

═══════════════════════════════════════════════════════════════════════════════

OPTION 1: DOWNLOAD & INSTALL (RECOMMENDED)
───────────────────────────────────────────

1. Visit: https://www.libreoffice.org/download/download/

2. Select your operating system: Windows (64-bit or 32-bit)

3. Click "Download Version X.X.X"
   - Recommended: Latest stable version
   - File: LibreOffice_X.X.X_Win_x64.msi (for 64-bit Windows)

4. Double-click the downloaded .msi file

5. Installation wizard will appear
   
   Step 1: License Agreement
   └─ Click "Accept" and "Next"
   
   Step 2: Installation Type
   ├─ Choose "Typical" installation (recommended)
   └─ Click "Next"
   
   Step 3: Installation Location
   ├─ Default: C:\\Program Files\\LibreOffice
   └─ Click "Next"
   
   Step 4: Ready to Install
   └─ Click "Install"

6. Wait for installation to complete
   - This may take 1-2 minutes
   - Computer may request admin privileges

7. Click "Finish" when complete

8. Verify installation:
   - Press Windows key and search for "libreoffice"
   - Should find LibreOffice Start Center

═══════════════════════════════════════════════════════════════════════════════

OPTION 2: COMMAND-LINE INSTALLATION (ADVANCED)
───────────────────────────────────────────────

If you have a downloaded installer:

1. Open PowerShell as Administrator

2. Run:
   msiexec /i "C:\\path\\to\\LibreOffice_X.X.X_Win_x64.msi" /qb

3. Wait for completion

═══════════════════════════════════════════════════════════════════════════════

OPTION 3: WINDOWS PACKAGE MANAGER (if available)
──────────────────────────────────────────────────

Open PowerShell and run:
  winget install -e --id TheDocumentFoundation.LibreOffice

═══════════════════════════════════════════════════════════════════════════════

VERIFICATION:
──────────────

After installation, verify the 'soffice' command is accessible:

PowerShell command:
  where soffice

Expected output:
  C:\\Program Files\\LibreOffice\\program\\soffice.exe

If you see this path, installation was successful!

Alternative verification:
  "C:\\Program Files\\LibreOffice\\program\\soffice.exe" --version

Should show version number like: 7.6.0

═══════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING:
────────────────

If 'soffice' is not found:

1. Check installation directory:
   ├─ Navigate to C:\\Program Files\\LibreOffice
   ├─ Should see "program" folder
   └─ Inside: soffice.exe

2. If not found, repair installation:
   ├─ Control Panel → Programs → Programs and Features
   ├─ Find "LibreOffice X.X"
   ├─ Click "Repair"
   └─ Wait for repair to complete

3. Restart computer after repair

4. Try verification command again

═══════════════════════════════════════════════════════════════════════════════

POST-INSTALLATION:
───────────────────

After LibreOffice is installed:

1. Restart the Flask server:
   - Stop current server process
   - Run: python server.py
   - Or: flask run

2. Test preview with DOCX file:
   - Upload Report.docx
   - Click "live preview"
   - Should show PDF preview of first 3 pages

3. Check server logs for confirmation:
   - Look for: "LibreOffice return code: 0"
   - Indicates successful conversion

═══════════════════════════════════════════════════════════════════════════════

SUPPORTED FILE TYPES (WITH LIBREOFFICE):
──────────────────────────────────────────

Document formats:
  ✓ DOCX  (Microsoft Word)
  ✓ DOC   (Legacy Word - requires LibreOffice)
  ✓ ODT   (OpenDocument Text)
  ✓ RTF   (Rich Text Format)
  ✓ TXT   (Plain text)

Spreadsheet formats:
  ✓ XLSX  (Excel)
  ✓ XLS   (Legacy Excel)
  ✓ ODS   (OpenDocument Spreadsheet)
  ✓ CSV   (Comma-separated values)

Presentation formats:
  ✓ PPTX  (PowerPoint)
  ✓ ODP   (OpenDocument Presentation)

Without LibreOffice, only XLSX, CSV work (via ReportLab).

═══════════════════════════════════════════════════════════════════════════════

UNINSTALLATION (if needed):
────────────────────────────

1. Control Panel → Programs → Programs and Features

2. Find "LibreOffice X.X.X"

3. Click "Uninstall"

4. Follow wizard to completion

5. Computer restart may be required

═══════════════════════════════════════════════════════════════════════════════

NEXT STEPS:
───────────

1. Download LibreOffice from: https://www.libreoffice.org/download/
2. Run the installer (.msi file)
3. Click through installation wizard
4. Restart your Flask server
5. Test preview with any DOCX file
6. Check logs for conversion confirmation

═══════════════════════════════════════════════════════════════════════════════
══════════════════════════════════════════════════════════════════════════════

DAEMON MODE (Optional — Linux / Server deployments)
──────────────────────────────────────────────────────────────────────────────

For higher throughput and much lower per-conversion latency, run LibreOffice
as a long-running daemon and use the UNO bridge from Python.

Example: start a headless LibreOffice daemon that listens on TCP port 2002

Linux (systemd / direct):
```bash
# Start in the foreground for testing
soffice --headless --accept="socket,host=0.0.0.0,port=2002;urp;" --norestore --nofirststartwizard

# Production: use systemd unit (see deployment/libreoffice-daemon.service)
systemctl enable --now libreoffice-daemon.service
```

Environment variables (used by the hybrid conversion code):

```bash
export LIBREOFFICE_PREFER_DAEMON=1
export LIBREOFFICE_DAEMON_HOST=localhost
export LIBREOFFICE_DAEMON_PORT=2002
```

Notes:
- The Python-side UNO bridge requires `pyuno` (the LibreOffice Python bindings).
- If `uno` is not importable the code will automatically fall back to the
   `soffice` CLI conversion path.
- For Docker deployments use `docker/libreoffice-daemon-compose.yml` to launch
   a container that exposes the UNO socket.

Troubleshooting:
- If conversions fail with UNO errors, set `LIBREOFFICE_PREFER_DAEMON=0` to
   force CLI mode while debugging.

References:
- https://wiki.documentfoundation.org/Development/Headless
- https://api.libreoffice.org/docs/pyuno/

"""

if __name__ == '__main__':
    print(INSTALL_GUIDE)
