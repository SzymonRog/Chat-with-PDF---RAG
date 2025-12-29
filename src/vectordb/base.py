from abc import ABC, abstractmethod
from typing import List

from src.models.embedding import EmbeddedDocument, EmbeddedChunk


class BaseVectorStore(ABC):
    """Defines a common interface for vector database stores."""

    @abstractmethod
    def __init__(self, batch_size: int = 50):
        """
        Initializes the vector store configuration.

        Args:
            batch_size (int): Number of vectors processed in a single batch.
        """
        self.batch_size = batch_size

    @abstractmethod
    def create_index(self, dimensions: int):
        """
        Creates the vector index if it does not exist.

        Args:
            dimensions (int): Dimensionality of the embedding vectors.
        """
        pass

    @abstractmethod
    def _upsert_batch(self, batch: List[EmbeddedChunk]):
        """
        Upserts a batch of embedded chunks into the vector store.

        Args:
            batch (List[EmbeddedChunk]): Embedded chunks to store.
        """
        pass

    @abstractmethod
    def upsert_document(self, embedded_document: EmbeddedDocument):
        """
        Upserts all embedded chunks of a document.

        Args:
            embedded_document (EmbeddedDocument): Document with embedded chunks.
        """
        pass

    @abstractmethod
    def delete_index(self):
        """
        Deletes the vector index.
        """
        pass

    @abstractmethod
    def reset_index(self):
        """
        Resets the vector index by deleting and recreating it.
        """
        pass
