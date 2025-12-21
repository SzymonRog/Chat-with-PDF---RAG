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
                    filename = f"page{page.page_number}_{img['name']}.png"
                    # identyfikator obrazu
                    stream_id = id(img['stream'])
                    if stream_id in seen_streams:
                        continue  # już był
                    seen_streams.add(stream_id)

                    x0, top, x1, bottom = img['x0'], img['top'], img['x1'], img['bottom']
                    pil_cropped = pil_page.crop((x0, top, x1, bottom))
                    pil_cropped.save(f'../../data/images/{filename}.png')


        return self.imgs




