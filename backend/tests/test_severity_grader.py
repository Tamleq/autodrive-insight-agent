from backend.skills.severity_grader import grade_severity


def _base_event() -> dict:
    return {
        "aeb_triggered": False,
        "takeover": False,
        "brake_acc": -1.0,
        "ttc": 3.0,
        "object_confidence": 0.9,
        "scene_type": "普通道路",
    }


def test_no_factors_returns_d_level():
    result = grade_severity(_base_event(), [])

    assert result["score"] == 0
    assert result["level"] == "D"
    assert result["factors"] == []
    assert "no scoring factors triggered" in result["reason"]


def test_all_factors_return_s_level():
    event = {
        "aeb_triggered": True,
        "takeover": True,
        "brake_acc": -3.5,
        "ttc": 1.5,
        "object_confidence": 0.49,
        "scene_type": "城市路口",
    }

    result = grade_severity(event, [{"rule_id": "R001"}, {"rule_id": "R006"}])

    assert result["score"] == 110
    assert result["level"] == "S"
    assert len(result["factors"]) == 6
    assert "Matched 2 rule(s)" in result["reason"]


def test_takeover_and_aeb_return_b_level():
    event = _base_event()
    event.update({"aeb_triggered": True, "takeover": True})

    result = grade_severity(event, [])

    assert result["score"] == 50
    assert result["level"] == "B"


def test_scene_type_matches_highway_or_urban_intersection_text():
    highway_event = _base_event()
    highway_event["scene_type"] = "高速跟车急刹"

    urban_event = _base_event()
    urban_event["scene_type"] = "城市路口两轮车疑似误刹"

    assert grade_severity(highway_event, [])["score"] == 10
    assert grade_severity(urban_event, [])["score"] == 10


def test_invalid_numeric_values_are_ignored():
    event = _base_event()
    event.update(
        {
            "brake_acc": "not-a-number",
            "ttc": None,
            "object_confidence": "unknown",
        }
    )

    result = grade_severity(event, None)

    assert result["score"] == 0
    assert result["level"] == "D"
