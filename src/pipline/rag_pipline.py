from pathlib import Path
from src.pipline.indexing_pipline import IndexingPipline
from src.pipline.query_pipline import QueryPipline


class RAGPipline:

    def __init__(self, pdf_path: Path, model_name:str = "sentence-transformers/all-mpnet-base-v2", provider:str = "local", strategy: str ="sentence" ,llm_name: str = "llama3.2"):
        self.llm_name = llm_name
        self.pdf_path = pdf_path
        self.document_id = None
        self.provider = provider
        self.model_name = model_name

        self.indexing_pipline = IndexingPipline(
            pdf_path=pdf_path,
            model_name=model_name,
            provider=provider,
            strategy=strategy,
        )
        self.query_pipline = None



    def process_pdf(self):
        response = self.indexing_pipline.index_document(self.pdf_path)
        print(response)

        if response['success']:
            self.document_id = response['document_id']
            self.query_pipline = QueryPipline(
                llm_name=self.llm_name,
                model_name=self.model_name,
                provider=self.provider,
                document_id=self.document_id,
            )

            print("PDF processed successfully")
            print("Now you can chat with your PDF")
            self.chat()


    def chat(self):
        while True:
            prompt = input("Enter the query: ")
            self.query_pipline.query(query=prompt, top_k=3)

            want_to_quit = input("Would you like to quit? (y/n): ")
            if want_to_quit.lower() == "y":
                break
