# Key Design Decisions

## 1. Facade Pattern for Extraction (PDFExtractor)
**Decision:** Single entry point class wrapping complex pipeline

**Rationale:**
- Hide complexity from user
- Easy to use: `PDFExtractor(path).extract()`
- Clear separation: facade vs implementation

**Alternative Considered:** Direct use of PDFPageProcessor
**Why Rejected:** Requires understanding internal structure

---

## 2. Strategy Pattern for Chunking
**Decision:** Pluggable chunking strategies via ChunkingPipeline

**Rationale:**
- Easy to add new strategies (sentence, semantic, etc.)
- Switch strategies without code changes
- Compare strategies easily

**Alternative Considered:** One chunker class with if/else
**Why Rejected:** Violates Open/Closed Principle

---

## 3. Lazy Loading in ChunkingPipeline
**Decision:** Strategy loaded on first access
```python
@property
def strategy(self):
    if self._strategy is None:
        self._strategy = self._load_strategy()
    return self._strategy
```

**Rationale:**
- Avoid importing unused modules
- Faster initialization
- Pay-for-what-you-use

**Alternative Considered:** Eager loading in `__init__`
**Why Rejected:** Slower, imports unnecessary modules

---

## 4. Separate Extractors (Text, Table, Image)
**Decision:** Individual extractor classes instead of monolithic

**Rationale:**
- Single Responsibility Principle
- Easy to test individually
- Easy to replace (e.g., swap TextExtractor implementation)

**Alternative Considered:** All logic in PDFPageProcessor
**Why Rejected:** 500+ line God Object

---

## 5. Hash-Based IDs (Chunk, Document)
**Decision:** SHA-256 hash instead of simple strings
```python
chunk_id = hashlib.sha256(f"{document_id}_{chunk_index}".encode()).hexdigest()
```

**Rationale:**
- Deterministic (same input → same ID)
- Collision-resistant
- Fixed length (64 chars hex)

**Alternative Considered:** UUID or simple concatenation
**Why Rejected:** UUID not deterministic, concatenation not unique-guaranteed

---

## 6. Greedy Sentence Packing
**Decision:** Pack sentences until `max_chunk_size` reached

**Rationale:**
- Simple, fast
- Good enough for most use cases

**Alternative Considered:** Optimal packing (dynamic programming)
**Why Rejected:** Overkill, marginal benefit

---

## 7. No Abstract Base Classes for Strategies
**Decision:** Simple classes with `chunk()` method, no ABC inheritance

**Rationale:**
- Simpler code (less boilerplate)
- More flexible (strategies don't need to inherit)
- Pythonic (duck typing)

**Alternative Considered:** Abstract base with `@abstractmethod`
**Why Rejected:** Unnecessary complexity for this use case


