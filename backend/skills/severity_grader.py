def grade_mock_severity(event: dict, rule_hits: list[str]) -> str:
    if "aeb_triggered" in rule_hits or "ttc_too_low" in rule_hits:
        return "A"
    if "driver_takeover" in rule_hits:
        return "B"
    return event.get("severity", "D")
