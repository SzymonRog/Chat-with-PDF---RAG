from pathlib import Path
import pdfplumber

class PDFLoader:

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self._pdf = None

    def open_pdf(self):
        if self._pdf is None:
            self._pdf = pdfplumber.open(self.pdf_path)
        return self._pdf

    def close_pdf(self):
        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

    @property
    def pdf(self):
        if self._pdf is None:
            self.open_pdf()
