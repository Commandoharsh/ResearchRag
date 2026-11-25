from types import SimpleNamespace

from backend.rag.application_state import ApplicationState
from backend.rag.retrieval.bm25_retriever import BM25Retriever


class FakeVectorStore:
    def __init__(self):
        self.chunks = []
        self.count_calls = 0

    def count_chunks(self):
        self.count_calls += 1
        return len(self.chunks)

    def get_all_chunks(self):
        return list(self.chunks)


def test_bm25_refreshes_only_when_vector_count_changes():
    state = ApplicationState.__new__(ApplicationState)
    state.vector_store = FakeVectorStore()
    state.bm25_retriever = BM25Retriever()
    state._bm25_chunk_count = -1

    assert state.refresh_bm25_if_changed() is True
    assert state._bm25_chunk_count == 0

    assert state.refresh_bm25_if_changed() is False

    state.vector_store.chunks.append(
        SimpleNamespace(
            chunk_id="chunk-1",
            content="retrieval augmented generation",
            metadata={"source": "paper.pdf"},
        )
    )

    assert state.refresh_bm25_if_changed() is True
    assert state._bm25_chunk_count == 1
    assert state.bm25_retriever.retrieve("retrieval", top_k=1)[0].chunk_id == "chunk-1"
