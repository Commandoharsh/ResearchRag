import time
import pytest
from backend.evaluation.latency import LatencyTimer


def test_measure_returns_function_result_and_nonnegative_ms():
    result, elapsed = LatencyTimer().measure(lambda x: x + 1, 4)
    assert result == 5
    assert elapsed >= 0


def test_measure_propagates_function_exception():
    def fail():
        raise RuntimeError("expected")
    with pytest.raises(RuntimeError, match="expected"):
        LatencyTimer().measure(fail)


def test_benchmark_reports_expected_summary_fields():
    report = LatencyTimer().benchmark(lambda x: x * 2, [1, 2, 3], repeats=2)
    assert report["count"] == 6
    assert report["average_ms"] >= 0
    assert report["p95_ms"] >= 0
    assert report["min_ms"] <= report["max_ms"]


def test_benchmark_empty_inputs_returns_zero_summary():
    report = LatencyTimer().benchmark(lambda x: x, [])
    assert report == {"count": 0, "average_ms": 0.0, "p95_ms": 0.0}


def test_benchmark_rejects_callable_errors():
    def fail(_):
        raise ValueError("bad input")
    with pytest.raises(ValueError, match="bad input"):
        LatencyTimer().benchmark(fail, [1])
