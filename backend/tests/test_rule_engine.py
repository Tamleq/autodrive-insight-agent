from backend.skills.rule_engine import screen_event_rules


def _normal_event() -> dict:
    return {
        "brake_acc": -1.2,
        "aeb_triggered": False,
        "object_confidence": 0.9,
        "takeover": False,
        "ego_speed": 35,
        "lane_confidence": 0.8,
        "lateral_offset": 0.1,
        "ttc": 3.2,
        "planning_status": "normal",
        "perception_status": "stable",
    }


def _rule_ids(event: dict) -> list[str]:
    return [rule["rule_id"] for rule in screen_event_rules(event)]


def test_normal_event_matches_no_rules():
    assert screen_event_rules(_normal_event()) == []


def test_hard_braking_rule():
    event = _normal_event()
    event["brake_acc"] = -3.5

    rules = screen_event_rules(event)

    assert "R001" in [rule["rule_id"] for rule in rules]
    rule = next(rule for rule in rules if rule["rule_id"] == "R001")
    assert rule["rule_name"] == "强制动"
    assert rule["evidence"] == {"brake_acc": -3.5}
    assert isinstance(rule["risk_score"], int)


def test_aeb_triggered_rule():
    event = _normal_event()
    event["aeb_triggered"] = True

    assert "R002" in _rule_ids(event)


def test_suspected_false_brake_rule():
    event = _normal_event()
    event.update(
        {
            "aeb_triggered": True,
            "object_confidence": 0.49,
            "brake_acc": -3.0,
        }
    )

    assert "R003" in _rule_ids(event)


def test_high_risk_takeover_rule():
    event = _normal_event()
    event.update({"takeover": True, "ego_speed": 41})

    assert "R004" in _rule_ids(event)


def test_lane_line_anomaly_rule():
    event = _normal_event()
    event.update({"lane_confidence": 0.39, "lateral_offset": 0.51})

    assert "R005" in _rule_ids(event)


def test_low_ttc_rule():
    event = _normal_event()
    event["ttc"] = 1.5

    assert "R006" in _rule_ids(event)


def test_planning_anomaly_rule():
    event = _normal_event()
    event["planning_status"] = "trajectory deviation detected"

    assert "R007" in _rule_ids(event)


def test_perception_anomaly_rule():
    event = _normal_event()
    event["perception_status"] = "object low_confidence"

    assert "R008" in _rule_ids(event)
