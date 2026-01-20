from flask import Flask, request, jsonify
from pathlib import Path
import uuid
import time

from src.cache.document_database import Cache
from src.pipline.query_pipline import QueryPipline
from src.pipline.rag_pipline import RAGPipline
from src.app.middleware.validate_pdf_bytes import validate_pdf_bytes

app = Flask(__name__)

UPLOAD_DIR = Path("data/pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    return jsonify({
        "success": True,
    })
@app.route("/api/upload", methods=["POST"])
def upload():
    start_time = time.time()

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400


    data = file.read()


    try:
        validate_pdf_bytes(data)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    filename = f"{uuid.uuid4()}.pdf"
    path = UPLOAD_DIR / filename

    try:
        path.write_bytes(data)

        rag = RAGPipline(pdf_path=path)
        result = rag.process_pdf()

        if not result["success"]:
            return jsonify(result), 500

        return jsonify({
            "success": True,
            "document_id": result["document_id"],
            "processing_time": time.time() - start_time
        })

    finally:

        if path.exists():
            path.unlink()

@app.route('/api/messages/<document_id>', methods=["POST"])
def messages(document_id):
    start_time = time.time()
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        llm_name = data.get("llm_name")


        query_pipline = QueryPipline(document_id=document_id, llm_name=llm_name)
        response = query_pipline.query(query=prompt, top_k=5)

        if response["success"]:
            return jsonify({
                "success": True,
                "response": response["response"],
                "processing_time": time.time() - start_time
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": response["message"],
                "processing_time": time.time() - start_time
            }), 500

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/delete_file/<document_id>", methods=["DELETE"])
def delete_file(document_id):
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        db_path = base_dir / "data/tables/document_database.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        document_db = Cache(db_path)

        response = document_db.delete_document(document_id)
        return jsonify({
            "success": response["success"],
            "message": response["message"],
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400





def delete_files():
    for file in UPLOAD_DIR.iterdir():
        file.unlink()


if __name__ == "__main__":
    app.run(debug=True)

