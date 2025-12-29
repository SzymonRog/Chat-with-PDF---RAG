import time
from typing import List

from pinecone import Pinecone, ServerlessSpec
import dotenv
import os
from src.models.embedding import EmbeddedDocument, EmbeddedChunk
from src.vectordb.base import BaseVectorStore

dotenv.load_dotenv()


class VectordbStore(BaseVectorStore):
    """Manages storage and retrieval of embeddings in a Pinecone vector index."""

    def __init__(self, batch_size: int = 50):
        """
        Initializes the Pinecone vector store.

        Args:
            batch_size (int): Number of vectors upserted in a single batch.
        """

        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "chat-with-pdf"
        self.index = None
        self.batch_size = batch_size

        if self.pc.has_index(self.index_name):
            self.index = self.pc.Index(self.index_name)

    def create_index(self, dimensions: int = 384):
        """
            Creates the Pinecone index if it does not already exist.

            Args:
                dimensions (int): Dimensionality of the embedding vectors.
        """
        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                name=self.index_name,
                dimension=dimensions,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                )
            )

            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(0.1)
                print(f"Index {self.index_name} created and ready")
        else:
            self.index = self.pc.Index(self.index_name)
            print(f"Index {self.index_name} already exists")

            self.index = self.pc.Index(self.index_name)
            print(self.index)

    def _upsert_batch(self, batch: List[EmbeddedChunk]):
        """
            Uploads a batch of embedded chunks to the vector index.

            Args:
                batch (List[EmbeddedChunk]): Embedded chunks to upsert.
        """

        prepared_batch = []
        for embedded_chunk in batch:
            prepared_batch.append({
                "id": embedded_chunk.chunk.chunk_id,
                "values": embedded_chunk.embedding,
                "metadata": {
                    "document_id": embedded_chunk.chunk.document_id,  # snake_case
                    "chunk_index": embedded_chunk.chunk.chunk_index,
                    "text": embedded_chunk.chunk.text  # dodaj tekst do wyszukiwania!
                },
            })

        self.index.upsert(vectors=prepared_batch)

    def upsert_document(self, embedded_document: EmbeddedDocument):
        """
            Uploads all embedded chunks of a document to the vector index.

            Args:
                embedded_document (EmbeddedDocument): Document containing embedded chunks.
        """

        if self.index is None:
            raise ValueError("Index not initialized. Call create_index() first.")

        embedded_chunks = embedded_document.embedded_chunks
        for i in range(0, len(embedded_chunks), self.batch_size):
            batch = embedded_chunks[i: i + self.batch_size]
            self._upsert_batch(batch)
            print(f"Uploaded batch {i // self.batch_size + 1}")

    def delete_index(self):
        """
            Deletes the existing Pinecone index.
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call create_index() first.")
        self.pc.delete_index(self.index_name)
        self.index = None

    def reset_index(self):
        """
            Deletes and recreates the Pinecone index.
        """
        self.delete_index()
        self.create_index()
