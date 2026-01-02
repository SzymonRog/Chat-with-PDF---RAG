from pathlib import Path

from src.pipline.rag_pipline import RAGPipline


rag_pipline = RAGPipline(
    pdf_path=Path("../../pdfs/test8.pdf")
)

if __name__ == "__main__":
    rag_pipline.process_pdf()