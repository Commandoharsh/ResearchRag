"""Storage abstraction for local development and Cloudflare R2.

The database stores opaque object keys, never container-local absolute paths.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Protocol


class DocumentStorage(Protocol):
    def upload_fileobj(self, fileobj: BinaryIO, key: str) -> str: ...
    def download_file(self, key: str, destination: str | Path) -> Path: ...
    def delete_file(self, key: str) -> None: ...


def _safe_key(key: str) -> str:
    path = PurePosixPath(key)
    if path.is_absolute() or not path.parts or any(p in ("", ".", "..") for p in path.parts):
        raise ValueError("Invalid storage object key.")
    return str(path)


class LocalDocumentStorage:
    def __init__(self, root: str | Path = "data/objects"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = _safe_key(key)
        target = (self.root / Path(*PurePosixPath(safe).parts)).resolve()
        if self.root not in target.parents:
            raise ValueError("Storage key escapes the configured root.")
        return target

    def upload_fileobj(self, fileobj: BinaryIO, key: str) -> str:
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        fileobj.seek(0)
        with target.open("wb") as destination:
            shutil.copyfileobj(fileobj, destination)
        return _safe_key(key)

    def download_file(self, key: str, destination: str | Path) -> Path:
        source = self._path(key)
        if not source.is_file():
            raise FileNotFoundError(f"Stored document not found: {key}")
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return target

    def delete_file(self, key: str) -> None:
        target = self._path(key)
        if target.exists():
            target.unlink()


class R2DocumentStorage:
    def __init__(
        self,
        endpoint_url: str,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
        region: str = "auto",
    ):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "R2 storage requires boto3. Install project requirements."
            ) from exc
        if not all((endpoint_url, bucket, access_key_id, secret_access_key)):
            raise ValueError("R2 endpoint, bucket, and credentials are required.")
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )

    def upload_fileobj(self, fileobj: BinaryIO, key: str) -> str:
        safe = _safe_key(key)
        fileobj.seek(0)
        self.client.upload_fileobj(fileobj, self.bucket, safe)
        return safe

    def download_file(self, key: str, destination: str | Path) -> Path:
        safe = _safe_key(key)
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self.bucket, safe, str(target))
        return target

    def delete_file(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=_safe_key(key))


_storage_instance: DocumentStorage | None = None


def get_document_storage() -> DocumentStorage:
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    backend = os.getenv("STORAGE_BACKEND", "local").strip().lower()
    if backend == "local":
        root = os.getenv("LOCAL_STORAGE_DIR", "data/objects")
        _storage_instance = LocalDocumentStorage(root)
    elif backend == "r2":
        _storage_instance = R2DocumentStorage(
            endpoint_url=os.getenv("R2_ENDPOINT_URL", ""),
            bucket=os.getenv("R2_BUCKET_NAME", ""),
            access_key_id=os.getenv("R2_ACCESS_KEY_ID", ""),
            secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY", ""),
            region=os.getenv("R2_REGION", "auto"),
        )
    else:
        raise ValueError("STORAGE_BACKEND must be either 'local' or 'r2'.")
    return _storage_instance


def reset_document_storage_for_tests() -> None:
    global _storage_instance
    _storage_instance = None
