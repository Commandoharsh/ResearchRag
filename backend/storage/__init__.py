"""Document storage backends."""
from backend.storage.document_storage import (
    DocumentStorage,
    LocalDocumentStorage,
    R2DocumentStorage,
    get_document_storage,
)

__all__ = [
    "DocumentStorage",
    "LocalDocumentStorage",
    "R2DocumentStorage",
    "get_document_storage",
]
