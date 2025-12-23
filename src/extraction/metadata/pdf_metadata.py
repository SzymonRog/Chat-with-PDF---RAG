import hashlib

from src.models.document import DocumentMetadata
from datetime import datetime
from pathlib import Path
from pdfplumber import PDF

class PDFMetadata:

    def get_metadata(self, pdf: PDF, pdf_path: Path) -> DocumentMetadata:
        metadata_dict = pdf.metadata
        num_pages = len(pdf.pages)
        document_id = self.make_document_id(pdf_path.name, pdf_path.stat().st_size)
        metadata = DocumentMetadata(
            filename=pdf_path.name,
            filepath=pdf_path,
            num_pages=num_pages,
            file_size_bytes=pdf_path.stat().st_size,
            created_at=datetime.now(),
            author=metadata_dict.get("Author"),
            title=metadata_dict.get("Title"),
            document_id= document_id
        )

        return metadata

    def make_document_id(self, filename: str, size: int) -> str:
        return hashlib.sha256(f"{filename}_{size}".encode('utf-8')).hexdigest()