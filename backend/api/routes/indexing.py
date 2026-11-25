from pathlib import Path
import tempfile
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.rag.application import create_rag_application
from backend.storage.document_storage import get_document_storage


router = APIRouter(prefix="/index", tags=["Indexing"])

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB


@router.post("/pdf")
async def index_pdf(file: UploadFile = File(...)):
    """Persist an uploaded PDF, then index it from a temporary local copy."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    safe_filename = Path(file.filename).name
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    total_size = 0
    storage_key = f"documents/{uuid4().hex}.pdf"
    temp_path: Path | None = None
    storage = get_document_storage()

    try:
        with tempfile.NamedTemporaryFile(prefix="researchrag-", suffix=".pdf", delete=False) as tmp:
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

        application = create_rag_application()
        result = application.index_pdf(
            str(temp_path),
            stored_file_path=storage_key,
        )
        return {"status": "success", "result": result}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        await file.close()
