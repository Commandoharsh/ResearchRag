import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    # ---------------------------------------------------------
    # LLM PROVIDER
    # ---------------------------------------------------------

    LLM_PROVIDER = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).strip().lower()

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2",
    )

    # ---------------------------------------------------------
    # GEMINI
    # ---------------------------------------------------------

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    GEMINI_BASE_URL = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    )

    GEMINI_TIMEOUT = int(
        os.getenv(
            "GEMINI_TIMEOUT",
            "120",
        )
    )

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    RAG_TOP_K = int(
        os.getenv(
            "RAG_TOP_K",
            "5",
        )
    )

    RAG_RETRIEVAL_K = int(
        os.getenv(
            "RAG_RETRIEVAL_K",
            "20",
        )
    )

    RAG_FINAL_K = int(
        os.getenv(
            "RAG_FINAL_K",
            "5",
        )
    )

    # ---------------------------------------------------------
    # UPLOADS
    # ---------------------------------------------------------

    MAX_UPLOAD_SIZE_MB = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_MB",
            "25",
        )
    )

    # ---------------------------------------------------------
    # JWT AUTHENTICATION
    # ---------------------------------------------------------

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "development-secret-change-this",
    )

    JWT_ALGORITHM = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "60",
        )
    )


settings = Settings()