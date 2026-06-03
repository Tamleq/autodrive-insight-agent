import asyncio
import json
from urllib.parse import urlencode

from backend.main import app


def request(method: str, path: str, query: dict | None = None) -> tuple[int, dict | list]:
    messages = []
    query_string = urlencode(query or {}).encode("ascii")
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": query_string,
        "headers": [(b"host", b"testserver")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(app(scope, receive, send))

    status_code = next(message["status"] for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return status_code, json.loads(body)


def test_health_returns_200():
    status_code, body = request("GET", "/health")

    assert status_code == 200
    assert body == {
        "status": "ok",
        "service": "AutoDrive Insight Agent",
    }


def test_get_events_returns_list():
    status_code, events = request("GET", "/api/events")

    assert status_code == 200
    assert isinstance(events, list)
    assert events
    assert events[0]["event_id"] == "EVT_0001"


def test_get_event_returns_single_event():
    status_code, event = request("GET", "/api/events/EVT_0001")

    assert status_code == 200
    assert event["event_id"] == "EVT_0001"
    assert event["vehicle_id"]
    assert "scene_type" in event


def test_missing_event_returns_404():
    status_code, _body = request("GET", "/api/events/EVT_9999")

    assert status_code == 404


def test_analyze_event_returns_analysis_result():
    status_code, result = request("POST", "/api/analyze/EVT_0001")

    assert status_code == 200
    assert result["event"]["event_id"] == "EVT_0001"
    assert isinstance(result["matched_rules"], list)
    assert isinstance(result["severity"], dict)
    assert isinstance(result["ai_analysis"], dict)
    assert isinstance(result["report"], str)
