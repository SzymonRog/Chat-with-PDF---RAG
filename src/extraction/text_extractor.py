from collections import defaultdict

from src.extraction.base import BaseExtractor
from pathlib import Path
from src.models.extracted_text import ExtractedText
import pdfplumber

class TextExtractor:
    """Text Extractor class."""

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

                # Group words into lines, allowing slight vertical variance
                lines = defaultdict(list)
                tolerance = 3
                for word in words:
                    placed = False
                    for top in lines:
                        if abs(top - word['top']) <= tolerance:
                            lines[top].append(word)
                            placed = True
                            break
                    if not placed:
                        lines[word['top']].append(word)

                # Sort lines top-to-bottom
                sorted_lines = sorted(lines.items(), key=lambda x: x[0], reverse=False)
                page_lines = []
                for _, line_words in sorted_lines:
                    line_words.sort(key=lambda x: x['x0'])  # left-to-right order
                    line_text = " ".join(word['text'] for word in line_words)
                    page_lines.append(line_text)

                page_texts.append("\n".join(page_lines))

        full_text = "\n\n".join(page_texts)

        return ExtractedText(
            text=full_text,
            page_text=page_texts
        )



