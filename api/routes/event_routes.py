"""
event_routes.py

Purpose:
API routes for AI runtime events.
"""

from fastapi import APIRouter

from api.services.event_service import (
    get_all_events,
    get_recent_events,
    get_blocked_events,
)


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("/")
def fetch_all_events():

    return get_all_events()


@router.get("/recent")
def fetch_recent_events(limit: int = 50):

    return get_recent_events(limit)


@router.get("/blocked")
def fetch_blocked_events():

    return get_blocked_events()