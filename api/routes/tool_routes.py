"""
tool_routes.py

Purpose:
API routes for AI tool registry.
"""

from fastapi import APIRouter

from api.services.tool_service import (
    get_all_tools,
    get_tool_by_id,
)


router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)


@router.get("/")
def fetch_all_tools():

    return get_all_tools()


@router.get("/{tool_id}")
def fetch_tool_by_id(tool_id: str):

    return get_tool_by_id(tool_id)