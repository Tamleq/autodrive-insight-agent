from pathlib import Path

from backend.skills.report_generator import generate_markdown_report, save_report


def _sample_event() -> dict:
    return {
        "event_id": "EVT_REPORT_001",
        "vehicle_id": "VH_TEST_01",
        "timestamp": "2026-01-01T08:07:00",
        "scene_type": "城市路口疑似误刹",
        "weather": "晴",
        "ego_speed": 18.0,
        "brake_acc": -5.47,
        "ttc": 1.02,
        "aeb_triggered": True,
        "takeover": False,
        "log_text": "城市路口目标置信度波动后出现急刹。",
    }


def _matched_rules() -> list[dict]:
    return [
        {
            "rule_id": "R001",
            "rule_name": "强制动",
            "description": "brake_acc <= -3.5",
            "evidence": {"brake_acc": -5.47},
            "risk_score": 70,
        },
        {
            "rule_id": "R006",
            "rule_name": "TTC 过低",
            "description": "ttc <= 1.5",
            "evidence": {"ttc": 1.02},
            "risk_score": 88,
        },
    ]


def _severity() -> dict:
    return {
        "level": "A",
        "score": 75,
        "reason": "Severity level A with score 75.",
        "factors": ["AEB triggered (+25)", "Hard braking (+20)"],
    }


def _ai_analysis() -> dict:
    return {
        "summary": "事件存在急刹和低 TTC 风险。",
        "scenario_description": "车辆在城市路口接近目标物时触发 AEB。",
        "possible_causes": ["目标置信度波动", "跟车距离偏低"],
        "risk_assessment": "建议按高风险事件跟进。",
        "recommendations": ["复核感知日志", "回放事件窗口"],
        "need_human_review": True,
    }


def _report() -> str:
    return generate_markdown_report(
        _sample_event(),
        _matched_rules(),
        _severity(),
        _ai_analysis(),
    )


def test_generate_markdown_report_returns_string():
    report = _report()

    assert isinstance(report, str)
    assert report.startswith("# AutoDrive Insight")
    assert "## 1. 事件基本信息" in report


def test_report_contains_event_id():
    assert "EVT_REPORT_001" in _report()


def test_report_contains_severity_level():
    report = _report()

    assert "severity level：A" in report
    assert "severity score：75" in report


def test_report_contains_matched_rules():
    report = _report()

    assert "规则命中情况" in report
    assert "R001 强制动" in report
    assert "R006 TTC 过低" in report


def test_save_report_writes_file():
    report = _report()
    path = Path(save_report("EVT_REPORT_001", report))

    assert path.exists()
    assert path.name == "EVT_REPORT_001_report.md"
    assert path.read_text(encoding="utf-8") == report
