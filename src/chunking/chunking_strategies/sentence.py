from typing import List
import hashlib
import re
from src.models.chunk import Chunk
from transformers import AutoTokenizer

class SentenceChunker:
    """
    Sentence-aware text chunker with a fixed-size fallback.

    Strategy:
    - Split text into paragraphs.
    - Split paragraphs into sentences.
    - Pack multiple sentences into a chunk until `max_chunk_size` is reached.
    - If a single sentence exceeds `max_chunk_size`, fall back to
      fixed-size chunking with overlap (sliding window).
    """

    def __init__(self, max_chunk_size: int, overlap: int, tokenizer):
        """
        Initialize the chunker.

        :param max_chunk_size: Maximum number of tokens per chunk.
        :param overlap: Number of overlapping tokens between chunks
                        when fixed-size fallback is used.
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.tokenizer = tokenizer

    def chunk(self, text: str, document_id: str) -> List[Chunk]:
        """
        Split input text into semantic chunks.

        :param text: Full document text.
        :param document_id: Stable identifier of the source document.
        :return: List of Chunk objects.
        """
        SENTENCE_DELIMITERS = [ "?", "!", ";", ":"]
        chunks: List[Chunk] = []

        # Normalize sentence delimiters to a single character ('.')
        for delimiter in SENTENCE_DELIMITERS:
            text = text.replace(delimiter, ".")

        paragraphs = text.split("\n\n")

        chunk_index = 0
        buffer = ""

        for paragraph in paragraphs:
            sentences = self.split_sentences_safely(text=paragraph)


            for sentence in sentences:
                tokens = self.tokenizer.encode(sentence, add_special_tokens=False)
                num_tokens = len(tokens)
                # Fallback: very long sentence → fixed-size sliding window
                if num_tokens > self.max_chunk_size:

                    step = self.max_chunk_size - self.overlap

                    for i in range(0, num_tokens, step):
                        token_window = tokens[i : i + self.max_chunk_size]
                        chunk_text = self.tokenizer.decode(token_window)

                        chunks.append(
                            self._make_chunk(
                                text=chunk_text,
                                document_id=document_id,
                                chunk_index=chunk_index,
                            )
                        )
                        chunk_index += 1

                    buffer = " "
                    continue

                # Normal sentence packing
                if self.count_tokens(buffer + sentence) <= self.max_chunk_size:
                    buffer += sentence
                else:
                    chunks.append(
                        self._make_chunk(
                            text=buffer.strip(),
                            document_id=document_id,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1
                    buffer = sentence + " "

        # Flush remaining buffered text
        if buffer:
            chunks.append(
                self._make_chunk(
                    text=buffer.strip(),
                    document_id=document_id,
                    chunk_index=chunk_index,
                )
            )

        return chunks

    def split_sentences_safely(self,text: str) -> list[str]:
        """
        Split text into sentences while ignoring:
        - numeric list items (e.g. '5.')
        - short abbreviations (1–2 letters, e.g. 'dr.', 'nr.')
        """

        sentences = []
        buffer = ""

        tokens = re.split(r"(\.)", text)

        for i in range(0, len(tokens) - 1, 2):
            part = tokens[i].strip()
            dot = tokens[i + 1]

            buffer += part + dot

            # Look behind before dot
            match = re.search(r"(\b\w+)$", part)
            last_token = match.group(1) if match else ""

            # Rules: do NOT split
            if last_token.isdigit():
                continue
            if len(last_token) <= 3 and last_token.isalpha():
                continue

            # Otherwise → sentence boundary
            sentences.append(buffer.strip())
            buffer = ""

        if buffer.strip():
            sentences.append(buffer.strip())

        return sentences

    def _make_chunk(
        self,
        text: str,
        document_id: str,
        chunk_index: int,
    ) -> Chunk:
        """
        Create a Chunk object with deterministic ID.

        :param text: Chunk text.
        :param document_id: Identifier of the source document.
        :param chunk_index: Sequential index of the chunk within the document.
        :param start_char: Start character offset (optional).
        :param end_char: End character offset (optional).
        :return: Chunk instance.
        """
        return Chunk(
            text=text,
            document_id=document_id,
            chunk_index=chunk_index,
            chunk_id=self.make_chunk_id(document_id, chunk_index),

        )

    def make_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """
        Generate a deterministic chunk ID based on document ID and chunk index.

        :param document_id: Identifier of the source document.
        :param chunk_index: Sequential index of the chunk.
        :return: SHA-256 hash as a hex string.
        """
        return hashlib.sha256(
            f"{document_id}_{chunk_index}".encode()
        ).hexdigest()

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text."""
        return len(self.tokenizer.encode(text, add_special_tokens=True))
