"""
Tools Database and Metadata
Contains configuration for all 100+ converter tools
"""

TOOLS_CATEGORIES = {
    "image": "Image Converters",
    "document": "Document Converters",
    "pdf": "PDF Tools",
    "audio": "Audio Converters",
    "video": "Video Converters",
    "compression": "Compression Tools"
}

TOOLS_DATABASE = {
    # ========== IMAGE CONVERTERS ==========
    "jpg-to-png": {
        "slug": "jpg-to-png",
        "title": "JPG to PNG",
        "description": "Convert JPG images to PNG format with transparency support",
        "category": "image",
        "icon": "🖼️",
        "from_format": "JPG",
        "to_format": "PNG",
        "supported_formats": ["JPG", "JPEG"],
        "output_format": "PNG",
        "key_features": [
            "Keep original quality",
            "Transparency support",
            "Batch conversion",
            "Fast processing"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select JPG file"},
            {"num": 2, "title": "Configure", "description": "Choose quality settings"},
            {"num": 3, "title": "Convert", "description": "Process conversion"},
            {"num": 4, "title": "Download", "description": "Get PNG file"}
        ],
        "related_tools": ["png-to-jpg", "webp-to-png", "image-to-pdf"],
        "faq": [
            {"q": "Will I lose quality?", "a": "No, PNG stores images losslessly."},
            {"q": "Can I convert multiple files?", "a": "Yes, batch conversion is supported."},
            {"q": "What's the file size limit?", "a": "Up to 100MB per file."},
            {"q": "How long does it take?", "a": "Usually 1-5 seconds depending on size."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Ultra-fast conversions"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "Lossless output"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,  # 100MB in bytes
        "processing_time_seconds": 5,
        "success_rate": 99.8
    },
    
    "png-to-jpg": {
        "slug": "png-to-jpg",
        "title": "PNG to JPG",
        "description": "Convert PNG images to JPG/JPEG format with compression",
        "category": "image",
        "icon": "🎨",
        "from_format": "PNG",
        "to_format": "JPG",
        "supported_formats": ["PNG"],
        "output_format": "JPG",
        "key_features": [
            "Reduce file size",
            "Custom compression",
            "Batch processing",
            "High definition output"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PNG file"},
            {"num": 2, "title": "Compress", "description": "Set compression level"},
            {"num": 3, "title": "Convert", "description": "Process conversion"},
            {"num": 4, "title": "Download", "description": "Get JPG file"}
        ],
        "related_tools": ["jpg-to-png", "webp-to-jpg", "image-to-pdf"],
        "faq": [
            {"q": "Will transparency be lost?", "a": "Yes, JPG doesn't support transparency."},
            {"q": "How much smaller will it be?", "a": "Usually 50-80% reduction depending on quality."},
            {"q": "Can I adjust compression?", "a": "Yes, we provide compression level options."},
            {"q": "Best for photos?", "a": "Yes, JPG is ideal for photographs."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Ultra-fast conversions"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "📦", "title": "Quality", "description": "Adjustable compression"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 5,
        "success_rate": 99.9
    },
    
    "webp-to-png": {
        "slug": "webp-to-png",
        "title": "WebP to PNG",
        "description": "Convert WebP images to PNG with transparency",
        "category": "image",
        "icon": "🌐",
        "from_format": "WebP",
        "to_format": "PNG",
        "supported_formats": ["WebP"],
        "output_format": "PNG",
        "key_features": [
            "Free conversion",
            "Keep transparency",
            "No quality loss",
            "Fast processing"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select WebP file"},
            {"num": 2, "title": "Preview", "description": "Review conversion"},
            {"num": 3, "title": "Convert", "description": "Process conversion"},
            {"num": 4, "title": "Download", "description": "Get PNG file"}
        ],
        "related_tools": ["png-to-webp", "jpg-to-png", "image-to-pdf"],
        "faq": [
            {"q": "Is WebP widely supported?", "a": "Modern browsers support WebP, PNG is universal."},
            {"q": "Can I batch convert?", "a": "Yes, multiple files at once."},
            {"q": "Will quality change?", "a": "No, PNG conversion is lossless."},
            {"q": "What about file size?", "a": "PNG will be larger than WebP."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Ultra-fast conversions"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "Lossless output"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 4,
        "success_rate": 99.7
    },
    
    "image-to-pdf": {
        "slug": "image-to-pdf",
        "title": "Image to PDF",
        "description": "Convert images (JPG, PNG, WebP) to PDF documents",
        "category": "image",
        "icon": "📄",
        "from_format": "JPG/PNG/WebP",
        "to_format": "PDF",
        "supported_formats": ["JPG", "PNG", "WebP", "BMP", "TIFF"],
        "output_format": "PDF",
        "key_features": [
            "Multiple formats support",
            "Preserve quality",
            "Create multi-page PDFs",
            "Custom page sizes"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select image files"},
            {"num": 2, "title": "Arrange", "description": "Order pages"},
            {"num": 3, "title": "Convert", "description": "Process conversion"},
            {"num": 4, "title": "Download", "description": "Get PDF file"}
        ],
        "related_tools": ["pdf-to-image", "png-to-jpg", "compress-pdf"],
        "faq": [
            {"q": "Can I convert multiple images?", "a": "Yes, create multi-page PDFs."},
            {"q": "What formats are supported?", "a": "JPG, PNG, WebP, BMP, and TIFF."},
            {"q": "Can I customize page size?", "a": "Yes, A4, Letter, or custom sizes."},
            {"q": "Will quality be preserved?", "a": "Yes, full quality is maintained."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Fast multi-page processing"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "Lossless output"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 8,
        "success_rate": 99.5
    },
    
    # ========== DOCUMENT CONVERTERS ==========
    "pdf-to-docx": {
        "slug": "pdf-to-docx",
        "title": "PDF to Word",
        "description": "Convert PDF documents to editable Word (DOCX) format",
        "category": "document",
        "icon": "📝",
        "from_format": "PDF",
        "to_format": "DOCX",
        "supported_formats": ["PDF"],
        "output_format": "DOCX",
        "key_features": [
            "Editable Word format",
            "Maintain formatting",
            "Preserve text layers",
            "Fast conversion"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PDF file"},
            {"num": 2, "title": "Extract", "description": "Parse document structure"},
            {"num": 3, "title": "Convert", "description": "Generate Word document"},
            {"num": 4, "title": "Download", "description": "Get DOCX file"}
        ],
        "related_tools": ["docx-to-pdf", "pdf-to-excel", "pdf-to-pptx"],
        "faq": [
            {"q": "Will formatting be preserved?", "a": "Most formatting is preserved, complex layouts may need adjustment."},
            {"q": "Can I edit the output?", "a": "Yes, DOCX is fully editable in Microsoft Word."},
            {"q": "How long does conversion take?", "a": "Usually 10-30 seconds for standard documents."},
            {"q": "What about large files?", "a": "Supports files up to 100MB."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Fast document processing"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "Format preservation"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 20,
        "success_rate": 95.5
    },
    
    "docx-to-pdf": {
        "slug": "docx-to-pdf",
        "title": "Word to PDF",
        "description": "Convert Word documents (DOCX) to PDF format",
        "category": "document",
        "icon": "📄",
        "from_format": "DOCX",
        "to_format": "PDF",
        "supported_formats": ["DOCX", "DOC"],
        "output_format": "PDF",
        "key_features": [
            "Preserve formatting",
            "Secure PDF output",
            "Support DOC & DOCX",
            "Instant conversion"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select Word document"},
            {"num": 2, "title": "Format", "description": "Preserve layout"},
            {"num": 3, "title": "Convert", "description": "Generate PDF"},
            {"num": 4, "title": "Download", "description": "Get PDF file"}
        ],
        "related_tools": ["pdf-to-docx", "excel-to-pdf", "pptx-to-pdf"],
        "faq": [
            {"q": "Does it support images in docs?", "a": "Yes, images are included."},
            {"q": "What about page breaks?", "a": "Page breaks are preserved."},
            {"q": "Is conversion instant?", "a": "Yes, usually 1-5 seconds."},
            {"q": "Can I password protect?", "a": "Yes, optional PDF encryption available."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Ultra-fast conversion"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "Perfect formatting"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 5,
        "success_rate": 99.8
    },
    
    "pdf-to-excel": {
        "slug": "pdf-to-excel",
        "title": "PDF to Excel",
        "description": "Extract tables from PDF to Excel (XLSX) format",
        "category": "document",
        "icon": "📊",
        "from_format": "PDF",
        "to_format": "XLSX",
        "supported_formats": ["PDF"],
        "output_format": "XLSX",
        "key_features": [
            "Extract tables",
            "Smart table detection",
            "Preserve formatting",
            "Batch processing"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PDF with tables"},
            {"num": 2, "title": "Detect", "description": "Find table structure"},
            {"num": 3, "title": "Convert", "description": "Extract to Excel"},
            {"num": 4, "title": "Download", "description": "Get XLSX file"}
        ],
        "related_tools": ["pdf-to-docx", "excel-to-pdf", "csv-to-excel"],
        "faq": [
            {"q": "Can it detect complex tables?", "a": "Yes, smart AI table detection."},
            {"q": "What if there's no table?", "a": "Converts text to columns."},
            {"q": "Multi-page PDFs?", "a": "Yes, creates multiple sheets."},
            {"q": "Accuracy rate?", "a": "95%+ accuracy with most PDFs."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Smart table detection"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "📊", "title": "Quality", "description": "95%+ accuracy"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 15,
        "success_rate": 92.0
    },
    
    "excel-to-pdf": {
        "slug": "excel-to-pdf",
        "title": "Excel to PDF",
        "description": "Convert Excel spreadsheets to PDF documents",
        "category": "document",
        "icon": "📊",
        "from_format": "XLSX",
        "to_format": "PDF",
        "supported_formats": ["XLSX", "XLS", "CSV"],
        "output_format": "PDF",
        "key_features": [
            "Preserve spreadsheet layout",
            "Support multiple sheets",
            "Print-ready output",
            "Keep formatting"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select Excel file"},
            {"num": 2, "title": "Configure", "description": "Choose sheet options"},
            {"num": 3, "title": "Convert", "description": "Generate PDF"},
            {"num": 4, "title": "Download", "description": "Get PDF file"}
        ],
        "related_tools": ["pdf-to-excel", "docx-to-pdf", "csv-to-excel"],
        "faq": [
            {"q": "Can I select specific sheets?", "a": "Yes, choose which sheets to convert."},
            {"q": "Will formulas be included?", "a": "Values are included, not formulas."},
            {"q": "Support multiple sheets?", "a": "Yes, creates multi-page PDF."},
            {"q": "Print quality?", "a": "Yes, print-ready PDF format."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Fast conversion"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "📊", "title": "Quality", "description": "Print-ready output"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 8,
        "success_rate": 99.2
    },
    
    "pdf-to-pptx": {
        "slug": "pdf-to-pptx",
        "title": "PDF to PowerPoint",
        "description": "Convert PDF to PowerPoint (PPTX) presentations",
        "category": "document",
        "icon": "🎞️",
        "from_format": "PDF",
        "to_format": "PPTX",
        "supported_formats": ["PDF"],
        "output_format": "PPTX",
        "key_features": [
            "Convert each page to slide",
            "Editable presentation",
            "Maintain layout",
            "Batch conversion"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PDF file"},
            {"num": 2, "title": "Page-to-Slides", "description": "Convert each page"},
            {"num": 3, "title": "Create", "description": "Generate presentation"},
            {"num": 4, "title": "Download", "description": "Get PPTX file"}
        ],
        "related_tools": ["pptx-to-pdf", "pdf-to-docx", "pdf-to-excel"],
        "faq": [
            {"q": "One page per slide?", "a": "Yes, each PDF page becomes one slide."},
            {"q": "Can I edit the output?", "a": "Yes, fully editable PowerPoint file."},
            {"q": "Preserve images?", "a": "Yes, all images are included."},
            {"q": "How many pages supported?", "a": "Up to 500 pages per PDF."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Fast conversion"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "🎞️", "title": "Quality", "description": "Editable output"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 15,
        "success_rate": 93.0
    },
    
    "pptx-to-pdf": {
        "slug": "pptx-to-pdf",
        "title": "PowerPoint to PDF",
        "description": "Convert PowerPoint presentations to PDF format",
        "category": "document",
        "icon": "🎞️",
        "from_format": "PPTX",
        "to_format": "PDF",
        "supported_formats": ["PPTX", "PPT"],
        "output_format": "PDF",
        "key_features": [
            "Preserve slide design",
            "Include animations",
            "Compressed output",
            "Instant conversion"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PowerPoint file"},
            {"num": 2, "title": "Render", "description": "Process slides"},
            {"num": 3, "title": "Convert", "description": "Generate PDF"},
            {"num": 4, "title": "Download", "description": "Get PDF file"}
        ],
        "related_tools": ["pdf-to-pptx", "docx-to-pdf", "excel-to-pdf"],
        "faq": [
            {"q": "Will animations show?", "a": "Animations become static in PDF."},
            {"q": "Speaker notes included?", "a": "Optional to include notes as text."},
            {"q": "Color preservation?", "a": "Yes, full color support."},
            {"q": "How long for large presentations?", "a": "Usually 5-15 seconds."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Ultra-fast conversion"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "Perfect formatting"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 10,
        "success_rate": 99.0
    },
    
    # ========== PDF TOOLS ==========
    "pdf-to-image": {
        "slug": "pdf-to-image",
        "title": "PDF to Image",
        "description": "Convert PDF pages to image format (JPG, PNG, WebP)",
        "category": "pdf",
        "icon": "🖼️",
        "from_format": "PDF",
        "to_format": "JPG/PNG",
        "supported_formats": ["PDF"],
        "output_format": "JPG",
        "key_features": [
            "High resolution output",
            "All pages converted",
            "Multiple format export",
            "Batch processing"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PDF file"},
            {"num": 2, "title": "Select", "description": "Choose pages to convert"},
            {"num": 3, "title": "Convert", "description": "Render to images"},
            {"num": 4, "title": "Download", "description": "Get image files"}
        ],
        "related_tools": ["image-to-pdf", "pdf-to-docx", "compress-pdf"],
        "faq": [
            {"q": "What resolution?", "a": "300 DPI for high quality."},
            {"q": "Select specific pages?", "a": "Yes, convert page ranges."},
            {"q": "Multiple formats?", "a": "JPG, PNG, and WebP available."},
            {"q": "File size?", "a": "Typically larger than PDF."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Fast rendering"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✨", "title": "Quality", "description": "300 DPI output"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 12,
        "success_rate": 98.5
    },
    
    "compress-pdf": {
        "slug": "compress-pdf",
        "title": "Compress PDF",
        "description": "Reduce PDF file size while maintaining quality",
        "category": "pdf",
        "icon": "📦",
        "from_format": "PDF",
        "to_format": "PDF",
        "supported_formats": ["PDF"],
        "output_format": "PDF",
        "key_features": [
            "Reduce file size",
            "Maintain quality",
            "Fast compression",
            "Multiple compression levels"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PDF file"},
            {"num": 2, "title": "Optimize", "description": "Choose compression level"},
            {"num": 3, "title": "Compress", "description": "Process compression"},
            {"num": 4, "title": "Download", "description": "Get compressed PDF"}
        ],
        "related_tools": ["pdf-to-image", "merge-pdf", "split-pdf"],
        "faq": [
            {"q": "How much smaller?", "a": "Usually 30-70% reduction."},
            {"q": "Quality loss?", "a": "Minimal with smart compression."},
            {"q": "Best compression level?", "a": "Medium level recommended."},
            {"q": "Time to compress?", "a": "Usually 5-15 seconds."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Fast compression"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "📦", "title": "Quality", "description": "30-70% smaller"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 10,
        "success_rate": 99.8
    },
    
    "merge-pdf": {
        "slug": "merge-pdf",
        "title": "Merge PDFs",
        "description": "Combine multiple PDF files into one document",
        "category": "pdf",
        "icon": "📚",
        "from_format": "PDF(s)",
        "to_format": "PDF",
        "supported_formats": ["PDF"],
        "output_format": "PDF",
        "key_features": [
            "Merge multiple files",
            "Reorder pages",
            "Batch combining",
            "Instant merge"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select multiple PDFs"},
            {"num": 2, "title": "Order", "description": "Arrange file order"},
            {"num": 3, "title": "Merge", "description": "Combine files"},
            {"num": 4, "title": "Download", "description": "Get merged PDF"}
        ],
        "related_tools": ["split-pdf", "compress-pdf", "pdf-to-image"],
        "faq": [
            {"q": "How many files?", "a": "Merge up to 50 files."},
            {"q": "Preserve page numbers?", "a": "Yes, sequential numbering."},
            {"q": "Reorder pages?", "a": "Yes, drag to reorganize."},
            {"q": "File size limit?", "a": "100MB total for all files."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Instant merging"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "📚", "title": "Quality", "description": "Combine up to 50"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 8,
        "success_rate": 99.9
    },
    
    "split-pdf": {
        "slug": "split-pdf",
        "title": "Split PDF",
        "description": "Extract pages or split PDF into separate documents",
        "category": "pdf",
        "icon": "✂️",
        "from_format": "PDF",
        "to_format": "PDF(s)",
        "supported_formats": ["PDF"],
        "output_format": "PDF",
        "key_features": [
            "Extract specific pages",
            "Split into individual pages",
            "Select page ranges",
            "Batch extraction"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select PDF file"},
            {"num": 2, "title": "Select", "description": "Choose pages to extract"},
            {"num": 3, "title": "Split", "description": "Process extraction"},
            {"num": 4, "title": "Download", "description": "Get split PDFs"}
        ],
        "related_tools": ["merge-pdf", "compress-pdf", "pdf-to-image"],
        "faq": [
            {"q": "Extract single page?", "a": "Yes, select individual pages."},
            {"q": "Page ranges?", "a": "Yes, use ranges like 1-5, 10-15."},
            {"q": "Multiple files output?", "a": "Yes, each section as separate PDF."},
            {"q": "Large PDFs?", "a": "Supports 500+ page documents."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Instant splitting"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "✂️", "title": "Quality", "description": "Per-page extraction"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 6,
        "success_rate": 99.9
    },
    
    "csv-to-excel": {
        "slug": "csv-to-excel",
        "title": "CSV to Excel",
        "description": "Convert CSV (comma-separated values) to Excel XLSX format",
        "category": "document",
        "icon": "📊",
        "from_format": "CSV",
        "to_format": "XLSX",
        "supported_formats": ["CSV", "TSV"],
        "output_format": "XLSX",
        "key_features": [
            "Preserve data integrity",
            "Auto-format columns",
            "Handle delimiters",
            "Batch conversion"
        ],
        "steps": [
            {"num": 1, "title": "Upload", "description": "Select CSV file"},
            {"num": 2, "title": "Parse", "description": "Detect delimiters"},
            {"num": 3, "title": "Convert", "description": "Generate Excel"},
            {"num": 4, "title": "Download", "description": "Get XLSX file"}
        ],
        "related_tools": ["excel-to-pdf", "pdf-to-excel", "json-to-excel"],
        "faq": [
            {"q": "Custom delimiters?", "a": "Yes, comma, tab, semicolon, etc."},
            {"q": "Data type detection?", "a": "Auto-formats numbers and dates."},
            {"q": "Large CSV files?", "a": "Supports 100,000+ rows."},
            {"q": "Encoding?", "a": "UTF-8, ISO-8859-1, and more."}
        ],
        "quality_indicators": [
            {"icon": "⚡", "title": "Speed", "description": "Instant conversion"},
            {"icon": "🔒", "title": "Security", "description": "Encrypted transfers"},
            {"icon": "📊", "title": "Quality", "description": "Auto-formatting"},
            {"icon": "📱", "title": "All Devices", "description": "Desktop & mobile"}
        ],
        "max_file_size": 104857600,
        "processing_time_seconds": 4,
        "success_rate": 99.5
    }
}

COMPRESSION_TOOLS = [
    "compress-pdf",
    "compress-image",
    "zip-files"
]

CONVERSION_TOOLS = [
    "jpg-to-png",
    "png-to-jpg",
    "pdf-to-docx",
    "docx-to-pdf",
    "excel-to-pdf",
    "csv-to-excel"
]

EXTRACTION_TOOLS = [
    "pdf-to-image",
    "pdf-to-excel",
    "pdf-to-docx"
]

ORGANIZATION_TOOLS = [
    "merge-pdf",
    "split-pdf"
]

def get_tool_by_slug(slug):
    """Get tool metadata by slug"""
    return TOOLS_DATABASE.get(slug)

def get_all_tools():
    """Get all tools list"""
    return list(TOOLS_DATABASE.values())

def get_tools_by_category(category):
    """Get tools for specific category"""
    return [tool for tool in TOOLS_DATABASE.values() if tool['category'] == category]

def search_tools(query):
    """Search tools by title, description, or slug"""
    query = query.lower()
    results = []
    for tool in TOOLS_DATABASE.values():
        if (query in tool['slug'].lower() or 
            query in tool['title'].lower() or 
            query in tool['description'].lower()):
            results.append(tool)
    return results

def get_related_tools(tool_slug, limit=3):
    """Get related tools for a given tool"""
    tool = get_tool_by_slug(tool_slug)
    if not tool:
        return []
    
    related_slugs = tool.get('related_tools', [])
    related_tools = []
    for slug in related_slugs[:limit]:
        related_tool = get_tool_by_slug(slug)
        if related_tool:
            related_tools.append(related_tool)
    
    return related_tools

def is_tool_available(slug):
    """Check if tool is available"""
    return slug in TOOLS_DATABASE

def get_category_name(category_key):
    """Get category display name"""
    return TOOLS_CATEGORIES.get(category_key, "Other")
