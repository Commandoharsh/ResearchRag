from types import SimpleNamespace
from backend.rag.generation.citation_extractor import CitationExtractor
from backend.rag.generation.citation_validator import CitationValidator
from backend.rag.generation.citation_service import CitationService


def test_citation_extractor_handles_case_and_duplicates():
    assert CitationExtractor().extract("[SOURCE 1] source 2 SOURCE 1") == [1, 2]


def test_citation_extractor_empty_answer():
    assert CitationExtractor().extract("") == []


def test_citation_validator_filters_out_of_range_and_deduplicates():
    assert CitationValidator().validate([1, 2, 2, 0, 5], 2) == [1, 2]


def test_citation_validator_empty_sources():
    assert CitationValidator().validate([1, 2], 0) == []


def test_citation_service_maps_valid_citation_to_result_metadata():
    result = SimpleNamespace(
        chunk_id="paper.pdf_2_0",
        metadata={"source": "paper.pdf", "page": "2"},
    )
    response = CitationService().build_response("Evidence [SOURCE 1]", [result])
    assert response.answer == "Evidence [SOURCE 1]"
    assert len(response.citations) == 1
    assert response.citations[0].source == "paper.pdf"
    assert response.citations[0].page == "2"
    assert response.citations[0].chunk_id == "paper.pdf_2_0"


def test_citation_service_drops_invalid_citation_ids():
    result = SimpleNamespace(chunk_id="p.pdf_1_0", metadata={"source": "p.pdf", "page": "1"})
    response = CitationService().build_response("[SOURCE 99]", [result])
    assert response.citations == []
