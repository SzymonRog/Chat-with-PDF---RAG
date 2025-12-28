import time
from pathlib import Path
from typing import List

from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer

from src.embeddings.cache import Cache
from src.embeddings.cost_tracker import cost_tracker
from src.models.chunk import Chunk
from src.models.embedding import EmbeddedChunk


class LocalEmbedder:
    """
    Embeds text chunks locally using a Sentence-Transformers model.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        ),
        embedding_cache = Cache(Path("../../data/tables/embedding_cache.db")),
    ):
        """
        Load the embedding model and tokenizer.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        self.tokenizer = tokenizer
        self.embedding_cache = embedding_cache


    def embed_batch(
        self,
        chunks: List[Chunk],
        batch_size: int = 5,
    ) -> List[EmbeddedChunk]:
        """
        Embed chunks in fixed-size batches and return their embeddings.
        """
        embedded_chunks: List[EmbeddedChunk] = []

        cached_chunks: List[EmbeddedChunk] = []
        new_chunks: List[Chunk] = []

        for chunk in chunks:
            cashed_vector = self.embedding_cache.get_embedding(chunk_id=chunk.chunk_id, document_id=chunk.document_id)
            if cashed_vector is not None:
                print("This chunk already embedded")
                cached_chunks.append(
                    EmbeddedChunk(
                        chunk=chunk,
                        embedding=cashed_vector,
                        model_name=self.model_name,
                        embedding_time=0.0
                    )
                )
            else:
                new_chunks.append(chunk)

        for i in range(0, len(new_chunks), batch_size):
            batch = new_chunks[i : i + batch_size]
            texts = [chunk.text for chunk in batch]

            start_time = time.time()

            # Generate normalized embeddings
            vectors = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
            )

            elapsed_time = time.time() - start_time

            # Track token usage for the batch
            token_count = self.count_tokens(" ".join(texts))
            cost_tracker.track_request(
                model_name="local",
                num_tokens=token_count,
            )

            # Attach embeddings to original chunks
            for chunk, vector in zip(batch, vectors):
                embedded_chunk = EmbeddedChunk(
                        chunk=chunk,
                        embedding=vector,
                        model_name=self.model_name,
                        embedding_time=elapsed_time,
                )
                embedded_chunks.append(embedded_chunk)
                self.embedding_cache.save_embedding(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    embedding=vector,
                )

        all_chunks = cached_chunks + embedded_chunks
        all_chunks.sort(key=lambda x: x.chunk.chunk_index)

        return all_chunks

    def count_tokens(self, text: str) -> int:
        """
        Count tokens using the configured tokenizer.
        """
        return len(self.tokenizer.encode(text, add_special_tokens=False))
