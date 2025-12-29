from pathlib import Path
from src.extraction.pipeline.pdf_extractor import PDFExtractor
import time
def main():
    pdf_path = Path("../../pdfs/test1.pdf")

    if not pdf_path.exists():
        print(f"PDF '{pdf_path}' nie istnieje. Wrzuc plik testowy do folderu pdfs/")
        return

    # Tworzymy extractor
    extractor = PDFExtractor(pdf_path)
    start = time.time()
    data = extractor.extract()
    end = time.time()

    total_time = end - start


    print(f"Total time: {total_time} seconds.")

    print("\n=== Liczba stron ===")
    print(len(data.page_text))
    # Sprawdzenie wyników
    print("=== Pełny tekst dokumentu (pierwsze 1000 znaków) ===")
    print(data.text[:1000])
    print("\n=== Tabele ===")
    for tabela in data.tables:
        print(tabela)
    print("\n=== Image ===")
    for image in data.images:
        print(image)
    print("\n=== PDF ===")
    print(data.metadata)





if __name__ == "__main__":
    main()