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

Reserved mock APIs:

- `GET /api/events`
- `GET /api/events/{event_id}`
- `POST /api/analyze/{event_id}`
- `GET /api/report/{event_id}`

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

Backend test dependencies are included in `backend/requirements.txt`. The `backend/tests` directory is reserved for future unit tests.

```bash
cd autodrive-insight-agent/backend
pytest
```

Data module checks can be run from the repository root:

```bash
python -m compileall backend
python -m pytest backend/tests/test_data_loader.py
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
