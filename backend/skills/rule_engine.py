def _to_float(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _contains_any(value: object, keywords: tuple[str, ...]) -> bool:
    if not isinstance(value, str):
        return False
    normalized_value = value.lower()
    return any(keyword in normalized_value for keyword in keywords)


def _build_rule(
    rule_id: str,
    rule_name: str,
    description: str,
    evidence: dict,
    risk_score: int,
) -> dict:
    return {
        "rule_id": rule_id,
        "rule_name": rule_name,
        "description": description,
        "evidence": evidence,
        "risk_score": risk_score,
    }


def screen_event_rules(event: dict) -> list:
    matched_rules = []

    brake_acc = _to_float(event.get("brake_acc"))
    object_confidence = _to_float(event.get("object_confidence"))
    ego_speed = _to_float(event.get("ego_speed"))
    lane_confidence = _to_float(event.get("lane_confidence"))
    lateral_offset = _to_float(event.get("lateral_offset"))
    ttc = _to_float(event.get("ttc"))
    aeb_triggered = event.get("aeb_triggered") is True
    takeover = event.get("takeover") is True
    planning_status = event.get("planning_status")
    perception_status = event.get("perception_status")

    if brake_acc is not None and brake_acc <= -3.5:
        matched_rules.append(
            _build_rule(
                "R001",
                "强制动",
                "brake_acc <= -3.5",
                {"brake_acc": event.get("brake_acc")},
                70,
            )
        )

    if aeb_triggered:
        matched_rules.append(
            _build_rule(
                "R002",
                "AEB触发",
                "aeb_triggered == True",
                {"aeb_triggered": event.get("aeb_triggered")},
                80,
            )
        )

    if (
        aeb_triggered
        and object_confidence is not None
        and object_confidence < 0.5
        and brake_acc is not None
        and brake_acc <= -3.0
    ):
        matched_rules.append(
            _build_rule(
                "R003",
                "疑似误刹",
                "aeb_triggered == True and object_confidence < 0.5 and brake_acc <= -3.0",
                {
                    "aeb_triggered": event.get("aeb_triggered"),
                    "object_confidence": event.get("object_confidence"),
                    "brake_acc": event.get("brake_acc"),
                },
                90,
            )
        )

    if takeover and ego_speed is not None and ego_speed > 40:
        matched_rules.append(
            _build_rule(
                "R004",
                "高风险接管",
                "takeover == True and ego_speed > 40",
                {
                    "takeover": event.get("takeover"),
                    "ego_speed": event.get("ego_speed"),
                },
                85,
            )
        )

    if (
        lane_confidence is not None
        and lane_confidence < 0.4
        and lateral_offset is not None
        and lateral_offset > 0.5
    ):
        matched_rules.append(
            _build_rule(
                "R005",
                "车道线异常",
                "lane_confidence < 0.4 and lateral_offset > 0.5",
                {
                    "lane_confidence": event.get("lane_confidence"),
                    "lateral_offset": event.get("lateral_offset"),
                },
                75,
            )
        )

    if ttc is not None and ttc <= 1.5:
        matched_rules.append(
            _build_rule(
                "R006",
                "TTC过低",
                "ttc <= 1.5",
                {"ttc": event.get("ttc")},
                88,
            )
        )

    if _contains_any(planning_status, ("abnormal", "deviation")):
        matched_rules.append(
            _build_rule(
                "R007",
                "规划异常",
                "planning_status contains abnormal or deviation",
                {"planning_status": planning_status},
                72,
            )
        )

    if _contains_any(perception_status, ("unstable", "lost", "low_confidence")):
        matched_rules.append(
            _build_rule(
                "R008",
                "感知异常",
                "perception_status contains unstable, lost, or low_confidence",
                {"perception_status": perception_status},
                78,
            )
        )

    return matched_rules


def apply_mock_rules(event: dict) -> list[str]:
    event_type = event.get("event_type", "")
    rule_map = {
        "AEB_TRIGGER": ["aeb_triggered", "ttc_too_low"],
        "TAKEOVER": ["driver_takeover", "lane_line_confidence_low"],
        "PLANNING_ANOMALY": ["planning_output_unstable"],
    }
    return rule_map.get(event_type, ["manual_review_required"])
