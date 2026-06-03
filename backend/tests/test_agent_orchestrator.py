from pathlib import Path

from backend.agent_orchestrator import analyze_event


def test_analyze_event_returns_complete_result_for_existing_event():
    result = analyze_event("EVT_0001")

    assert "error" not in result
    assert result["event"]["event_id"] == "EVT_0001"
    assert isinstance(result["matched_rules"], list)
    assert isinstance(result["severity"], dict)
    assert isinstance(result["ai_analysis"], dict)
    assert isinstance(result["report"], str)
    assert isinstance(result["report_path"], str)


def test_analyze_event_returns_error_for_missing_event():
    result = analyze_event("EVT_9999")

    assert result["error"] == "Event not found"
    assert result["event_id"] == "EVT_9999"
    assert "No event exists" in result["message"]


def test_analyze_event_output_contains_required_keys():
    result = analyze_event("EVT_0001")

    for key in ("event", "matched_rules", "severity", "ai_analysis", "report"):
        assert key in result


def test_analyze_event_generates_report_path():
    result = analyze_event("EVT_0001")
    report_path = Path(result["report_path"])

    assert report_path.exists()
    assert report_path.name == "EVT_0001_report.md"
    assert report_path.read_text(encoding="utf-8") == result["report"]
