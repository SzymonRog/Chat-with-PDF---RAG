
from src.chunking.chunking_pipline import ChunkingPipeline
from pathlib import Path
from src.extraction.pipeline.pdf_extractor import PDFExtractor
import time
from transformers import AutoTokenizer

def main():
    tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2",
            local_files_only=True,
    )
    pdf_path = Path("../../pdfs/test.pdf")

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
        chunk_size=200,
        overlap=15,
        tokenizer = tokenizer
    )
    start = time.time()
    chunked_document = chunker.chunk_document(data)
    end = time.time()
    total_time = end - start
    print(f"Total time for chunking pipline: {total_time} seconds.")


    print(f"ID of doc: {chunked_document.document_id}")
    print(f"\n====== Chunks======")
    for chunk in chunked_document.chunks:
        print(chunk.text)
        print(f"-----------------")



if __name__ == "__main__":
    main()

