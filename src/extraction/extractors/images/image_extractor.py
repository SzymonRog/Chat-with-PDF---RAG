from typing import List, Set
from PIL import Image
from pdfplumber.page import Page
from pathlib import Path

class ImageExtractor:

    def __init__(self):
        self.imgs: List[str] = []
        self.seen_streams: Set[int] = set()


        self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.images_dir = self.project_root / "data/images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def on_page(self, page: Page) -> None:
        """Process a single PDF page and extract images."""
        pil_page = page.to_image().original

        for img in page.images:
            stream_id = id(img['stream'])
            if stream_id in self.seen_streams:
                continue
            self.seen_streams.add(stream_id)

            x0, top, x1, bottom = img['x0'], img['top'], img['x1'], img['bottom']
            pil_cropped = pil_page.crop((x0, top, x1, bottom))

            if not self.filter_image(pil_cropped):
                continue

            filename = f"page{page.page_number}_{img['name']}.png"
            save_path = self.images_dir / filename
            pil_cropped.save(save_path)  # zapisujemy w absolutnej ścieżce
            self.imgs.append(filename)

    def build_result(self) -> List[str]:
        """Return list of extracted image filenames."""
        return self.imgs

    def filter_image(self, img: Image.Image) -> bool:
        """Return True if the image is worth keeping."""
        min_width = 20
        min_height = 20
        max_ratio = 10

        w, h = img.size
        if w < min_width or h < min_height:
            return False
        if max(w / h, h / w) > max_ratio:
            return False
        return True
