from abc import ABC, abstractmethod
from pathlib import Path
from src.models.document import ExtractedDocument

class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.
    """

    def extract_from_file(self, pdf_path: Path) -> ExtractedDocument:
        """
        Main method to extract from pdf file.
        :param pdf_path: path to pdf file.
        :return: processed extracted document.
        :raises FileNotFoundError: if pdf file doesn't exist.
        """

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file '{pdf_path}' doesn't exist.")

        return self.extract()

    @abstractmethod
    def extract(self) -> ExtractedDocument:
        """
        Extract content from pdf file.
        :param pdf_path: path to pdf file.
        :return: Extracted document.
        """
        pass
