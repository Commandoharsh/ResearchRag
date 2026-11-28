from backend.rag.embeddings.embedding_model import EmbeddingModel
from backend.rag.retrieval.vector_store import VectorStore
from backend.rag.retrieval.bm25_retriever import BM25Retriever


class ApplicationState:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(
            collection_name="research_documents",
            vector_size=384,
            storage_path="data/qdrant",
        )
        self.bm25_retriever = BM25Retriever()
        self._bm25_chunk_count = -1
        self.refresh_bm25_if_changed()
        self.initialized = True

    def refresh_bm25_if_changed(self):
        """Refresh the process-local BM25 index after another worker adds vectors."""
        current_count = self.vector_store.count_chunks()
        if current_count != self._bm25_chunk_count:
            chunks = self.vector_store.get_all_chunks()
            self.bm25_retriever.index(chunks)
            self._bm25_chunk_count = current_count
            return True
        return False

    def close(self):
        self.vector_store.close()
