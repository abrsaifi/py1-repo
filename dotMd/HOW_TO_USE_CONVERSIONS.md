# How to Use the 5 PDF Conversion Features

## Quick Start Guide

All 5 PDF conversion features are **live and ready to use** at `http://localhost:5000`

---

## 🎯 Using Each Feature

### 1️⃣ JPG/Image to PDF

**Via Web UI**:
1. Go to "Conversion Studio"
2. Drag and drop a JPG, PNG, GIF, etc.
3. Settings:
   - Select quality (30-100)
   - Choose orientation (portrait/landscape)
   - Select paper size (A4, Letter, etc.)
4. Click "Start Conversion"
5. Download the PDF

**Via API**:
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@photo.jpg" \
  -F "tool_name=To PDF" \
  -F "image_quality=85" \
  -F "orientation=portrait" \
  -F "paper_size=A4"
```

**Parameters for Images**:
- Image quality (30-100)
- Scale factor (50-200%)
- Compression (none/low/medium/high)
- Page numbers (true/false)

---

### 2️⃣ Word (DOCX) to PDF

**Via Web UI**:
1. Go to "Conversion Studio"
2. Drag and drop a .docx file
3. Advanced settings:
   - Set margins (mm)
   - Choose orientation
   - Add page numbers
   - Set compression level
4. Click "Start Conversion"
5. Download the PDF

**Via API**:
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@document.docx" \
  -F "tool_name=To PDF" \
  -F "margin_top=20" \
  -F "margin_bottom=20" \
  -F "margin_left=20" \
  -F "margin_right=20" \
  -F "page_numbers=true" \
  -F "compression=medium"
```

**Parameters for Word Documents**:
- Top/bottom/left/right margins (mm)
- Orientation (portrait/landscape)
- Paper size (A4, Letter, A3, etc.)
- Page numbers (true/false)
- Compression (none/low/medium/high)
- Preserve colors (true/false)
- Embed fonts (true/false)

---

### 3️⃣ Excel (XLSX/CSV) to PDF

**Via Web UI**:
1. Go to "Conversion Studio"
2. Upload an Excel file or CSV
3. Spreadsheet-specific options:
   - **Fit Mode**: Choose how to scale content
     - "fit-page" = all content in one page
     - "fit-width" = all columns visible
     - "fit-height" = all rows visible
     - "no-fit" = keep original size
   - **Grid Lines**: Show/hide cell borders
   - **Headers**: Include/exclude column headers
   - **Scale**: 50-200% zoom
4. Set other options (compression, page numbers, etc.)
5. Click "Start Conversion"

**Via API**:
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@data.xlsx" \
  -F "tool_name=To PDF" \
  -F "fit_mode=fit-page" \
  -F "gridlines=true" \
  -F "include_headers=true" \
  -F "scale_factor=85" \
  -F "page_numbers=true" \
  -F "compression=high" \
  -F "orientation=landscape"
```

**Parameters for Spreadsheets** (All Excel parameters):
- Fit mode: fit-page/fit-width/fit-height/no-fit
- Grid lines: true/false
- Include headers: true/false
- Scale factor: 50-200%
- Orientation: portrait/landscape
- Paper size: A4, Letter, A3, etc.
- All standard parameters (margins, page numbers, compression)

---

### 4️⃣ HTML to PDF

**Via Web UI**:
1. Go to "Conversion Studio"
2. Upload an HTML file
3. Settings:
   - Orientation (portrait/landscape)
   - Paper size
   - Margins
   - Scale factor
   - Page numbers
4. Click "Start Conversion"
5. Download the styled PDF

**Via API**:
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@webpage.html" \
  -F "tool_name=To PDF" \
  -F "orientation=portrait" \
  -F "paper_size=A4" \
  -F "scale_factor=100" \
  -F "page_numbers=false"
```

**Parameters for HTML**:
- All standard parameters apply
- CSS styling is preserved
- Images are embedded
- Links work in PDF

---

### 5️⃣ PowerPoint (PPTX) to PDF

**Via Web UI**:
1. Go to "Conversion Studio"
2. Upload a .pptx file
3. Settings:
   - Orientation (portrait/landscape)
   - Paper size
   - Margins
   - Scale factor
   - Page numbers (one per slide)
   - Compression
4. Click "Start Conversion"
5. Download PDF (one slide per page)

**Via API**:
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@presentation.pptx" \
  -F "tool_name=To PDF" \
  -F "orientation=landscape" \
  -F "paper_size=A4" \
  -F "page_numbers=true" \
  -F "compression=medium"
