# AutoDrive Insight Agent

AutoDrive Insight Agent is an AI product demo for intelligent driving production data analysis. It showcases an end-to-end workflow for automatic abnormal event screening, severity grading, AI-assisted root cause analysis, and report generation.

## Project Positioning

This project targets intelligent driving mass-production feedback data scenarios. The current demo uses mock driving events and reserved module boundaries so the system can later evolve into a full pipeline with CSV data loading, rule-based event detection, S/A/B/C/D severity grading, Mock or real LLM analysis, and Markdown report generation.

## Current Status

This version completes the local base skeleton only:

- FastAPI backend with health check and mock API routes
- Skill-style backend modules for data loading, rule engine, severity grading, LLM analysis, and report generation
- React + TypeScript + Vite frontend
- Ant Design layout with Dashboard, Event List, Event Detail, and Report pages
- Data, reports, docs, and screenshots directories reserved for future modules

## Backend Startup

```bash
cd autodrive-insight-agent/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

API endpoints:

- `GET /health`
  - Returns `{"status": "ok", "service": "AutoDrive Insight Agent"}`.
- `GET /api/events`
  - Returns the event list.
  - Supports optional query parameters: `scene_type`, `takeover`, and `aeb_triggered`.
  - Example: `GET /api/events?takeover=true&aeb_triggered=true`
- `GET /api/events/{event_id}`
  - Returns one event by ID.
  - Returns `404` when the event does not exist.
- `POST /api/analyze/{event_id}`
  - Runs `agent_orchestrator.analyze_event(event_id)` and returns the complete analysis result, including event data, matched rules, severity, AI analysis, Markdown report, and report path.
  - Returns `404` when the event does not exist.
- `GET /api/report/{event_id}`
  - Returns the Markdown report as `{"event_id": "...", "report_format": "markdown", "content": "..."}`.
  - Stable behavior: if `reports/{event_id}_report.md` already exists, the API returns it directly; if it does not exist, the API automatically calls `analyze_event(event_id)` to generate and save the report before returning it.
  - Returns `404` when the event does not exist.

Interactive API docs are available after startup at:

```text
http://127.0.0.1:8000/docs
```

## Data Module

The demo intelligent-driving event dataset is stored in `data/demo_events.csv`.
It contains 500 simulated abnormal events with event IDs from `EVT_0001` to
`EVT_0500`, covering urban intersection false braking, highway following hard
braking, rainy lane-confidence degradation, nighttime pedestrian miss detection,
ramp planning offset, construction-zone lane recognition anomalies, ACC
following instability, NOA exit, driver takeover, and AEB false trigger cases.

`backend/skills/data_loader.py` provides:

- `load_events()`
- `get_event_by_id(event_id)`
- `filter_events(scene_type=None, takeover=None, aeb_triggered=None)`

Numeric driving metrics are converted to `float` after CSV loading, while
`takeover` and `aeb_triggered` are converted to `bool`.

## Frontend Startup

```bash
cd autodrive-insight-agent/frontend
npm install
npm run dev
```

Vite will serve the frontend at:

```text
http://localhost:5173
```

## Testing

Backend test dependencies are included in `backend/requirements.txt`.

```bash
cd autodrive-insight-agent/backend
pytest
```

Data module checks can be run from the repository root:

```bash
python -m compileall backend
python -m pytest backend/tests/test_data_loader.py
```

API checks can be run from the repository root:

```bash
python -m compileall backend
python -m pytest backend/tests/test_api.py
```

At this stage, complex business logic has not been implemented yet. The goal is to keep the structure clear and ready for incremental module development.

## Rule Engine

The backend rule engine is implemented in `backend/skills/rule_engine.py`.
Use `screen_event_rules(event: dict) -> list` to screen one intelligent driving event.

Each matched rule returns:

- `rule_id`
- `rule_name`
- `description`
- `evidence`
- `risk_score`

Implemented rules:

- `R001` 强制动: `brake_acc <= -3.5`
- `R002` AEB触发: `aeb_triggered == True`
- `R003` 疑似误刹: `aeb_triggered == True`, `object_confidence < 0.5`, and `brake_acc <= -3.0`
- `R004` 高风险接管: `takeover == True` and `ego_speed > 40`
- `R005` 车道线异常: `lane_confidence < 0.4` and `lateral_offset > 0.5`
- `R006` TTC过低: `ttc <= 1.5`
- `R007` 规划异常: `planning_status` contains `abnormal` or `deviation`
- `R008` 感知异常: `perception_status` contains `unstable`, `lost`, or `low_confidence`

## Severity Grading

The severity grading skill is implemented in `backend/skills/severity_grader.py`.
Use `grade_severity(event: dict, matched_rules: list) -> dict` to convert one
screened event into an S/A/B/C/D severity result.

The returned dictionary contains:

- `score`: integer severity score
- `level`: one of `S`, `A`, `B`, `C`, or `D`
- `reason`: readable summary of the grading result
- `factors`: scoring factors triggered by the event

Scoring factors:

- `aeb_triggered == True`: +25
- `takeover == True`: +25
- `brake_acc <= -3.5`: +20
- `ttc <= 1.5`: +20
- `object_confidence < 0.5`: +10
- `scene_type` contains `高速` or `城市路口`: +10

Level mapping:

- `S`: score >= 80
- `A`: score >= 60
- `B`: score >= 40
- `C`: score >= 20
- `D`: score < 20

## Report Generation

报告生成 Skill 位于 `backend/skills/report_generator.py`，用于把单个智能驾驶异常事件、规则命中结果、严重度评级和 AI 分析结果汇总为中文 Markdown 报告。

核心函数：

- `generate_markdown_report(event: dict, matched_rules: list, severity: dict, ai_analysis: dict) -> str`
- `save_report(event_id: str, report_content: str) -> str`

报告固定包含以下章节：

- 事件基本信息
- 场景描述
- 规则命中情况
- 严重度评级
- AI 原因分析
- 关键证据
- 处理建议
- 是否建议人工复核

生成内容会包含 `event_id`、`vehicle_id`、`timestamp`、`scene_type`、`weather`、`ego_speed`、`brake_acc`、`ttc`、`severity level` 和 `severity score`。`save_report` 会把报告保存到 `reports/{event_id}_report.md`，当 `reports/` 不存在时会自动创建目录。

可从仓库根目录运行报告生成测试：

```bash
python -m compileall backend
python -m pytest backend/tests/test_report_generator.py
```

## AI Analysis Skill

The AI analysis skill is implemented in `backend/skills/llm_analyzer.py`.
Use `analyze_with_llm(event: dict, matched_rules: list, severity: dict) -> dict`
to produce a structured analysis for one screened and graded event.

By default, the skill runs in Mock mode and does not require `OPENAI_API_KEY`.
If `OPENAI_API_KEY` is present, the module has a reserved real-LLM integration
point, but the local demo and tests still run without external API dependency.

The returned dictionary contains:

- `summary`: concise event-level analysis summary
- `scenario_description`: scenario and key driving-signal context
- `possible_causes`: at least two possible causes derived from event data and matched rules
- `risk_assessment`: severity-aware risk explanation
- `recommendations`: at least two follow-up recommendations
- `need_human_review`: `True` for `S` or `A` severity levels

AI analysis checks can be run from the repository root:

```bash
python -m compileall backend
python -m pytest backend/tests/test_llm_analyzer.py
```

## Agent Workflow Orchestrator

The lightweight Agent Orchestrator is implemented in
`backend/agent_orchestrator.py`. It coordinates the backend skills in this
fixed workflow:

```text
load_event(event_id)
-> rule_screening(event)
-> severity_grading(event, matched_rules)
-> llm_analysis(event, matched_rules, severity)
-> report_generation(event, matched_rules, severity, ai_analysis)
```

Use `analyze_event(event_id: str) -> dict` to run the full pipeline for one
event. A successful result contains:

- `event`
- `matched_rules`
- `severity`
- `ai_analysis`
- `report`
- `report_path`

If the event ID does not exist, `analyze_event` returns an explicit error
dictionary with `error`, `event_id`, and `message`.

Reports are generated as Markdown and saved automatically under
`reports/{event_id}_report.md`.

Run the orchestrator from the repository root:

```bash
python backend/agent_orchestrator.py --event_id EVT_0001
```

The command prints the analysis summary, severity, matched-rule count, and saved
report path.

Orchestrator checks can be run from the repository root:

```bash
python -m compileall backend
python -m pytest backend/tests/test_agent_orchestrator.py
```
