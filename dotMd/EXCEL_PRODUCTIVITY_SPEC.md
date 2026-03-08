# EXCEL PRODUCTIVITY SUITE

## Purpose: Improve spreadsheet usability and prepare for printing/distribution

## 6 New Tools:

### 1️⃣ Excel → Print-Ready PDF
Convert spreadsheets to professional PDF format optimized for printing
- Preserve formatting, fonts, colors, and column widths
- Auto-scale to fit page width
- Optional header/footer with page numbers
- Support: .xlsx, .xls, .ods
- **Route**: `POST /excel-to-pdf`

### 2️⃣ Remove Colors (Black & White)
Convert colored spreadsheets to monochrome for reducing print costs
- Strip all cell colors (background + text)
- Keep text intact, apply neutral formatting
- Preserve all data and formulas
- Useful for internal documentation
- **Route**: `POST /excel-remove-colors`

### 3️⃣ Convert Formulas → Values
Replace all Excel formulas with their calculated values
- Useful for sharing read-only snapshots
- Remove dependency on linked workbooks
- Prevent accidental formula changes
- Maintains cell formatting
- **Route**: `POST /excel-formulas-to-values`

### 4️⃣ Clean Charts for Print
Optimize charts for monochrome printing
- Convert gradient colors to solid grays
- Remove background transparency (set white)
- Increase line thickness for visibility
- Enlarge axis labels for readability
- **Route**: `POST /excel-clean-charts`

### 5️⃣ Normalize Tables
Standardize Excel table formatting
- Auto-fit all columns to content width
- Apply consistent header styling (bold + light background)
- Remove merged cells (split into individual cells)
- Apply standard borders and alignment
- **Route**: `POST /excel-normalize-tables`

### 6️⃣ Split Sheets into PDFs
Extract each sheet as a separate PDF
- One file per worksheet (e.g., sheet1.pdf, sheet2.pdf)
- Batch download as ZIP
- Preserves formatting per sheet
- Useful for distributing individual reports
- **Route**: `POST /excel-split-sheets-pdf`

## UI Integration
- **Section**: Office Conversions (after existing tools)
- **Upload**: Drag-drop area supporting .xlsx/.xls/.ods files
- **Tabs**: 6 new tab buttons with emojis
- **Forms**: Simple with toggle checkboxes where needed
- **Output**: Direct download or ZIP packaging
