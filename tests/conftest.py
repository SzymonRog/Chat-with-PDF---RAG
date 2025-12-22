import pytest
from pathlib import Path

@pytest.fixture
def sample_pdf_path() -> Path:
    return Path("pdfs/test2.pdf")