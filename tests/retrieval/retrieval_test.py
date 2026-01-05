from transformers import AutoTokenizer
from src.chunking.chunking_pipline import ChunkingPipeline
from pathlib import Path
from src.extraction.pipeline.pdf_extractor import PDFExtractor
from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.retrieval.retriever import Retriever
from src.vectordb.pinecone_store import VectordbStore
from src.cache.document_database import Cache

import time
def main():


    embedding_cache = Cache(Path("../../data/tables/document_database.db"))
    tokenizer = AutoTokenizer.from_pretrained(
        "sentence-transformers/all-mpnet-base-v2",
    )
    pdf_path = Path("../../pdfs/test8.pdf")

    if not pdf_path.exists():
        print(f"PDF '{pdf_path}' nie istnieje. Wrzuc plik testowy do folderu pdfs/")
        return



    # Tworzymy extractor
    extractor = PDFExtractor(pdf_path)
    start = time.time()
    data = extractor.extract()
    end = time.time()
    total_time = end - start

    document_id = data.metadata.document_id
    print(f"Document ID: {document_id}")

    print(f"Total time for extraction: {total_time} seconds.")

    chunker = ChunkingPipeline(
        strategy="sentence",
        chunk_size=175,
        overlap=15,
        tokenizer=tokenizer,
    )

    embedding_cache.delete_document_embedding(document_id)

    start = time.time()
    chunked_document = chunker.chunk_document(data)
    end = time.time()
    total_time = end - start

    print(f"Total time for chunking pipline: {total_time} seconds.")

    embedder = EmbeddingPipeline(
        provider="local",
        model_name="sentence-transformers/all-mpnet-base-v2",
        batch_size=3,
        tokenizer=tokenizer,
    )
    start = time.time()
    embedded_document = embedder.embed_document(chunked_document)
    end = time.time()

    total_time = end - start


    print("\n --------- Embedding ---------")
    print(f"Total time for embedding: {total_time} seconds.")
    print(f"Model name: {embedded_document.model_name}")


    pinecone_store = VectordbStore()
    # pinecone_store.delete_index()
    # pinecone_store.create_index(dimensions=768)
    # pinecone_store.delete_document(document_id)

    start = time.time()
    pinecone_store.upsert_document(embedded_document)
    end = time.time()
    total_time = end - start

    print("\n --------- VectorDb ---------")
    print(f"Total time for upserting: {total_time} seconds.")
    while True:

        str_query = input("Enter query: ")
        vector = embedder.embed_text(str_query)


        print(vector)

        retriever = Retriever(vectordb=pinecone_store)
        start = time.time()

        result = retriever.retrieve(
            vector=vector,
            document_id=document_id,
            top_k=3
        )
        end = time.time()
        total_time = end - start

        print(f"Total time for retrieval: {total_time} seconds.")
        print("---------  Retrival -----------------")
        for match in result:
            print(match['metadata']['text'])
            print(match['score'])
            print("-------------------------")


        want_to_guit = input("press q to exit: ") == "q"
        if want_to_guit:
            break


if __name__ == "__main__":
    main()

