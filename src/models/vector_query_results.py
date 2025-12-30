from typing import TypedDict, Dict, Any, List, Optional


class SearchHit(TypedDict):
    id: str
    score: float
    values: Optional[List[float]]
    metadata: Dict[str, Any]


class SearchResult(TypedDict):
    matches: List[SearchHit]