import hashlib
from typing import List
from src.models.chunk import Chunk
class FixedSizeChunker:

    def __init__(self, chunk_size, overlap):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text, document_id) -> List[Chunk]:

        chunks = []
        step = self.chunk_size - self.overlap
        for i in range(0, len(text), step):
            chunk_index = int(i / step)
            chunk_id = self.make_chunk_id(document_id, chunk_index)
            start_char = i
            end_char = i + self.chunk_size

            chunk = text[i : i + self.chunk_size]
            chunks.append(Chunk(
                text=chunk,
                document_id=document_id,
                chunk_index=chunk_index,
                chunk_id=chunk_id,
                start_char=start_char,
                end_char=end_char,
            ))

        return chunks

    def make_chunk_id(self, document_id: str, chunk_index) -> str:
        return hashlib.sha256(f"{document_id}_{chunk_index}".encode()).hexdigest()
