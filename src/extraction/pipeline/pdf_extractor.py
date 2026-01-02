from pathlib import Path

from src.extraction.pipeline.base import BaseExtractor
from src.extraction.pipeline.pdf_loader import PDFLoader
from src.extraction.pipeline.pdf_page_processor import PDFPageProcessor
from src.models.document import ExtractedDocument


class PDFExtractor(BaseExtractor):
    """
    High-level PDF extraction pipeline.

    Responsibilities:
    - Open and close the PDF document
    - Delegate page processing to PDFPageProcessor
    - Return a fully extracted document object

    This class acts as a facade and does not perform
    any extraction logic itself.
    """

    def __init__(self, pdf_path: Path) -> None:
        self.pdf_path = pdf_path
        self.pdf_loader = PDFLoader(pdf_path)
        self.page_processor = PDFPageProcessor()

    def extract(self) -> ExtractedDocument:
        """
        Run the full PDF extraction pipeline.

        Steps:
        1. Open PDF document
        2. Process all pages (text, tables, images, metadata)
        3. Build extracted document result
        4. Close PDF document

        Returns:
            ExtractedDocument: Complete extraction result
        """
        pdf = self.pdf_loader.open_pdf()

        try:
            self.page_processor.process_pages(pdf, self.pdf_path)
            return self.page_processor.build_result()
        finally:
            self.pdf_loader.close_pdf()


