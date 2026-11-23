import json
from backend.evaluation.report import EvaluationReport


def test_report_save_and_load_round_trip(tmp_path):
    report = EvaluationReport(str(tmp_path))
    payload = {"run_id": "test-run", "metrics": {"mrr": 0.75}, "cases": []}
    path = report.save(payload)
    assert path.exists()
    assert report.load() == payload


def test_report_supports_custom_filename(tmp_path):
    report = EvaluationReport(str(tmp_path))
    path = report.save({"ok": True}, "custom.json")
    assert path.name == "custom.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {"ok": True}


def test_report_load_missing_file_raises(tmp_path):
    report = EvaluationReport(str(tmp_path))
    try:
        report.load("missing.json")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")
