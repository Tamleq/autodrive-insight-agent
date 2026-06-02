from skills.data_loader import load_mock_events
from skills.llm_analyzer import generate_mock_analysis
from skills.report_generator import build_mock_report
from skills.rule_engine import apply_mock_rules
from skills.severity_grader import grade_mock_severity


def list_events() -> list[dict]:
    return load_mock_events()


def get_event_by_id(event_id: str) -> dict | None:
    return next((event for event in load_mock_events() if event["event_id"] == event_id), None)


def analyze_event(event_id: str) -> dict | None:
    event = get_event_by_id(event_id)
    if event is None:
        return None

    rule_hits = apply_mock_rules(event)
    severity = grade_mock_severity(event, rule_hits)
    analysis = generate_mock_analysis(event, rule_hits, severity)
    report = build_mock_report(event, rule_hits, severity, analysis)

    return {
        "event": event,
        "rule_hits": rule_hits,
        "severity": severity,
        "analysis": analysis,
        "report": report,
    }
