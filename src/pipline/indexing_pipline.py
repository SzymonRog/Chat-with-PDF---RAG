from pathlib import Path
from typing import Dict, Literal

from pdfplumber import PDF
from transformers import AutoTokenizer

from src.chunking.chunking_pipline import ChunkingPipeline
from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.extraction.metadata.pdf_metadata import PDFMetadata
from src.cache.document_database import Cache

from src.extraction.pipeline.pdf_extractor import PDFExtractor
from src.extraction.pipeline.pdf_loader import PDFLoader
from src.models.chunk import ChunkedDocument
from src.models.document import ExtractedDocument
from src.models.embedding import EmbeddedDocument
from src.vectordb.pinecone_store import VectordbStore


class IndexingPipline:

    def __init__(self, pdf_path: Path, model_name: str, provider: str, strategy:  Literal["fixed_size", "sentence"] = "sentence", chunk_size: int = 200, overlap: int = 20) -> None:

        self.model_name = model_name
        self.provider = provider
        self.strategy = strategy

        self.chunk_size = chunk_size
        self.overlap = overlap

        self.pdf_path = pdf_path

        self.pdf_metadata = PDFMetadata()
        self.document_db = Cache(Path("../../data/tables/document_database.db"))
        self.pdf_loader = PDFLoader(pdf_path)

        self.pdf_extractor = None
        self.chunker = None
        self.embedder = None

        self.pinecone_store = VectordbStore()
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
        )
        self.document_id = None

        self.batch_size = 512 // chunk_size

    def index_document(self, pdf_path: Path) -> Dict:
        try:
            pdf = self.pdf_loader.open_pdf()
            doc_id = self.check_if_exists(pdf_path, pdf)
            has_changed = self.check_if_changed(doc_id)

            if doc_id and not has_changed:
                print(f"Document already exists in DB\nDocument ID: {doc_id}")
                return {'success': True, 'message': 'Document already exists and is embedded','document_id': doc_id, 'has_changed': False}
            else:
                self.pdf_extractor = PDFExtractor(pdf_path)
                self.chunker = ChunkingPipeline(
                    strategy='sentence',
                    chunk_size=self.chunk_size,
                    overlap=self.overlap,
                    tokenizer=self.tokenizer,
                )
                self.embedder = EmbeddingPipeline(
                    provider=self.provider,
                    model_name=self.model_name,
                    batch_size=self.batch_size,
                    tokenizer=self.tokenizer,
                )

                print("Extracting documents...")
                extracted_data: ExtractedDocument = self.pdf_extractor.extract()
                print("Documents extracted.")


                print("Chunking Document...")
                chunked_document: ChunkedDocument = self.chunker.chunk_document(extracted_data)
                print("Document Chunked")


                self.document_id = extracted_data.metadata.document_id
                print(self.document_id)

                if has_changed is None:
                    self.document_db.add_document(
                        document_id=self.document_id,
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.overlap,
                        embedding_model=self.model_name,
                        strategy=self.strategy,
                    )
                elif has_changed:
                    self.document_db.update_document(
                        document_id=self.document_id,
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.overlap,
                        embedding_model=self.model_name,
                        strategy=self.strategy,
                    )



                print("Embedding Document...")
                embedded_document: EmbeddedDocument = self.embedder.embed_document(chunked_document)
                print("Document Embedded")

                self.document_db.mark_as_embedded(self.document_id)

                self.pinecone_store.delete_document(self.document_id)
                self.pinecone_store.upsert_document(embedded_document)

                return {'success': True, 'message': 'Document successfully indexed', 'document_id': self.document_id, 'has_changed': True}

        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            self.pdf_loader.close_pdf()

    def check_if_exists(self, pdf_path: Path, pdf: PDF) -> str | None:
        pdf_metadata = self.pdf_metadata.get_metadata(pdf=pdf,pdf_path=pdf_path)
        pdf_id = pdf_metadata.document_id
        exists = self.document_db.document_exists(pdf_id)

        if exists:
            return pdf_id
        else:
            return None

    def check_if_changed(self, document_id: str) -> bool:
        return self.document_db.params_changed(document_id, self.chunk_size, self.overlap, self.model_name, self.strategy)


