from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict




@dataclass
class ExtractedText:
    """Text from extracted pages"""
    text: str
    page_text: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        """Number of characters extracted."""
        return len(self.text)

    @property
    def num_words(self) -> int:
        """Number of words extracted."""
        return len(self.text.split())