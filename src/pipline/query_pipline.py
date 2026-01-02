from pathlib import Path

from transformers import AutoTokenizer

from src.embeddings.embedding_pipline import EmbeddingPipeline
from src.generation.generator import Generator
from src.retrieval import retriever
from src.retrieval.retriever import Retriever
from src.vectordb.pinecone_store import VectordbStore


class QueryPipline:
    def __init__(self,llm_name: str, model_name: str, provider: str, document_id: str) -> None:
        self.pinecone_store = VectordbStore()
        self.llm_name = llm_name
        self.document_id = document_id

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
        )

        self.embedder = EmbeddingPipeline(
            provider=provider,
            model_name=model_name,
            batch_size=3,
            tokenizer=self.tokenizer,
        )

        self.retriever = Retriever(vectordb=self.pinecone_store)
        self.generator = Generator(self.llm_name)





    def query(self, query: str, top_k: int) ->dict:
        embedded_query = self.embedder.embed_text(query)

        result = self.retriever.retrieve(
            vector=embedded_query,
            document_id=self.document_id,
            top_k=top_k,
        )
        self.generator.generate_response(retrival=result, prompt=query)
        return {'status': 'SUCCESS'}

