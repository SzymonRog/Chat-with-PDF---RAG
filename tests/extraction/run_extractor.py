from pathlib import Path

from src.extraction.image_extractor import ImageExtractor
from src.extraction.text_extractor import TextExtractor
import time
def main():
    pdf_path = Path("../../pdfs/test2.pdf")

    if not pdf_path.exists():
        print(f"PDF '{pdf_path}' nie istnieje. Wrzuc plik testowy do folderu pdfs/")
        return

    # Tworzymy extractor
    text_extractor = TextExtractor()
    img_extractor = ImageExtractor()

    # Ekstrakcja tekstu
    time_start = time.time()
    extracted = text_extractor.extract(pdf_path)
    time_end = time.time()

    text_time = time_end - time_start

    time_start = time.time()
    imgs = img_extractor.extract(pdf_path)
    time_end = time.time()

    img_time = time_end - time_start

    print(f"Extracted text took {text_time} seconds.")
    print(f"Images extracted took {img_time} seconds.")

    print("\n=== Liczba stron ===")
    print(len(extracted.page_text))
    # Sprawdzenie wyników
    print("=== Pełny tekst dokumentu (pierwsze 1000 znaków) ===")
    print(extracted.text[:1000])






if __name__ == "__main__":
    main()