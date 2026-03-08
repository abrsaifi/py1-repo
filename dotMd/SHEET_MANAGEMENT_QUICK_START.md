# Sheet Management Quick Reference

## What You Can Do Now

### 1. **List Sheets** - See what's in your files
```bash
POST /list-sheets
Upload Excel/CSV → Get all sheet names, dimensions, and data preview
```

### 2. **Convert Excel Sheets to PDF** - Multiple ways to organize
```bash
POST /excel-to-pdf-sheets

Options:
• Convert ALL sheets → Single merged PDF
• Convert ALL sheets → Separate PDFs in ZIP  
• Convert SPECIFIC sheets ("Sales", "Q1,Q2") → PDF or ZIP
• Set orientation, margins, paper size
• Include/exclude column headers and gridlines
```

### 3. **Combine CSV Files** - Build multi-sheet Excel workbooks
```bash
POST /combine-csvs
Upload multiple CSVs → Get single Excel with each CSV as a sheet tab
```

---

## Common Tasks

### Task 1: I have a big Excel file, I only want certain sheets as PDF
```bash
1. First: POST /list-sheets (to see what sheets exist)
2. Then: POST /excel-to-pdf-sheets with sheets="Sheet1,Sheet3"
3. Output: Single PDF with those sheets merged
```

### Task 2: I need each sheet as a separate PDF file
```bash
POST /excel-to-pdf-sheets with:
  sheets="all"
  merge="false"
Output: ZIP file containing one PDF per sheet
```

### Task 3: I have monthly CSV files, need them combined
```bash
POST /combine-csvs with:
  files=[jan.csv, feb.csv, mar.csv]
  sheet_names=["January", "February", "March"]
Output: Single Excel with 3 sheet tabs
```

### Task 4: Custom formatting for PDF export
```bash
POST /excel-to-pdf-sheets with:
  sheets="all"
  orientation="landscape"        # Wider orientation
  paper_size="A3"               # Bigger paper
  margin_top="10"               # Smaller margins (in mm)
  margin_left="10"
  include_headers="true"        # Show row/column numbers
  gridlines="true"              # Show cell grid
  scale_factor="80"             # Zoom out to 80%
```

---

## Parameter Reference

### Sheet Selection (`sheets` parameter)
```
"all"                    → All sheets
"Q1 Sales,Q2 Sales"      → Specific sheet names (comma-separated)
"0,1,3"                  → Sheet indices (0-based, comma-separated)
"0"                      → Single sheet by index
```

### PDF Formatting
```
orientation  : "portrait" (default) | "landscape"
paper_size   : "A4" (default) | "A3" | "A5" | "LETTER" | "LEGAL"
margin_*     : Distance in mm (default 25)
  - margin_top
  - margin_bottom
  - margin_left
  - margin_right
```

### Display Options
```
include_headers : "true" | "false"  (Show column/row headers)
gridlines      : "true" | "false"  (Show cell grid)
scale_factor   : 1-400 percentage  (Default 100)
```

### Output Options
```
merge : "true"  → Single merged PDF
        "false" → ZIP with separate PDFs per sheet
```

---

## JSON Response Examples

### List Sheets Response:
```json
{
  "success": true,
  "file_name": "sales.xlsx",
  "file_type": "excel",
  "sheets": [
    {
      "name": "Q1 2024",
      "index": 0,
      "rows": 150,
      "columns": 12,
      "preview": [["Date", "Region", "Amount"], ["2024-01-01", "North", 5000], ...]
    }
  ]
}
```

### Error Response:
```json
{
  "success": false,
  "error": "File must be Excel (.xlsx, .xls, .ods) or CSV"
}
```

---

## Tips & Tricks

### Reduce File Size
```bash
scale_factor=75    # Zoom out files to reduce page count
margin_top=10      # Smaller margins save space
```

### Better Readability  
```bash
orientation=landscape    # More horizontal space
include_headers=true     # See column letters/row numbers
gridlines=true          # Clear cell boundaries
```

### Professional Output
```bash
paper_size=A4          # Standard business paper
margin_top=20          # Standard margins
margin_left=20
orientation=portrait   # Standard orientation
```

---

## Workflow Examples

### Example 1: Export Specific Department Data
```bash
# Step 1: See what departments available
curl -X POST /list-sheets -F "file=@company_data.xlsx"

# Step 2: Export only Sales and Marketing sheets as single PDF
curl -X POST /excel-to-pdf-sheets \
  -F "file=@company_data.xlsx" \
  -F "sheets=Sales,Marketing" \
  -F "merge=true" \
  -F "orientation=landscape"
```

### Example 2: Monthly Report Generation
```bash
# Step 1: Combine CSV exports from each system
curl -X POST /combine-csvs \
  -F "files=@billing_export.csv" \
  -F "files=@hours_export.csv" \
  -F "files=@expenses_export.csv" \
  -F 'sheet_names=["Billing", "Hours", "Expenses"]'

# Step 2: Convert to nice business PDF
curl -X POST /excel-to-pdf-sheets \
  -F "file=@report.xlsx" \
  -F "sheets=all" \
  -F "merge=true" \
  -F "orientation=landscape" \
  -F "include_headers=true"
```

### Example 3: Archive by Department  
```bash
# Export each department as separate PDF (for filing)
curl -X POST /excel-to-pdf-sheets \
  -F "file=@company_data.xlsx" \
  -F "sheets=all" \
  -F "merge=false"    # Creates ZIP with one PDF per sheet

# Extract and organize
unzip pdfs.zip -d ./department_reports/
```

---

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success - file returned |
| 400 | Bad request - check parameters |
| 401 | Unauthorized - invalid API key |
| 500 | Server error - conversion failed |

---

## Need Help?

- Check file format is supported (Excel: .xlsx/.xls/.ods, CSV: .csv)
- Verify API key is correct
- Check sheet names exactly (case-sensitive for CSV, case-insensitive for Excel)
- Use /list-sheets first to see available sheets
- Large files may take longer to process
