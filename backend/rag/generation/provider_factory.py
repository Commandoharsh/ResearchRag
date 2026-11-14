from backend.config import settings
from backend.rag.generation.llm_provider import LLMProvider
from backend.rag.generation.mock_llm import MockLLM
from backend.rag.generation.ollama_provider import OllamaProvider


def create_llm_provider(
    provider_name: str | None = None,
) -> LLMProvider:
    """Create a language model provider from configuration."""

    name = (
        provider_name
        if provider_name is not None
        else settings.LLM_PROVIDER
    ).strip().lower()

    if name == "ollama":
        return OllamaProvider(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    if name == "mock":
        return MockLLM()

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{name}'. "
        "Supported providers are: ollama, mock."
    )