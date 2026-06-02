from pydantic import BaseModel, Field


class DrivingEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    vehicle_id: str
    event_type: str
    severity: str
    summary: str


class AnalysisResult(BaseModel):
    event: DrivingEvent
    rule_hits: list[str]
    severity: str
    analysis: str
    report: str
