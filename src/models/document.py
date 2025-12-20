from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict

@dataclass
class DocumentMetadata:
    """Information about a document."""
    filename: str
    filepath: Path
    num_pages: int
    file_size_bytes: int
    created_at: datetime
    pdf_version: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None

    @property
    def file_size_mb(self) -> float:
        return self.file_size_bytes / (1024 * 1024)


@dataclass
class ExtractedDocument:
    """Result od Document Extraction"""
    text: str
    metadata: DocumentMetadata
    page_text: List[str] = field(default_factory=list)
    tables: List[Any] = field(default_factory=list)
    images: List[Any] = field(default_factory=list)

    def __len__(self) -> int:
        """Number of characters extracted."""
        return len(self.text)

    @property
    def num_words(self) -> int:
        """Number of words extracted."""
        return len(self.text.split())

    def get_page_text(self, page_num) -> str:
        """Get the text from the specified page.
        Args:
            page_num (int): Page number (from 0)
        Returns:
            str: Page text
        """
        if  0 <= page_num < len(self.page_text):
            return self.page_text[page_num]
        raise IndexError(f"Page {page_num} out of range")

class PDFExtractionError(Exception):
    """Exception raised when an error occurs while extracting PDF."""
    pass

class InvalidPDFError(PDFExtractionError):
    """Raised when PDF file is invalid or corrupted."""

class ExtractionFailedError(PDFExtractionError):
    """Raised when text extraction failed."""



