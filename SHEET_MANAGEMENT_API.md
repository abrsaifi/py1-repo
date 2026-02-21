# Sheet Management API Documentation

## Overview
The DocumentPro API now supports comprehensive sheet management for Excel and CSV files, allowing users to:
- List all sheets with metadata and previews
- Convert specific sheets or all sheets to PDF
- Combine multiple CSV files into a single Excel workbook
- Merge multiple sheets into a single PDF or keep them separate

---

## Endpoints

### 1. GET Sheet Information
**Endpoint:** `POST /list-sheets`

**Description:** Get detailed information about all sheets in an Excel or CSV file, including row/column counts and data preview.

**Request (multipart/form-data):**
```
file: [Excel or CSV file]
```

**Supported Formats:**
- Excel: `.xlsx`, `.xls`, `.ods`
- CSV: `.csv`

**Response (JSON):**
```json
{
  "success": true,
  "file_name": "report.xlsx",
  "file_type": "excel",
  "sheets": [
    {
      "name": "Sales Q1",
      "index": 0,
      "rows": 150,
      "columns": 12,
      "preview": [
        ["Date", "Region", "Amount", ...],
        ["2024-01-01", "North", 5000, ...],
        ["2024-01-02", "South", 3200, ...],
        ...
      ]
    },
    {
      "name": "Sales Q2",
      "index": 1,
      "rows": 165,
      "columns": 12,
      "preview": [...]
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/list-sheets \
  -F "file=@report.xlsx" \
  -H "X-API-Key: your-api-key"
```

---

### 2. Convert Excel Sheets to PDF
**Endpoint:** `POST /excel-to-pdf-sheets`

**Description:** Convert specific sheets from Excel to PDF with support for merging multiple sheets or keeping them separate.

**Request (multipart/form-data):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| file | file | required | Excel file (.xlsx, .xls, .ods) |
| sheets | string | "all" | Sheet specification: "all", "Sheet1,Sheet2", or "0,2" for indices |
| merge | string | "false" | "true" to merge sheets into one PDF |
| orientation | string | "portrait" | "portrait" or "landscape" |
| paper_size | string | "A4" | "A4", "A3", "A5", "LETTER", "LEGAL" |
| margin_top | string | "25" | Top margin in mm |
| margin_bottom | string | "25" | Bottom margin in mm |
| margin_left | string | "25" | Left margin in mm |
| margin_right | string | "25" | Right margin in mm |
| include_headers | string | "true" | "true" to show column/row headers |
| gridlines | string | "false" | "true" to show gridlines |
| scale_factor | string | "100" | Zoom percentage (1-400) |

**Response:**
- **Single sheet or merge=true:** PDF file
- **Multiple sheets + merge=false:** ZIP file containing individual PDFs per sheet

**Example 1: Convert all sheets to separate PDFs (ZIP):**
```bash
curl -X POST http://localhost:5000/excel-to-pdf-sheets \
  -F "file=@sales.xlsx" \
  -F "sheets=all" \
  -F "merge=false" \
  -F "orientation=landscape" \
  -F "paper_size=A4" \
  -H "X-API-Key: your-api-key" \
  -o sheets.zip
```

**Example 2: Convert specific sheets merged into one PDF:**
```bash
curl -X POST http://localhost:5000/excel-to-pdf-sheets \
  -F "file=@sales.xlsx" \
  -F "sheets=Sales Q1,Sales Q2" \
  -F "merge=true" \
  -F "orientation=landscape" \
  -F "margin_top=20" \
  -F "margin_left=20" \
  -H "X-API-Key: your-api-key" \
  -o merged.pdf
```

**Example 3: Convert by sheet index:**
```bash
curl -X POST http://localhost:5000/excel-to-pdf-sheets \
  -F "file=@sales.xlsx" \
  -F "sheets=0,2" \
  -F "merge=false" \
  -H "X-API-Key: your-api-key" \
  -o sheets.zip
```

---

### 3. Combine CSV Files into Excel
**Endpoint:** `POST /combine-csvs`

**Description:** Merge multiple CSV files into a single Excel workbook, with each CSV becoming a separate sheet.

**Request (multipart/form-data):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| files | file[] | required | Multiple CSV files |
| sheet_names | string | (auto) | JSON array of sheet names: ["Q1", "Q2", "Q3"] |

**Response:** Excel file (.xlsx) with CSV files as sheet tabs

