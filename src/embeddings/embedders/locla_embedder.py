import time
from typing import List
from transformers import AutoTokenizer

from sentence_transformers import SentenceTransformer
from src.embeddings.cost_tracker import cost_tracker
from src.models.chunk import Chunk
from src.models.embedding import EmbeddedChunk

class LocalEmbedder:

    def __init__(self, model_name:str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            local_files_only=True
        )


    def embed_batch(
            self,
            chunks: List[Chunk],
            batch_size: int = 5
    ) -> List[EmbeddedChunk]:
        embedded_chunks = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i + batch_size]
            start_time = time.time()
            texts = [chunk.text for chunk in batch]

            response = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
            )


            elapsed_time = time.time() - start_time
            text = " ".join(texts)
            token_num = self.count_tokens(text)

            cost = cost_tracker.track_request(
                model_name="local",
                num_tokens = token_num,
            )

            for chunk, vector in zip(batch, response):
                embedded_chunks.append(EmbeddedChunk(
                    chunk=chunk,
                    embedding=vector,
                    model_name=self.model_name,
                    embedding_time=elapsed_time,
            ))

        return embedded_chunks

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))
