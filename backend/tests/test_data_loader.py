from backend.skills.data_loader import filter_events, get_event_by_id, load_events


def test_load_events_returns_records():
    events = load_events()

    assert len(events) == 500
    assert events[0]["event_id"] == "EVT_0001"
    assert events[-1]["event_id"] == "EVT_0500"
    assert isinstance(events[0]["ego_speed"], float)
    assert isinstance(events[0]["brake_acc"], float)
    assert isinstance(events[0]["steering_angle"], float)
    assert isinstance(events[0]["lane_confidence"], float)
    assert isinstance(events[0]["object_confidence"], float)
    assert isinstance(events[0]["ttc"], float)
    assert isinstance(events[0]["lateral_offset"], float)
    assert isinstance(events[0]["takeover"], bool)
    assert isinstance(events[0]["aeb_triggered"], bool)


def test_get_event_by_id_existing_event():
    event = get_event_by_id("EVT_0001")

    assert event is not None
    assert event["event_id"] == "EVT_0001"
    assert event["scene_type"] == "城市路口两轮车疑似误刹"


def test_get_event_by_id_missing_event():
    assert get_event_by_id("EVT_9999") is None


def test_filter_events_by_scene_type():
    events = filter_events(scene_type="高速跟车急刹")

    assert len(events) == 50
    assert all(event["scene_type"] == "高速跟车急刹" for event in events)


def test_filter_events_by_takeover():
    events = filter_events(takeover=True)

    assert events
    assert all(event["takeover"] is True for event in events)


def test_filter_events_by_aeb_triggered():
    events = filter_events(aeb_triggered=True)

    assert events
    assert all(event["aeb_triggered"] is True for event in events)
