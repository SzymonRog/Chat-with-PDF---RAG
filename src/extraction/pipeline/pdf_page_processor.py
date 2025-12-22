from pathlib import Path
from typing import Optional

from pdfplumber import PDF

from src.extraction.extractors.text.text_extractor import TextExtractor
from src.extraction.extractors.images.image_extractor import ImageExtractor
from src.extraction.extractors.tables.table_extractor import TableExtractor
from src.extraction.metadata.pdf_metadata import PDFMetadata

from src.models.document import ExtractedDocument
from src.models.extracted_text import ExtractedText


class PDFPageProcessor:
    """
    Orchestrates page-by-page PDF processing.
    Delegates extraction to specialized extractors and builds final result.
    """

    def __init__(self) -> None:
        self.text_extractor = TextExtractor()
        self.image_extractor = ImageExtractor()
        self.table_extractor = TableExtractor()
        self.metadata_extractor = PDFMetadata()

        self.metadata = None
        self.text_result: Optional[ExtractedText] = None
        self.image_result = None
        self.table_result = None

    def process_pages(self, pdf: PDF, pdf_path: Path) -> None:
        """Process all pages of the PDF."""

        for page in pdf.pages:
            self.text_extractor.on_page(page)
            self.image_extractor.on_page(page)
            self.table_extractor.on_page(page)

        self.text_result = self.text_extractor.build_result()
        self.image_result = self.image_extractor.build_result()
        self.table_result = self.table_extractor.build_result()
        self.metadata = self.metadata_extractor.get_metadata(pdf, pdf_path)

    def build_result(self) -> ExtractedDocument:
        """Build and return the extracted document."""

        if self.text_result is None or self.metadata is None:
            raise RuntimeError("PDF must be processed before building result")

        return ExtractedDocument(
            text=self.text_result.text,
            page_text=self.text_result.page_text,
            tables=self.table_result,
            images=self.image_result,
            metadata=self.metadata,
        )
