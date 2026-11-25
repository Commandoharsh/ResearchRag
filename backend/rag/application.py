from pathlib import Path

from backend.config import settings

from backend.database.database import Database
from backend.database.document_repository import DocumentRepository
from backend.database.document_service import DocumentService

from backend.rag.application_state import ApplicationState
from backend.rag.indexing.indexing_pipeline import IndexingPipeline

from backend.rag.retrieval.retriever import SemanticRetriever
from backend.rag.retrieval.hybrid_retriever import HybridRetriever
from backend.rag.retrieval.reranker import Reranker
from backend.rag.retrieval.reranking_pipeline import RerankingPipeline

from backend.rag.generation.answer_generator import AnswerGenerator
from backend.rag.generation.provider_factory import create_llm_provider

from backend.rag.rag_service import RAGService


class RAGApplication:
    """
    Main ResearchRAG application.

    Initializes the database, indexing pipeline, retrieval pipeline,
    language model provider, and RAG query service.
    """

    def __init__(self):
        # --------------------------------------------------
        # Application state
        
        # --------------------------------------------------
        self.state = ApplicationState()

        # --------------------------------------------------
        # Database
        # --------------------------------------------------
        self.database = Database()

        self.document_repository = DocumentRepository(
            self.database
        )

        self.document_service = DocumentService(
            self.document_repository
        )

        # --------------------------------------------------
        # Indexing pipeline
        # --------------------------------------------------
        self.indexing_pipeline = IndexingPipeline(
            embedding_model=self.state.embedding_model,
            vector_store=self.state.vector_store,
            bm25_retriever=self.state.bm25_retriever,
        )

        # --------------------------------------------------
        # Semantic retrieval
        # --------------------------------------------------
        self.semantic_retriever = SemanticRetriever(
            embedding_model=self.state.embedding_model,
            vector_store=self.state.vector_store,
        )

        # --------------------------------------------------
        # Hybrid retrieval
        # --------------------------------------------------
        self.hybrid_retriever = HybridRetriever(
            semantic_retriever=self.semantic_retriever,
            bm25_retriever=self.state.bm25_retriever,
        )

        # --------------------------------------------------
        # Reranking
        # --------------------------------------------------
        self.reranker = Reranker()

        self.reranking_pipeline = RerankingPipeline(
            retriever=self.hybrid_retriever,
            reranker=self.reranker,
        )

        # --------------------------------------------------
        # Language model provider
        # --------------------------------------------------
        # Provider selection is controlled by LLM_PROVIDER.
        # Supported values: "ollama" and "mock".
        self.llm = create_llm_provider()

        # --------------------------------------------------
        # Answer generation
        # --------------------------------------------------
        self.answer_generator = AnswerGenerator(
            llm=self.llm
        )

        # --------------------------------------------------
        # Main RAG service
        # --------------------------------------------------
        self.rag_service = RAGService(
            retriever=self.reranking_pipeline,
            answer_generator=self.answer_generator,
        )

    # ======================================================
    # DOCUMENT INDEXING
    # ======================================================

    def index_pdf(self, file_path: str, stored_file_path: str | None = None):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        document = self.document_service.register(
            filename=path.name,
            file_path=stored_file_path or str(path),
            file_size=path.stat().st_size,
            file_type="pdf",
        )

        try:
            self.document_service.mark_indexing(
                document.id
            )

            result = self.indexing_pipeline.index_pdf(
                str(path)
            )

            self.document_service.mark_indexed(
                document.id,
                result["chunks"],
            )

            result["document_id"] = document.id
            result["status"] = "indexed"

            return result

        except Exception as exc:
            self.document_service.mark_failed(
                document.id,
                str(exc),
            )
            raise

    def index_registered_pdf(self, document_id: str, file_path: str):
        """Index a previously registered document (used by background workers)."""
        path = Path(file_path)
        if not path.is_file() or path.suffix.lower() != ".pdf":
            raise ValueError("A valid PDF file is required.")

        try:
            self.document_service.mark_indexing(document_id)
            result = self.indexing_pipeline.index_pdf(str(path))
            self.document_service.mark_indexed(document_id, result["chunks"])
            result["document_id"] = document_id
            result["status"] = "indexed"
            return result
        except Exception as exc:
            self.document_service.mark_failed(document_id, str(exc))
            raise

    # ======================================================
    # QUERY
    # ======================================================

    def query(
        self,
        question: str,
        conversation_context=None,
    ):
        return self.rag_service.query(
            question=question,
            conversation_context=conversation_context,
        )

    # ======================================================
    # DOCUMENT MANAGEMENT
    # ======================================================

    def get_document(self, document_id: str):
        return self.document_repository.get(
            document_id
        )

    def list_documents(self):
        return self.document_repository.list()

    def delete_document_record(self, document_id: str):
        self.document_repository.delete(
            document_id
        )

    # ======================================================
    # SHUTDOWN
    # ======================================================

    def close(self):
        self.state.close()


# ==========================================================
# APPLICATION SINGLETON
# ==========================================================

_application = None


def create_rag_application():
    """
    Return the shared RAG application instance.

    The instance is created lazily on the first call.
    """
    global _application

    if _application is None:
        _application = RAGApplication()

    return _application