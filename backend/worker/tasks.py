"""Background tasks for document ingestion and indexing."""
import tempfile
from pathlib import Path

from backend.rag.application import create_rag_application
from backend.storage.document_storage import get_document_storage
from backend.worker.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="researchrag.index_document",
    max_retries=3,
    default_retry_delay=15,
)
def index_document(self, document_id: str, storage_key: str):
    """Download a stored PDF and index it with bounded automatic retries."""
    application = create_rag_application()
    temp_path = None

    try:
        document = application.get_document(document_id)
        if document is None:
            raise LookupError(f"Document {document_id} does not exist.")

        with tempfile.NamedTemporaryFile(
            prefix="researchrag-worker-",
            suffix=".pdf",
            delete=False,
        ) as tmp:
            temp_path = Path(tmp.name)

        get_document_storage().download_file(storage_key, temp_path)
        result = application.index_registered_pdf(
            document_id=document_id,
            file_path=str(temp_path),
        )
        return {
            "document_id": document_id,
            "status": "indexed",
            "chunks": result["chunks"],
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        application.document_service.mark_failed(document_id, str(exc))
        raise
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
