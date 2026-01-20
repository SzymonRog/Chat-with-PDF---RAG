import time
from typing import Literal, Dict
from pathlib import Path
from src.pipline.indexing_pipline import IndexingPipline
from src.pipline.query_pipline import QueryPipline


class RAGPipline:

    def __init__(self, pdf_path: Path, model_name:str = "sentence-transformers/all-mpnet-base-v2", provider:str = "local", strategy: Literal["fixed_size", "sentence"] ="sentence" ,llm_name: str = "llama3.2", chunk_size:int = 200, overlap: int = 20):
        self.llm_name = llm_name
        self.pdf_path = pdf_path
        self.document_id = None
        self.provider = provider
        self.model_name = model_name
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.overlap = overlap

        self.indexing_pipline = IndexingPipline(
            pdf_path=pdf_path,
            model_name=model_name,
            provider=provider,
            strategy=strategy,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        self.query_pipline = None



    def process_pdf(self) -> Dict:
            start_time = time.time()
            response = self.indexing_pipline.index_document(self.pdf_path)

            if not response["success"]:
                return {
                    "success": False,
                    "message": response["message"],
                    "time": time.time() - start_time,
                }

            return {
                "success": True,
                "document_id": response["document_id"],
                "time": time.time() - start_time,
            }



    def query(self, prompt):
        response = self.query_pipline.query(query=prompt, top_k=5)
        return response




