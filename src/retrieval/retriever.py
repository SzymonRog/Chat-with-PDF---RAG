from typing import List

import numpy as np
from torch import Tensor
from src.models.vector_query_results import SearchResult
from src.vectordb.pinecone_store import VectordbStore


class Retriever:
    """Retrieves embeddings from a Pinecone vector index that are similar to the embedded query"""

    def __init__(self, vectordb: VectordbStore):
        self.vectordb = vectordb


    def retrieve(self, vector: List[float], document_id: str, top_k: int = 2) -> SearchResult:
        """Retrieves embeddings from a Pinecone vector index."""

        index = self.vectordb.index
        results = index.query(
            namespace="__default__",
            vector=vector,
            top_k=top_k,
            fields=["text", "document_id"],
            filter={"document_id": document_id},
            include_metadata = True,
            include_values=True,
        )



        return results.matches








