import argparse
from typing import Any

try:
    from backend.skills.data_loader import get_event_by_id as _load_event_by_id
    from backend.skills.data_loader import load_events
    from backend.skills.llm_analyzer import analyze_with_llm
    from backend.skills.report_generator import generate_markdown_report, save_report
    from backend.skills.rule_engine import screen_event_rules
    from backend.skills.severity_grader import grade_severity
except ModuleNotFoundError:
    from skills.data_loader import get_event_by_id as _load_event_by_id
    from skills.data_loader import load_events
    from skills.llm_analyzer import analyze_with_llm
    from skills.report_generator import generate_markdown_report, save_report
    from skills.rule_engine import screen_event_rules
    from skills.severity_grader import grade_severity


def _with_api_defaults(event: dict[str, Any]) -> dict[str, Any]:
    event_with_defaults = dict(event)
    event_with_defaults.setdefault("event_type", "SMART_DRIVING_ANOMALY")
    event_with_defaults.setdefault("severity", "D")
    event_with_defaults.setdefault("summary", event_with_defaults.get("log_text", ""))
    return event_with_defaults


def list_events() -> list[dict[str, Any]]:
    return [_with_api_defaults(event) for event in load_events()]


def get_event_by_id(event_id: str) -> dict[str, Any] | None:
    event = load_event(event_id)
    if event is None:
        return None
    return _with_api_defaults(event)


def load_event(event_id: str) -> dict[str, Any] | None:
    return _load_event_by_id(event_id)


def rule_screening(event: dict[str, Any]) -> list[dict[str, Any]]:
    return screen_event_rules(event)


def severity_grading(
    event: dict[str, Any],
    matched_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    return grade_severity(event, matched_rules)


def llm_analysis(
    event: dict[str, Any],
    matched_rules: list[dict[str, Any]],
    severity: dict[str, Any],
) -> dict[str, Any]:
    return analyze_with_llm(event, matched_rules, severity)


def report_generation(
    event: dict[str, Any],
    matched_rules: list[dict[str, Any]],
    severity: dict[str, Any],
    ai_analysis: dict[str, Any],
) -> tuple[str, str]:
    report = generate_markdown_report(event, matched_rules, severity, ai_analysis)
    report_path = save_report(str(event["event_id"]), report)
    return report, report_path


def analyze_event(event_id: str) -> dict[str, Any]:
    event = load_event(event_id)
    if event is None:
        return {
            "error": "Event not found",
            "event_id": event_id,
            "message": f"No event exists for event_id={event_id}.",
        }

    matched_rules = rule_screening(event)
    severity = severity_grading(event, matched_rules)
    ai_analysis = llm_analysis(event, matched_rules, severity)
    report, report_path = report_generation(event, matched_rules, severity, ai_analysis)

    return {
        "event": event,
        "matched_rules": matched_rules,
        "severity": severity,
        "ai_analysis": ai_analysis,
        "report": report,
        "report_path": report_path,
    }


def _print_cli_summary(result: dict[str, Any]) -> None:
    if "error" in result:
        print(f"Error: {result['message']}")
        return

    event = result["event"]
    severity = result["severity"]
    ai_analysis = result["ai_analysis"]
    matched_rules = result["matched_rules"]

    print("AutoDrive Insight Agent analysis summary")
    print(f"Event ID: {event.get('event_id')}")
    print(f"Severity: {severity.get('level')} (score={severity.get('score')})")
    print(f"Matched rules: {len(matched_rules)}")
    print(f"AI summary: {ai_analysis.get('summary')}")
    print(f"Report path: {result['report_path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AutoDrive Insight Agent analysis.")
    parser.add_argument("--event_id", required=True, help="Event ID, for example EVT_0001")
    args = parser.parse_args()

    result = analyze_event(args.event_id)
    _print_cli_summary(result)
    return 1 if "error" in result else 0


if __name__ == "__main__":
    raise SystemExit(main())
