
from src.chunking.fixed_size import FixedSizeChunker
from src.chunking.sentence import SentenceChunker
from pathlib import Path
from src.extraction.pipeline.pdf_extractor import PDFExtractor
import time
def main():
    pdf_path = Path("../../pdfs/test4.pdf")

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

    fixed_size = FixedSizeChunker(
        chunk_size=400,
        overlap=75,
    )
    start = time.time()
    fixed_chunks = fixed_size.chunk(data.text, 1)
    end = time.time()
    total_time = end - start
    print(f"Total time for fixed chunking: {total_time} seconds.")

    sentence_chunker = SentenceChunker(
        max_chunk_size=400,
        overlap=75,
    )
    start = time.time()
    sentence_chunks = sentence_chunker.chunk(data.text, "1")
    end = time.time()
    total_time = end - start
    print(f"Total time for sentence chunking: {total_time} seconds.")


    print(f"\n======Fixed Chunks======")
    for chunk in fixed_chunks[0:10]:
        print(chunk.text)


    print(f"\n======Sentence Chunks======")
    for chunk in sentence_chunks[0:10]:
        print(chunk.text)
        print(f"-----------------")









if __name__ == "__main__":
    main()