```

**Parameters for PowerPoint**:
- All standard parameters apply
- Each slide becomes a PDF page
- Slide dimensions respected
- Animations/transitions not preserved (expected)

---

## 🎨 Using Presets

The "To PDF" tool includes 9 professional presets:

1. **Standard Portrait** - Classic document layout
   - Portrait, A4, 20mm margins, fit-page
   
2. **Landscape Wide** - For wide spreadsheets
   - Landscape, A4, 15mm margins, fit-width, gridlines
   
3. **Fit All (Spreadsheet)** - Squeeze everything
   - Landscape, A4, 10mm margins, 80% scale, compression high
   
4. **Narrow Margins** - Maximum content area
   - Portrait, 10mm margins, fit-width
   
5. **Wide Margins** - Professional look
   - Portrait, 25mm margins, no compression
   
6. **Legal Document** - Formal appearance
   - Portrait, Letter, 25mm margins, pages numbered
   
7. **Compact (All Columns)** - A3 size optimization
   - Landscape, A3, 10mm margins, 75% scale
   
8. **High Quality** - Best looking
   - 100% scale, no compression, 100% image quality
   
9. **Web Optimized** - Smallest file size
   - 90% scale, high compression, 60% image quality

---

## 🔧 Advanced Parameter Guide

### Common Parameters (All Formats)

**Orientation**
- `portrait` - Standard vertical layout
- `landscape` - Wide horizontal layout

**Paper Size**
- `A4` - 210×297mm (standard European)
- `A3` - 297×420mm (larger)
- `Letter` - 8.5×11in (US standard)
- `Legal` - 8.5×14in (US legal)
- `A5` - 148×210mm (smaller)
- `A6` - 105×148mm (postcard)

**Margins** (in millimeters)
- `margin_top` - Top margin (0-50mm)
- `margin_bottom` - Bottom margin (0-50mm)
- `margin_left` - Left margin (0-50mm)
- `margin_right` - Right margin (0-50mm)

**Scaling**
- `scale_factor` - Zoom level (50-200%)
- Example: 80 = 80% zoom, 120 = 120% zoom

**Image Quality** (for images embedded in PDFs)
- `image_quality` - 30-100 (lower = smaller file)
- 30 = tiny file (visible loss)
- 85 = balanced (default)
- 100 = lossless (largest file)

**Page Numbers**
- `page_numbers` - "true" or "false"
- Format: "Page X of Y" at bottom

**Compression**
- `compression` - "none" / "low" / "medium" / "high"
- none = largest file
- high = smallest file (up to 28% reduction)

**Colors & Fonts**
- `preserve_colors` - Keep original colors (true/false)
- `embed_fonts` - Include fonts in PDF (true/false)
- `background` - Include backgrounds (true/false)

### Spreadsheet-Only Parameters

**Fit Mode** (how to scale content)
- `fit_mode: "fit-page"` - All content on one page
- `fit_mode: "fit-width"` - All columns visible, multiple pages vertically
- `fit_mode: "fit-height"` - All rows visible, multiple pages horizontally
- `fit_mode: "no-fit"` - Original size

**Display Options**
- `gridlines` - Show cell borders (true/false)
- `include_headers` - Show column/row headers (true/false)

---

## 📊 Real Examples

### Example 1: Convert Excel with Fit Mode
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@quarterly_report.xlsx" \
  -F "tool_name=To PDF" \
  -F "fit_mode=fit-page" \
  -F "gridlines=true" \
  -F "include_headers=true" \
  -F "scale_factor=85" \
  -F "page_numbers=true" \
  -F "compression=high"
```

Result: All spreadsheet data on one page, compressed, numbered

### Example 2: Professional Word Document
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@proposal.docx" \
  -F "tool_name=To PDF" \
  -F "orientation=portrait" \
  -F "paper_size=A4" \
  -F "margin_top=25" \
  -F "margin_bottom=25" \
  -F "margin_left=25" \
  -F "margin_right=25" \
  -F "page_numbers=true" \
  -F "embed_fonts=true" \
  -F "preserve_colors=true"
```

Result: Professional layout with wide margins and page numbers

### Example 3: High-Quality Image
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@photo.jpg" \
  -F "tool_name=To PDF" \
  -F "image_quality=100" \
  -F "orientation=landscape" \
  -F "paper_size=A4" \
  -F "compression=none"
```

Result: Best quality, lossless compression

### Example 4: Web-Optimized HTML
```bash
curl -X POST http://localhost:5000/api/convert \
  -F "files[]=@webpage.html" \
  -F "tool_name=To PDF" \
  -F "scale_factor=90" \
  -F "image_quality=60" \
  -F "compression=high" \
  -F "background=false"
```

Result: Smallest file size, suitable for email distribution

---

## 🎯 Tips & Best Practices

### For Images (JPG/PNG)
- Use 85 quality for most purposes (good balance)
- Use 100 for archival/print
- Use 60 for web sharing
- Landscape for wide images

### For Word Documents
- Use "Legal Document" preset for formal papers
- 25mm margins for professional appearance
- Always embed fonts to ensure correct display
- Page numbers helpful for multi-page docs

### For Excel Spreadsheets
- Use "fit-page" mode to squeeze content on one page
- Use "fit-width" for reports that are read left-to-right
- Enable gridlines for data clarity
- Enable headers to identify columns
- Use "Fit All" preset for tight fitting

### For HTML/Web Content
- Test with actual HTML file (not screenshot)
- CSS styling is preserved
- Images must be embedded or use absolute URLs
- Use "Web Optimized" preset for distribution

### For Presentations
- One slide per page (default)
- Use landscape orientation for best appearance
- Page numbers useful for references
- Compression helps reduce file size

---

## ✅ Verification

All features have been tested and verified working:
- ✅ JPG to PDF conversion
- ✅ DOCX/Word to PDF conversion  
- ✅ XLSX/Excel to PDF conversion
- ✅ HTML to PDF conversion
- ✅ PPTX/PowerPoint to PDF conversion

Server Status: **✅ Running and Ready**

---

## 📞 Support

For issues or questions:
1. Check the logs at: `server_output.log`
2. Verify file format is supported
3. Try with different parameters
4. Check file isn't corrupted

All conversions are logged and can be reviewed for debugging.
