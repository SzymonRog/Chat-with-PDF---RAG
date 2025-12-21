from pathlib import Path

from src.extraction.image_extractor import ImageExtractor
from src.extraction.text_extractor import TextExtractor
from src.extraction.table_extractor import TableExtractor
import time
def main():
    pdf_path = Path("../../pdfs/test4.pdf")

    if not pdf_path.exists():
        print(f"PDF '{pdf_path}' nie istnieje. Wrzuc plik testowy do folderu pdfs/")
        return

    # Tworzymy extractor
    text_extractor = TextExtractor()
    img_extractor = ImageExtractor()
    table_extractor = TableExtractor()

    # Ekstrakcja tekstu
    time_start = time.time()
    extracted = text_extractor.extract(pdf_path)
    time_end = time.time()

    text_time = time_end - time_start

    # Ekstrakcja imges

    time_start = time.time()
    imgs = img_extractor.extract(pdf_path)
    time_end = time.time()

    img_time = time_end - time_start

    # Ekstrakcja tabel
    time_start = time.time()
    tables = table_extractor.extract(pdf_path)
    time_end = time.time()
    table_time = time_end - time_start

    total_time = text_time + img_time + table_time

    print(f"Extracted text took {text_time} seconds.")
    print(f"Images extracted took {img_time} seconds.")
    print(f"Table extracted took {table_time} seconds.")

    print(f"Total time: {total_time} seconds.")

    print("\n=== Liczba stron ===")
    print(len(extracted.page_text))
    # Sprawdzenie wyników
    print("=== Pełny tekst dokumentu (pierwsze 1000 znaków) ===")
    print(extracted.text[:1000])
    print("\n=== Tabele ===")
    for tabela in tables:
        print(tabela)





if __name__ == "__main__":
    main()