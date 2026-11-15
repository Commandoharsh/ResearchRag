import re


class CitationExtractor:
    """
    Extract source identifiers from generated RAG answers.

    Supports:
        [SOURCE 1]
        SOURCE 1
        Source 1 (Page 2)
        [Source 1, Source 3]
    """

    CITATION_PATTERN = re.compile(
        r"\[?\s*SOURCE\s+(\d+)\s*\]?",
        re.IGNORECASE,
    )

    def extract(self, answer: str) -> list[int]:
        if not answer:
            return []

        matches = self.CITATION_PATTERN.findall(answer)

        return sorted(set(int(match) for match in matches))