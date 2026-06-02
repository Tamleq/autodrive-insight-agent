def build_mock_report(
    event: dict,
    rule_hits: list[str],
    severity: str,
    analysis: str,
) -> str:
    return (
        "# AutoDrive Insight Report\n\n"
        f"## Event\n"
        f"- Event ID: {event['event_id']}\n"
        f"- Vehicle ID: {event['vehicle_id']}\n"
        f"- Event Type: {event['event_type']}\n"
        f"- Severity: {severity}\n\n"
        f"## Rule Hits\n"
        + "\n".join(f"- {rule}" for rule in rule_hits)
        + f"\n\n## AI Analysis\n{analysis}\n"
    )
