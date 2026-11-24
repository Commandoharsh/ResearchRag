import os
from pathlib import Path
from typing import List
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import Distance, PointStruct, VectorParams

from backend.rag.chunking.chunk import Chunk


def create_qdrant_client(
    storage_path: str = "data/qdrant",
    *,
    url: str | None = None,
    api_key: str | None = None,
    timeout: float = 30.0,
):
    """Create a local embedded or remote managed Qdrant client.

    Explicit arguments take precedence; otherwise QDRANT_URL and
    QDRANT_API_KEY are read from the environment. When no remote URL is
    configured, the existing local persistent mode is preserved.
    """
    remote_url = (url or os.getenv("QDRANT_URL", "")).strip()
    remote_api_key = api_key or os.getenv("QDRANT_API_KEY") or None

    if remote_url:
        return QdrantClient(
            url=remote_url,
            api_key=remote_api_key,
            timeout=timeout,
        )

    Path(storage_path).mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=storage_path)


class VectorStore:
    def __init__(
        self,
        collection_name: str = "research_documents",
        vector_size: int = 384,
        storage_path: str = "data/qdrant",
        qdrant_url: str | None = None,
        qdrant_api_key: str | None = None,
        timeout: float = 30.0,
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.storage_path = storage_path
        self.remote = bool(
            (qdrant_url or os.getenv("QDRANT_URL", "")).strip()
        )
        self.client = create_qdrant_client(
            storage_path,
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=timeout,
        )
        self._create_collection(vector_size)

    def _create_collection(self, vector_size: int):
        collections = self.client.get_collections()
        existing_collections = [
            collection.name for collection in collections.collections
        ]
        if self.collection_name not in existing_collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def _point_id(self, chunk: Chunk) -> str:
        return str(uuid5(NAMESPACE_URL, chunk.chunk_id))

    @staticmethod
    def _convert_vector(embedding):
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return list(embedding)

    def add_chunks(self, chunks: List[Chunk], embeddings):
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings."
            )

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                PointStruct(
                    id=self._point_id(chunk),
                    vector=self._convert_vector(embedding),
                    payload={
                        "content": chunk.content,
                        "metadata": chunk.metadata,
                    },
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search(self, query_embedding, limit: int = 5):
        if limit <= 0:
            return []
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=self._convert_vector(query_embedding),
            limit=limit,
        )
        return results.points

    def get_all_chunks(self):
        records, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=False,
        )
        chunks = []
        for record in records:
            payload = record.payload or {}
            chunks.append(
                Chunk(
                    content=payload.get("content", ""),
                    metadata=payload.get("metadata", {}),
                )
            )
        return chunks

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def delete_by_metadata(self, key: str, value: str):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchValue(value=value),
                    )
                ]
            ),
        )
