from io import BytesIO
from PyPDF2 import PdfReader

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_pdf_bytes(data: bytes) -> None:
    if len(data) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    if not data.startswith(b"%PDF-"):
        raise ValueError("Not a PDF")

    try:
        PdfReader(BytesIO(data))
    except Exception:
        raise ValueError("Corrupted PDF")
