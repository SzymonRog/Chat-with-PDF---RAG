import hashlib
from typing import List
from transformers import AutoTokenizer
from src.models.chunk import Chunk
class FixedSizeChunker:

    def __init__(self, chunk_size, overlap, tokenizer):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.tokenizer = tokenizer

    def chunk(self, text, document_id) -> List[Chunk]:

        chunks = []
        step = self.chunk_size - self.overlap
        num_tokens = self.count_tokens(text)
        for i in range(0, num_tokens, step):
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

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=True))
