from pathlib import Path

from src.pipline.rag_pipline import RAGPipline


rag_pipline = RAGPipline(
    pdf_path=Path("../../pdfs/test1.pdf"),
    model_name="sentence-transformers/all-mpnet-base-v2",
    provider="local",
    strategy="sentence",
    llm_name="llama3.2",
    chunk_size=200,
    overlap=20,
)

if __name__ == "__main__":
    rag_pipline.process_pdf()