import json
from collections.abc import Iterator

import requests

from backend.rag.generation.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Google Gemini API provider.

    Supports:
    - Normal text generation
    - Streaming text generation
    - System instructions
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        base_url: str = (
            "https://generativelanguage.googleapis.com/v1beta"
        ),
        timeout: int = 120,
    ):

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required when using Gemini."
            )

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        })

    # ---------------------------------------------------------
    # REQUEST PAYLOAD
    # ---------------------------------------------------------

    def _build_payload(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> dict:

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ],
                }
            ],
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [
                    {
                        "text": system_prompt,
                    }
                ]
            }

        return payload

    # ---------------------------------------------------------
    # RESPONSE EXTRACTION
    # ---------------------------------------------------------

    @staticmethod
    def _extract_text(data: dict) -> str:

        candidates = data.get(
            "candidates",
            [],
        )

        if not candidates:
            return ""

        content = candidates[0].get(
            "content",
            {},
        )

        parts = content.get(
            "parts",
            [],
        )

        return "".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict)
        )

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        payload = self._build_payload(
            prompt,
            system_prompt,
        )

        url = (
            f"{self.base_url}/models/"
            f"{self.model}:generateContent"
        )

        response = self.session.post(
            url,
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        result = response.json()

        answer = self._extract_text(
            result
        )

        if not answer.strip():
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return answer.strip()

    # ---------------------------------------------------------
    # STREAM
    # ---------------------------------------------------------

    def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> Iterator[str]:

        payload = self._build_payload(
            prompt,
            system_prompt,
        )

        url = (
            f"{self.base_url}/models/"
            f"{self.model}:streamGenerateContent"
            "?alt=sse"
        )

        with self.session.post(
            url,
            json=payload,
            stream=True,
            timeout=self.timeout,
        ) as response:

            response.raise_for_status()

            for line in response.iter_lines(
                decode_unicode=True
            ):

                if not line:
                    continue

                if line.startswith("data:"):
                    line = line[5:].strip()

                if not line or line == "[DONE]":
                    continue

                try:
                    data = json.loads(line)

                except json.JSONDecodeError:
                    continue

                token = self._extract_text(
                    data
                )

                if token:
                    yield token