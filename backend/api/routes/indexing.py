from pathlib import Path
import tempfile
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.rag.application import create_rag_application
from backend.storage.document_storage import get_document_storage
from backend.worker.tasks import index_document


router = APIRouter(prefix="/index", tags=["Indexing"])
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB


@router.post("/pdf", status_code=status.HTTP_202_ACCEPTED)
async def index_pdf(file: UploadFile = File(...)):
    """Store a PDF and enqueue indexing without blocking the request."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    safe_filename = Path(file.filename).name
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    total_size = 0
    storage_key = f"documents/{uuid4().hex}.pdf"
    temp_path: Path | None = None
    stored = False
    document_id: str | None = None
    application = create_rag_application()
    storage = get_document_storage()

    try:
        with tempfile.NamedTemporaryFile(
            prefix="researchrag-upload-",
            suffix=".pdf",
            delete=False,
        ) as tmp:
            temp_path = Path(tmp.name)
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the 25 MB upload limit.",
                    )
                tmp.write(chunk)

        if total_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")

        with temp_path.open("rb") as uploaded_file:
            storage.upload_fileobj(uploaded_file, storage_key)
        stored = True

        document = application.document_service.register(
            filename=safe_filename,
            file_path=storage_key,
            file_size=total_size,
            file_type="pdf",
        )
        document_id = document.id

        task = index_document.delay(document_id, storage_key)
        return {
            "status": "queued",
            "document_id": document_id,
            "task_id": task.id,
            "filename": safe_filename,
        }

    except HTTPException:
        raise
    except Exception as exc:
        if document_id is not None:
            application.delete_document_record(document_id)
        if stored:
            try:
                storage.delete_file(storage_key)
            except Exception:
                pass
        raise HTTPException(status_code=503, detail=f"Could not queue document indexing: {exc}") from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        await file.close()
