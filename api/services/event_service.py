"""
event_service.py

Purpose:
Loads and saves AI runtime governance events.
"""

from pathlib import Path
import json


EVENTS_FILE = Path("data/runtime/ai_runtime_events.json")


def ensure_event_file_exists():
    """
    Creates runtime folder and event file if missing.
    """

    EVENTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not EVENTS_FILE.exists():
        with open(EVENTS_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def load_events() -> list:
    """
    Loads all runtime events.
    """

    ensure_event_file_exists()

    with open(EVENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_event(event: dict) -> dict:
    """
    Appends one runtime event.
    """

    events = load_events()

    events.append(event)

    with open(EVENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4)

    return event


def get_recent_events(limit: int = 1000) -> list:
    """
    Returns most recent runtime events.
    """

    events = load_events()

    return events[-limit:]


def get_blocked_events() -> list:
    """
    Returns blocked runtime events.
    """

    events = load_events()

    return [
        event
        for event in events
        if event.get("decision") == "Blocked"
    ]

def get_all_events() -> list:
    """
    Backward-compatible function used by event_routes.py.
    Returns all runtime events.
    """

    return load_events()