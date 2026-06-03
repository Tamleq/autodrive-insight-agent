from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="服务健康状态")
    service: str = Field(..., description="服务名称")


class DrivingEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str = Field(..., description="事件唯一标识")
    vehicle_id: str = Field(..., description="车辆标识")
    timestamp: str = Field(..., description="事件发生时间")
    scene_type: str = Field(..., description="驾驶场景类型")
    weather: str = Field(..., description="天气")
    ego_speed: float = Field(..., description="自车速度")
    brake_acc: float = Field(..., description="制动加速度")
    takeover: bool = Field(..., description="是否发生人工接管")
    aeb_triggered: bool = Field(..., description="是否触发 AEB")
    event_type: str = Field(..., description="标准化事件类型")
    severity: str = Field(..., description="默认展示严重度")
    summary: str = Field(..., description="事件摘要")


class AnalysisResult(BaseModel):
    event: dict[str, Any] = Field(..., description="事件原始数据")
    matched_rules: list[dict[str, Any]] = Field(..., description="命中的规则列表")
    severity: dict[str, Any] = Field(..., description="严重度评级结果")
    ai_analysis: dict[str, Any] = Field(..., description="AI 分析结果")
    report: str = Field(..., description="Markdown 报告内容")
    report_path: str = Field(..., description="报告保存路径")


class ReportResponse(BaseModel):
    event_id: str = Field(..., description="事件 ID")
    report_format: str = Field(default="markdown", description="报告格式")
    content: str = Field(..., description="Markdown 报告内容")
