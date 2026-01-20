import hashlib

from src.models.document import DocumentMetadata
from datetime import datetime
from pathlib import Path
from pdfplumber import PDF

class PDFMetadata:

    def get_metadata(self, pdf: PDF, pdf_path: Path) -> DocumentMetadata:
        """
            Extracts metadata from a PDF file and returns it as a DocumentMetadata object.

            Args:
                pdf (PDF): PDF object containing pages and metadata.
                pdf_path (Path): Path to the PDF file.

            Returns:
                DocumentMetadata: Extracted document metadata.
        """

        metadata_dict = pdf.metadata
        num_pages = len(pdf.pages)

        page_text = pdf.pages[0].extract_text()

        document_id = self._make_document_id(text=page_text, size=pdf_path.stat().st_size)
        metadata = DocumentMetadata(
            filename=pdf_path.name,
            filepath=pdf_path,
            num_pages=num_pages,
            file_size_bytes=pdf_path.stat().st_size,
            created_at=datetime.now(),
            author=metadata_dict.get("Author"),
            title=metadata_dict.get("Title") if metadata_dict.get("Title") else pdf_path.name,
            document_id= document_id
        )

        return metadata

    def _make_document_id(self, text: str, size: int) -> str:
        """
            Generates a deterministic unique document ID based on filename and file size.

            Args:
                text (str): Name of the file.
                size (int): File size in bytes.

            Returns:
                str: SHA-256 hash used as document ID.
        """

        return hashlib.sha256(f"{text}_{size}".encode('utf-8')).hexdigest()