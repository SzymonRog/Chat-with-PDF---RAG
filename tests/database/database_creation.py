from pathlib import Path

from src.cache.document_database import Cache

document_store = Cache(Path("../../data/tables/document_database.db"))
document_store.delete_document("670fbf63056fdf50e6931c463bca912a362ce9e055953948acf0f6ecd4c14a29")