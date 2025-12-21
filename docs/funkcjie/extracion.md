# PDF Extractor Documentation

## General Architecture

The project consists of modules for extracting data from PDFs:

1. **TextExtractor** – extracts readable text
2. **TableExtractor** – extracts tables
3. **ImageExtractor** – extracts images
4. **ExtractedDocument / DocumentMetadata** – data structures to store extraction results and document metadata
5. **Error Handling** – custom exceptions for PDF extraction errors

All extractors use **pdfplumber**, with images additionally processed via **PIL** (Python Imaging Library).

---

## TextExtractor

### Purpose
- Extract readable text from PDF documents
- Group words into lines to preserve reading order

### How It Works
- `pdfplumber` returns words for each page (`page.extract_words()`)
- Words are grouped into lines based on **y-coordinate** (`top`) with a tolerance of 3 points
- Lines are sorted top-to-bottom, words sorted left-to-right (`x0`)
- Returns full text and per-page text

### Strengths
- Simple and fast for standard documents
- Preserves logical word order
- Easy to use for embedding in RAG pipelines

### Limitations
- Non-standard layouts, multiple columns, charts, or unusual fonts may break reading order

### Improvement Opportunities
- Group words by **x-coordinate** for multi-column layouts
- Add OCR support for scanned documents
- Optimize to open PDF only once for all extractors

---

## TableExtractor

### Purpose
- Extract tables from PDFs and filter irrelevant data

### How It Works
- `pdfplumber` detects tables on a page (`page.extract_table()`)
- Filters tables based on:
  - Minimum number of rows and columns
  - Maximum ratio of empty cells
- Processed tables are added to the result

### Strengths
- Simple logic to clean tables
- Filters out empty or irrelevant fragments

### Limitations
- pdfplumber may detect “tables” where there aren’t any (e.g., repeating text)
- Irregular tables may not be handled correctly
- Heuristics may need to be tuned per document

### Improvement Opportunities
- Automatic table quality assessment
- OCR support for scanned tables
- Integration with TextExtractor to avoid multiple PDF loads

---

## ImageExtractor

### Purpose
- Extract images from PDF for embedding or further analysis

### How It Works
- `pdfplumber` returns a list of images (`page.images`)
- Each image is cropped to its page position (`crop(x0, top, x1, bottom)`)
- Basic filtering:
  - Minimum width and height
  - Maximum width-to-height ratio
- Avoids duplicate images by `stream_id`
- Saves images to `data/images`

### Strengths
- Simple extraction with filtering
- Prepares images for embedding or visualization
- Avoids duplicates

### Limitations
- Single-threaded; slow for large PDFs
- Cannot distinguish “content” images from decorative images
- OCR or content analysis requires additional logic

### Improvement Opportunities
- Multi-threading or GPU acceleration for large documents
- Integration with TextExtractor and TableExtractor to load PDF only once
- Optional image classification (e.g., chart, logo, photo)

---

## ExtractedDocument / DocumentMetadata

### Purpose
- Standardize extraction results
- Facilitate storage, API responses, or database saving

### Features
- Stores text, tables, images, and metadata
- Counts number of characters and words
- Retrieve text for specific pages
- Easily extendable with additional metadata (OCR, embeddings, user IDs)

---

## General Notes and Recommendations

- Each extractor currently opens the PDF independently – consider combining into a single pipeline
- Multi-threading can speed up image and table extraction
- OCR can be added after the pipeline and embeddings are stable
- For RAG, **text is most important**; images and tables are optional and useful only if they enrich embeddings
- The project demonstrates a modular approach and attention to data quality, making it strong for a portfolio
