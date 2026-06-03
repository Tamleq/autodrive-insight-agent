from backend.skills.llm_analyzer import analyze_with_llm


def _sample_event() -> dict:
    return {
        "event_id": "EVT_TEST_001",
        "scene_type": "urban intersection",
        "ego_speed": 42,
        "brake_acc": -3.6,
        "ttc": 1.4,
        "object_confidence": 0.45,
        "lane_confidence": 0.7,
        "takeover": True,
        "aeb_triggered": True,
    }


def _matched_rules() -> list[dict]:
    return [
        {
            "rule_id": "R001",
            "rule_name": "Hard braking",
            "description": "brake_acc <= -3.5",
            "evidence": {"brake_acc": -3.6},
            "risk_score": 70,
        },
        {
            "rule_id": "R006",
            "rule_name": "Low TTC",
            "description": "ttc <= 1.5",
            "evidence": {"ttc": 1.4},
            "risk_score": 88,
        },
    ]


def test_returns_mock_analysis_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = analyze_with_llm(
        _sample_event(),
        _matched_rules(),
        {"level": "B", "score": 50, "reason": "Severity level B with score 50."},
    )

    assert result["summary"]
    assert "EVT_TEST_001" in result["summary"]
    assert "R001" in result["summary"]


def test_output_contains_required_fields(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = analyze_with_llm(
        _sample_event(),
        _matched_rules(),
        {"level": "B", "score": 50, "reason": "Severity level B with score 50."},
    )

    assert set(result) == {
        "summary",
        "scenario_description",
        "possible_causes",
        "risk_assessment",
        "recommendations",
        "need_human_review",
    }


def test_a_or_s_level_requires_human_review(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    a_result = analyze_with_llm(_sample_event(), _matched_rules(), {"level": "A"})
    s_result = analyze_with_llm(_sample_event(), _matched_rules(), {"level": "S"})

    assert a_result["need_human_review"] is True
    assert s_result["need_human_review"] is True


def test_recommendations_are_not_empty(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = analyze_with_llm(_sample_event(), _matched_rules(), {"level": "C"})

    assert result["recommendations"]
    assert len(result["recommendations"]) >= 2


def test_possible_causes_are_not_empty(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = analyze_with_llm(_sample_event(), _matched_rules(), {"level": "C"})

    assert result["possible_causes"]
    assert len(result["possible_causes"]) >= 2
