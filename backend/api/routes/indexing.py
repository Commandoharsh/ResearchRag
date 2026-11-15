from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from backend.rag.application import create_rag_application


router = APIRouter(
    prefix="/index",
    tags=["Indexing"],
)

DATA_DIR = Path("data/raw")
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post("/pdf")
async def index_pdf(file: UploadFile = File(...)):
    """Upload and index a PDF document."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    safe_filename = Path(file.filename).name

    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    destination = DATA_DIR / safe_filename
    total_size = 0

    try:
        with destination.open("wb") as buffer:
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

                buffer.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty.",
            )

        application = create_rag_application()

        result = application.index_pdf(
            str(destination)
        )

        return {
            "status": "success",
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        await file.close()