"""Migrate an existing embedded Qdrant database into a Qdrant server.

Stop the API and Celery worker before running this script so the embedded
source database is not locked by another process.
"""
from __future__ import annotations

import argparse
import os

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


def migrate(source_path: str, target_url: str, api_key: str | None = None) -> int:
    source = QdrantClient(path=source_path)
    target = QdrantClient(url=target_url, api_key=api_key or None)

    migrated_total = 0
    try:
        collections = source.get_collections().collections
        if not collections:
            print("Source Qdrant contains no collections; nothing to migrate.")
            return 0

        target_names = {
            collection.name
            for collection in target.get_collections().collections
        }

        for collection in collections:
            name = collection.name
            source_info = source.get_collection(name)

            if name not in target_names:
                target.create_collection(
                    collection_name=name,
                    vectors_config=source_info.config.params.vectors,
                )
                print(f"Created target collection: {name}")

            offset = None
            collection_total = 0
            while True:
                points, next_offset = source.scroll(
                    collection_name=name,
                    limit=256,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True,
                )
                if points:
                    target.upsert(
                        collection_name=name,
                        points=[
                            PointStruct(
                                id=point.id,
                                vector=point.vector,
                                payload=point.payload,
                            )
                            for point in points
                        ],
                        wait=True,
                    )
                    collection_total += len(points)

                if next_offset is None:
                    break
                offset = next_offset

            migrated_total += collection_total
            print(f"Migrated {collection_total} points from {name}")

        return migrated_total
    finally:
        source.close()
        target.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-path", default="data/qdrant")
    parser.add_argument(
        "--target-url",
        default=os.getenv("QDRANT_MIGRATION_TARGET_URL", "http://qdrant:6333"),
    )
    parser.add_argument("--api-key", default=os.getenv("QDRANT_API_KEY"))
    args = parser.parse_args()

    total = migrate(args.source_path, args.target_url, args.api_key)
    print(f"Migration finished. Total points copied: {total}")


if __name__ == "__main__":
    main()