**Example 1: Simple combine with auto-generated sheet names:**
```bash
curl -X POST http://localhost:5000/combine-csvs \
  -F "files=@q1_sales.csv" \
  -F "files=@q2_sales.csv" \
  -F "files=@q3_sales.csv" \
  -H "X-API-Key: your-api-key" \
  -o quarterly_sales.xlsx
```

**Example 2: With custom sheet names:**
```bash
curl -X POST http://localhost:5000/combine-csvs \
  -F "files=@sales.csv" \
  -F "files=@expenses.csv" \
  -F "files=@forecast.csv" \
  -F 'sheet_names=["Sales", "Expenses", "Forecast"]' \
  -H "X-API-Key: your-api-key" \
  -o report.xlsx
```

---

## Usage Patterns

### Pattern 1: List and Convert Specific Sheets
```bash
# First, list all sheets to see what's available
curl -X POST http://localhost:5000/list-sheets \
  -F "file=@workbook.xlsx" \
  -H "X-API-Key: your-api-key" | jq '.sheets[].name'

# Then convert just the sheets you need
curl -X POST http://localhost:5000/excel-to-pdf-sheets \
  -F "file=@workbook.xlsx" \
  -F "sheets=Sheet1,Sheet3" \
  -F "merge=true" \
  -H "X-API-Key: your-api-key" \
  -o selected_sheets.pdf
```

### Pattern 2: Batch CSV to Excel Conversion
```bash
# Combine multiple CSVs
curl -X POST http://localhost:5000/combine-csvs \
  -F "files=@data1.csv" \
  -F "files=@data2.csv" \
  -F "files=@data3.csv" \
  -F 'sheet_names=["Dataset 1", "Dataset 2", "Dataset 3"]' \
  -H "X-API-Key: your-api-key" \
  -o combined.xlsx

# Then convert to PDF if needed
curl -X POST http://localhost:5000/excel-to-pdf-sheets \
  -F "file=@combined.xlsx" \
  -F "sheets=all" \
  -F "merge=true" \
  -F "orientation=landscape" \
  -H "X-API-Key: your-api-key" \
  -o report.pdf
```

### Pattern 3: Multi-Sheet PDF Export
```bash
# Convert all sheets, save as individual PDFs in ZIP
curl -X POST http://localhost:5000/excel-to-pdf-sheets \
  -F "file=@quarterly_report.xlsx" \
  -F "sheets=all" \
  -F "merge=false" \
  -F "paper_size=A4" \
  -F "include_headers=true" \
  -H "X-API-Key: your-api-key" \
  -o quarterly_pdfs.zip

# Extract and process each sheet separately
unzip quarterly_pdfs.zip
for pdf in *.pdf; do
  # Process each PDF...
done
```

---

## Sheet Selection Syntax

The `sheets` parameter supports multiple formats:

| Format | Example | Description |
|--------|---------|-------------|
| "all" | "all" | Convert all sheets |
| Single name | "Sales" | Convert named sheet |
| Multiple names | "Sales,Expenses,Forecast" | Convert multiple named sheets |
| Single index | "0" | Convert first sheet (0-indexed) |
| Multiple indices | "0,2,4" | Convert sheets at indices 0, 2, 4 |

---

## Output Options

### merge = "true"
- **Multiple sheets:** Create a single PDF with all sheets combined
- **Single sheet:** Return single PDF
- **Output:** `.pdf` file

### merge = "false"
- **Multiple sheets:** Create ZIP file with individual PDFs per sheet
- **Single sheet:** Return single PDF
- **Output:** `.zip` file (or `.pdf` if single sheet)

---

## Error Handling

All endpoints return standardized error responses:

**Success:**
```json
{
  "success": true,
  ...
}
```

**Error:**
```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

**Common Errors:**
- `400 Bad Request`: Missing required parameters or invalid file format
- `401 Unauthorized`: Missing or invalid API key
- `500 Internal Server Error`: Conversion failed

---

## Performance Notes

- **Large files with many sheets:** Consider streaming the response
- **ZIP creation:** May take longer with many sheets
- **PDF merging:** Each sheet is converted separately then merged
- **Memory usage:** All sheets processed in serial to minimize memory

---

## Limits

- **Maximum file size:** 16 MB (configurable in Flask)
- **Maximum sheets:** No hard limit, but performance degrades with many sheets
- **CSV combining:** Supports combining sheets into single Excel workbook
- **Sheet name length:** Excel maximum 31 characters per sheet

---

## API Key Requirements

All endpoints require API key authentication via:
- Header: `X-API-Key: your-api-key`
- OR Query parameter: `?api_key=your-api-key`
- OR Form parameter: `api_key=your-api-key`
