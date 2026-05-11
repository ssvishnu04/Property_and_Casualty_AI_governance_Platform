"""
metrics_routes.py

Purpose:
API routes for governance dashboard metrics.
"""

from fastapi import APIRouter

from api.services.metrics_service import (
    calculate_summary_metrics,
)


router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


@router.get("/summary")
def fetch_summary_metrics():

    return calculate_summary_metrics()