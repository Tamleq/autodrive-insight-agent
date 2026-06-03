from pathlib import Path as FsPath
from typing import Any

from fastapi import FastAPI, HTTPException, Path, Query

try:
    from backend.agent_orchestrator import analyze_event, get_event_by_id, list_events
    from backend.models.schemas import AnalysisResult, DrivingEvent, HealthResponse, ReportResponse
except ModuleNotFoundError:
    from agent_orchestrator import analyze_event, get_event_by_id, list_events
    from models.schemas import AnalysisResult, DrivingEvent, HealthResponse, ReportResponse


app = FastAPI(
    title="AutoDrive Insight Agent 后端 API",
    description="面向智能驾驶异常事件的分析接口，支持事件查询、规则分析、严重度评级和 Markdown 报告生成。",
    version="0.1.0",
    openapi_tags=[
        {"name": "系统状态", "description": "后端服务状态检查接口。"},
        {"name": "事件查询", "description": "智能驾驶异常事件列表、筛选和详情查询接口。"},
        {"name": "分析报告", "description": "事件分析和 Markdown 报告生成接口。"},
    ],
)

SERVICE_NAME = "AutoDrive Insight Agent"
REPORTS_DIR = FsPath(__file__).resolve().parents[1] / "reports"


def _not_found(event_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"事件不存在：{event_id}")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["系统状态"],
    summary="健康检查",
    description="返回后端服务是否可用。",
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME)


@app.get(
    "/api/events",
    response_model=list[DrivingEvent],
    tags=["事件查询"],
    summary="查询事件列表",
    description="返回智能驾驶异常事件列表，并支持按场景、接管标记和 AEB 触发标记筛选。",
)
def get_events(
    scene_type: str | None = Query(default=None, description="按驾驶场景类型筛选"),
    takeover: bool | None = Query(default=None, description="按是否发生人工接管筛选"),
    aeb_triggered: bool | None = Query(default=None, description="按是否触发 AEB 筛选"),
) -> list[dict[str, Any]]:
    events = list_events()
    if scene_type is not None:
        events = [event for event in events if event["scene_type"] == scene_type]
    if takeover is not None:
        events = [event for event in events if event["takeover"] is takeover]
    if aeb_triggered is not None:
        events = [event for event in events if event["aeb_triggered"] is aeb_triggered]
    return events


@app.get(
    "/api/events/{event_id}",
    response_model=DrivingEvent,
    tags=["事件查询"],
    summary="查询事件详情",
    description="根据 event_id 返回单个智能驾驶异常事件详情；事件不存在时返回 404。",
)
def get_event(
    event_id: str = Path(..., description="事件 ID，例如 EVT_0001"),
) -> dict[str, Any]:
    event = get_event_by_id(event_id)
    if event is None:
        raise _not_found(event_id)
    return event


@app.post(
    "/api/analyze/{event_id}",
    response_model=AnalysisResult,
    tags=["分析报告"],
    summary="分析事件",
    description="调用 Agent Orchestrator 完成规则命中、严重度评级、AI 分析和报告生成。",
)
def analyze_event_by_id(
    event_id: str = Path(..., description="事件 ID，例如 EVT_0001"),
) -> dict[str, Any]:
    result = analyze_event(event_id)
    if "error" in result:
        raise _not_found(event_id)
    return result


@app.get(
    "/api/report/{event_id}",
    response_model=ReportResponse,
    tags=["分析报告"],
    summary="获取 Markdown 报告",
    description="返回事件 Markdown 报告；如果报告尚不存在，会先自动分析并生成报告。",
)
def get_report(
    event_id: str = Path(..., description="事件 ID，例如 EVT_0001"),
) -> ReportResponse:
    event = get_event_by_id(event_id)
    if event is None:
        raise _not_found(event_id)

    report_path = REPORTS_DIR / f"{event_id}_report.md"
    if not report_path.exists():
        result = analyze_event(event_id)
        if "error" in result:
            raise _not_found(event_id)
        content = result["report"]
    else:
        content = report_path.read_text(encoding="utf-8")

    return ReportResponse(event_id=event_id, report_format="markdown", content=content)
