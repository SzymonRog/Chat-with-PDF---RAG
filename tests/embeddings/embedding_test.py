
from src.chunking.chunking_pipline import ChunkingPipeline
from pathlib import Path
from src.extraction.pipeline.pdf_extractor import PDFExtractor
from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.embeddings.cost_tracker import cost_tracker


import time
def main():
    pdf_path = Path("../../pdfs/test2.pdf")

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
        chunk_size=300,
        overlap=40,
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
    )
    start = time.time()
    embedded_document = embedding.embed_document(chunked_document)
    end = time.time()

    total_time = end - start

    print("\n --------- Embedding ---------")
    print(f"Total time for embedding pipline (class): {embedded_document.total_time} seconds.")
    print(f"Total time for embedding: {total_time} seconds.")

    print(f"Model name: {embedded_document.model_name}")

    print("\n --------- Embeded chanks ---------")
    for emb_chunk in embedded_document.embedded_chunks[0:1]:
        print(emb_chunk)
        print("---------------------")

    print(cost_tracker.get_summary())


if __name__ == "__main__":
    main()

