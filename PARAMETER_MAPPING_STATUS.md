# Service Parameter Mapping - Backend vs Frontend

## Fixed ✅
- PDF to B&W: dpi (select→number)
- Image Convert: targetFormat → output_format
- Text to PDF: fontSize (select→number)
- Batch Watermark: watermarkText → watermark_text, fontSize → font_size (select→number)
- Thumbnail Generator: thumbSize → size (select→number)  
- PDF to B&W Pro: dpi (select→number)
- PDF to PPT: imagesPerSlide (select→number)

## Still Checklist

### Services with camelCase parameters (might not match backend):

| Service | Parameter Name | Expected by Backend | Issue |
|---------|-----------------|-------------------|-------|
| Image Resize | keepAspect | keep_aspect | camelCase vs snake_case |
| Add Watermark | watermarkText | watermark_text | ✓ FIXED - Batch Watermark |
| Excel to CSV | delimiter | delimiter | ✓ OK|
| Remove Colors | colorMode | color_mode | camelCase vs snake_case |
| Image Resize (dup) | (duplicate service) | - | Needs cleanup |
| Remove Pages | pagesToRemove | pages_to_remove | camelCase vs snake_case |
| Remove Background | preserveEdges | preserve_edges | camelCase vs snake_case |
| Remove Background | outputFormat | output_format | camelCase vs snake_case |
| Page Reorder | newOrder | new_order | camelCase vs snake_case |
| Page Reorder | reverseOrder | reverse_order | camelCase vs snake_case |
| Smart Extract | extractMode | extract_mode | camelCase vs snake_case |
| Smart Extract | createSeparate | create_separate | camelCase vs snake_case |
| Pro Merge | removeBlankPages | remove_blank_pages | camelCase vs snake_case |
| Pro Merge | addBookmarks | add_bookmarks | camelCase vs snake_case |
| Secure Encrypt | ownerPassword | owner_password | camelCase vs snake_case |
| Secure Encrypt | allowPrinting | allow_printing | camelCase vs snake_case |
| Secure Encrypt | allowCopying | allow_copying | camelCase vs snake_case |
| Advanced OCR | preserveImages | preserve_images | camelCase vs snake_case |
| Advanced OCR | outputPDF | output_pdf | camelCase vs snake_case |
| Excel to PDF | includeHeaders | include_headers | camelCase vs snake_case |
| Excel to PDF | fitToWidth | fit_to_width | camelCase vs snake_case |
| HTML to PDF | marginTop | margin_top | camelCase vs snake_case |
| HTML to PDF | marginBottom | margin_bottom | camelCase vs snake_case |
| HTML to PDF | landscape | landscape | ✓ OK |
| Clean PDF | removeAnnotations | remove_annotations | camelCase vs snake_case |
| Clean PDF | removeMetadata | remove_metadata | camelCase vs snake_case |
| Redact Content | searchTerms | search_terms | camelCase vs snake_case |
| Redact Content | redactionColor | redaction_color | camelCase vs snake_case |
| Redact Content | caseSensitive | case_sensitive | camelCase vs snake_case |
| PDF to HTML | includeImages | include_images | camelCase vs snake_case |
| PDF to HTML | cssOptimization | css_optimization | camelCase vs snake_case |
| PDF to HTML | preserveLayout | preserve_layout | camelCase vs snake_case |
| Form Fill | autoDetect | auto_detect | camelCase vs snake_case |
| Extract Metadata | outputFormat | output_format | camelCase vs snake_case |
| Extract Metadata | includeImages | include_images | camelCase vs snake_case |
| Split Sheets | outputFormat | output_format | camelCase vs snake_case |
| Split Sheets | includeHeaders | include_headers | camelCase vs snake_case |
| Data Validator | validateFormat | validate_format | camelCase vs snake_case |
| Data Validator | validateContent | validate_content | camelCase vs snake_case |
| Data Validator | reportFormat | report_format | camelCase vs snake_case |
| Normalize Data | handleMissing | handle_missing | camelCase vs snake_case |
| Normalize Data | roundDecimals | round_decimals | camelCase vs snake_case |
| Remove Background | tolerance | tolerance | ✓ OK |
| Remove Background | preserveEdges | preserve_edges | camelCase vs snake_case |
| Remove Background | outputFormat | output_format | camelCase vs snake_case |
| PPT to PDF | pageSize | page_size | camelCase vs snake_case |
| PPT to PDF | includeNotes | include_notes | camelCase vs snake_case |
| Image Compress | removeMetadata | remove_metadata | camelCase vs snake_case |
| Batch Compress | removeImages | remove_images | camelCase vs snake_case |
| Batch Compress | reduceQuality | reduce_quality | camelCase vs snake_case |

### Critical Issue: 

**The convertBtn handler does NOT convert camelCase to snake_case!**

The handler at line 2360+ does:
```javascript
formData.append(param.name, input.value);
```

This means it sends whatever parameter name is defined in SERVICE_PARAMETERS as-is. So if the backend expects 'include_headers' but SERVICE_PARAMETERS defines 'includeHeaders', the parameter will be silently ignored!

## Solution: 

Option 1: Convert all parameter names in SERVICE_PARAMETERS to snake_case to match backend
Option 2: Add camelCase→snake_case conversion in convertBtn handler
Option 3: Update backend handlers to accept both camelCase and snake_case names

Recommended: Option 1 - Convert all frontend parameter names to snake_case to match backend expectations.
