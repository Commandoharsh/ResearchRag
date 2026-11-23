import json
from types import SimpleNamespace
import pytest
from backend.evaluation.benchmark_runner import (
    load_dataset, RetrievalBenchmarkRunner, export_chunk_inventory, write_reports,
)


def test_load_dataset_validates_and_loads(tmp_path):
    p = tmp_path / 'data.json'
    p.write_text(json.dumps({'cases': [{'id':'q1','question':'What?','relevant_chunks':['a']}]}))
    cases = load_dataset(p)
    assert cases[0].id == 'q1' and cases[0].relevant_chunks == {'a'}


def test_load_dataset_rejects_duplicate_ids(tmp_path):
    p = tmp_path / 'data.json'
    p.write_text(json.dumps([{'id':'q','question':'a','relevant_chunks':['x']},{'id':'q','question':'b','relevant_chunks':['x']}]))
    with pytest.raises(ValueError, match='Duplicate'):
        load_dataset(p)


def test_load_dataset_requires_ground_truth_for_answerable_case(tmp_path):
    p = tmp_path / 'data.json'
    p.write_text(json.dumps([{'id':'q','question':'a','relevant_chunks':[]}]))
    with pytest.raises(ValueError, match='require at least one'):
        load_dataset(p)


class FakeRetriever:
    def retrieve(self, query, top_k=5):
        return [SimpleNamespace(chunk_id='doc.pdf_1_0', metadata={'source':'doc.pdf'})]


class FakeApp:
    def __init__(self):
        self.semantic_retriever = FakeRetriever()
        self.hybrid_retriever = FakeRetriever()
        self.reranking_pipeline = FakeRetriever()
        self.state = SimpleNamespace(bm25_retriever=FakeRetriever(), vector_store=SimpleNamespace(
            get_all_chunks=lambda: [SimpleNamespace(chunk_id='doc.pdf_1_0', content='text', metadata={'source':'doc.pdf'})]))


def test_runner_scores_all_four_strategies():
    app = FakeApp()
    from backend.evaluation.benchmark_runner import BenchmarkCase
    report = RetrievalBenchmarkRunner(app, 5).run([BenchmarkCase('q1','question',{'doc.pdf_1_0'})])
    assert set(report['strategies']) == {'semantic','bm25','hybrid','hybrid_reranker'}
    assert report['strategies']['semantic']['metrics']['mrr'] == 1.0


def test_runner_rejects_unknown_ground_truth_ids():
    from backend.evaluation.benchmark_runner import BenchmarkCase
    with pytest.raises(ValueError, match='not present'):
        RetrievalBenchmarkRunner(FakeApp()).run([BenchmarkCase('q1','question',{'missing'})])


def test_export_inventory_csv(tmp_path):
    path = export_chunk_inventory(FakeApp(), tmp_path/'inventory.csv')
    assert path.exists() and 'doc.pdf_1_0' in path.read_text(encoding='utf-8-sig')


def test_write_reports_creates_json_csv_markdown(tmp_path):
    report = {'run_id':'r1','dataset_cases':1,'top_k':5,'strategies':{'semantic':{'metrics':{'precision@5':1,'recall@5':1,'mrr':1,'ndcg@5':1},'latency_ms':{'mean':1,'p95':1}}},'case_results':{'semantic':[{'case_id':'q1','question':'Q','retrieved_chunk_ids':['a'],'retrieved_sources':['a.pdf'],'latency_ms':1,'metrics':{'precision@5':1}}]},'notes':[]}
    paths = write_reports(report, tmp_path)
    assert all(p.exists() for p in paths.values())
    assert 'ResearchRAG Benchmark Report' in paths['markdown'].read_text()
