import time
from pathlib import Path
from typing import List



from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer

from src.cache.document_database import Cache
from src.cost_tracker.cost_tracker import cost_tracker
from src.models.chunk import Chunk
from src.models.embedding import EmbeddedChunk


class LocalEmbedder:
    """
    Embeds text chunks locally using a Sentence-Transformers model.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        ),
        document_db = Cache(Path("../../data/tables/document_store.db")),
    ):

        """
            Initializes the local embedder.

            Args:
                model_name (str): Name of the Sentence-Transformers model,
                tokenizer: Tokenizer used for token counting,
                embedding_cache (Cache): Cache used to store and retrieve embeddings.
        """

        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        self.tokenizer = tokenizer
        self.document_db = document_db


    def embed_batch(
        self,
        chunks: List[Chunk],
        batch_size: int = 5,
    ) -> List[EmbeddedChunk]:
        """
            Embeds chunks in batches with optional cache reuse.

            Cached embeddings are reused when available, while missing embeddings

            Are generated using the local model.
            Args:
                chunks (List[Chunk]): Chunks to embed,
                batch_size (int): Number of chunks processed in a single batch.
                tables (List[str]): Tables to embed,
            Returns:
                List[EmbeddedChunk]: Embedded chunks ordered by chunk index.
        """


        embedded_chunks: List[EmbeddedChunk] = []
        document_id = chunks[0].document_id

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

        self.document_db.mark_as_embedded(document_id=document_id)
        return embedded_chunks

    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in the given text.
        Args:
            text (str): Input text.
        Returns:
            int: Number of tokens.
        """

        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def embed_text(self, text: str) -> list[float]:
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )
        return vector.tolist()







