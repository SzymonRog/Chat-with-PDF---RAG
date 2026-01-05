import sqlite3
from pathlib import Path
from typing import Literal




class Cache:
    """Provides SQLite-based caching for document metadata and embedding status."""

    def __init__(self, db_path: Path):
        """
        Initializes the cache with the given database path.

        Args:
            db_path (Path): Path to the SQLite database file.
        """
        self.db_path = db_path

    def create_database(self):
        """
        Creates the documents table if it does not exist.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS documents
                           (
                               document_id TEXT PRIMARY KEY NOT NULL,
                               is_embedded BOOLEAN NOT NULL DEFAULT FALSE,
                               chunk_size INTEGER NOT NULL,
                               chunk_overlap INTEGER NOT NULL,
                               embedding_model TEXT NOT NULL,
                               strategy TEXT
                           )
                           """)

            conn.commit()
            print("Database created!")
        except sqlite3.OperationalError:
            print("Database already exists!")
        finally:
            conn.close()


    def add_document(self, document_id: str, chunk_size: int, chunk_overlap: int,
                     embedding_model: str,strategy: Literal["fixed_size", "sentence"], is_embedded: bool = False, ):
        """
        Adds a new document to the cache.

        Args:
            document_id (str): Unique identifier of the document
            chunk_size (int): Size of chunks used
            chunk_overlap (int): Overlap between chunks
            embedding_model (str): Name of the embedding model used
            is_embedded (bool): Whether the document has been embedded
            strategy (Literal["fixed_size", "sentence"]): What strategy to use
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           INSERT INTO documents (document_id, is_embedded, chunk_size, chunk_overlap, embedding_model, strategy)
                           VALUES (?, ?, ?, ?, ?, ?)
                           """, (document_id, is_embedded, chunk_size, chunk_overlap, embedding_model, strategy))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Document {document_id} already exists in cache")
        finally:
            conn.close()

    def document_exists(self, document_id: str) -> bool:
        """
        Checks whether a document exists in the cache.

        Args:
            document_id (str): Document identifier

        Returns:
            bool: True if the document exists, otherwise False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT 1
                           FROM documents
                           WHERE document_id = ?
                           """, (document_id,))
            exists = cursor.fetchone() is not None
            return exists
        finally:
            conn.close()

    def is_document_embedded(self, document_id: str) -> bool:
        """
        Checks whether a document has been embedded.

        Args:
            document_id (str): Document identifier

        Returns:
            bool: True if the document is embedded, False otherwise or if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT is_embedded
                           FROM documents
                           WHERE document_id = ?
                           """, (document_id,))
            result = cursor.fetchone()
            return result[0] if result else False
        finally:
            conn.close()

    def get_document_params(self, document_id: str) -> dict | None:
        """
        Retrieves all parameters for a document.

        Args:
            document_id (str): Document identifier

        Returns:
            dict | None: Dictionary with document parameters or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT chunk_size, chunk_overlap, embedding_model, is_embedded, strategy
                           FROM documents
                           WHERE document_id = ?
                           """, (document_id,))
            result = cursor.fetchone()

            if result:
                return {
                    'chunk_size': result[0],
                    'chunk_overlap': result[1],
                    'embedding_model': result[2],
                    'is_embedded': result[3],
                    'strategy': result[4]
                }
            return None
        finally:
            conn.close()

    def params_changed(self, document_id: str, chunk_size: int,
                       chunk_overlap: int, embedding_model: str, strategy: str) -> bool | None:
        """
        Checks if any parameters have changed compared to cached values.

        Args:
            document_id (str): Document identifier
            chunk_size (int): New chunk size
            chunk_overlap (int): New chunk overlap
            embedding_model (str): New embedding model
            strategy (str): New chunking strategy

        Returns:
            bool: True if any parameter changed or document doesn't exist, False otherwise
        """
        params = self.get_document_params(document_id)

        if params is None:
            return None  # Document doesn't exist, consider it as "changed"

        return (params['chunk_size'] != chunk_size or
                params['chunk_overlap'] != chunk_overlap or
                params['embedding_model'] != embedding_model or
                params['strategy'] != strategy)

    def update_document(self, document_id: str, chunk_size: int = None,
                        chunk_overlap: int = None, embedding_model: str = None,
                        is_embedded: bool = None, strategy: Literal["fixed_size", "sentence"] = None) -> bool:
        """
        Updates document parameters. Only updates provided parameters.

        Args:
            document_id (str): Document identifier
            chunk_size (int, optional): New chunk size
            chunk_overlap (int, optional): New chunk overlap
            embedding_model (str, optional): New embedding model
            is_embedded (bool, optional): New embedding status
            strategy (str, optional): New chunking strategy
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if chunk_size is not None:
            updates.append("chunk_size = ?")
            values.append(chunk_size)
        if chunk_overlap is not None:
            updates.append("chunk_overlap = ?")
            values.append(chunk_overlap)
        if embedding_model is not None:
            updates.append("embedding_model = ?")
            values.append(embedding_model)
        if is_embedded is not None:
            updates.append("is_embedded = ?")
            values.append(is_embedded)
        if strategy is not None:
            updates.append("strategy = ?")
            values.append(strategy)

        if not updates:
            conn.close()
            return False

        values.append(document_id)
        query = f"UPDATE documents SET {', '.join(updates)} WHERE document_id = ?"

        try:
            cursor.execute(query, values)
            conn.commit()
            return True
        finally:
            conn.close()

    def mark_as_embedded(self, document_id: str):
        """
        Marks a document as embedded.

        Args:
            document_id (str): Document identifier
        """
        self.update_document(document_id, is_embedded=True)

    def delete_document(self, document_id: str):
        """
        Deletes a document from the cache.

        Args:
            document_id (str): Document identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           DELETE
                           FROM documents
                           WHERE document_id = ?
                           """, (document_id,))
            conn.commit()
            print(f"Document {document_id} deleted from cache")
        finally:
            conn.close()

    def get_all_documents(self) -> list[dict]:
        """
        Retrieves all documents from the cache.

        Returns:
            list[dict]: List of all documents with their parameters
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT document_id, is_embedded, chunk_size, chunk_overlap, embedding_model
                           FROM documents
                           """)
            results = cursor.fetchall()

            return [
                {
                    'document_id': row[0],
                    'is_embedded': row[1],
                    'chunk_size': row[2],
                    'chunk_overlap': row[3],
                    'embedding_model': row[4]
                }
                for row in results
            ]
        finally:
            conn.close()

    def add_column(self, col_name, col_type):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        allowed_types = {"TEXT", "INTEGER", "REAL", "BOOLEAN", "TIMESTAMP"}

        if col_type.upper() not in allowed_types:
            raise ValueError("Invalid column type")

        try:
            sql = f"""
            ALTER TABLE documents
            ADD COLUMN {col_name} {col_type}
            """
            cursor.execute(sql)
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"Could not add column: {e}")
        finally:
            conn.close()
