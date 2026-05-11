"""
tool_service.py

Purpose:
Handles AI tool registry operations.
"""

from pathlib import Path
import json


TOOLS_FILE = Path(
    "data/semi_structured/tools.json"
)


def load_tools():

    with open(TOOLS_FILE, "r") as f:

        tools = json.load(f)

    return tools


def get_all_tools():

    return load_tools()


def get_tool_by_id(tool_id: str):

    tools = load_tools()

    for tool in tools:

        if tool["tool_id"] == tool_id:
            return tool

    return None