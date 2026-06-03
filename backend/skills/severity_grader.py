def grade_mock_severity(event: dict, rule_hits: list[str]) -> str:
    if "aeb_triggered" in rule_hits or "ttc_too_low" in rule_hits:
        return "A"
    if "driver_takeover" in rule_hits:
        return "B"
    return event.get("severity", "D")


LEVEL_THRESHOLDS = (
    (80, "S"),
    (60, "A"),
    (40, "B"),
    (20, "C"),
    (0, "D"),
)

HIGH_RISK_SCENES = {"高速", "城市路口"}


def _as_number(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _level_for_score(score: int) -> str:
    for threshold, level in LEVEL_THRESHOLDS:
        if score >= threshold:
            return level
    return "D"


def _is_high_risk_scene(scene_type: object) -> bool:
    if not isinstance(scene_type, str):
        return False
    return any(scene in scene_type for scene in HIGH_RISK_SCENES)


def grade_severity(event: dict, matched_rules: list) -> dict:
    score = 0
    factors = []

    if event.get("aeb_triggered") is True:
        score += 25
        factors.append("AEB triggered (+25)")

    if event.get("takeover") is True:
        score += 25
        factors.append("Driver takeover (+25)")

    brake_acc = _as_number(event.get("brake_acc"))
    if brake_acc is not None and brake_acc <= -3.5:
        score += 20
        factors.append("Hard braking: brake_acc <= -3.5 (+20)")

    ttc = _as_number(event.get("ttc"))
    if ttc is not None and ttc <= 1.5:
        score += 20
        factors.append("Low TTC: ttc <= 1.5 (+20)")

    object_confidence = _as_number(event.get("object_confidence"))
    if object_confidence is not None and object_confidence < 0.5:
        score += 10
        factors.append("Low object confidence < 0.5 (+10)")

    if _is_high_risk_scene(event.get("scene_type")):
        score += 10
        factors.append("High-risk scene: 高速 or 城市路口 (+10)")

    level = _level_for_score(score)
    rule_count = len(matched_rules or [])
    reason = (
        f"Severity level {level} with score {score}. "
        f"Matched {rule_count} rule(s); "
        f"{'; '.join(factors) if factors else 'no scoring factors triggered'}."
    )

    return {
        "score": int(score),
        "level": level,
        "reason": reason,
        "factors": factors,
    }
