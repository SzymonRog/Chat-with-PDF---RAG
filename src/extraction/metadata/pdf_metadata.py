from src.models.document import DocumentMetadata
from datetime import datetime
from pathlib import Path
from pdfplumber import PDF

class PDFMetadata:

    def get_metadata(self, pdf: PDF, pdf_path: Path) -> DocumentMetadata:
        metadata_dict = pdf.metadata
        num_pages = len(pdf.pages)

        metadata = DocumentMetadata(
            filename=pdf_path.name,
            filepath=pdf_path,
            num_pages=num_pages,
            file_size_bytes=pdf_path.stat().st_size,
            created_at=datetime.now(),
            author=metadata_dict.get("Author"),
            title=metadata_dict.get("Title")
        )

        return metadata