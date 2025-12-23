# PDF Extraction Pipeline

## Purpose
Extract structured data (text, tables, images, metadata) from PDF documents 
with high accuracy and performance.

## Architecture
PDFExtractor (Facade)↓

PDFLoader ← Opens/closes PDF file

↓

PDFPageProcessor (Orchestrator)

├─→ TextExtractor (line-by-line word positioning)

├─→ TableExtractor (pdfplumber table detection)

├─→ ImageExtractor (crop & filter images)

└─→ PDFMetadata (extract file metadata)

↓
ExtractedDocument (Result)

## Core Components

### PDFExtractor
- **Role:** Entry point / Facade pattern
- **Responsibility:** Orchestrate PDF opening, processing, and closing
- **Key Method:** `extract() -> ExtractedDocument`

### PDFLoader
- **Role:** PDF file lifecycle management
- **Responsibility:** Open/close pdfplumber PDF object safely
- **Pattern:** Resource manager (prevents memory leaks)

### PDFPageProcessor
- **Role:** Page-by-page orchestration
- **Responsibility:** Delegate to specialized extractors, aggregate results
- **Pattern:** Coordinator pattern

### TextExtractor
- **Role:** Text extraction with layout awareness
- **Responsibility:** Group words into lines, preserve reading order
- **Algorithm:** Y-tolerance grouping (tolerance_y=3px)

### TableExtractor
- **Role:** Table detection and validation
- **Responsibility:** Extract tables, filter by quality metrics
- **Filtering:** Min 2x2, max 50% empty cells

### ImageExtractor
- **Role:** Image extraction and filtering
- **Responsibility:** Crop images, filter noise, save to disk
- **Filtering:** Min 20x20px, max aspect ratio 10:1

## Design Decisions

### Why Facade Pattern (PDFExtractor)?
**Problem:** Complex initialization (loader + processor + extractors)
**Solution:** Single entry point `PDFExtractor(pdf_path).extract()`
**Benefit:** Simple API, hides complexity

### Why Separate Extractors?
**Problem:** PDFPageProcessor would be 500+ lines (God Object)
**Solution:** Single Responsibility - each extractor does ONE thing
**Benefit:** 
- Easy to test individually
- Easy to swap implementations
- Clear separation of concerns

### Why Y-tolerance Grouping?
**Problem:** PDF words have slight vertical variance (floating point positions)
**Solution:** Group words within 3px Y-distance as same line
**Tradeoff:** May merge slightly offset lines (rare)
**Alternative Considered:** Clustering (overkill for most PDFs)

### Why Filter Images?
**Problem:** PDFs contain decorative elements (lines, bullets, icons)
**Solution:** Size + aspect ratio filtering
**Benefit:** Reduce noise, save storage

## Future Improvements

### High Priority
- [ ] **Column detection** - Currently merges multi-column text
  - Consider: pdfplumber layout analysis or clustering X positions
  
- [ ] **OCR fallback** - No support for scanned PDFs
  - Add: Tesseract/EasyOCR when text extraction fails
  
- [ ] **Better table parsing** - Complex tables (merged cells) fail
  - Consider: Camelot or custom table detection

### Medium Priority
- [ ] **Progress callbacks** - No feedback for large PDFs
- [ ] **Parallel page processing** - Process pages concurrently
- [ ] **Streaming API** - Yield pages instead of loading all

### Low Priority
- [ ] **Form field extraction** - Interactive PDFs not supported
- [ ] **Annotation extraction** - Comments/highlights ignored

## Performance Characteristics

| PDF Type | Speed | Accuracy | Notes |
|----------|-------|----------|-------|
| Simple text | Fast (0.1s/page) | 95%+ | Single column, no tables |
| Multi-column | Fast (0.1s/page) | 70% | Text order may be wrong |
| Tables | Medium (0.3s/page) | 85% | Depends on table complexity |
| Scanned | N/A | 0% | No OCR support yet |

## Related Modules
- [Chunking Pipeline](../chunking/README.md) - Consumes ExtractedDocument
- [Models](../../api/models.md) - ExtractedDocument, ExtractedText data classes
