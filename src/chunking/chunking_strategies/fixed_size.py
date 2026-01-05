import hashlib
from typing import List

from src.models.chunk import Chunk


class FixedSizeChunker:
    """Splits text into fixed-size overlapping chunks."""

    def __init__(self, chunk_size, overlap, tokenizer):
        """Initializes the chunker configuration."""
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.tokenizer = tokenizer

    def chunk(self, text, document_id) -> List[Chunk]:
        """Splits the input text into chunks and returns them."""
        chunks = []
        step = self.chunk_size - self.overlap
        tokens = self.tokenizer.encode(text, include_special_tokens=True)
        num_tokens = len(tokens)

        for i in range(0, num_tokens, step):
            chunk_index = int(i / step)
            chunk_id = self._make_chunk_id(document_id, chunk_index)

            chunk_ids = tokens[i : i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_ids)

            chunks.append(Chunk(
                text=chunk_text,
                document_id=document_id,
                chunk_index=chunk_index,
                chunk_id=chunk_id,
            ))

        return chunks

    def _make_chunk_id(self, document_id: str, chunk_index) -> str:
        """Generates a unique chunk ID based on document ID and chunk index."""
        return hashlib.sha256(f"{document_id}_{chunk_index}".encode()).hexdigest()

