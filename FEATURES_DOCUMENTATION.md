# DocPro - New Features Documentation

## Table of Contents
1. [Duplicate Remover](#duplicate-remover)
2. [Data Validator](#data-validator)
3. [PDF Export Enhancements](#pdf-export-enhancements)
4. [Basic Reporting](#basic-reporting)
5. [Database Integration](#database-integration)
6. [Authentication & API Keys](#authentication--api-keys)
7. [File Validation & Security](#file-validation--security)
8. [Monitoring & Logging](#monitoring--logging)

---

## Duplicate Remover

### Description
Remove duplicate rows from CSV, Excel (XLSX/XLS), and TXT files automatically.

### Features
- ✓ Detects and removes duplicate rows
- ✓ Smart matching options
- ✓ Batch processing support
- ✓ Preserves original data types
- ✓ Fast processing with pandas

### Usage

#### Web Interface
1. Go to "Duplicate Remover" on the home page
2. Upload your CSV/Excel file
3. Click "Remove Duplicates"
4. Download the cleaned file

#### API
```bash
curl -X POST -F "file=@data.csv" \
  http://localhost:5000/api/data/duplicate-remover \
  -H "X-API-Key: your-api-key"
```

### Response
- **Success (200)**: Returns cleaned CSV/Excel file
- **Error (400)**: Invalid file or format
- **Error (401)**: Unauthorized (missing/invalid API key)

### File Size Limit
- Maximum: **100 MB**
- Formats: CSV, XLSX, XLS, TXT

---

## Data Validator

### Description
Validate and analyze data quality with comprehensive reports.

### Features
- ✓ Format validation
- ✓ Data type checking
- ✓ Missing value detection
- ✓ Quality scoring (0-100%)
- ✓ Duplicate row counting
- ✓ Detailed validation reports

### Usage

#### Web Interface
1. Go to "Data Validator" on the home page
2. Upload your CSV/Excel file
3. Click "Validate Data"
4. View comprehensive quality report

#### API
```bash
curl -X POST -F "file=@data.csv" \
  http://localhost:5000/api/data/validate \
  -H "X-API-Key: your-api-key"
```

### Response Format
```json
{
  "success": true,
  "report": {
    "total_rows": 100,
    "total_columns": 5,
    "columns": ["Name", "Email", "Age", "Status", "Score"],
    "missing_values": {"Email": 2, "Score": 1},
    "data_types": {"Name": "object", "Age": "int64"},
    "duplicate_rows": 3,
    "quality_score": 95.5
  }
}
```

### Quality Score Calculation
- Formula: `100 - (missing_percentage + duplicate_percentage)`
- 100 = Perfect data quality
- 0 = Critical issues (all data missing or duplicated)

---

## PDF Export Enhancements

### Description
Export data to professional PDF reports with multiple formatting options.

### Features
- ✓ Multiple format options (Table, List, Compact)
- ✓ Custom styling and branding
- ✓ Professional table layouts
- ✓ Batch export capability
- ✓ Optimized for print and web

### Usage

#### Web Interface
1. Go to "PDF Export Enhancements" on the home page
2. Upload your CSV/Excel file
3. Select format (Table, List, or Compact)
4. Click "Export to PDF"
5. Download PDF report

#### API
```bash
curl -X POST -F "file=@data.csv" \
  -F "format=table" \
  http://localhost:5000/api/data/export-pdf \
  -H "X-API-Key: your-api-key"
```

### Format Options
- **Table**: Headers with data in tabular format
- **List**: Key-value pairs for each row
- **Compact**: Condensed format for large datasets

---

## Basic Reporting

### Description
Automatically generate charts, graphs, and summary statistics from your data.

### Features
- ✓ Visual charts & graphs
- ✓ Data summaries with statistics
- ✓ Mean, median, min, max calculations
- ✓ Standard deviation reporting
- ✓ Export capabilities
- ✓ Multiple chart types

### Usage

#### Web Interface
1. Go to "Basic Reporting" on the home page
2. Upload your CSV/Excel file
3. Click "Generate Report"
4. View summary statistics and insights

#### API
```bash
curl -X POST -F "file=@data.csv" \
  http://localhost:5000/api/data/reporting \
  -H "X-API-Key: your-api-key"
```

### Response Format
```json
{
  "success": true,
  "report": {
    "file_name": "sales_data.csv",
    "total_rows": 50,
    "total_columns": 3,
    "summary_statistics": {
      "Sales": {
        "mean": 55750.0,
        "median": 55000.0,
        "min": 50000.0,
        "max": 60000.0,
        "std": 3700.5
      }
    }
  }
}
```

### Supported Statistics
- Mean (Average)
- Median (Middle value)
- Min (Minimum value)
- Max (Maximum value)
- Std (Standard deviation)

---

## Database Integration

### Description
Connect and sync your documents with databases for advanced workflows.

### Features
- ✓ Multiple database support (MySQL, PostgreSQL, MongoDB, SQLite, SQL Server)
- ✓ Direct data sync
- ✓ Power user API access
- ✓ Connection pooling
- ✓ Query optimization

### Supported Databases
- **PostgreSQL**: Enterprise-grade relational
- **MySQL**: Popular open-source relational
- **MongoDB**: Document-based NoSQL
- **SQLite**: Embedded/lightweight
- **MS SQL Server**: Enterprise Microsoft database

### Usage

#### Web Interface
1. Go to "Database Integration" on the home page
2. Select database type
3. Enter connection details:
   - Host (IP/hostname)
   - Port (default for selected DB)
   - Database name
   - Username
4. Click "Test Connection"

#### API
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "db_type": "postgresql",
    "host": "localhost",
    "port": "5432",
    "database": "mydb",
    "username": "user"
  }' \
  http://localhost:5000/api/data/database-connect
```

### Response Format
```json
{
  "success": true,
  "connection": {
    "status": "ready",
    "db_type": "postgresql",
    "host": "localhost",
    "port": "5432",
    "database": "mydb",
    "message": "Database connection configured. Ready for data sync operations."
  }
}
```

---

## Authentication & API Keys

### Description
Secure API access with user accounts and API key management.

### Features
- ✓ User registration and login
- ✓ API key generation
- ✓ Password hashing (PBKDF2)
- ✓ Session management
- ✓ Audit logging

### Creating an API Key

#### Via API
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourusername",
    "password": "yourpassword"
  }' \
  http://localhost:5000/api/auth/login
```

#### Using API Key
```bash
curl -X POST -F "file=@data.csv" \
  -H "X-API-Key: dpk_your_api_key_here" \
  http://localhost:5000/api/data/duplicate-remover
```

### API Key Format
- **Format**: `dpk_` prefix + 43 character secure token
- **Example**: `dpk_WD9h8fD7sH9jK2mL4nP6qR8sT0uV2wX4yZ`
- **Validity**: Indefinite (until revoked)

### Security Best Practices
- ✓ Never commit API keys to version control
- ✓ Rotate keys regularly
- ✓ Use different keys for different applications
- ✓ Revoke compromised keys immediately
- ✓ Monitor key usage in logs

---

## File Validation & Security

### Description
Comprehensive file validation and security constraints.

### File Size Limits
| Feature | Max Size | Formats |
|---------|----------|---------|
| Duplicate Remover | 100 MB | CSV, XLSX, XLS, TXT |
| Data Validator | 100 MB | CSV, XLSX, XLS, TXT |
| PDF Export | 100 MB | CSV, XLSX, XLS, TXT |
| Reporting | 100 MB | CSV, XLSX, XLS, TXT |
| Database Integration | N/A | Connection-based |

### Validation Checks
- ✓ File size validation
- ✓ Extension whitelisting
- ✓ Empty file detection
- ✓ Path traversal prevention
- ✓ Filename sanitization
- ✓ Malicious pattern detection

### Error Responses

**Empty File**
```json
{
  "success": false,
  "error": "File is empty"
}
```

**File Too Large**
```json
{
  "success": false,
  "error": "File size exceeds 100MB limit (Current: 120.5MB)"
}
```

**Invalid Extension**
```json
{
  "success": false,
  "error": "File type .exe not allowed. Allowed: csv, xlsx, xls, txt"
}
```

---

## Monitoring & Logging

### Description
Comprehensive logging and monitoring system for all operations.

### Log Files
Located in `/logs/` directory:

1. **app.log**: All application events (DEBUG level)
2. **errors.log**: Errors and exceptions only
3. **audit.log**: User actions and API calls

### Log Format
```json
{
  "timestamp": "2026-02-16T10:30:45.123456",
  "level": "INFO",
  "logger": "duplicate-remover",
  "message": "Operation completed successfully",
  "module": "data.py",
  "function": "duplicate_remover",
  "line": 45,
  "duration_seconds": 2.345,
  "metadata": {
    "removed_rows": 10,
    "output_file": "data_no_duplicates.csv"
  }
}
```

### Log Rotation
- **Max Log Size**: 10 MB (app.log), 5 MB (errors.log)
- **Backup Files**: 10 backups retained (app), 5 backups (errors)
- **Format**: JSON (structured logging)

### Metrics Tracked
- Operation start/end times
- File sizes (input/output)
- Processing duration
- Success/failure status
- Error messages and stack traces
- User/API key information

### Analytics Database
Stored in `docpro_database.db`:

```sql
SELECT operation_type, success_count, failure_count, 
       total_files_processed, total_data_processed_mb 
FROM analytics;
```

### Viewing Logs

#### Recent Errors
```bash
tail -f logs/errors.log
```

#### JSON Analysis
```bash
cat logs/app.log | grep "duplicate-remover" | python -m json.tool
```

#### Performance Metrics
```bash
grep "duration_seconds" logs/app.log | python -m json.tool
```

---

## Configuration

### Environment Variables
```env
# File Upload
MAX_FILE_SIZE_MB=100
UPLOAD_API_KEY=your-api-key

# Database
DATABASE_PATH=/path/to/docpro_database.db

# Logging
LOG_LEVEL=INFO
LOG_DIR=/path/to/logs

# Authentication
SESSION_TIMEOUT_MINUTES=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

### Updated Configuration
See `app/config.py` for all available settings.

---

## Troubleshooting

### Common Issues

**Issue**: "File size exceeds limit"
**Solution**: Upload smaller files or increase `MAX_FILE_SIZE_MB` in config

**Issue**: "Invalid API key"
**Solution**: Check API key in X-API-Key header, regenerate if needed

**Issue**: "Database connection failed"
**Solution**: Verify database credentials and network connectivity

**Issue**: "Processing timeout"
**Solution**: Increase timeout in config or split large files

### Getting Help
- Check `logs/errors.log` for detailed error messages
- Review audit logs for operation history
- Contact support with operation ID from database

---

## Examples

### Complete Workflow Example

```bash
# 1. Create user and get API key
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}' \
  http://localhost:5000/api/auth/create-user

# 2. Validate data
curl -X POST -F "file=@data.csv" \
  -H "X-API-Key: dpk_xxxxx" \
  http://localhost:5000/api/data/validate

# 3. Remove duplicates
curl -X POST -F "file=@data.csv" \
  -H "X-API-Key: dpk_xxxxx" \
  http://localhost:5000/api/data/duplicate-remover \
  -o data_clean.csv

# 4. Generate report
curl -X POST -F "file=@data_clean.csv" \
  -H "X-API-Key: dpk_xxxxx" \
  http://localhost:5000/api/data/reporting

# 5. Export to PDF
curl -X POST -F "file=@data_clean.csv" \
  -F "format=table" \
  -H "X-API-Key: dpk_xxxxx" \
  http://localhost:5000/api/data/export-pdf \
  -o report.pdf
```

---

## Version History

### v2.0.0 (February 2026)
- ✓ Added Duplicate Remover
- ✓ Added Data Validator
- ✓ Added PDF Export Enhancements
- ✓ Added Basic Reporting
- ✓ Added Database Integration
- ✓ Implemented Authentication & API Keys
- ✓ Added comprehensive file validation
- ✓ Implemented monitoring & logging
- ✓ Created test suite

---

**Last Updated**: February 16, 2026
**Maintainer**: DocPro Team
**License**: Proprietary
