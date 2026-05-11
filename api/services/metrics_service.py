"""
metrics_service.py

Purpose:
Calculates governance dashboard metrics.
"""

from api.services.event_service import (
    load_events,
)


def calculate_summary_metrics():
    """
    Calculates executive governance metrics.
    """

    events = load_events()

    total_requests = len(events)

    if total_requests == 0:

        return {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "review_required_requests": 0,
            "high_risk_events": 0,
            "average_risk_score": 0,
            "average_hallucination_score": 0,
            "blocked_rate": 0,
        }

    allowed_requests = len(
        [
            event
            for event in events
            if event.get("decision") == "Allowed"
        ]
    )

    blocked_requests = len(
        [
            event
            for event in events
            if event.get("decision") == "Blocked"
        ]
    )

    review_required_requests = len(
        [
            event
            for event in events
            if event.get("decision") == "Allowed with Review"
        ]
    )

    high_risk_events = len(
        [
            event
            for event in events
            if event.get("risk_score", 0) >= 0.75
        ]
    )

    average_risk_score = round(
        sum(
            event.get("risk_score", 0)
            for event in events
        ) / total_requests,
        2,
    )

    average_hallucination_score = round(
        sum(
            event.get("hallucination_risk_score", 0)
            for event in events
        ) / total_requests,
        2,
    )

    blocked_rate = round(
        (blocked_requests / total_requests) * 100,
        2,
    )

    return {
        "total_requests": total_requests,
        "allowed_requests": allowed_requests,
        "blocked_requests": blocked_requests,
        "review_required_requests": review_required_requests,
        "high_risk_events": high_risk_events,
        "average_risk_score": average_risk_score,
        "average_hallucination_score": average_hallucination_score,
        "blocked_rate": blocked_rate,
    }