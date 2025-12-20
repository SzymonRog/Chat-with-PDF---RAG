from pathlib import Path
from src.extraction.text_extractor import TextExtractor
import time
def main():
    pdf_path = Path("../../pdfs/test3.pdf")

    if not pdf_path.exists():
        print(f"PDF '{pdf_path}' nie istnieje. Wrzuc plik testowy do folderu pdfs/")
        return

    # Tworzymy extractor
    extractor = TextExtractor()

    # Ekstrakcja tekstu
    time_start = time.time()
    extracted = extractor.extract(pdf_path)
    time_end = time.time()

    print(f"Extracted text took {time_end - time_start} seconds.")

    print("\n=== Liczba stron ===")
    print(len(extracted.page_text))
    # Sprawdzenie wyników
    print("=== Pełny tekst dokumentu (pierwsze 1000 znaków) ===")
    print(extracted.text[:1000])

    print("\n=== Tekst pierwszej strony ===")
    print(extracted.page_text[0])




if __name__ == "__main__":
    main()