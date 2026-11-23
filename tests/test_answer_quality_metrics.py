import pytest
from backend.evaluation.answer_metrics import token_set, answer_keyword_overlap
from backend.evaluation.answer_relevance import answer_relevance_score
from backend.evaluation.faithfulness import faithfulness_score


def test_token_set_is_case_insensitive_and_removes_duplicates():
    assert token_set("RAG rag Retrieval") == {"rag", "retrieval"}


def test_answer_keyword_overlap_full_match():
    assert answer_keyword_overlap("RAG retrieves external context", "RAG retrieves external context") == 1.0


def test_answer_keyword_overlap_partial_match():
    assert answer_keyword_overlap("retrieves context", "RAG retrieves external context") == pytest.approx(0.5)


def test_answer_keyword_overlap_empty_reference_is_zero():
    assert answer_keyword_overlap("some answer", "") == 0.0


def test_answer_relevance_full_question_term_coverage():
    assert answer_relevance_score("RAG?", "RAG is a retrieval system") == 1.0


def test_answer_relevance_empty_question_is_zero():
    assert answer_relevance_score("", "some answer") == 0.0


def test_faithfulness_lexical_overlap_full_support():
    assert faithfulness_score("RAG retrieves external context", "RAG retrieves external context") == 1.0


def test_faithfulness_empty_answer_is_zero():
    assert faithfulness_score("", "some context") == 0.0


def test_faithfulness_is_bounded():
    score = faithfulness_score("RAG retrieves unknown facts", "RAG retrieves context")
    assert 0.0 <= score <= 1.0
