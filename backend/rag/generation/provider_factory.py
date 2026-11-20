from backend.config import settings

from backend.rag.generation.llm_provider import LLMProvider
from backend.rag.generation.mock_llm import MockLLM
from backend.rag.generation.ollama_provider import OllamaProvider
from backend.rag.generation.gemini_provider import GeminiProvider


def create_llm_provider(
    provider_name: str | None = None,
) -> LLMProvider:
    """
    Create an LLM provider based on configuration.

    Supported providers:
    - ollama
    - gemini
    - mock
    """

    name = (
        provider_name
        if provider_name is not None
        else settings.LLM_PROVIDER
    ).strip().lower()

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------

    if name == "ollama":

        return OllamaProvider(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    # ---------------------------------------------------------
    # GEMINI
    # ---------------------------------------------------------

    if name == "gemini":

        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            base_url=settings.GEMINI_BASE_URL,
            timeout=settings.GEMINI_TIMEOUT,
        )

    # ---------------------------------------------------------
    # MOCK
    # ---------------------------------------------------------

    if name == "mock":
        return MockLLM()

    # ---------------------------------------------------------
    # INVALID PROVIDER
    # ---------------------------------------------------------

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{name}'. "
        "Supported providers are: ollama, gemini, mock."
    )