import csv
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "demo_events.csv"

FLOAT_FIELDS = {
    "ego_speed",
    "brake_acc",
    "steering_angle",
    "lane_confidence",
    "object_confidence",
    "ttc",
    "lateral_offset",
}
BOOL_FIELDS = {"takeover", "aeb_triggered"}
TRUE_VALUES = {"1", "true", "yes", "y"}


def _to_bool(value: str) -> bool:
    return value.strip().lower() in TRUE_VALUES


def _convert_event(row: dict[str, str]) -> dict[str, Any]:
    event: dict[str, Any] = dict(row)
    for field in FLOAT_FIELDS:
        event[field] = float(event[field])
    for field in BOOL_FIELDS:
        event[field] = _to_bool(event[field])
    return event


def load_events() -> list[dict[str, Any]]:
    with DATA_FILE.open(newline="", encoding="utf-8") as csv_file:
        return [_convert_event(row) for row in csv.DictReader(csv_file)]


def get_event_by_id(event_id: str) -> dict[str, Any] | None:
    return next((event for event in load_events() if event["event_id"] == event_id), None)


def filter_events(
    scene_type: str | None = None,
    takeover: bool | None = None,
    aeb_triggered: bool | None = None,
) -> list[dict[str, Any]]:
    events = load_events()
    if scene_type is not None:
        events = [event for event in events if event["scene_type"] == scene_type]
    if takeover is not None:
        events = [event for event in events if event["takeover"] is takeover]
    if aeb_triggered is not None:
        events = [event for event in events if event["aeb_triggered"] is aeb_triggered]
    return events


def load_mock_events() -> list[dict[str, Any]]:
    events = load_events()
    for event in events:
        event.setdefault("event_type", "SMART_DRIVING_ANOMALY")
        event.setdefault("severity", "D")
        event.setdefault("summary", event["log_text"])
    return events
