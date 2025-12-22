from collections import defaultdict
from pdfplumber.page import Page
from src.models.extracted_text import ExtractedText


class TextExtractor:
    """Collects and builds text extracted from PDF pages."""

    def __init__(self):
        self.tolerance_y = 3
        self.page_texts: list[str] = []

    def on_page(self, page: Page) -> None:
        words = page.extract_words()
        page_text = self._process_page_words(words)
        self.page_texts.append(page_text)

    def build_result(self) -> ExtractedText:
        full_text = "\n\n".join(self.page_texts)
        return ExtractedText(
            text=full_text,
            page_text=self.page_texts
        )

    def _process_page_words(self, words: list[dict]) -> str:
        if not words:
            return ""

        lines_y = defaultdict(list)

        for word in words:
            for top in lines_y:
                if abs(top - word["top"]) <= self.tolerance_y:
                    lines_y[top].append(word)
                    break
            else:
                lines_y[word["top"]].append(word)

        page_lines = []
        for _, line in sorted(lines_y.items(), key=lambda x: x[0]):
            line.sort(key=lambda w: w["x0"])
            page_lines.append(" ".join(w["text"] for w in line))

        return "\n".join(page_lines)
