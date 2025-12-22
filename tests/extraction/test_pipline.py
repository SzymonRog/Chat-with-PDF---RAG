from src.extraction.pipeline.pdf_extractor import PDFExtractor
from src.models.document import ExtractedDocument


def test_pdf_extraction_pipeline_returns_document(sample_pdf_path):
    extractor = PDFExtractor(sample_pdf_path)
    result = extractor.extract()

    assert isinstance(result, ExtractedDocument)

def test_pdf_extraction_result_structure(sample_pdf_path):
    extractor = PDFExtractor(sample_pdf_path)
    doc = extractor.extract()

    assert doc.text is not None
    assert isinstance(doc.page_text, list)
    assert isinstance(doc.tables, list)
    assert isinstance(doc.images, list)
    assert doc.metadata is not None

def test_pdf_metadata_fields(sample_pdf_path):
    extractor = PDFExtractor(sample_pdf_path)
    doc = extractor.extract()
    meta = doc.metadata

    assert meta.filename == sample_pdf_path.name
    assert meta.filepath == sample_pdf_path
    assert meta.num_pages > 0
    assert meta.file_size_bytes > 0


def test_pdf_without_tables_or_images_does_not_crash(sample_pdf_path):
    extractor = PDFExtractor(sample_pdf_path)
    doc = extractor.extract()

    # nawet jeśli puste, to mają istnieć
    assert isinstance(doc.tables, list)
    assert isinstance(doc.images, list)


def test_pdf_extraction_is_repeatable(sample_pdf_path):
    extractor1 = PDFExtractor(sample_pdf_path)
    extractor2 = PDFExtractor(sample_pdf_path)

    doc1 = extractor1.extract()
    doc2 = extractor2.extract()

    assert doc1.text == doc2.text
    assert doc1.metadata.num_pages == doc2.metadata.num_pages




