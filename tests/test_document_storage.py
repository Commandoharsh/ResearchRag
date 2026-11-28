from pathlib import Path

import pytest

from backend.storage.document_storage import LocalDocumentStorage


def test_local_storage_upload_download_and_delete(tmp_path):
    storage = LocalDocumentStorage(tmp_path / "objects")
    source = tmp_path / "source.pdf"
    source.write_bytes(b"%PDF-1.7 sample")

    with source.open("rb") as stream:
        key = storage.upload_fileobj(stream, "documents/test.pdf")

    downloaded = storage.download_file(key, tmp_path / "downloaded.pdf")
    assert downloaded.read_bytes() == source.read_bytes()

    storage.delete_file(key)
    with pytest.raises(FileNotFoundError):
        storage.download_file(key, tmp_path / "missing.pdf")


@pytest.mark.parametrize("key", ["../escape.pdf", "/absolute.pdf", "documents/../../escape.pdf"])
def test_local_storage_rejects_path_traversal(tmp_path, key):
    storage = LocalDocumentStorage(tmp_path / "objects")
    with pytest.raises(ValueError):
        storage.download_file(key, tmp_path / "output.pdf")


def test_local_storage_does_not_overwrite_different_uploads(tmp_path):
    storage = LocalDocumentStorage(tmp_path / "objects")
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    with first.open("rb") as stream:
        storage.upload_fileobj(stream, "documents/one.pdf")
    with second.open("rb") as stream:
        storage.upload_fileobj(stream, "documents/two.pdf")

    assert storage.download_file("documents/one.pdf", tmp_path / "one").read_bytes() == b"first"
    assert storage.download_file("documents/two.pdf", tmp_path / "two").read_bytes() == b"second"
