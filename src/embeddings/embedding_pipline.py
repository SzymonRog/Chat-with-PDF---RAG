import time
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from torch import Tensor

from src.cache.cache import Cache
from src.models.chunk import Chunk
from src.models.embedding import EmbeddedChunk, EmbeddedDocument
from transformers import AutoTokenizer

load_dotenv()

class EmbeddingPipeline:
    """Handles embedding generation using different embedding providers."""

    def __init__(self, provider="local", model_name=None, batch_size=50, tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")):
        """
            Initializes the embedding pipeline.

            Args:
                provider (str): Embedding provider identifier ("local" or "openai").
                model_name (str | None): Name of the embedding model to use.
                batch_size (int): Number of chunks embedded in a single batch.
                tokenizer: Tokenizer used for token counting.
        """

        self.provider = provider
        self.model_name = model_name
        self.batch_size = batch_size
        self.total_time = 0
        self._embedder = None
        self.tokenizer = tokenizer
        self.embedding_cache = Cache(Path("../../data/tables/embedding_cache.db"))

    @property
    def embedder(self):
        """
            Returns the embedder instance.

            Returns:
                The initialized embedder, loaded on first access.
        """

        if self._embedder is None:
            self._embedder = self._load_embedder()
        return self._embedder

    def _load_embedder(self):
        """
            Loads the embedder implementation based on the configured provider.

            Returns:
                An embedder instance compatible with the pipeline.
        """

        if self.provider == "openai":
            from src.embeddings.embedders.openai_embedder import OpenAIEmbedder
            return OpenAIEmbedder(
                model_name=self.model_name,
        )

        elif self.provider == "local":
            from src.embeddings.embedders.locla_embedder import LocalEmbedder
            return LocalEmbedder(
                model_name=self.model_name,
                tokenizer=self.tokenizer,
                embedding_cache=self.embedding_cache,
        )

        else:
            raise ValueError(f"Unknown embedder provider: {self.provider}")


    def embed_chunks(self, chunks: List[Chunk]) -> List[EmbeddedChunk]:
        """
            Embeds a list of text chunks.

            Args:
                chunks (List[Chunk]): Chunks to be embedded.

            Returns:
                List[EmbeddedChunk]: Embedded chunks with vector representations.
        """

        start_time = time.time()
        embedded_chunks = self.embedder.embed_batch(chunks=chunks, batch_size=self.batch_size)
        self.total_time += time.time() - start_time
        return embedded_chunks


    def embed_document(self, chunked_doc) -> EmbeddedDocument:
        """
            Embeds all chunks of a document.

            Args:
                chunked_doc: Object containing document ID and chunk list.

            Returns:
                EmbeddedDocument: Embedded document with metadata and embeddings.
        """

        return EmbeddedDocument(
            document_id=chunked_doc.document_id,
            embedded_chunks=self.embed_chunks(chunked_doc.chunks),
            model_name=self.model_name,
            total_time=self.total_time,
        )

    def embed_text(self, text: str) -> List[float]:
        return self.embedder.embed_text(text)
