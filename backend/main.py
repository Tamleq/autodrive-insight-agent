from fastapi import FastAPI, HTTPException

from agent_orchestrator import analyze_event, get_event_by_id, list_events


app = FastAPI(
    title="AutoDrive Insight Agent API",
    description="AI demo API for intelligent driving event analysis.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "autodrive-insight-agent"}


@app.get("/api/events")
def get_events() -> list[dict]:
    return list_events()


@app.get("/api/events/{event_id}")
def get_event(event_id: str) -> dict:
    event = get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/analyze/{event_id}")
def analyze_event_by_id(event_id: str) -> dict:
    result = analyze_event(event_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return result


@app.get("/api/report/{event_id}")
def get_report(event_id: str) -> dict:
    event = get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "event_id": event_id,
        "report_format": "markdown",
        "content": (
            f"# AutoDrive Insight Report\n\n"
            f"- Event ID: {event['event_id']}\n"
            f"- Severity: {event['severity']}\n"
            f"- Summary: {event['summary']}\n"
        ),
    }
