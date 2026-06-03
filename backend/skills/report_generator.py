from pathlib import Path


REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"


def _value(data: dict | None, key: str, default: str = "未知") -> object:
    if not isinstance(data, dict):
        return default
    value = data.get(key)
    if value is None or value == "":
        return default
    return value


def _yes_no(value: object) -> str:
    return "是" if value is True else "否"


def _markdown_list(items: list | tuple | None, empty_text: str = "暂无") -> str:
    if not items:
        return f"- {empty_text}"
    return "\n".join(f"- {item}" for item in items)


def _format_evidence(evidence: object) -> str:
    if not isinstance(evidence, dict) or not evidence:
        return "无"
    return "，".join(f"{key}={value}" for key, value in evidence.items())


def _format_rules(matched_rules: list | None) -> str:
    if not matched_rules:
        return "- 未命中规则"

    lines = []
    for index, rule in enumerate(matched_rules, start=1):
        if isinstance(rule, dict):
            rule_id = rule.get("rule_id", f"R{index:03d}")
            rule_name = rule.get("rule_name", "未命名规则")
            description = rule.get("description", "无描述")
            risk_score = rule.get("risk_score", "未知")
            evidence = _format_evidence(rule.get("evidence"))
            lines.append(
                f"- {rule_id} {rule_name}：{description}；"
                f"风险分={risk_score}；证据：{evidence}"
            )
        else:
            lines.append(f"- {rule}")
    return "\n".join(lines)


def _collect_key_evidence(event: dict, matched_rules: list | None) -> list[str]:
    evidence = [
        f"ego_speed={_value(event, 'ego_speed')} km/h",
        f"brake_acc={_value(event, 'brake_acc')} m/s²",
        f"ttc={_value(event, 'ttc')} s",
        f"aeb_triggered={_yes_no(event.get('aeb_triggered'))}",
        f"takeover={_yes_no(event.get('takeover'))}",
    ]

    for rule in matched_rules or []:
        if isinstance(rule, dict) and rule.get("evidence"):
            rule_id = rule.get("rule_id", "未知规则")
            evidence.append(f"{rule_id} 证据：{_format_evidence(rule.get('evidence'))}")

    return evidence


def generate_markdown_report(
    event: dict,
    matched_rules: list,
    severity: dict,
    ai_analysis: dict,
) -> str:
    """Generate a Chinese Markdown report for one intelligent-driving event."""
    severity_level = _value(severity, "level")
    severity_score = _value(severity, "score")
    severity_reason = _value(severity, "reason")
    recommendations = _value(ai_analysis, "recommendations", [])
    possible_causes = _value(ai_analysis, "possible_causes", [])
    need_human_review = _value(ai_analysis, "need_human_review", None)

    if need_human_review is None:
        need_human_review = severity_level in {"S", "A"}

    return (
        f"# AutoDrive Insight 事件分析报告\n\n"
        f"## 1. 事件基本信息\n\n"
        f"- event_id：{_value(event, 'event_id')}\n"
        f"- vehicle_id：{_value(event, 'vehicle_id')}\n"
        f"- timestamp：{_value(event, 'timestamp')}\n"
        f"- scene_type：{_value(event, 'scene_type')}\n"
        f"- weather：{_value(event, 'weather')}\n"
        f"- ego_speed：{_value(event, 'ego_speed')}\n"
        f"- brake_acc：{_value(event, 'brake_acc')}\n"
        f"- ttc：{_value(event, 'ttc')}\n\n"
        f"## 2. 场景描述\n\n"
        f"{_value(ai_analysis, 'scenario_description', _value(event, 'log_text'))}\n\n"
        f"## 3. 规则命中情况\n\n"
        f"{_format_rules(matched_rules)}\n\n"
        f"## 4. 严重度评级\n\n"
        f"- severity level：{severity_level}\n"
        f"- severity score：{severity_score}\n"
        f"- 评级原因：{severity_reason}\n"
        f"- 评分因子：\n{_markdown_list(_value(severity, 'factors', []))}\n\n"
        f"## 5. AI 原因分析\n\n"
        f"- 分析摘要：{_value(ai_analysis, 'summary')}\n"
        f"- 风险判断：{_value(ai_analysis, 'risk_assessment')}\n"
        f"- 可能原因：\n{_markdown_list(possible_causes)}\n\n"
        f"## 6. 关键证据\n\n"
        f"{_markdown_list(_collect_key_evidence(event, matched_rules))}\n\n"
        f"## 7. 处理建议\n\n"
        f"{_markdown_list(recommendations)}\n\n"
        f"## 8. 是否建议人工复核\n\n"
        f"- 结论：{_yes_no(need_human_review)}\n"
    )


def save_report(event_id: str, report_content: str) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{event_id}_report.md"
    report_path.write_text(report_content, encoding="utf-8")
    return str(report_path)


def build_mock_report(
    event: dict,
    rule_hits: list[str],
    severity: str,
    analysis: str,
) -> str:
    return generate_markdown_report(
        event,
        rule_hits,
        {"level": severity, "score": "未知", "reason": "Mock severity result."},
        {
            "summary": analysis,
            "scenario_description": event.get("log_text", "Mock event scenario."),
            "possible_causes": [analysis],
            "risk_assessment": "Mock AI analysis result.",
            "recommendations": ["复核事件日志和规则命中结果。"],
            "need_human_review": severity in {"S", "A"},
        },
    )
