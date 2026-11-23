# ResearchRAG API image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Build tools are not needed for the pinned wheels; install only runtime OS packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install "uvicorn[standard]"

COPY backend ./backend
COPY scripts ./scripts
COPY tests ./tests
COPY data ./data

RUN mkdir -p /app/data/raw /app/data/qdrant /app/data/evaluation /app/.cache/huggingface

EXPOSE 8000

# One worker is intentional: embedded Qdrant uses a local filesystem lock.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
