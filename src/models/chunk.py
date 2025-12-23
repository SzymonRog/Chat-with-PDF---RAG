
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Chunk:
    """
    Single chunk with metadata

    Used for embedding and retrival
    """

    text: str
    chunk_id: str
    document_id: str
    chunk_index: int

    start_char: int = 0
    end_char: int = 0

    def __len__(self):
        return len(self.text)

    @property
    def num_words(self):
        return len(self.text.split())

    def __repr__(self) -> str:
        preview = self.text[:50] + '...' if len(self.text) > 50 else self.text
        return f"Chunk(id={self.chunk_id}, words={self.num_words}, text='{preview}')"


@dataclass
class ChunkedDocument:
    """
    Document splited into chunks
    """
    chunks: List[Chunk]
    document_id: str
    original_text: str
    chunking_method: str


    chunk_size: int = 0
    overlap: int = 0

    def __len__(self) -> int:
        """Liczba chunków"""
        return len(self.chunks)

    def __getitem__(self, index: int) -> Chunk:
        """Pobierz chunk po indeksie"""
        return self.chunks[index]

    @property
    def total_chars(self) -> int:
        """Suma znaków we wszystkich chunkach"""
        return sum(len(chunk) for chunk in self.chunks)

    @property
    def avg_chunk_size(self) -> float:
        """Średni rozmiar chunka"""
        return self.total_chars / len(self.chunks) if self.chunks else 0