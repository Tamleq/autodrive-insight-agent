def generate_mock_analysis(event: dict, rule_hits: list[str], severity: str) -> str:
    return (
        f"Mock LLM analysis: event {event['event_id']} is graded as {severity}. "
        f"Key rule hits include {', '.join(rule_hits)}. "
        "Further validation should review perception, planning, and vehicle state logs."
    )
