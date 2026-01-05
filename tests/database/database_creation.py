from pathlib import Path

from src.cache.document_database import Cache

document_store = Cache(Path("../../data/tables/document_database.db"))
document_store.add_column(col_name="strategy", col_type="TEXT")