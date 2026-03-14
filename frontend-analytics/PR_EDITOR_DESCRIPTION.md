# Editor feature: in-browser editing + document previews

Summary
- Added an Editor UI that supports:
  - Image canvas editing and annotation
  - Multi-page PDF preview + per-page annotation and page navigation
  - DOCX preview via `mammoth`
  - CSV preview/edit and export to CSV then upload
  - Client-side chunked uploads (5MB chunks) with progress bar
  - `target_format` selector to request server-side conversion (defaults set per file type)

Files changed
- `frontend-analytics/src/pages/EditorPage.jsx` — main implementation

Build & Test
- `npm run build` completed successfully (Vite v5.4.21).
- `tool_runtime_smoke.py` executed against local backend/frontend — all exercised endpoints passed.
- Ran `scripts/test_upload_editor.py`: upload assembled successfully and conversion to `pdf` returned HTTP 200 with PDF bytes.

Notes for PR description
- This branch: `feat/editor-integration`
- Key runtime endpoints used: `/api/upload-chunk` and `/api/convert-uploaded`.
- The conversion API may require `target_format`; the Editor UI now includes a selector and sets sensible defaults: images→`png`, PDFs→`pdf`, DOCX→`pdf`, CSV→`xlsx`.

Manual verification steps
1. Start backend on port 5060 and frontend dev server on 5173.
2. Open Editor at `/editor`.
3. Load an image or PDF, annotate, choose a `Convert to` format, then click `Upload to Backend`.
4. Wait for progress to complete; when conversion is finished a download link (if provided by the server) will appear.

If you want I can update the GitHub PR body directly (requires GitHub token) or open a PR for you — currently the branch is pushed and ready.
