from transformers import AutoTokenizer

from src.chunking.chunking_pipline import ChunkingPipeline
from pathlib import Path
from src.extraction.pipeline.pdf_extractor import PDFExtractor
from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.vectordb.pinecone_store import VectordbStore
from src.cache.cache import Cache

import time
def main():
    embedding_cache = Cache(Path("../../data/tables/embedding_cache.db"))

    tokenizer = AutoTokenizer.from_pretrained(
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    pdf_path = Path("../../pdfs/test5.pdf")

    if not pdf_path.exists():
        print(f"PDF '{pdf_path}' nie istnieje. Wrzuc plik testowy do folderu pdfs/")
        return

    # Tworzymy extractor
    extractor = PDFExtractor(pdf_path)
    start = time.time()
    data = extractor.extract()
    end = time.time()
    total_time = end - start

    print(f"Total time for extraction: {total_time} seconds.")

    chunker = ChunkingPipeline(
        strategy="sentence",
        chunk_size=250,
        overlap=30,
        tokenizer=tokenizer,
    )
    start = time.time()
    chunked_document = chunker.chunk_document(data)
    end = time.time()
    total_time = end - start

    print(f"Total time for chunking pipline: {total_time} seconds.")

    embedding = EmbeddingPipeline(
        provider="local",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=2,
        tokenizer=tokenizer,
    )
    start = time.time()
    embedded_document = embedding.embed_document(chunked_document)
    end = time.time()

    total_time = end - start


    print("\n --------- Embedding ---------")
    print(f"Total time for embedding: {total_time} seconds.")
    print(f"Model name: {embedded_document.model_name}")


    pinecone_store = VectordbStore()
    pinecone_store.create_index(dimensions=384)
    start = time.time()
    pinecone_store.upsert_document(embedded_document)
    end = time.time()
    total_time = end - start

    print("\n --------- VectorDb ---------")
    print(f"Total time for upserting: {total_time} seconds.")

if __name__ == "__main__":
    main()

