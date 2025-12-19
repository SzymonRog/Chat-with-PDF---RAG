# Architecture Overview

## High-Level Design
```
┌─────────────┐
│ PDF Input   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Extraction Module   │  ← Week 1
│ - Text (pypdf)      │
│ - Tables (plumber)  │
│ - OCR (tesseract)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Chunking Module     │  ← Week 2
│ - Fixed size        │
│ - Semantic          │
│ - Recursive         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Embedding Module    │  ← Week 3
│ - OpenAI API        │
│ - Caching           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Vector DB           │  ← Week 3
│ - ChromaDB          │
│ - Similarity search │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Retrieval Module    │  ← Week 4
│ - Hybrid search     │
│ - Reranking         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Generation Module   │  ← Week 5
│ - LLM (GPT/Claude)  │
│ - Prompt templates  │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│ Answer      │
└─────────────┘
```

## Design Principles

1. **Modularity**: Each module is independent and testable
2. **Abstraction**: Use ABC for swappable implementations
3. **Type Safety**: Full type hints everywhere
4. **Testing**: 80%+ coverage, integration tests
5. **Documentation**: Every decision documented

## Technology Stack

- **Language**: Python 3.11+
- **PDF**: pypdf, pdfplumber, pymupdf
- **Embeddings**: OpenAI API
- **Vector DB**: ChromaDB (local), Pinecone (production)
- **LLM**: OpenAI GPT-3.5/4
- **Testing**: pytest, pytest-cov
- **CI/CD**: GitHub Actions
- **Code Quality**: black, ruff, mypy, pre-commit

## Module Responsibilities

### Extraction
- Input: PDF file path
- Output: Structured document (text, tables, images)
- Handles: Text-based, scanned, hybrid PDFs

### Chunking
- Input: Document text
- Output: List of chunks with metadata
- Handles: Multiple strategies, overlap optimization

### Embeddings
- Input: Text chunks
- Output: Vector embeddings
- Handles: Caching, batch processing, cost optimization

### Vector DB
- Input: Embeddings + metadata
- Output: Storage interface
- Handles: Indexing, similarity search, filtering

### Retrieval
- Input: Query string
- Output: Relevant chunks
- Handles: Hybrid search, reranking, query optimization

### Generation
- Input: Query + retrieved context
- Output: Generated answer
- Handles: Prompt engineering, streaming, error handling

## Future Enhancements

- [ ] Multi-modal support (images, charts)
- [ ] Streaming responses
- [ ] User feedback loop
- [ ] A/B testing framework
- [ ] Cost analytics dashboard
