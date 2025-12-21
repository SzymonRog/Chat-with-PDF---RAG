from collections import defaultdict
from pathlib import Path
from src.models.extracted_text import ExtractedText
import pdfplumber

class TextExtractor:
    """Text Extractor class."""
    def __init__(self):
        self.tolerance_y = 3


    def extract(self, pdf_path: Path) -> ExtractedText:
        """
        Extract text from a PDF page by page.

        Groups words into lines based on vertical position, sorts lines top-to-bottom
        and words left-to-right to preserve reading order. Returns full text and per-page text.
        """
        page_texts = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                page_text = self._process_page_words(words)

                page_texts.append(page_text)
        full_text = "\n\n".join(page_texts)

        return ExtractedText(
            text=full_text,
            page_text=page_texts
        )

    def _process_page_words(self, words: list) -> str:
        """
        Process words on a page
        """
        if not words:
            return ""


        lines_y = defaultdict(list)

        for word in words:
            placed = False
            for top in lines_y:
                if abs(top - word['top']) <= self.tolerance_y:
                    lines_y[top].append(word)
                    placed = True
                    break

            if not placed:
                lines_y[word['top']].append(word)


        sorted_lines = sorted(lines_y.items(), key=lambda x: x[0])


        page_lines = []
        for top, line in sorted_lines:
            line.sort(key=lambda w: w["x0"])
            line_text = " ".join(w["text"] for w in line)
            page_lines.append(line_text)


        return "\n".join(page_lines)



