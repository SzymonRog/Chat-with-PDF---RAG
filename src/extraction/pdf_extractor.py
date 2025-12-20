from datetime import datetime
from src.extraction.base import BaseExtractor
from pathlib import Path
from src.models.document import ExtractedDocument, DocumentMetadata
from src.models.extracted_text import ExtractedText

from src.extraction.text_extractor import TextExtractor



class PDFExtractor(BaseExtractor):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text_extractor = TextExtractor()

    def extract(self, pdf_path:Path) -> ExtractedDocument:
        text =  self.text_extractor.extract(pdf_path)
        tables = []
        images = []
        
        metadata = DocumentMetadata(
            filename="Test",
            filepath=pdf_path,
            num_pages=1,
            file_size_bytes=1,
            created_at=datetime.now(),
            pdf_version='A',
            author='Szymon',
            title='PDF TEST',

        )


        return ExtractedDocument(
            text=text.text,
            page_text=text.page_text,
            tables=tables,
            images=images,
            metadata=metadata
        )