# RAG PDF Query System 

Production-grade Retrieval-Augmented Generation system for PDF documents.

## Project Goal

Build a professional RAG system for summer internship portfolio, demonstrating:
- Clean code architecture
- Test-driven development
- Performance optimization
- Production-ready practices

Timeline (6 weeks)

- **Week 1**: PDF Extraction (text, tables, OCR)
- **Week 2**: Chunking Strategies
- **Week 3**: Embeddings & Vector DB
- **Week 4**: Retrieval & Reranking
- **Week 5**: LLM Generation & Cost Optimization
- **Week 6**: Testing, CI/CD, Documentation

## Current Status
```
┌─────────────────┬──────────┬──────────┐
│ Module          │ Status   │ Coverage │
├─────────────────┼──────────┼──────────┤
│ Extraction      │ 🚧 WIP   │ 70%       │
│ Chunking        │ ⚪ Todo  │ -        │
│ Embeddings      │ ⚪ Todo  │ -        │
│ Retrieval       │ ⚪ Todo  │ -        │
│ Generation      │ ⚪ Todo  │ -        │
└─────────────────┴──────────┴──────────┘
```

## Quick Start
```bash
# Clone
git clone https://github.com/yourusername/rag-system.git
cd rag-system

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check --fix src/ tests/
```

##  Documentation

- [Architecture](docs/architecture.md)
- [API Documentation](docs/api/usage.md)
- [Design Decisions](docs/decisions/)

##  Development
```bash
# Install pre-commit hooks
pre-commit install

# Run specific tests
pytest tests/extraction/

# Check coverage
pytest --cov

# Type checking
mypy src/
```

## Benchmarks

Coming soon...

## Contributing

This is a personal learning project, but feedback is welcome!

##  License

MIT License
EOF
