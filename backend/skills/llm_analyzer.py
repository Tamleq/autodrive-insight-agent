import os


ANALYSIS_KEYS = (
    "summary",
    "scenario_description",
    "possible_causes",
    "risk_assessment",
    "recommendations",
    "need_human_review",
)


def _severity_level(severity: dict | str | None) -> str:
    if isinstance(severity, dict):
        return str(severity.get("level", "D")).upper()
    if severity is None:
        return "D"
    return str(severity).upper()


def _event_value(event: dict, key: str, default: str = "unknown") -> str:
    value = event.get(key)
    if value is None or value == "":
        return default
    return str(value)


def _rule_labels(matched_rules: list | None) -> list[str]:
    labels = []
    for rule in matched_rules or []:
        if isinstance(rule, dict):
            rule_id = rule.get("rule_id")
            rule_name = rule.get("rule_name") or rule.get("description")
            if rule_id and rule_name:
                labels.append(f"{rule_id} {rule_name}")
            elif rule_id:
                labels.append(str(rule_id))
            elif rule_name:
                labels.append(str(rule_name))
        else:
            labels.append(str(rule))
    return labels


def _possible_causes(event: dict, matched_rules: list | None) -> list[str]:
    causes = []
    rule_ids = {
        rule.get("rule_id")
        for rule in matched_rules or []
        if isinstance(rule, dict) and rule.get("rule_id")
    }

    if "R003" in rule_ids or event.get("object_confidence") not in (None, ""):
        causes.append("Perception confidence may be unstable around the target object.")
    if "R005" in rule_ids or event.get("lane_confidence") not in (None, ""):
        causes.append("Lane recognition or lateral localization may have degraded.")
    if "R006" in rule_ids or event.get("ttc") not in (None, ""):
        causes.append("Following distance or relative-speed estimation may be insufficient.")
    if "R007" in rule_ids:
        causes.append("Planning output may contain abnormal trajectory or deviation signals.")
    if "R008" in rule_ids:
        causes.append("Perception status indicates lost, unstable, or low-confidence tracking.")
    if "R001" in rule_ids or event.get("brake_acc") not in (None, ""):
        causes.append("Vehicle control logs may show abrupt braking demand or actuator response.")
    if event.get("takeover") is True:
        causes.append("Driver takeover suggests the automation behavior may have exceeded comfort or safety boundaries.")
    if event.get("aeb_triggered") is True:
        causes.append("AEB trigger conditions should be checked for true positive versus false positive behavior.")

    fallback_causes = [
        "Rule evidence should be correlated with perception, planning, and vehicle-state logs.",
        "Scenario context may include traffic participant behavior not fully captured by the rule engine.",
    ]
    for cause in fallback_causes:
        if len(causes) >= 2:
            break
        causes.append(cause)

    return causes


def _recommendations(level: str, matched_rules: list | None) -> list[str]:
    recommendations = [
        "Review synchronized perception, planning, control, and vehicle-state logs for the event window.",
        "Replay the scenario and compare rule evidence against raw sensor traces and driver takeover timing.",
    ]

    rule_ids = {
        rule.get("rule_id")
        for rule in matched_rules or []
        if isinstance(rule, dict) and rule.get("rule_id")
    }

    if "R003" in rule_ids:
        recommendations.append("Validate whether the AEB trigger was caused by low object confidence or object misclassification.")
    if "R005" in rule_ids:
        recommendations.append("Inspect lane-line confidence, lateral offset, and map alignment around the anomaly.")
    if "R006" in rule_ids:
        recommendations.append("Check TTC calculation inputs, lead-object tracking continuity, and relative-speed estimates.")
    if level in {"S", "A"}:
        recommendations.append("Escalate to safety review before closing the event.")

    return recommendations


def _mock_analysis(event: dict, matched_rules: list | None, severity: dict | str | None) -> dict:
    level = _severity_level(severity)
    score = severity.get("score") if isinstance(severity, dict) else None
    severity_reason = severity.get("reason") if isinstance(severity, dict) else None
    event_id = _event_value(event, "event_id", "unknown event")
    scene_type = _event_value(event, "scene_type", "unknown scene")
    rule_labels = _rule_labels(matched_rules)
    rule_text = ", ".join(rule_labels) if rule_labels else "no matched rules"
    score_text = f" with score {score}" if score is not None else ""

    summary = (
        f"Event {event_id} is assessed as severity {level}{score_text}; "
        f"matched evidence: {rule_text}."
    )
    scenario_description = (
        f"Scene={scene_type}, speed={_event_value(event, 'ego_speed')} km/h, "
        f"brake_acc={_event_value(event, 'brake_acc')}, "
        f"ttc={_event_value(event, 'ttc')}, "
        f"takeover={event.get('takeover', False)}, "
        f"aeb_triggered={event.get('aeb_triggered', False)}."
    )
    risk_assessment = severity_reason or (
        f"Severity {level} is derived from the provided event metrics and matched rules."
    )

    return {
        "summary": summary,
        "scenario_description": scenario_description,
        "possible_causes": _possible_causes(event, matched_rules),
        "risk_assessment": risk_assessment,
        "recommendations": _recommendations(level, matched_rules),
        "need_human_review": level in {"S", "A"},
    }


def _call_real_llm(event: dict, matched_rules: list | None, severity: dict | str | None) -> dict | None:
    # Reserved integration point. The module intentionally stays dependency-free
    # so tests and local demos run without an API key or network access.
    if not os.getenv("OPENAI_API_KEY"):
        return None
    return None


def analyze_with_llm(event: dict, matched_rules: list, severity: dict) -> dict:
    real_result = _call_real_llm(event, matched_rules, severity)
    if real_result is not None:
        return real_result
    return _mock_analysis(event, matched_rules, severity)


def generate_mock_analysis(event: dict, rule_hits: list[str], severity: str) -> str:
    analysis = analyze_with_llm(event, rule_hits, severity)
    return analysis["summary"]
