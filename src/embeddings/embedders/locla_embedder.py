import time
from typing import List

from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer

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
    ):
        """
        Load the embedding model and tokenizer.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        self.tokenizer = tokenizer

    def embed_batch(
        self,
        chunks: List[Chunk],
        batch_size: int = 5,
    ) -> List[EmbeddedChunk]:
        """
        Embed chunks in fixed-size batches and return their embeddings.
        """
        embedded_chunks: List[EmbeddedChunk] = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
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
                embedded_chunks.append(
                    EmbeddedChunk(
                        chunk=chunk,
                        embedding=vector,
                        model_name=self.model_name,
                        embedding_time=elapsed_time,
                    )
                )

        return embedded_chunks

    def count_tokens(self, text: str) -> int:
        """
        Count tokens using the configured tokenizer.
        """
        return len(self.tokenizer.encode(text, add_special_tokens=False))
