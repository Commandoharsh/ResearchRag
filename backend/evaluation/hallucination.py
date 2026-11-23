"""
Deterministic hallucination-risk proxy metrics.

These are lexical heuristics, not a semantic proof that a statement is true
or false. Use an LLM judge or human review for stronger claim-level assessment.
"""
import re

from backend.evaluation.answer_metrics import token_set


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "by",
    "can", "could", "did", "do", "does", "for", "from", "had", "has",
    "have", "he", "her", "hers", "him", "his", "how", "i", "if", "in",
    "into", "is", "it", "its", "may", "might", "more", "most", "of",
    "on", "or", "our", "she", "should", "that", "the", "their", "them",
    "there", "these", "they", "this", "those", "to", "was", "we", "were",
    "what", "when", "where", "which", "who", "will", "with", "would",
    "you", "your",
}


def _content_tokens(text: str) -> set[str]:
    return token_set(text) - _STOPWORDS


def sentence_support_scores(
    answer: str,
    context: str,
) -> list[float]:
    """Return lexical context-overlap scores for answer sentences."""
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", answer.strip())
        if sentence.strip()
    ]

    context_tokens = _content_tokens(context)
    scores = []

    for sentence in sentences:
        sentence_tokens = _content_tokens(sentence)
        if not sentence_tokens:
            scores.append(1.0 if not context_tokens else 0.0)
            continue

        scores.append(
            len(sentence_tokens & context_tokens) / len(sentence_tokens)
        )

    return scores


def hallucination_rate(
    answer: str,
    context: str,
    support_threshold: float = 0.30,
) -> float:
    """
    Fraction of answer sentences with lexical support below threshold.

    0.0 means every sentence met the overlap threshold; 1.0 means none did.
    This is a heuristic risk indicator, not a factuality guarantee.
    """
    if not answer.strip():
        return 0.0

    scores = sentence_support_scores(answer, context)
    if not scores:
        return 0.0

    unsupported = sum(score < support_threshold for score in scores)
    return unsupported / len(scores)
