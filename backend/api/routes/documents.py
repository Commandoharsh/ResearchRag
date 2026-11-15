from fastapi import APIRouter, HTTPException

from backend.rag.application import create_rag_application


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get("")
def list_documents():
    """Return all registered documents."""

    application = create_rag_application()

    documents = application.list_documents()

    return {
        "documents": [
            {
                "id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "status": document.status,
                "chunk_count": document.chunk_count,
                "created_at": document.created_at,
                "updated_at": document.updated_at,
                "error_message": document.error_message,
            }
            for document in documents
        ]
    }


@router.get("/{document_id}")
def get_document(document_id: str):
    """Return information about a specific document."""

    application = create_rag_application()

    document = application.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "chunk_count": document.chunk_count,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "error_message": document.error_message,
    }