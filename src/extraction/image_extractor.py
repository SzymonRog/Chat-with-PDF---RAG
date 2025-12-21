from pathlib import Path
from typing import List, Any
import pdfplumber
from PIL import Image
class ImageExtractor:

    def __init__(self):
        self.imgs: List[Any] = []

    def extract(self, pdf_path: Path) -> List[Any]:
        """Extract images from PDF."""
        with pdfplumber.open(pdf_path) as pdf:

            seen_streams = set()

            for page in pdf.pages:
                page_image = page.to_image()
                pil_page = page_image.original

                for img in page.images:
                    # Image id
                    stream_id = id(img['stream'])

                    if stream_id in seen_streams:
                        continue
                    seen_streams.add(stream_id)

                    x0, top, x1, bottom = img['x0'], img['top'], img['x1'], img['bottom']
                    pil_cropped = pil_page.crop((x0, top, x1, bottom))

                    # filtrujemy obraz
                    if not self.filter_image(pil_cropped):
                        continue

                    filename = f"page{page.page_number}_{img['name']}.png"
                    pil_cropped.save(f'../../data/images/{filename}')
                    self.imgs.append(filename)

        return self.imgs

    def filter_image(self, img: Image.Image) -> bool:
        """Return True if the image is worth keeping."""
        min_width = 20
        min_height = 20
        max_ratio = 10  # np. szerokość do wysokości

        w, h = img.size
        if w < min_width or h < min_height:
            return False
        if max(w/h, h/w) > max_ratio:
            return False
        return True





