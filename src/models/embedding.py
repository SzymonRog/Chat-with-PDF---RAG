from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict
from src.models.chunk import Chunk


@dataclass
class EmbeddedChunk:
    chunk: Chunk
    embedding: List[float]
    model_name: str
    embedding_time: float

    @property
    def dimension(self) -> int:
        return len(self.embedding)



@dataclass
class EmbeddedDocument:
    document_id: str
    embedded_chunks: List[EmbeddedChunk]
    model_name: str
    total_time: float
    total_cost: Optional[float] = None

    def __len__(self) -> int:
        return len(self.embedded_chunks)

    @property
    def avg_embedding_time(self) -> float:
        return self.total_time / len(self)