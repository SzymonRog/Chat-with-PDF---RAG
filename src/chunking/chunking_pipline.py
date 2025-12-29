# src/chunking/base.py
"""
Chunking Pipeline - orchestrates different chunking strategies.
"""

from typing import List, Literal

from tokenizers import Tokenizer
from transformers import AutoTokenizer

from src.models.document import ExtractedDocument
from src.models.chunk import Chunk, ChunkedDocument


class ChunkingPipeline:
    """
    Main pipeline for chunking text documents.

    Manages different chunking strategies (fixed_size, sentence, semantic).
    Allows easy switching between strategies without changing code.

    Example:
        # Fixed size chunks
        pipeline = ChunkingPipeline(strategy="fixed_size", chunk_size=500)
        chunked_doc = pipeline.chunk_document(document)

        # Sentence-based chunks
        pipeline = ChunkingPipeline(strategy="sentence", chunk_size=1000)
        chunked_doc = pipeline.chunk_document(document)
    """

    def __init__(
            self,
            strategy: Literal["fixed_size", "sentence"] = "sentence",
            chunk_size: int = 500,
            overlap: int = 50,
            tokenizer: AutoTokenizer = None,
    ):
        """
        Initialize chunking pipeline.

        Args:
            strategy: Which chunking strategy to use
            chunk_size: Target size of each chunk (in characters)
            overlap: Number of overlapping characters between chunks
        """
        self.strategy_name = strategy
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._strategy = None  # Lazy loaded
        self.tokenizer = tokenizer

    @property
    def strategy(self):
        """
        Get the chunking strategy instance.

        Lazy loads the strategy on first access.
        """
        if self._strategy is None:
            self._strategy = self._load_strategy()
        return self._strategy

    def _load_strategy(self):
        """
        Load the appropriate chunking strategy.

        Returns:
            Instance of the selected chunking strategy

        Raises:
            ValueError: If the strategy name is not recognized
        """
        if self.strategy_name == "fixed_size":
            from src.chunking.chunking_strategies.fixed_size import FixedSizeChunker
            return FixedSizeChunker(
                chunk_size=self.chunk_size,
                overlap=self.overlap,
                tokenizer=self.tokenizer
            )

        elif self.strategy_name == "sentence":
            from src.chunking.chunking_strategies.sentence import SentenceChunker
            return SentenceChunker(
                max_chunk_size=self.chunk_size,
                overlap=self.overlap,
                tokenizer=self.tokenizer
            )
        else:
            raise ValueError(
                f"Unknown strategy: {self.strategy_name}. "
                f"Available: fixed_size, sentence, semantic"
            )

    def chunk_document(self, document: ExtractedDocument) -> ChunkedDocument:
        """
        Split a document into chunks.

        Args:
            document: ProcessedDocument from extraction

        Returns:
            ChunkedDocument with list of chunks and metadata
        """
        # Delegate to strategy
        chunks = self.strategy.chunk(
            text=document.text,
            document_id=document.metadata.document_id
        )

        return ChunkedDocument(
            chunks=chunks,
            document_id=document.metadata.document_id,
            original_text=document.text,
            chunking_method=f"{self.strategy_name}_{self.chunk_size}_{self.overlap}",
            chunk_size=self.chunk_size,
            overlap=self.overlap
        )

    def chunk_text(self, text: str, document_id: str = "unknown") -> List[Chunk]:
        """
        Convenience method to chunk raw text.

        Args:
            text: Text to split into chunks
            document_id: Optional document identifier

        Returns:
            List of Chunk objects
        """
        return self.strategy.chunk(text, document_id)