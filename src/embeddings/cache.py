import sqlite3
from pathlib import Path

import numpy as np


class Cache:

    def __init__(self, db_path: Path):
        self.db_path = db_path


    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding BLOB NOT NULL
            )
            """)

        cursor.execute("""
                       CREATE INDEX IF NOT EXISTS idx_document_id
                           ON embeddings(document_id)
                       """)

        conn.commit()
        conn.close()
        print("Database created!")

    def save_embedding(self, chunk_id: str, document_id: str, chunk_index: int, embedding: np.ndarray):
        """Save embedding to cache"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO embeddings (chunk_id, document_id, chunk_index, embedding)
            VALUES (?, ?, ?, ?)
            """, (chunk_id, document_id, chunk_index, embedding.tobytes()))

            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()

    def embedding_exists(self, chunk_id: str, document_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT 1 FROM embeddings WHERE chunk_id = ? AND document_id = ?""", (chunk_id, document_id))

            exists = cursor.fetchone() is not None
            conn.close()

            return exists
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_embedding(self, chunk_id: str, document_id: str) -> np.ndarray | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT embedding FROM embeddings WHERE chunk_id = ? AND document_id = ?
            """, (chunk_id, document_id))

            result = cursor.fetchone()

            if result:
                return np.frombuffer(result[0], dtype=np.float32)
            else:
                return None

        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_document_embeddings(self, document_id: str) -> np.ndarray | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """SELECT chunk_id, document_id, chunk_index, embedding FROM embeddings WHERE document_id = ? ORDER BY CHUNK_INDEX ASC """, (document_id,))

            response = cursor.fetchall()
            results = []
            if response:
                for row in response:
                    results.append(
                        {
                            'chunk_id': row[0],
                            'document_id': row[1],
                            'chunk_index': row[2],
                            'embedding': np.frombuffer(row[3], dtype=np.float32),
                        }
                    )
                return results
            else:
                return None
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def delete_document_embedding(self, document_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            DELETE FROM embeddings WHERE document_id = ?""", (document_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
