import time
from typing import List
from dotenv import load_dotenv
from src.embeddings.embedders.openai_embedder import OpenAIEmbedder
from src.models.chunk import Chunk
from src.models.embedding import EmbeddedChunk, EmbeddedDocument
from transformers import AutoTokenizer

load_dotenv()

class EmbeddingPipeline:
    """
    Manager for different embedding providers.

    Similar architecture to ChunkingPipeline:
    - User interacts only with this class
    - Internally delegates to OpenAIEmbedder/LocalEmbedder
    - Lazy loads embedder on first use
    """

    def __init__(self, provider="openai", model_name=None, batch_size=50):
        self.provider = provider
        self.model_name = model_name
        self.batch_size = batch_size
        self.total_time = 0
        self._embedder = None

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = self._load_embedder()
        return self._embedder

    def _load_embedder(self):
        if self.provider == "openai":
            from src.embeddings.embedders.openai_embedder import OpenAIEmbedder
            return OpenAIEmbedder(
                model_name=self.model_name,
        )

        elif self.provider == "local":
            from src.embeddings.embedders.locla_embedder import LocalEmbedder
            return LocalEmbedder(
                model_name=self.model_name
        )

        else:
            raise ValueError(f"Unknown embedder provider: {self.provider}")


    def embed_chunks(self, chunks: List[Chunk]) -> List[EmbeddedChunk]:
        start_time = time.time()
        embedded_chunks = self.embedder.embed_batch(chunks=chunks, batch_size=self.batch_size)
        self.total_time += time.time() - start_time
        return embedded_chunks


    def embed_document(self, chunked_doc) -> EmbeddedDocument:
        return EmbeddedDocument(
            document_id=chunked_doc.document_id,
            embedded_chunks=self.embed_chunks(chunked_doc.chunks),
            model_name=self.model_name,
            total_time=self.total_time,
        )