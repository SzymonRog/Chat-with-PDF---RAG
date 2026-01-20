from pathlib import Path

from transformers import AutoTokenizer

from src.cache.document_database import Cache
from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.generation.generator import Generator
from src.retrieval import retriever
from src.retrieval.retriever import Retriever
from src.vectordb.pinecone_store import VectordbStore


class QueryPipline:
    def __init__(self, document_id: str,llm_name: str = "llama3.2", model_name: str = "sentence-transformers/all-mpnet-base-v2", provider: str = "local") -> None:
        self.pinecone_store = VectordbStore()
        self.llm_name = llm_name
        self.document_id = document_id

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
        )
        base_dir = Path(__file__).resolve().parent.parent.parent
        db_path = base_dir / "data/tables/document_database.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.embedder = EmbeddingPipeline(
            provider=provider,
            model_name=model_name,
            batch_size=3,
            tokenizer=self.tokenizer,
            document_db = Cache(db_path)
        )

        self.retriever = Retriever(vectordb=self.pinecone_store)
        self.generator = Generator(self.llm_name)

    def query(self, query: str, top_k: int) -> dict:
        try:
            embedded_query = self.embedder.embed_text(query)

            result = self.retriever.retrieve(
                vector=embedded_query,
                document_id=self.document_id,
                top_k=top_k,
            )

            response = self.generator.generate_response(
                retrival=result,
                prompt=query,
            )

            if response:
                return {
                    "success": True,
                    "status": "complete",
                    "response": response,
                }

            return {
                "success": False,
                "status": "complete",
                "message": "No response generated",
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": str(e),
            }





