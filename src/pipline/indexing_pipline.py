from pathlib import Path
from typing import Dict

from pdfplumber import PDF
from transformers import AutoTokenizer

from src.chunking.chunking_pipline import ChunkingPipeline
from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.extraction.metadata.pdf_metadata import PDFMetadata
from src.cache.cache import Cache

from src.extraction.pipeline.pdf_extractor import PDFExtractor
from src.extraction.pipeline.pdf_loader import PDFLoader
from src.models.chunk import ChunkedDocument
from src.models.document import ExtractedDocument
from src.models.embedding import EmbeddedDocument
from src.vectordb.pinecone_store import VectordbStore


class IndexingPipline:

    def __init__(self, pdf_path: Path, model_name: str, provider: str, strategy: str) -> None:

        self.model_name = model_name
        self.provider = provider
        self.strategy = strategy

        self.pdf_path = pdf_path

        self.pdf_metadata = PDFMetadata()
        self.cache = Cache(Path("../../data/tables/embedding_cache.db"))
        self.pdf_loader = PDFLoader(pdf_path)

        self.pdf_extractor = None
        self.chunker = None
        self.embedder = None

        self.pinecone_store = VectordbStore()
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
        )

    def index_document(self, pdf_path: Path) -> Dict:
        try:
            pdf = self.pdf_loader.open_pdf()
            exists = self.check_if_exists(pdf_path, pdf)

            if exists:
                print(f"Document already exists in DB\nDocument ID: {exists}")

                return {'success': True, 'message': 'Document already exists','document_id': exists}

            else:
                self.pdf_extractor = PDFExtractor(pdf_path)
                self.chunker = ChunkingPipeline(
                    strategy='sentence',
                    chunk_size=175,
                    overlap=20,
                    tokenizer=self.tokenizer,
                )
                self.embedder = EmbeddingPipeline(
                    provider=self.provider,
                    model_name=self.model_name,
                    batch_size=3,
                    tokenizer=self.tokenizer,
                )

                print("Extracting documents...")
                extracted_data: ExtractedDocument = self.pdf_extractor.extract()
                print("Documents extracted.")

                print("Chunking Document...")
                chunked_document: ChunkedDocument = self.chunker.chunk_document(extracted_data)
                print("Document Chunked")

                print("Embedding Document...")
                embedded_document: EmbeddedDocument = self.embedder.embed_document(chunked_document)
                print("Document Embedded")

                document_id = extracted_data.metadata.document_id

                self.pinecone_store.upsert_document(embedded_document)

                return {'success': True, 'message': 'Document successfully indexed', 'document_id': {document_id}}

        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            self.pdf_loader.close_pdf()

    def check_if_exists(self, pdf_path: Path, pdf: PDF) -> str | None:
        pdf_metadata = self.pdf_metadata.get_metadata(pdf=pdf,pdf_path=pdf_path)
        pdf_id = pdf_metadata.document_id
        exists = self.cache.check_if_document_exists(pdf_id)

        if exists:
            return pdf_id
        else:
            return None


